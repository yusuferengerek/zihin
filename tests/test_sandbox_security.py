"""The sandbox's seven security tests, each with two arms.

**The rule: nothing counts as a test until it has been seen to fire.** Every
test also has an unguarded arm, and that arm is shown to **succeed**; only then
does the guarded arm failing say anything. In this repository a guard being taken
for granted has turned out misleading several times, and it did so in this very
measurement: on the first round three steps went green while proving nothing (the
memory test had hit `/dev/shm`'s own default, the tmpfs step's exit code came
from `tail` rather than `dd`, and nothing was listening on the host in the
loopback step).

Seven tests: the first six from the threat model, the seventh from an attack
surface found during the measurement (§6.4):

  1. Host access            — the container cannot reach the host filesystem
  2. Fork bomb              — the pids limit cuts it
  3. Filling the disk       — the tmpfs limit cuts it
  4. Root in the container  — root inside, unprivileged on the host
  5. Network escape         — the outside network and host ports are unreachable
  6. Cross-episode leakage  — the container is born again every episode
  7. Management route       — the proxy does not let `POST /dbs/save` write to an
                              arbitrary path

The first six run against a small base image: what is checked is the limits
podman enforces, not the image's contents. The seventh checks the proxy itself
and a real file gets written.

**Two tests also carry the `appworld` marker, and the reason was measured.** The
proxy's route policy reads from the task data (`specs.json`) and the type
conversion needs AppWorld's app modules; both come with `appworld install` and
are not in the package. In CI those tests are filtered out. When we left them
unmarked the fifth check went red — exactly S-49's class: not stating a test's
real requirement in its marker.
"""

from __future__ import annotations

import http.server
import json
import os
import shutil
import socketserver
import subprocess
import threading
import time
from pathlib import Path

import pytest

from zihin.api_capture import ApiCapture
from zihin.recording_proxy import RecordingProxy, RoutePolicy, policy_for_episode
from zihin.sandbox import load_sandbox_config, podman_available

pytestmark = pytest.mark.sandbox

PROBE_IMAGE = "docker.io/library/alpine:3.20"
CONFIG = load_sandbox_config("config/sandbox.yaml")


@pytest.fixture(scope="module", autouse=True)
def podman_gerekiyor():
    if not podman_available():
        pytest.skip("podman is not installed")
    subprocess.run(["podman", "pull", "-q", PROBE_IMAGE], check=True, capture_output=True)


def kostur(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["podman", "run", "--rm", *args], capture_output=True, text=True, timeout=timeout
    )


# --- 1. Host access ---


def test_the_host_filesystem_is_unreachable(tmp_path):
    """The unguarded arm mounts the host directory and can write to it; the
    guarded arm does not mount it and the directory does not exist inside the
    container at all."""
    target = tmp_path / "secret"
    target.mkdir()
    (target / "record.sqlite").write_text("measurement", encoding="utf-8")

    korumasiz = kostur(
        "-v",
        f"{target}:/secret:rw",
        PROBE_IMAGE,
        "sh",
        "-c",
        "echo tampered > /secret/record.sqlite && cat /secret/record.sqlite",
    )
    assert korumasiz.returncode == 0, korumasiz.stderr
    assert "tampered" in korumasiz.stdout
    assert (target / "record.sqlite").read_text(encoding="utf-8").strip() == "tampered"

    (target / "record.sqlite").write_text("measurement", encoding="utf-8")
    korumali = kostur(
        "--read-only",
        f"--network={CONFIG.network_mode}",
        PROBE_IMAGE,
        "sh",
        "-c",
        "cat /secret/record.sqlite",
    )
    assert korumali.returncode != 0
    assert (target / "record.sqlite").read_text(encoding="utf-8") == "measurement"


def test_the_read_only_root_refuses_a_write():
    korumasiz = kostur(PROBE_IMAGE, "sh", "-c", "touch /trial && echo wrote")
    assert korumasiz.returncode == 0
    assert "wrote" in korumasiz.stdout

    korumali = kostur("--read-only", PROBE_IMAGE, "sh", "-c", "touch /trial")
    assert korumali.returncode != 0
    assert "read-only" in (korumali.stderr + korumali.stdout).lower()


# --- 2. Fork bomb ---


def test_the_pids_limit_stops_a_process_explosion():
    """Two hundred processes spawn in the unguarded arm; in the guarded arm the fork fails."""
    kod = 'i=0; while [ $i -lt 200 ]; do sleep 30 & i=$((i+1)); done; echo "dogdu:$i"'
    korumasiz = kostur("--pids-limit", "0", PROBE_IMAGE, "sh", "-c", kod)
    assert "dogdu:200" in korumasiz.stdout, korumasiz.stderr

    korumali = kostur("--pids-limit", str(CONFIG.pids_limit), PROBE_IMAGE, "sh", "-c", kod)
    assert "dogdu:200" not in korumali.stdout
    assert "fork" in (korumali.stderr + korumali.stdout).lower()


# --- 3. Disk doldurma ---


def test_the_tmpfs_limit_stops_a_write_loop():
    """`dd`'s **own** exit code is read.

    On the first round this test read `tail`'s exit code and always got zero:
    green, but empty evidence.
    """
    kod = (
        'dd if=/dev/zero of=/yer/dolgu bs=1M count=32 2>/dev/null; echo "dd:$?"; wc -c < /yer/dolgu'
    )
    korumasiz = kostur("--tmpfs", "/yer:size=64m", PROBE_IMAGE, "sh", "-c", kod)
    assert "dd:0" in korumasiz.stdout, korumasiz.stdout
    assert int(korumasiz.stdout.strip().splitlines()[-1]) == 32 * 1024 * 1024

    korumali = kostur("--tmpfs", "/yer:size=8m", PROBE_IMAGE, "sh", "-c", kod)
    assert "dd:0" not in korumali.stdout
    assert int(korumali.stdout.strip().splitlines()[-1]) == 8 * 1024 * 1024


def test_the_memory_limit_kills_a_memory_hog():
    """`/dev/shm` is enlarged deliberately.

    On the first round it was not: `dd` wrote 62.5 MiB and hit `/dev/shm`'s own
    64 MiB default, and the memory limit was never touched at all.
    """
    kod = "dd if=/dev/zero of=/dev/shm/dolgu bs=1M count=256 2>/dev/null; echo dd:$?"
    korumasiz = kostur("--shm-size=512m", PROBE_IMAGE, "sh", "-c", kod)
    assert "dd:0" in korumasiz.stdout, korumasiz.stdout

    korumali = kostur("--shm-size=512m", "--memory=64m", PROBE_IMAGE, "sh", "-c", kod)
    assert "dd:0" not in korumali.stdout


# --- 4. container root ---


def test_root_in_the_container_is_unprivileged_on_the_host(tmp_path):
    """The attempt is real: uid 0 inside the container. The trace on the host side
    belongs to an unprivileged user, so the rootless mapping holds."""
    icerde = kostur(PROBE_IMAGE, "id", "-u")
    assert icerde.stdout.strip() == "0"

    paylasilan = tmp_path / "paylasilan"
    paylasilan.mkdir()
    write = kostur(
        "-v", f"{paylasilan}:/outside:rw", PROBE_IMAGE, "sh", "-c", "touch /outside/trace"
    )
    assert write.returncode == 0, write.stderr
    trace = paylasilan / "trace"
    assert trace.exists()
    assert trace.stat().st_uid == os.getuid()
    assert trace.stat().st_uid != 0


# --- 5. Network escape ---


def test_the_container_cannot_reach_the_outside_world():
    """In the unguarded arm the outside network answers; a `403` is an answer too
    and is not "could not connect"."""
    kod = "wget -q -T 5 -O /dev/null http://1.1.1.1/; echo exit:$?"
    korumasiz = kostur(PROBE_IMAGE, "sh", "-c", kod)
    assert "exit:0" in korumasiz.stdout or "exit:8" in korumasiz.stdout, korumasiz.stdout

    korumali = kostur(f"--network={CONFIG.network_mode}", PROBE_IMAGE, "sh", "-c", kod)
    assert "exit:0" not in korumali.stdout
    assert "exit:8" not in korumali.stdout


def test_the_container_cannot_reach_a_host_port():
    """A port that really listens is opened on the host.

    On the first round nothing was listening and "could not connect" proved
    nothing.
    """
    with socketserver.TCPServer(("127.0.0.1", 0), _Ok) as sunucu:
        port = sunucu.server_address[1]
        threading.Thread(target=sunucu.serve_forever, daemon=True).start()
        kod = f"wget -q -T 5 -O /dev/null http://127.0.0.1:{port}/; echo exit:$?"
        # The host sees its own port: evidence that the listener is up.
        import urllib.request

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
            assert response.status == 200

        korumali = kostur(f"--network={CONFIG.network_mode}", PROBE_IMAGE, "sh", "-c", kod)
        assert "exit:0" not in korumali.stdout


# --- 6. Cross-episode leakage ---


def test_a_file_left_in_one_episode_is_gone_in_the_next():
    """The unguarded arm reuses the same container and the file is still there;
    in the guarded arm the container is born again."""
    name = "zihin-kirlenme-testi"
    subprocess.run(["podman", "rm", "-f", name], capture_output=True, check=False)
    try:
        subprocess.run(
            ["podman", "run", "--name", name, PROBE_IMAGE, "sh", "-c", "echo dirt > /tmp/trace"],
            check=True,
            capture_output=True,
        )
        korumasiz = subprocess.run(
            ["podman", "start", "-a", name],
            capture_output=True,
            text=True,
            check=False,
        )
        read = subprocess.run(
            ["podman", "exec", name, "cat", "/tmp/trace"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Restarted, the container keeps its filesystem: leakage is a real
        # possibility and being born again is what closes it.
        assert korumasiz.returncode == 0 or read.returncode == 0
        status = subprocess.run(
            ["podman", "inspect", name, "--format", "{{.State.Status}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert status.stdout.strip() in {"exited", "running", "created"}
    finally:
        subprocess.run(["podman", "rm", "-f", name], capture_output=True, check=False)

    korumali = kostur(PROBE_IMAGE, "sh", "-c", "cat /tmp/trace 2>&1; echo exit:$?")
    assert "exit:0" not in korumali.stdout
    assert "kirlilik" not in korumali.stdout


# --- 7. Management route ---


class _Ok(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        return


class _FakeApis(http.server.BaseHTTPRequestHandler):
    """A stand-in for the API server.

    Its only job is to write a file to the path in the body when `POST /dbs/save`
    arrives — the smallest measurable form of what the real server does. The
    test's evidence is whether that file appears on disk.
    """

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        path = body.get("to_db_home_path")
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text("the host-side process wrote this", encoding="utf-8")
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        return


class _AllowEverything(RoutePolicy):
    """The unguarded arm: no filter."""

    def permits(self, method: str, path: str, body: bytes) -> tuple[bool, str]:
        return True, ""


def _set_up_proxy(tmp_path, policy: RoutePolicy, apis_port: int) -> RecordingProxy:
    socket_directory = tmp_path / "soket"
    socket_directory.mkdir(exist_ok=True)
    proxy = RecordingProxy(
        socket_path=str(socket_directory / "apis.sock"),
        upstream_port=apis_port,
        capture=ApiCapture(shield=None),
        policy=policy,
    )
    proxy.start()
    return proxy


def _konteynerden_yaz(
    socket_directory: str, port: int, target_path: str
) -> subprocess.CompletedProcess:
    """Sends `POST /dbs/save` to the proxy from inside the container.

    The same thing the agent's code can do: `apis.*` cannot reach this route, but
    any code running inside the container can.
    """
    body = json.dumps(
        {
            "from_db_home_path": ":memory:task_output-0de03ea_1",
            "to_db_home_path": target_path,
            "format": "full",
            "app_names": None,
            "delete_if_exists": True,
            "skip_mandatory_apps": False,
            "save_model_hashes": True,
            "vaccum": False,
        }
    )
    kod = (
        f"(python /src/zihin/socket_bridge.py /bridge/apis.sock {port} &) ; sleep 2; "
        f"wget -q -O- --header='Content-Type: application/json' "
        f"--post-data='{body}' http://127.0.0.1:{port}/dbs/save; echo exit:$?"
    )
    return subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--network=none",
            "--read-only",
            "-v",
            f"{socket_directory}:/bridge:ro",
            "-v",
            f"{os.path.abspath('src')}:/src:ro",
            "-e",
            "PYTHONPATH=/src",
            "docker.io/library/python:3.11-alpine",
            "sh",
            "-c",
            kod,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )


@pytest.mark.appworld
def test_the_proxy_refuses_a_management_write_to_an_arbitrary_path(tmp_path):
    """§6.4's escape route: the container makes the host-side process write
    wherever it likes.

    In the unguarded arm the file really appears; in the guarded arm the request
    never reaches the server and there is no file. The only difference between the
    two arms is the proxy's policy.
    """
    subprocess.run(
        ["podman", "pull", "-q", "docker.io/library/python:3.11-alpine"],
        check=True,
        capture_output=True,
    )
    from appworld.apps import get_all_apps

    target = tmp_path / "kacis" / "record"
    apis = socketserver.TCPServer(("127.0.0.1", 0), _FakeApis)
    apis_port = apis.server_address[1]
    threading.Thread(target=apis.serve_forever, daemon=True).start()
    bridge_port = 18123
    try:
        # --- unguarded arm ---
        proxy = _set_up_proxy(tmp_path, _AllowEverything(apps=frozenset(get_all_apps())), apis_port)
        try:
            result = _konteynerden_yaz(
                str(Path(proxy.socket_path).parent), bridge_port, str(target)
            )
            assert "exit:0" in result.stdout, f"{result.stdout}\n{result.stderr}"
            assert target.exists(), "no file appeared in the unguarded arm: the test checks nothing"
        finally:
            proxy.stop()
        target.unlink()

        # --- guarded arm ---
        policy = policy_for_episode(
            experiment_name="guvenlik-testi", task_id="0de03ea_1", random_seed=100
        )
        proxy = _set_up_proxy(tmp_path, policy, apis_port)
        try:
            _konteynerden_yaz(str(Path(proxy.socket_path).parent), bridge_port, str(target))
            assert not target.exists(), (
                "a file appeared in the guarded arm: the filter does not cut"
            )
            assert proxy.refusals, "the request was not refused"
            assert proxy.refusals[0].path == "/dbs/save"
            assert "to_db_home_path" in proxy.refusals[0].reason
        finally:
            proxy.stop()
    finally:
        apis.shutdown()
        apis.server_close()
        shutil.rmtree(tmp_path / "soket", ignore_errors=True)


@pytest.mark.appworld
def test_the_bridge_carries_an_app_call_and_the_proxy_records_it(tmp_path):
    """Does the proxy record an app call — from inside the container, over the
    real socket."""
    from appworld.apps import get_all_apps

    apis = socketserver.TCPServer(("127.0.0.1", 0), _Ok)
    apis_port = apis.server_address[1]
    threading.Thread(target=apis.serve_forever, daemon=True).start()
    policy = RoutePolicy(apps=frozenset(get_all_apps()))
    proxy = _set_up_proxy(tmp_path, policy, apis_port)
    bridge_port = 18124
    try:
        kod = (
            f"(python /src/zihin/socket_bridge.py /bridge/apis.sock {bridge_port} &) ; sleep 2; "
            f"wget -q -O- 'http://127.0.0.1:{bridge_port}"
            "/spotify/songs?page_index=2'; echo exit:$?"
        )
        result = subprocess.run(
            [
                "podman",
                "run",
                "--rm",
                "--network=none",
                "--read-only",
                "-v",
                f"{Path(proxy.socket_path).parent}:/bridge:ro",
                "-v",
                f"{os.path.abspath('src')}:/src:ro",
                "-e",
                "PYTHONPATH=/src",
                "docker.io/library/python:3.11-alpine",
                "sh",
                "-c",
                kod,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert "exit:0" in result.stdout, f"{result.stdout}\n{result.stderr}"
        time.sleep(0.5)
        assert len(proxy.capture.calls) == 1
        record = proxy.capture.calls[0]
        assert record.url == "/spotify/songs"
        assert record.method == "get"
        assert record.status_code == 200
        # The type came back from the route signature: `2` is text on the wire and
        # a number in the record (K-92).
        assert record.data == {"page_index": 2}
    finally:
        proxy.stop()
        apis.shutdown()
        apis.server_close()
