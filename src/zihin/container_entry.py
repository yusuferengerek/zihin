"""The container's entry point: two bridges and AppWorld's own environment server.

**What it does.** Three things, and all three are transport:

1. Opens a bridge inside the container listening on `127.0.0.1:<port>` and joins
   it to the bound unix socket. The agent's `apis.*` calls go from there to the
   proxy.
2. Runs AppWorld's **own** environment server on the file descriptor it
   inherited. The host connects to that socket and calls `world.execute`.
3. Nothing else.

**Why a file descriptor.** The network mode is `--network=none` and it cuts both
directions; the container not reaching out is what we want, but the host has to
reach in. Writable mounts are forbidden, so the container cannot create a socket
file the host can see. The host binds the socket itself and passes the descriptor
across (`--preserve-fds`); the container only accepts. Measured: this works under
a read-only root and `--network=none`.

**The environment server is the reference itself.**
`appworld.serve.environment:app` runs as-is; the only thing that changes is where
it binds. This is exactly K-19's transport-layer exemption: the same messages go
out and the same text comes back.

**The agent's code runs in this same process.** The environment server executes
code in an embedded IPython shell, so the agent's code can do anything this
process can do. What the container defends is not this process but the host: the
record, the verifier and the API server's management surface are outside it and
behind the proxy (S-50).
"""

from __future__ import annotations

import os
import socket
import sys
import threading

from zihin.socket_bridge import serve as bridge_serve

# The socket the host bound arrives on this descriptor. `--preserve-fds 1` starts
# numbering at fd 3.
ENVIRONMENT_FD = 3


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("usage: python -m zihin.container_entry <apis-socket> <apis-port>")
    apis_socket, apis_port = args[0], int(args[1])

    threading.Thread(
        target=bridge_serve, args=(apis_socket, apis_port), daemon=True, name="apis-bridge"
    ).start()

    import uvicorn
    from appworld.serve.environment import app

    listener = socket.socket(fileno=ENVIRONMENT_FD)
    # Uvicorn listens on the descriptor itself; here we only confirm it is valid.
    # If it is invalid the error should surface now: surfacing later leaves the
    # host with a timeout and no reason for it.
    listener.getsockname()
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    uvicorn.run(app, fd=ENVIRONMENT_FD, log_level="warning")


if __name__ == "__main__":
    main()
