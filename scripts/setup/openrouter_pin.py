"""A forwarder that pins the OpenRouter provider, because the scaffold cannot.

**Why this exists, measured.** OpenRouter routes one model tag to several
providers and the quantisation is the provider's choice, so an unpinned run is not
one condition (protocol §14.2). The routing is set by a `provider` field in the
request body. The scaffold cannot carry it: `LanguageModel` filters generation
kwargs against `litellm.completion`'s signature, where `extra_body` does not
appear, and `non_cached_lm_call` raises on any key outside its own signature.
Both reject loudly rather than dropping silently — which is good — but the field
still never reaches the wire.

**Why not change the scaffold.** K-19 takes the reference scaffold unchanged. This
is the transport layer, where `api_capture` and the recording proxy already sit,
and the scaffold constraint leaves it out.

**What it does.** Listens on loopback, adds
`{"provider": {"only": [...], "allow_fallbacks": false}}` to every chat completion
body, forwards to OpenRouter, and returns the response untouched to the caller.

**What it measures on the way through.** The provider that actually served the
request, read from OpenRouter's response rather than from the body we sent — so
"pinned" is an observation, not a declaration (§14.3). Also the accumulated cost,
so the run can stop at the ceiling (§14.5).

Usage:

    OPENROUTER_API_KEY=... uv run python scripts/setup/openrouter_pin.py \\
        --provider DeepInfra --port 87 --state /tmp/pin-state.json
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://openrouter.ai/api/v1"


class State:
    """What the forwarder observed, written where the runner can read it."""

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.lock = threading.Lock()
        self.calls = 0
        self.providers: dict[str, int] = {}
        self.cost = 0.0
        self.errors: list[str] = []

    def record(self, provider: str | None, cost: float | None, error: str | None) -> None:
        with self.lock:
            self.calls += 1
            if provider:
                self.providers[provider] = self.providers.get(provider, 0) + 1
            if cost:
                self.cost += cost
            if error:
                self.errors.append(error)
            self.path.write_text(
                json.dumps(
                    {
                        "calls": self.calls,
                        "providers": self.providers,
                        "cost_usd": round(self.cost, 6),
                        "errors": self.errors[-20:],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )


def handler_for(provider: str, key: str, state: State, ceiling: float):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args) -> None:  # noqa: D102
            return

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self.send_error(400, "body is not JSON")
                return

            # The pin. `allow_fallbacks: false` is the half that matters: without
            # it OpenRouter may still route elsewhere when the pinned provider is
            # busy, and the run would silently become two conditions.
            body["provider"] = {"only": [provider], "allow_fallbacks": False}
            body["usage"] = {"include": True}

            if state.cost >= ceiling:
                self.send_error(402, f"cost ceiling {ceiling} reached; the run must stop")
                return

            payload = json.dumps(body).encode("utf-8")
            request = urllib.request.Request(
                f"{UPSTREAM}{self.path}",
                data=payload,
                method="POST",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/zihin",
                    "X-Title": "zihin precondition measurement",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=600) as response:
                    answer = response.read()
                    code = response.status
            except urllib.error.HTTPError as error:
                answer, code = error.read(), error.code
                state.record(None, None, f"{code}: {answer[:300].decode('utf-8', 'replace')}")
            except Exception as error:  # noqa: BLE001
                state.record(None, None, repr(error))
                self.send_error(502, "upstream failed")
                return
            else:
                served, cost = None, None
                try:
                    parsed = json.loads(answer)
                    served = parsed.get("provider")
                    usage = parsed.get("usage") or {}
                    cost = usage.get("cost")
                except (json.JSONDecodeError, AttributeError):
                    pass
                state.record(served, cost, None)

            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(answer)))
            self.end_headers()
            self.wfile.write(answer)

        def do_GET(self) -> None:  # noqa: N802
            """Only `/models` is proxied; everything else is out of scope."""
            request = urllib.request.Request(
                f"{UPSTREAM}{self.path}", headers={"Authorization": f"Bearer {key}"}
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    answer, code = response.read(), response.status
            except Exception:  # noqa: BLE001
                self.send_error(502, "upstream failed")
                return
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(answer)))
            self.end_headers()
            self.wfile.write(answer)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--state", type=pathlib.Path, required=True)
    parser.add_argument("--cost-ceiling", type=float, required=True)
    arguments = parser.parse_args()

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set. The forwarder carries the key, never stores it.")

    state = State(arguments.state)
    state.record(None, None, None)
    server = ThreadingHTTPServer(
        ("127.0.0.1", arguments.port),
        handler_for(arguments.provider, key, state, arguments.cost_ceiling),
    )
    print(f"pinning provider={arguments.provider} on 127.0.0.1:{arguments.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
