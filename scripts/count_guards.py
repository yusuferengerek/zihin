"""Counts the things that need a guard, and checks each one has it.

**Why this exists and why the previous sweep was not enough.** The first sweep
read the protocol's prose and asked, for each check it declared, whether that
check is wired. That can only find gaps between what was *said* and what was
built. A guard that nobody ever declared — and that is exactly the kind that goes
missing — is invisible to it, so its count is a lower bound (K-114).

This one starts from the other end. It enumerates the **kinds** of thing that
need a guard, lists every member of each kind structurally, and asks whether the
member carries one. Nothing has to have been declared. The count is an upper
bound on that kind, and a member appearing with no guard is a finding whether or
not anyone wrote it down.

**Three kinds, and what each one's guard is.**

*Generated views* — a file produced from another file. Their failure is silent
staleness, and it has happened twice (S-33, K-103). The guard is a `--check`
mode wired into CI.

*Measurement runners* — scripts that spend episodes. Their failure is a wasted
run or, worse, a set that silently mixes two conditions. The guards are
`preflight` (the write path runs before thirty episodes start) and `resume_check`
(what is already written matches what is about to run).

*Parsed interfaces* — every place where one file's structure is read by code.
Their failure is a parser that keeps working while meaning something else, which
is how thirty rationales came out wrong. The guard is a test that pins the shape.

**What this does not do.** It does not check that a guard is *correct*, only that
one exists at each site. A `--check` that compares nothing passes here (K-106 is
the record of that happening), and only a negative test catches it.

Usage:

    uv run python scripts/count_guards.py
    uv run python scripts/count_guards.py --check   # non-zero if a site is bare
"""

from __future__ import annotations

import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]

# A generated view names its source and writes a target. Discovered structurally:
# a script under `scripts/` that both reads a repository file and writes one.
WRITES = re.compile(r"\.write_(?:text|bytes)\(|writer\.writerows\(")
CI = (REPOSITORY / ".github/workflows/ci.yml").read_text(encoding="utf-8")
LOCAL = (REPOSITORY / "scripts/local_checks.sh").read_text(encoding="utf-8")

# Runners spend episodes: they are the scripts that invoke `record_run.py`.
RUNNER_MARK = re.compile(r"record_run\.py")
RUNNER_GUARDS = ("def preflight", "resume_check", "missing_manifest_constraints")

# A parsed interface is a module-level compiled regex that reads a document.
DOCUMENT = re.compile(r"docs/[\w./-]+\.md|experiments/[\w./-]+\.md")


def generated_views() -> list[tuple[str, bool, bool]]:
    """(script, has --check, wired in CI or local_checks)."""
    found = []
    for path in sorted((REPOSITORY / "scripts").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if not (WRITES.search(text) and DOCUMENT.search(text)):
            continue
        name = f"scripts/{path.name}"
        found.append((name, "--check" in text, path.name in CI or path.name in LOCAL))
    return found


def runners() -> list[tuple[str, list[str]]]:
    """(runner, the guards it is missing)."""
    found = []
    for path in sorted((REPOSITORY / "scripts/setup").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if not RUNNER_MARK.search(text):
            continue
        missing = [guard for guard in RUNNER_GUARDS if guard not in text]
        found.append((f"scripts/setup/{path.name}", missing))
    return found


def parsed_interfaces() -> list[tuple[str, str, bool]]:
    """(script, the document it parses, whether a test pins the shape)."""
    tests = "\n".join(
        path.read_text(encoding="utf-8") for path in (REPOSITORY / "tests").glob("*.py")
    )
    found = []
    for path in sorted((REPOSITORY / "scripts").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        documents = sorted(set(DOCUMENT.findall(text)))
        if not documents or "re.compile" not in text:
            continue
        name = path.relative_to(REPOSITORY).as_posix()
        found.append((name, documents[0], path.stem in tests))
    return found


# Sites that are bare on purpose, each with the reason written down. The list is
# what makes `--check` usable today: without it the check would be red from the
# first run and would be turned off, and a check that is off is worse than none.
# A site not on this list and not guarded fails the run — that is the whole point.
ACCEPTED = {
    # Neither spends an episode and neither writes a manifest, so the three
    # runner guards have nothing to guard here. They are named rather than
    # filtered out by a pattern: an exception written down is visible where a
    # silently skipped one is not.
    "scripts/setup/measure_colab_environment.py": (
        "measures the environment and writes no manifest; it loads and unloads the "
        "model but spends no episode. Its own guards are require_server and the "
        "three residency states"
    ),
    "scripts/setup/require_colab_environment.py": (
        "it is a guard, not a runner: it refuses or permits, spends nothing and writes nothing"
    ),
    "scripts/setup/measure_context_cost.py": "reads the record and computes; spends no episode",
    "scripts/setup/measure_gpt4o_subset.py": "spends a paid API budget, not the local "
    "episode budget; its guards are a separate decision",
    "scripts/setup/measure_card_arms.py": "queued: the three-arm run is finished and its "
    "data is recorded, so guards go on before the next use, not retroactively",
    "scripts/setup/measure_card_demo.py": "queued with measure_card_arms.py for the same reason",
    "scripts/build_limitations_index.py": "queued: the parser has no shape test, and the "
    "class it would catch already bit once (K-103)",
    "scripts/build_skeleton_coverage.py": "queued with build_limitations_index.py",
    "scripts/check_language.py": "reads the decision record only to build a data corpus; "
    "it parses no structure, so there is no shape to pin",
    # Written by the public build for this tree only: the build's --check needs its
    # private inputs, which only the archive holds, so no CI step here can run it.
    "scripts/build_public_tree.py": "its --check needs the build's private inputs, which "
    "only the archive holds; the archive's CI runs it (K-205)",
}


def main() -> None:
    problems: list[str] = []

    views = generated_views()
    print(f"generated views: {len(views)}")
    for name, has_check, wired in views:
        mark = "ok " if has_check and wired else "GAP"
        print(f"  {mark} {name:44s} --check={has_check}  wired={wired}")
        if not (has_check and wired):
            problems.append(f"{name}: generated view without a wired --check")

    found = runners()
    print(f"\nmeasurement runners: {len(found)}")
    for name, missing in found:
        mark = "ok " if not missing else "GAP"
        print(f"  {mark} {name:44s} missing={missing or 'none'}")
        if missing:
            problems.append(f"{name}: runner missing {', '.join(missing)}")

    interfaces = parsed_interfaces()
    print(f"\nparsed interfaces: {len(interfaces)}")
    for name, document, pinned in interfaces:
        mark = "ok " if pinned else "GAP"
        print(f"  {mark} {name:44s} reads {document}  pinned={pinned}")
        if not pinned:
            problems.append(f"{name}: parses {document} with no test pinning the shape")

    total = len(views) + len(found) + len(interfaces)
    undeclared = [line for line in problems if line.split(":")[0] not in ACCEPTED]
    print(f"\nsites: {total}   bare: {len(problems)}   accepted: {len(problems) - len(undeclared)}")
    for line in problems:
        name = line.split(":")[0]
        reason = ACCEPTED.get(name)
        print(f"  {'accepted' if reason else 'UNDECLARED'}  {line}")
        if reason:
            print(f"            reason: {reason}")
    stale = sorted(set(ACCEPTED) - {line.split(":")[0] for line in problems})
    for name in stale:
        print(f"  STALE ACCEPTANCE  {name} is guarded now; take it off the list")
    if (undeclared or stale) and "--check" in sys.argv:
        sys.exit(f"{len(undeclared)} undeclared bare site(s), {len(stale)} stale acceptance(s)")


if __name__ == "__main__":
    main()
