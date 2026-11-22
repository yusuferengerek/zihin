"""Do the citations in the presentation skeleton and the pilot report resolve.

**Why it exists.** The skeleton's method is that a claim may be said only if its
citation slot is filled. That check was on the *presence* of a slot, never on
whether what the slot names exists. Two numbers that reached a report turned out
wrong only because they were checked by hand before being quoted; the ones
nobody quoted were never checked at all.

**What it checks.** Every `results/...json` path named in the two documents, and
every key path named next to it (`file → key.subkey`). A path that does not
exist, or a key that is not in the file it is attached to, is reported.

**And whether the artefact is in the repository.** Existing on this disk is not
enough: `results/` is mostly ignored, so a citation could resolve here and
resolve nowhere else. That is not hypothetical — it turned CI red on a branch
where thirty citations passed locally and eighteen failed in a fresh checkout.
A cited artefact is a tracked artefact.

**The one exception: a tracked derived-data manifest.** The public repository packs
some cited `results/` files into an encrypted bundle (K-205); git carries
`derived/MANIFEST.json`, which lists each packed file's path and sha256, and
`scripts/unpack_derived.py` restores them. A cited file git does not carry is
accepted when that tracked manifest lists it. If the file is on disk, its sha256
must match the manifest entry and its key is checked as usual; if it is absent, the
citation is accepted on the manifest's word and the summary says how many were.
Without a tracked manifest, as in the archive, nothing about this check changes.

**What it does not check.** Whether the number under the key supports the
sentence. That is a reading, and a reading is not mechanisable — but a citation
that does not resolve is, and it is the cheaper half.

Usage:

    uv run python scripts/check_citations.py
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
DOCUMENTS = (
    "docs/reports/sunum-iskeleti.md",
    "PILOT_REPORT.md",
    # The ledger's rows each name their artefact; a row whose artefact moved would
    # be a way out of the power problem that nobody can price any more.
    "docs/14-alternatives-ledger.tr.md",
    "docs/14-alternatives-ledger.en.md",
)

# `results/x.json` → `a.b`, or `results/x.json` → `a`, or a bare path.
FILE = re.compile(r"`(results/[\w./-]+\.json)`(?:\s*→\s*`([\w.\[\]]+)`)?")
# A key cited on its own, after a file was named earlier in the same row.
BARE_KEY = re.compile(r"`([a-z_]+(?:\.[a-z_]+)+)`")
# The floor. This check's failure mode is silence: a regex that stops matching
# examines nothing and reports that everything resolves. Thirty citations are
# found today; the floor sits below that so a deliberate removal does not trip
# it, and far above zero so a broken pattern does (K-114).
FLOOR = 20
OTHER_PATH = re.compile(r"`((?:docs|scripts|src|tests|experiments|config)/[\w./-]+\.\w+)`")
MANIFEST = "derived/MANIFEST.json"


def resolve(blob, dotted: str):
    """Follows a dotted key path into a loaded JSON document."""
    node = blob
    for part in dotted.replace("[]", "").split("."):
        if isinstance(node, list):
            if not node:
                return None, f"{part}: the list is empty"
            node = node[0]
        if not isinstance(node, dict) or part not in node:
            return None, part
        node = node[part]
    return node, None


def tracked() -> set[str]:
    """Everything git carries, so a citation can be told from a local file."""
    out = subprocess.run(
        ["git", "-C", str(REPOSITORY), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return set(out.split())


def derived_manifest(root: pathlib.Path, in_git: set[str]) -> dict[str, str]:
    """path -> sha256 from the derived-data manifest, only when git carries it."""
    if MANIFEST not in in_git:
        return {}
    try:
        files = json.loads((root / MANIFEST).read_text(encoding="utf-8"))["files"]
        return {item["path"]: item["sha256"] for item in files}
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(
            f"{MANIFEST} is tracked but cannot be read ({error}). Citations it would "
            "vouch for cannot be judged; the check declines rather than guessing."
        )


def file_problem(
    root: pathlib.Path, file_name: str, key: str, in_git: set[str], manifest: dict[str, str]
) -> tuple[str | None, str]:
    """What is wrong with one cited results file, if anything, and how it resolved.

    The second value is `git`, `manifest` (listed, on disk, sha256 matching),
    `manifest-absent` (listed, not on disk, accepted on the manifest's word),
    `missing` or `untracked`.
    """
    target = root / file_name
    if file_name not in in_git and file_name in manifest:
        if not target.exists():
            return None, "manifest-absent"
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != manifest[file_name]:
            return (
                f"{file_name} does not match {MANIFEST}: sha256 {digest} on disk, "
                f"{manifest[file_name]} listed",
                "manifest",
            )
        how = "manifest"
    elif not target.exists():
        return f"{file_name} does not exist", "missing"
    elif file_name not in in_git:
        return (
            f"{file_name} exists here but git does not carry it, so the citation "
            "resolves on this machine only",
            "untracked",
        )
    else:
        how = "git"
    if not key:
        return None, how
    try:
        blob = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return f"{file_name} is not readable: {error}", how
    _, missing = resolve(blob, key)
    if missing:
        return f"{file_name} has no key {key!r} (stopped at {missing!r})", how
    return None, how


def main() -> None:
    problems: list[str] = []
    checked = 0
    through_manifest: dict[str, int] = {"manifest": 0, "manifest-absent": 0}
    in_git = tracked()
    if not in_git:
        sys.exit(
            "`git ls-files` returned nothing. This check asks whether a cited "
            "artefact is in the repository and cannot answer without git; it "
            "declines rather than passing silently."
        )
    manifest = derived_manifest(REPOSITORY, in_git)
    for name in DOCUMENTS:
        path = REPOSITORY / name
        if not path.exists():
            problems.append(f"{name}: the document itself does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        print(f"### {name}")

        for line_number, line in enumerate(text.splitlines(), 1):
            for file_name, key in FILE.findall(line):
                checked += 1
                problem, how = file_problem(REPOSITORY, file_name, key, in_git, manifest)
                if how in through_manifest:
                    through_manifest[how] += 1
                if problem:
                    problems.append(f"{name}:{line_number} {problem}")

            for other in OTHER_PATH.findall(line):
                checked += 1
                if not (REPOSITORY / other).exists():
                    problems.append(f"{name}:{line_number} {other} does not exist")
                elif other not in in_git:
                    problems.append(
                        f"{name}:{line_number} {other} exists here but git does not carry it"
                    )

        print(f"  citations examined so far: {checked}")

    print()
    if checked < FLOOR:
        sys.exit(
            f"only {checked} citation(s) were found and the floor is {FLOOR}. The "
            "documents' shape changed and this parser no longer reads them. Nothing "
            "is reported: an empty sweep is not a clean one."
        )
    if any(through_manifest.values()):
        print(
            f"{sum(through_manifest.values())} citation(s) resolved through {MANIFEST}: "
            f"{through_manifest['manifest']} on disk with a matching sha256, "
            f"{through_manifest['manifest-absent']} not on disk, accepted on the manifest's "
            "word with their keys unchecked"
        )
    if not problems:
        print(f"all {checked} citation(s) resolve")
        return
    print(f"{len(problems)} CITATION(S) DO NOT RESOLVE, out of {checked}:")
    for line in problems:
        print(f"  - {line}")
    sys.exit(1)


if __name__ == "__main__":
    main()
