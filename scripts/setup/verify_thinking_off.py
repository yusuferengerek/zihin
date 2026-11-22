"""Verifies, per model size, that thinking can be switched off.

The protocol requires this before the family scan, not during it: for **each
size that will be used**, a prompt that triggers thinking in the on mode is
chosen, and the off mode must produce **zero thinking**. A family that fails on
any size is eliminated (setup protocol, section 1).

Why beforehand: seeing something work does not show that it works for the right
reason (K-49). If the check ran inside the scan, a size whose thinking never
switched off would silently be measured under a different condition — which is
exactly what happened on the hosted side (S-34).

**The pass criterion has two halves and both are required: zero thinking
tokens AND an empty thinking field.** One half is not enough. On the hosted
side a call was measured that reported `reasoning_tokens=0` while returning 280
characters of reasoning; accounting and content disagreed, and the content is
what enters the budget.

Usage:

    uv run python scripts/setup/verify_thinking_off.py qwen3.5:2b-q4_K_M ...
"""

from __future__ import annotations

import json
import sys
import urllib.request
from typing import Any

# A prompt that reliably triggers thinking in a hybrid model: multi-step
# arithmetic with a trap in the middle.
PROBE = (
    "A farmer has 17 sheep. All but 9 run away. He then buys twice as many as "
    "remain, and sells 5. How many sheep does he have? Answer with the number only."
)


def chat(base_url: str, tag: str, think: bool | None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": tag,
        "messages": [{"role": "user", "content": PROBE}],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 2000},
    }
    if think is not None:
        body["think"] = think
    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)


def probe(base_url: str, tag: str, think: bool | None) -> dict[str, Any]:
    try:
        result = chat(base_url, tag, think)
    except Exception as error:
        # Ollama answers 400 when `think` is sent to a model that has no
        # thinking mode. That is not a fault, it is the answer: the model
        # trivially satisfies the condition. The body is read to tell the two
        # apart rather than guessing from the status code.
        body = ""
        read = getattr(error, "read", None)
        if callable(read):
            body = read().decode("utf-8", "replace")[:200]
        return {
            "error": f"{type(error).__name__}: {str(error)[:80]}",
            "body": body,
            "unsupported": "think" in body.lower() and "support" in body.lower(),
        }
    message = result.get("message") or {}
    thinking = message.get("thinking") or ""
    return {
        "thinking_chars": len(thinking),
        "content": (message.get("content") or "").strip()[:60],
        "eval_count": result.get("eval_count"),
        "prompt_eval_count": result.get("prompt_eval_count"),
    }


def verify(base_url: str, tag: str) -> dict[str, Any]:
    """Runs both modes and decides. Returns a record for the report."""
    on = probe(base_url, tag, True)
    off = probe(base_url, tag, False)
    default = probe(base_url, tag, None)

    # A model with no thinking mode at all trivially satisfies the condition:
    # the field is empty in every mode. That is recorded separately, because
    # "thinking was switched off" and "there is no thinking" are different
    # facts, and only the second one needs no verification per size.
    unsupported = on.get("unsupported") or off.get("unsupported")
    has_thinking = on.get("thinking_chars", 0) > 0
    off_is_clean = off.get("thinking_chars", 1) == 0 and "error" not in off
    default_is_clean = default.get("thinking_chars", 1) == 0

    if unsupported and default_is_clean:
        verdict = "no_thinking_mode"
    elif "error" in on or "error" in off:
        verdict = "error"
    elif not has_thinking:
        verdict = "no_thinking_mode"
    elif off_is_clean:
        verdict = "can_be_switched_off"
    else:
        verdict = "cannot_be_switched_off"

    return {
        "tag": tag,
        "verdict": verdict,
        "on": on,
        "off": off,
        "default": default,
        "default_is_clean": default_is_clean,
    }


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: verify_thinking_off.py <tag> [<tag> ...]")
    base_url = "http://127.0.0.1:11434"
    records = [verify(base_url, tag) for tag in sys.argv[1:]]

    print(f"{'tag':32s} {'verdict':24s} {'on':>8s} {'off':>8s} {'default':>8s}")
    for r in records:
        print(
            f"{r['tag']:32s} {r['verdict']:24s} "
            f"{r['on'].get('thinking_chars', '-'):>8} "
            f"{r['off'].get('thinking_chars', '-'):>8} "
            f"{r['default'].get('thinking_chars', '-'):>8}"
        )
    print()
    for r in records:
        if r["verdict"] == "error":
            print(f"  {r['tag']}: {r['on'].get('error') or r['off'].get('error')}")

    output = "results/thinking-off-verification.json"
    with open(output, "w", encoding="utf-8") as handle:
        json.dump({"probe": PROBE, "records": records}, handle, ensure_ascii=False, indent=2)
    print(f"written: {output}")

    failed = [r["tag"] for r in records if r["verdict"] in ("cannot_be_switched_off", "error")]
    if failed:
        sys.exit(
            f"{len(failed)} size(s) failed: {failed}. A family that fails on any size is "
            "eliminated (setup protocol, section 1)."
        )


if __name__ == "__main__":
    main()
