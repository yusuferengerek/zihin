"""Asks whether upstream AppWorld's Git LFS storage will serve objects again.

**Why a script and not a memory.** On 2026-08-20 a Colab bootstrap stopped in
`uv sync`: fetching the pinned AppWorld source ran `git lfs fetch`, and GitHub
answered `This repository exceeded its LFS budget`. The repository is not ours,
the budget is not ours, and whether it comes back is not ours to decide. What is
ours is to stop guessing about it: this asks, and prints what it was told.

**Why the batch API and not `git lfs fetch`.** The question is whether the
objects are being served, not whether we can download two megabytes. One POST
answers it, costs upstream almost nothing, and returns the server's own words.
A fetch would answer the same question by consuming the bandwidth in dispute.

**What the answers mean.**

*`href` present* — the budget is available again. The mirror goes back to being
a fallback, and the primary path is the upstream source (`vendor/appworld/`
explains the order).

*An error on the object, or a non-200* — still blocked. The mirror stays in use
and the manifest keeps recording that it was used.

Usage:

    uv run python scripts/check_upstream_lfs.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BATCH = "https://github.com/StonyBrookNLP/appworld.git/info/lfs/objects/batch"

# One object is enough to answer the question. This is `apps.bundle` at the
# pinned commit; the oid is the content's sha256, which is how LFS names objects,
# so it doubles as a check that the object we hold is the object upstream means.
OBJECT = {
    "oid": "88d21fc526c1655bb3eee4adfca78ccac793921e4506f28f734ecdb19af77a62",
    "size": 193950,
}


def main() -> None:
    body = json.dumps(
        {
            "operation": "download",
            "transfers": ["basic"],
            "objects": [OBJECT],
            "hashAlgo": "sha256",
        }
    ).encode()
    request = urllib.request.Request(
        BATCH,
        data=body,
        headers={
            "Accept": "application/vnd.git-lfs+json",
            "Content-Type": "application/vnd.git-lfs+json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as answer:
            status, payload = answer.status, json.load(answer)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:400]
        print(f"HTTP {error.code}: {detail}")
        sys.exit(1)
    except Exception as error:
        print(f"the request did not complete: {error}")
        sys.exit(1)

    print(f"HTTP {status}")
    for entry in payload.get("objects", []):
        if "error" in entry:
            print(f"  object error {entry['error'].get('code')}: {entry['error'].get('message')}")
            sys.exit(1)
        actions = entry.get("actions") or {}
        if "download" in actions:
            print("  download action present: upstream LFS is serving objects again")
            print("  the mirror goes back to being a fallback; the upstream source is primary")
            return
        print(f"  no download action: {entry}")
    sys.exit(1)


if __name__ == "__main__":
    main()
