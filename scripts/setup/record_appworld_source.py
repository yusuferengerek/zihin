"""Records where AppWorld was installed from, and checks it is the same artefact.

**Why this exists.** On 2026-08-20 the upstream repository's Git LFS budget ran
out (HTTP 403, `This repository exceeded its LFS budget`) and `uv sync` could no
longer fetch the pinned commit's bundle objects. A mirror of the two wheels,
built from that same commit while the objects were still being served, lives in
`vendor/appworld/`. A fallback that leaves no trace would hide where a
measurement's benchmark came from, so the bootstrap calls this and the manifest
carries the answer through `os_environment_text()`.

**It measures rather than asserts.** Whichever path was taken, the installed
bundles are hashed and compared with the object ids recorded in
`vendor/appworld/PROVENANCE.json`. A bundle's Git LFS object id *is* the sha256
of its content, so a match is not a resemblance: it is the same object upstream
names at that commit. A mismatch stops the bootstrap, because at that point
nobody knows what is installed.

Usage:

    uv run python scripts/setup/record_appworld_source.py upstream
    uv run python scripts/setup/record_appworld_source.py mirror
"""

from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
PROVENANCE = REPOSITORY / "vendor/appworld/PROVENANCE.json"
REPORT = REPOSITORY / "results/appworld-kaynak.json"


def installed_bundles() -> dict[str, str]:
    """sha256 of every bundle in the installed appworld package."""
    import appworld

    source = pathlib.Path(appworld.__file__).parent / ".source"
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source.glob("*.bundle"))
    }


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("upstream", "mirror"):
        sys.exit("usage: record_appworld_source.py upstream|mirror")
    source = sys.argv[1]

    if not PROVENANCE.exists():
        sys.exit(f"{PROVENANCE} does not exist; the mirror's provenance is the reference")
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    expected = {b["file"]: b["sha256"] for b in provenance["bundles_inside_the_appworld_wheel"]}

    found = installed_bundles()
    if not found:
        sys.exit("no bundle found in the installed appworld package; the install is incomplete")

    differing = [
        f"{name}: expected {expected[name][:12]}, found {digest[:12]}"
        for name, digest in found.items()
        if name in expected and digest != expected[name]
    ]
    if differing:
        sys.exit(
            "the installed bundles are not the objects the pinned commit names:\n  "
            + "\n  ".join(differing)
            + "\nThe bootstrap stops here: what is installed is unknown."
        )

    missing = sorted(set(expected) - set(found))
    if missing:
        sys.exit(f"bundles absent from the install: {missing}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(
            {
                "source": source,
                "commit": provenance["source"]["commit"],
                "mirror_taken": provenance["mirror_taken"] if source == "mirror" else None,
                "bundles_verified": found,
                "recorded_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
                "note": (
                    "Written by the bootstrap. `os_environment_text()` reads it and the "
                    "manifest carries the answer, so a run installed from the mirror is "
                    "not silently indistinguishable from one installed upstream."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"appworld source: {source}; bundles match the pinned commit's LFS object ids")


if __name__ == "__main__":
    main()
