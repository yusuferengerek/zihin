"""Which podman network mode gives the container exactly one host port.

**The requirement.** The container should reach the proxy and nothing else: not
the outside network, not the host's other ports, nowhere. This is the threat
model's "loopback only, fixed app ports" clause put into practice.

**Why it is measured.** Three modes were tried in the first round and none of
them was what it looked like: `--network=none` cuts loopback as well, the default
netavark leaves the outside network open, and `slirp4netns` is not installed on
the GitHub runner. The decision has to be the same in WSL and on the runner, so
the measurement runs from this script in both places.

**Four questions measured, for every mode.** Can it reach the outside network;
can it reach a port the host listens on, from the container's own loopback; can
it reach the host by gateway name; and can it reach it over a bound unix socket.

The socket arm has a question of its own whose answer is not obvious in advance:
`connect` on a unix socket wants write permission, and a read-only mount may cut
it. If it does, the "no writable mount" rule and the "one channel" requirement
collide, and that has to be measured rather than assumed.

Output: `results/container-network.json`.
"""

from __future__ import annotations

import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time

OUTPUT = "results/container-network.json"
HOST_PORT = 18899
SOCKET_DIRECTORY = "/tmp/zihin-bridge"
SOCKET_NAME = "proxy.sock"
IMAGE = "docker.io/library/python:3.11-alpine"
DISH = "http://1.1.1.1/"

# The bridge that runs inside the container: joins a TCP port on 127.0.0.1 to the
# bound unix socket. The reference speaks through `requests` and `requests` only
# knows TCP, so a TCP listener on the container side is mandatory.
BRIDGE = r"""
import socket, threading, sys
sock_path, port = sys.argv[1], int(sys.argv[2])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", port)); server.listen(8)
def pipe(a, b):
    try:
        while True:
            data = a.recv(65536)
            if not data: break
            b.sendall(data)
    except OSError: pass
    finally:
        for s in (a, b):
            try: s.shutdown(socket.SHUT_RDWR)
            except OSError: pass
def serve(client):
    upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    upstream.connect(sock_path)
    threading.Thread(target=pipe, args=(client, upstream), daemon=True).start()
    pipe(upstream, client)
while True:
    client, _ = server.accept()
    threading.Thread(target=serve, args=(client,), daemon=True).start()
"""

# The probe that runs inside the container. It asks the four questions and answers
# them in one line.
PROBE = r"""
import json, socket, subprocess, sys, threading, time, urllib.request
sonuc = {}
def dene(ad, url, zaman=4):
    try:
        with urllib.request.urlopen(url, timeout=zaman) as response:
            sonuc[ad] = response.status
    except Exception as hata:
        sonuc[ad] = type(hata).__name__ + ": " + str(hata)[:70]
dene("dis_ag", "%s")
dene("kendi_loopback", "http://127.0.0.1:%d/")
dene("agi_gecidi_adi", "http://host.containers.internal:%d/")
dene("slirp_gecidi", "http://10.0.2.2:%d/")
import os
sock = "/bridge/%s"
sonuc["soket_dosyasi_var"] = os.path.exists(sock)
if sonuc["soket_dosyasi_var"]:
    try:
        trial = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        trial.settimeout(4); trial.connect(sock); trial.close()
        sonuc["sokete_baglanabildi"] = True
    except Exception as hata:
        sonuc["sokete_baglanabildi"] = type(hata).__name__ + ": " + str(hata)[:70]
    if sonuc.get("sokete_baglanabildi") is True:
        bridge = subprocess.Popen([sys.executable, "-c", BRIDGE, sock, "18123"])
        time.sleep(1.5)
        dene("socket_bridge", "http://127.0.0.1:18123/")
        bridge.terminate()
print("RESULT " + json.dumps(sonuc))
"""


class UnixHTTPServer(socketserver.UnixStreamServer):
    """HTTP over a unix socket. It stands in for the proxy in the real design."""

    def get_request(self):
        request, _ = super().get_request()
        return request, ("127.0.0.1", 0)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):  # silence the noise
        return


def start_tcp_server() -> socketserver.TCPServer:
    server = socketserver.TCPServer(("127.0.0.1", HOST_PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def start_unix_server(mode: int) -> UnixHTTPServer:
    shutil.rmtree(SOCKET_DIRECTORY, ignore_errors=True)
    os.makedirs(SOCKET_DIRECTORY, exist_ok=True)
    path = os.path.join(SOCKET_DIRECTORY, SOCKET_NAME)
    server = UnixHTTPServer(path, Handler)
    os.chmod(path, mode)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def configurations() -> list[tuple[str, list[str]]]:
    """The modes measured. The socket arm is tried in every mode, because its
    question is independent of the network."""
    return [
        ("A-none", ["--network=none"]),
        ("B-varsayilan", []),
        ("C-slirp4netns-host-loopback", ["--network=slirp4netns:allow_host_loopback=true"]),
        ("D-pasta", ["--network=pasta"]),
    ]


def run_probe(name: str, network: list[str], mount: str) -> dict:
    probe = PROBE % (DISH, HOST_PORT, HOST_PORT, HOST_PORT, SOCKET_NAME)
    program = "BRIDGE = " + repr(BRIDGE) + "\n" + probe
    command = [
        "podman",
        "run",
        "--rm",
        *network,
        "-v",
        f"{SOCKET_DIRECTORY}:/bridge:{mount}",
        IMAGE,
        "python",
        "-c",
        program,
    ]
    finished = subprocess.run(command, capture_output=True, text=True, timeout=300)
    for line in finished.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[6:])
    return {
        "hata": "yoklama sonuc dondurmedi",
        "cikis": finished.returncode,
        "stderr": finished.stderr[-400:],
    }


def main() -> None:
    if shutil.which("podman") is None:
        sys.exit("podman is not installed; the measurement cannot run.")
    version = subprocess.run(
        ["podman", "--version"], capture_output=True, text=True, check=True
    ).stdout.strip()
    backend = subprocess.run(
        ["podman", "info", "--format", "{{.Host.NetworkBackend}}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    subprocess.run(["podman", "pull", "-q", IMAGE], check=True, capture_output=True)

    tcp = start_tcp_server()
    report: dict = {
        "ne": "Which podman network mode gives the container exactly one host port",
        "podman": version,
        "ag_arka_ucu": backend,
        "imaj": IMAGE,
        "host_portu": HOST_PORT,
        "soket": os.path.join(SOCKET_DIRECTORY, SOCKET_NAME),
        "kipler": {},
    }
    try:
        # Two mount modes: read-only and writable. The question is whether
        # connecting to a unix socket needs write permission.
        for mount in ("ro", "rw"):
            server = start_unix_server(0o666)
            time.sleep(0.3)
            for name, network in configurations():
                key = f"{name}|baglama={mount}"
                try:
                    report["kipler"][key] = run_probe(name, network, mount)
                except subprocess.TimeoutExpired:
                    report["kipler"][key] = {"hata": "zaman asimi"}
                print(key, "->", json.dumps(report["kipler"][key], ensure_ascii=False))
            server.shutdown()
            server.server_close()
    finally:
        tcp.shutdown()
        shutil.rmtree(SOCKET_DIRECTORY, ignore_errors=True)

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print("written:", OUTPUT)


if __name__ == "__main__":
    main()
