"""Do the artefacts named in merged PR reports exist in main's tree?

A bounded check, not an open-ended audit. The risk it targets has one shape and
it has already happened once: the last commit of a branch is not pushed, the
earlier pushes keep CI green, the PR merges, and everything in that commit is
gone while the report says it landed (K-116).

File existence only. It does not read the files or judge them.
"""

import json
import pathlib
import re
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parents[1]
# An extension is required: a bare stem like `experiments/setup-protocol` is how
# the parity check names a document pair, not a file, and matching it produced
# the check's only false positive on its first run.
PATH = re.compile(r"`((?:docs|scripts|src|tests|experiments|config)/[\w./-]+\.\w+)`")


def run(args: list[str]) -> str:
    try:
        return subprocess.run(args, cwd=R, capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit(
            f"{args[0]} is not installed. This check reads merged pull requests from "
            "GitHub and cannot answer without it; it declines rather than passing "
            "silently. It belongs to `local_checks.sh`, not to an environment that "
            "has no `gh` — a Colab runtime, for instance."
        )


listed = run(
    ["gh", "pr", "list", "--state", "merged", "--limit", "6", "--json", "number,title,body"]
).strip()
if not listed:
    sys.exit(
        "`gh pr list` returned nothing. Either `gh` is not authenticated or this "
        "checkout has no GitHub remote. The check declines: an empty list is not "
        "the same answer as 'no artefact is missing'."
    )
merged = json.loads(listed)
tree = set(run(["git", "ls-tree", "-r", "--name-only", "origin/main"]).split())

missing_total = 0
for pr in sorted(merged, key=lambda p: p["number"]):
    named = sorted(set(PATH.findall(pr["body"] or "")))
    missing = [p for p in named if p not in tree]
    missing_total += len(missing)
    mark = "ok " if not missing else "GAP"
    print(f"{mark} PR #{pr['number']:<3} {len(named):2d} artefact named  {pr['title'][:56]}")
    for path in missing:
        print(f"      MISSING from origin/main: {path}")

print(f"\nmerged PRs checked: {len(merged)}   artefacts missing from main: {missing_total}")
sys.exit(1 if missing_total else 0)
