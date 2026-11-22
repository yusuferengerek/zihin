"""The bridge that runs inside the container: joins a local TCP port to the bound
unix socket.

**Why it is needed.** The reference `Requester` speaks through `requests`, and
`requests` only knows TCP. The container's network mode is `--network=none`, so
it can reach nowhere; but the `lo` interface stays up, and that is why a TCP
listener works inside the container. Measured, on two platforms.

**Why it is this small.** The bridge sits inside the measurement, so every line
of it can affect the record's correctness. It only moves bytes: it does not parse
HTTP, does not touch headers, does not retry. The place that parses and decides
is the proxy, and the proxy is outside the container.

**It has no dependencies.** The image carries the `appworld` package, so it
carries Python; nothing beyond the standard library is added.

Usage (inside the container):

    python -m zihin.socket_bridge /bridge/apis.sock 8123
"""

from __future__ import annotations

import socket
import sys
import threading

BUFFER = 65536


def _pipe(source: socket.socket, target: socket.socket) -> None:
    """Moves one direction and closes both sides when it ends.

    Closing is mandatory: if only one direction closes, the other waits forever
    and the episode hangs until the step timeout.
    """
    try:
        while True:
            data = source.recv(BUFFER)
            if not data:
                break
            target.sendall(data)
    except OSError:
        pass
    finally:
        for side in (source, target):
            try:
                side.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _serve_one(client: socket.socket, socket_path: str) -> None:
    upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        upstream.connect(socket_path)
    except OSError:
        client.close()
        return
    threading.Thread(target=_pipe, args=(client, upstream), daemon=True).start()
    _pipe(upstream, client)
    client.close()
    upstream.close()


def serve(
    socket_path: str,
    port: int,
    host: str = "127.0.0.1",
    listener: socket.socket | None = None,
) -> None:
    """Listens on the port and joins every connection to the socket. Never returns.

    `listener` can be passed in, because where the bind happens matters: bound
    inside a thread, an "address already in use" error is swallowed in that
    thread and the caller sees nothing. The host-side usage binds the port
    beforehand and hands the ready socket in.
    """
    if listener is None:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(16)
    while True:
        client, _ = listener.accept()
        threading.Thread(target=_serve_one, args=(client, socket_path), daemon=True).start()


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("usage: python -m zihin.socket_bridge <socket-path> <port>")
    serve(args[0], int(args[1]))


if __name__ == "__main__":
    main()
