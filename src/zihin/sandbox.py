"""Container lifecycle: born per episode, runs code, torn down.

**Topology.** Two unix sockets, two directions, and the container has no network:

    host                                        container
    ────                                        ─────────
    recording proxy  ◀── apis.sock (read-only mount) ◀── bridge ◀── apis.*
         │                                                        (the agent's code)
         ▼
    appworld serve apis (host, 127.0.0.1)

    AppWorld(remote_environment_url=…) ──▶ TCP bridge ──▶ environment socket
                                                            (fd 3, inherited)
                                                                 ▼
                                                    appworld serve environment

**Why two sockets.** `--network=none` cuts both directions: the container not
reaching out is what we want, the host reaching in is necessary. The
container→host direction is solved with a read-only mounted socket, the
host→container direction with a socket the host binds and whose descriptor it
passes across. The second does not require the container to write into the
directory; measured.

**Two ports, and keeping them apart was learned by measurement.**
`remote_apis_url` is a single string used on both sides: inside the container
`127.0.0.1:8123` is the bridge, on the host the same number is the API server.
The namespaces are separate, so the same string resolves to the right thing on
both sides. But the host-side **environment** bridge has to be on a different
number; on the first attempt, given the same number, the bridge could not bind
the port and — worse — the readiness check saw the API server's 200 and declared
"environment ready". The check now looks at the answering server's FastAPI title.

**What is recorded.** Nothing; the recording is in the proxy. This module only
manages the container's lifetime and enforces the limits.

**Logs are copied out after the episode ends** (K-94). There is no writable mount
during the run, because `experiments/outputs` also carries the databases the
verifier reads, and mounting that writable is exactly the first threat's surface.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from zihin.socket_bridge import serve as bridge_serve


def _megabytes(text: Any, index: int = 0) -> float:
    """Converts the `podman stats` memory field to megabytes: `161.4MB / 536.9MB`."""
    if not text:
        return 0.0
    parca = str(text).split("/")[index].strip()
    count = "".join(c for c in parca if c.isdigit() or c == ".")
    if not count:
        return 0.0
    value = float(count)
    if "GB" in parca:
        value *= 1024
    elif "kB" in parca or "KB" in parca:
        value /= 1024
    return round(value, 1)


def _percent(text: Any) -> float:
    if not text:
        return 0.0
    return round(float(str(text).replace("%", "").strip() or 0), 2)


class SandboxError(RuntimeError):
    """The container could not be built, did not run, or was not in the expected state."""


@dataclass(frozen=True)
class SandboxConfig:
    """Contents of `config/sandbox.yaml`.

    The module that consumes the schema is the one that reads it, the same
    pattern as `shield.load_write_set`: a reader outside the place that uses the
    value means a second schema that goes stale in silence.
    """

    image_name: str
    image_tag: str
    network_mode: str
    socket_directory: str
    socket_name: str
    bridge_port: int
    environment_port: int
    memory_bytes: int
    pids_limit: int
    step_timeout_seconds: int
    tmpfs_bytes: int
    cpus: float
    writable_path: str
    outputs_path: str
    data_directory: str

    @property
    def image(self) -> str:
        return f"{self.image_name}:{self.image_tag}"

    @property
    def apis_socket(self) -> str:
        return os.path.join(self.socket_directory, self.socket_name)

    @property
    def environment_socket(self) -> str:
        return os.path.join(self.socket_directory, "environment.sock")

    def manifest_fields(self) -> dict[str, Any]:
        """The fields that enter the manifest. The limits affect the measurement,
        so all of them enter the record (K-C)."""
        return {
            "sandbox_image": self.image,
            "sandbox_network_mode": self.network_mode,
            "sandbox_memory_bytes": self.memory_bytes,
            "sandbox_pids_limit": self.pids_limit,
            "sandbox_step_timeout_seconds": self.step_timeout_seconds,
            "sandbox_tmpfs_bytes": self.tmpfs_bytes,
            "sandbox_cpus": self.cpus,
        }


_FIELDS = {
    "image_name": str,
    "image_tag": str,
    "network_mode": str,
    "socket_directory": str,
    "socket_name": str,
    "bridge_port": int,
    "environment_port": int,
    "memory_bytes": int,
    "pids_limit": int,
    "step_timeout_seconds": int,
    "tmpfs_bytes": int,
    "cpus": float,
    "writable_path": str,
    "outputs_path": str,
    "data_directory": str,
}


def load_sandbox_config(path: str | Path = "config/sandbox.yaml") -> SandboxConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    missing = set(_FIELDS) - set(raw)
    extra = set(raw) - set(_FIELDS)
    if missing:
        raise SandboxError(f"missing field in sandbox config: {sorted(missing)}")
    if extra:
        raise SandboxError(f"unrecognised field in sandbox config: {sorted(extra)}")
    for name, kind in _FIELDS.items():
        value = raw[name]
        if kind is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if not isinstance(value, kind) or isinstance(value, bool):
            raise SandboxError(f"{name}: {kind.__name__} bekleniyordu, {value!r} geldi")
        raw[name] = value
    if raw["network_mode"] != "none":
        # Measured: the default netavark, pasta and slirp4netns modes all three
        # reach the outside network (K-95). Accepting another value would make a
        # measured isolation switchable off by configuration.
        raise SandboxError(
            f"network_mode can only be 'none', got {raw['network_mode']!r}: "
            "the other modes were measured to reach the outside network (K-95)"
        )
    for name in ("memory_bytes", "pids_limit", "step_timeout_seconds", "tmpfs_bytes"):
        if raw[name] <= 0:
            raise SandboxError(f"{name} must be positive, got {raw[name]!r}")
    return SandboxConfig(**raw)


def podman_available() -> bool:
    return shutil.which("podman") is not None


def image_exists(config: SandboxConfig) -> bool:
    finished = subprocess.run(
        ["podman", "image", "exists", config.image], capture_output=True, check=False
    )
    return finished.returncode == 0


def build_image(config: SandboxConfig, containerfile: str = "Containerfile") -> str:
    """Builds the image and returns its digest.

    The digest is the image's own digest, not a hand-incremented number: a
    hand-incremented number is a number the hand forgets.
    """
    subprocess.run(
        ["podman", "build", "-t", config.image, "-f", containerfile, "."],
        check=True,
    )
    return image_digest(config)


def image_digest(config: SandboxConfig) -> str:
    finished = subprocess.run(
        ["podman", "image", "inspect", config.image, "--format", "{{.Digest}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return finished.stdout.strip()


@dataclass
class Sandbox:
    """One episode's container.

    `name` is episode-specific: the container is born again every episode (the
    threat model's main defence against the second threat) and any leftover
    carrying the same name is torn down.
    """

    config: SandboxConfig
    name: str
    _process: Any = None
    _listener: Any = None
    _port_listener: Any = None
    _bridge: Any = None
    _sampling: bool = False
    samples: list = field(default_factory=list)

    # --- lifetime ---

    def start(self) -> None:
        if not podman_available():
            raise SandboxError("podman is not installed")
        self._remove_stale()
        os.makedirs(self.config.socket_directory, exist_ok=True)
        self._listener = self._bind_environment_socket()
        # The bridge's port is bound **here**, not inside the thread. The reason
        # is a measured fault: with the bind done in the thread, the exception was
        # swallowed in the daemon thread even when someone else held the port, the
        # run carried on, and `remote_environment_url` connected to **another**
        # server holding the port. The episode ran and never entered the
        # container.
        self._port_listener = self._bind_bridge_port()
        self._bridge = threading.Thread(
            target=bridge_serve,
            args=(self.config.environment_socket, self.config.environment_port),
            kwargs={"listener": self._port_listener},
            daemon=True,
            name="environment-bridge",
        )
        # The bridge is on the host side: `remote_environment_url` wants an
        # http:// address and `requests` does not know unix sockets.
        self._bridge.start()
        self._process = subprocess.Popen(
            self._launch_command(self._listener.fileno()),
            pass_fds=(self._listener.fileno(),),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if self._process.poll() is not None:
            raise SandboxError(f"podman exited immediately: code={self._process.returncode}")

    def _bind_bridge_port(self) -> socket.socket:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(("127.0.0.1", self.config.environment_port))
        except OSError as error:
            listener.close()
            raise SandboxError(
                f"the environment bridge's port ({self.config.environment_port}) could not "
                f"be bound: {error}. If another server holds the port the episode never "
                "enters the container."
            ) from error
        listener.listen(16)
        return listener

    # The launcher that moves the descriptor to 3 in the child and `exec`s
    # podman. It does not touch the parent's descriptor table.
    _REMAP = (
        "import os, sys; os.dup2(int(sys.argv[1]), 3); "
        "os.set_inheritable(3, True); os.execvp(sys.argv[2], sys.argv[2:])"
    )

    def _launch_command(self, fd: int) -> list[str]:
        """`podman run`, with the descriptor moved to 3 in the child.

        `--preserve-fds 1` wants the descriptor to be **exactly 3 in the child**,
        and where that move happens produced two faults:

        1. `dup2(fd, 3)` in the parent worked the first time and broke the
           second: when the proxy had started earlier it held fd 3, and `dup2`
           overwrote it in silence. The result was a bridge that raised no error
           and did not work.
        2. Moving it with a shell did not work either: `/bin/sh` here is dash and
           it refuses a multi-digit descriptor in a redirection with `Bad fd
           number`. When the proxy starts first the descriptor can exceed 10.

        The third form is deterministic: a small Python launcher does the `dup2`
        and `exec`s podman. No shell, no limit on the descriptor number, and the
        parent's table is untouched.
        """
        if fd == 3:
            return self._run_command()
        return [sys.executable, "-c", self._REMAP, str(fd), *self._run_command()]

    def _bind_environment_socket(self) -> socket.socket:
        """The host binds the socket itself and passes the descriptor across.

        Having the container create a socket file would need a writable mount and
        that is forbidden (K-94). In this direction the container only accepts.
        """
        path = self.config.environment_socket
        if os.path.exists(path):
            os.unlink(path)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(path)
        listener.listen(16)
        os.chmod(path, 0o666)
        # The descriptor will be inherited by the child; moving it to 3 happens
        # inside `_launch_command`, on the child's side.
        os.set_inheritable(listener.fileno(), True)
        return listener

    def _run_command(self) -> list[str]:
        data = os.path.abspath(self.config.data_directory)
        return [
            "podman",
            "run",
            "--rm",
            "--name",
            self.name,
            f"--network={self.config.network_mode}",
            "--read-only",
            f"--tmpfs={self.config.writable_path}:size={self.config.tmpfs_bytes}",
            # AppWorld writes its logs here. tmpfs, so it never touches the host
            # filesystem; they are fetched with `podman cp` after the episode ends
            # (K-94).
            f"--tmpfs={self.config.outputs_path}:size={self.config.tmpfs_bytes}",
            f"--memory={self.config.memory_bytes}",
            f"--pids-limit={self.config.pids_limit}",
            f"--cpus={self.config.cpus}",
            # No new privileges: inside the container a setuid binary becomes
            # useless.
            "--security-opt=no-new-privileges",
            "--cap-drop=ALL",
            # The proxy's socket is read-only. Connecting was measured to work
            # under a read-only mount as well.
            "-v",
            f"{os.path.abspath(self.config.socket_directory)}:/bridge:ro",
            "-v",
            f"{data}:/zihin/data:ro",
            "--preserve-fds",
            "1",
            self.config.image,
            f"/bridge/{self.config.socket_name}",
            str(self.config.bridge_port),
        ]

    # The environment server's own FastAPI title. This is the readiness check's
    # criterion and the reason is a measured fault: when the check only asked "did
    # it return 200", looking at the wrong port made the host's API server answer
    # 200 and the container was taken to be ready. A check that goes green for the
    # wrong reason (K-49). The title separates the two servers cleanly: the API
    # server's title is "AppWorld API Server".
    ENVIRONMENT_TITLE = "AppWorld Environment Server"

    def wait_until_ready(self, timeout_seconds: int = 180) -> None:
        """Waits until the environment server **itself** answers.

        The container being up is not enough, the server has to answer. And the
        answer is verified to come from the environment server: a check that only
        looks at the status code accepts another server's 200.
        """
        import json as _json
        import time
        import urllib.error
        import urllib.request

        deadline = time.monotonic() + timeout_seconds
        last = ""
        while time.monotonic() < deadline:
            if self._process is not None and self._process.poll() is not None:
                out, err = self._process.communicate()
                raise SandboxError(
                    "the container exited before starting: "
                    f"kod={self._process.returncode} "
                    f"stderr={err.decode('utf-8', 'replace')[-600:]}"
                    f" stdout={out.decode('utf-8', 'replace')[-200:]}"
                )
            try:
                with urllib.request.urlopen(
                    self.environment_url + "/openapi.json", timeout=5
                ) as response:
                    title = _json.load(response).get("info", {}).get("title")
                    if title == self.ENVIRONMENT_TITLE:
                        # The title names the right server **type**, not the right
                        # server: a leftover environment server carries the same
                        # title. That is why the identity check is separate and
                        # mandatory.
                        self.verify_identity()
                        return
                    last = f"the answering server's title is {title!r}"
            except (urllib.error.URLError, OSError, TimeoutError, ValueError) as error:
                last = f"{type(error).__name__}: {error}"
            time.sleep(1)
        raise SandboxError(
            f"the environment server was not ready within {timeout_seconds} s: {last}"
        )

    @property
    def environment_url(self) -> str:
        return f"http://127.0.0.1:{self.config.environment_port}"

    def container_pid(self) -> int | None:
        """The pid of the container's main process as the host sees it."""
        finished = subprocess.run(
            ["podman", "inspect", self.name, "--format", "{{.State.Pid}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        text = finished.stdout.strip()
        return int(text) if text.isdigit() and int(text) > 0 else None

    def peer_pid(self) -> int | None:
        """The pid of the process on the other end of the environment socket (`SO_PEERCRED`)."""
        import struct

        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            probe.settimeout(10)
            probe.connect(self.config.environment_socket)
            raw = probe.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
        except OSError:
            return None
        finally:
            probe.close()
        pid, _uid, _gid = struct.unpack("3i", raw)
        return pid or None

    def verify_identity(self) -> dict[str, int]:
        """Confirms that what we are talking to is the container we started.

        **The rule: a run does not count until it has verified it is talking to
        what it started.** The reason was measured three times, and each time a
        leftover state produced a false green: the mutation script ran on a dirty
        tree, the verification tool read a stale file, and in this item the
        container never started at all yet the episode ran against a leftover
        environment server and looked clean.

        The criterion is `SO_PEERCRED`: information a unix socket has and TCP does
        not. The peer's pid matches `podman inspect .State.Pid` exactly
        (measured). It needs no new route, no nonce and no extra `execute` call
        inside the episode — the third of those would pollute the text the
        transparency test compares.

        On a mismatch the run fails. Running against a leftover server means
        producing a wrong measurement in silence.
        """
        expected = self.container_pid()
        seen = self.peer_pid()
        if expected is None:
            raise SandboxError(
                f"{self.name} container's pid could not be read: the container may not be up"
            )
        if seen is None:
            raise SandboxError("the environment socket's peer could not be read (no SO_PEERCRED)")
        if seen != expected:
            raise SandboxError(
                f"the environment socket's peer is not the expected process: pid={seen}, "
                f"the container's pid is {expected}. A leftover server may be on the other "
                "end, and such a run produces a wrong measurement in silence."
            )
        return {"container_pid": expected, "peer_pid": seen}

    def copy_out(self, container_path: str, host_path: str) -> bool:
        """Copies files out of the container. Called after the episode ends.

        The destination directory is **not created in advance**: copying into an
        existing directory makes `podman cp` place the source inside it, and a
        nested `logs/logs/` comes out. Measured; in the first sandbox episode the
        logs landed one level down. The destination's **parent** is created, the
        destination itself is not.
        """
        os.makedirs(os.path.dirname(host_path.rstrip("/")) or ".", exist_ok=True)
        if os.path.isdir(host_path):
            shutil.rmtree(host_path)
        finished = subprocess.run(
            ["podman", "cp", f"{self.name}:{container_path}", host_path],
            capture_output=True,
            text=True,
            check=False,
        )
        return finished.returncode == 0

    def stop(self) -> None:
        self._remove_stale()
        if self._process is not None:
            try:
                self._process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
        if self._listener is not None:
            self._listener.close()
            self._listener = None
        if self._port_listener is not None:
            self._port_listener.close()
            self._port_listener = None
        for path in (self.config.environment_socket,):
            if os.path.exists(path):
                os.unlink(path)

    def _remove_stale(self) -> None:
        subprocess.run(
            ["podman", "rm", "-f", "--time", "5", self.name], capture_output=True, check=False
        )

    # --- measurement ---

    def usage(self) -> dict[str, Any]:
        """The container's instantaneous resource usage.

        K-C wants measurement rather than estimation: the limit numbers will come
        out of this reading. `podman stats` runs once and returns JSON.
        """
        finished = subprocess.run(
            ["podman", "stats", "--no-stream", "--format", "json", self.name],
            capture_output=True,
            text=True,
            check=False,
        )
        if finished.returncode != 0 or not finished.stdout.strip():
            return {}
        rows = json.loads(finished.stdout)
        return rows[0] if rows else {}

    def sample_usage(self, interval_seconds: float = 2.0) -> None:
        """Samples usage in the background and keeps the peaks.

        A single reading does not give the peak: the number K-C wants is the
        highest usage within the episode, and an episode runs for minutes. The
        sampling interval can miss a peak — the measured value is therefore a
        lower bound and the report says so.
        """
        import time

        def loop() -> None:
            while self._sampling:
                snapshot = self.usage()
                if snapshot:
                    self.samples.append(snapshot)
                time.sleep(interval_seconds)

        self._sampling = True
        self.samples = []
        threading.Thread(target=loop, daemon=True, name="kullanim-ornekleyici").start()

    def stop_sampling(self) -> dict[str, Any]:
        """Stops sampling and returns the peaks."""
        self._sampling = False
        if not self.samples:
            return {}
        return {
            "ornek_sayisi": len(self.samples),
            "tepe_bellek_mb": max(_megabytes(s.get("mem_usage")) for s in self.samples),
            "bellek_siniri_mb": _megabytes(self.samples[-1].get("mem_usage"), index=1),
            "tepe_surec": max(int(s.get("pids") or 0) for s in self.samples),
            "tepe_cpu_yuzde": max(_percent(s.get("cpu_percent")) for s in self.samples),
            "ag_giris_cikis": self.samples[-1].get("net_io"),
            "blok_giris_cikis": self.samples[-1].get("block_io"),
            "not": (
                "the sampling interval can miss a peak, so the measured value is a lower bound"
            ),
        }

    def exited_at_limit(self) -> str | None:
        """Did the container end by hitting a limit?

        K-D wants bindingness to be demonstrated, and for that to enter the record
        the reason for termination has to be told apart. 137 = SIGKILL, the trace
        the OOM killer leaves at the memory limit.
        """
        if self._process is None or self._process.poll() is None:
            return None
        code = self._process.returncode
        if code == 137:
            return "sandbox_memory"
        if code not in (0, None):
            return f"sandbox_exit_{code}"
        return None

    def __enter__(self) -> Sandbox:
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()
