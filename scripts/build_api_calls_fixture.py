"""Writes the route test's sample log: synthetic calls over ten AppWorld routes.

**Why it is synthetic.** The sample used to be a copy of a recorded run's
`api_calls.jsonl`, and every recorded run is an AppWorld experiment output (S-80).
The tests that read it need only the log's shape and its routes: three keys per
row, URLs that resolve, at least 20 calls, exactly ten distinct endpoints, and at
least one template reached through more than one id. A generated log has all of
that and carries no task text, no model output and no trajectory.

**Why these ten routes.** They are the routes the previous sample touched, so the
pinned count of ten does not move, and AppWorld shows all ten on its public API
Explorer. The ids in the paths are invented, and every call's `data` is empty.

Usage:

    uv run python scripts/build_api_calls_fixture.py
    uv run python scripts/build_api_calls_fixture.py --check
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPOSITORY / "tests" / "data" / "api_calls-synthetic.jsonl"

# (method, URL) in the order they are written. Two templates are called with
# several ids, so the identity abstraction has something to merge.
CALLS = (
    [("get", "/supervisor/account_passwords"), ("post", "/spotify/auth/token")]
    + [("get", "/api_docs/api_doc")] * 2
    + [("get", "/spotify/library/songs")] * 3
    + [("delete", f"/spotify/library/songs/{song_id}") for song_id in range(101, 106)]
    + [("get", "/spotify/library/albums")] * 2
    + [("delete", f"/spotify/library/albums/{album_id}") for album_id in range(201, 204)]
    + [("get", "/spotify/liked_songs")] * 2
    + [("get", "/spotify/downloaded_songs")] * 2
    + [("post", "/supervisor/message")]
)


def rendered() -> str:
    return "".join(
        json.dumps({"method": method, "url": url, "data": {}}) + "\n" for method, url in CALLS
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare, do not write")
    args = parser.parse_args()
    name = FIXTURE.relative_to(REPOSITORY)
    if args.check:
        current = FIXTURE.read_text(encoding="utf-8") if FIXTURE.exists() else ""
        if current != rendered():
            sys.exit(f"FAILED: {name} differs from what this script writes")
        print(f"{name}: current, {len(CALLS)} calls")
        return
    FIXTURE.write_text(rendered(), encoding="utf-8")
    print(f"wrote {name}: {len(CALLS)} calls")


if __name__ == "__main__":
    main()
