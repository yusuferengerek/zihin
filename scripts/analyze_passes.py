"""What a pass on a given task actually required, and what the episode did.

**Why this exists.** In the 14B scan two of three passes were on a task whose
anchor is 102 and which was finished in six steps. Reading the task showed why:
its evaluation carries two tests and only one of them fails for an agent that
does nothing — a string equality on an answer. The anchor measures the reference
solution's path, not what the task requires (S-62).

**What is read where.** The task's own `ground_truth/evaluation.py` is read from
the installed AppWorld data: how many tests it carries, and whether it checks an
**answer** or a **change in the world**. The run's side — how many of those tests
the episode passed, how many were meaningful, how many steps it took — is read
from a scan's JSON output. Neither is inferred from the other.

**What it does not do.** It does not decide whether a pass is "real". It puts the
numbers next to each other so that the question can be asked with them.

Usage:

    uv run python scripts/analyze_passes.py results/b14-taramasi.json
    uv run python scripts/analyze_passes.py <scan.json> --all
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
TASKS = REPOSITORY / "data/tasks"

# A test block in AppWorld's evaluation files: `with test(""" ... """):`
TEST_BLOCK = re.compile(r"^\s*with test\(", re.M)
# The two shapes a test can take. An answer test compares what the agent said;
# a world test compares what the agent changed. A task can carry both.
ANSWER_MARKS = ("ground_truth_answer", "predicted_answer")
WORLD_MARKS = ("changed_model_names", "models.end", "models.start")
# `assert no model changes` is the one that a do-nothing agent passes.
NO_CHANGE = re.compile(r"changed_model_names\(\),\s*[\"']is_falsy")


def task_shape(task: str) -> dict:
    """What the task's own evaluation asks for."""
    path = TASKS / task / "ground_truth" / "evaluation.py"
    if not path.exists():
        return {"tests": None, "kind": "unknown", "detail": f"{path} is absent"}
    text = path.read_text(encoding="utf-8")
    tests = len(TEST_BLOCK.findall(text))
    answer = any(mark in text for mark in ANSWER_MARKS)
    world = any(mark in text for mark in WORLD_MARKS)
    no_change = bool(NO_CHANGE.search(text))
    if answer and not no_change:
        kind = "answer+world"
    elif answer:
        kind = "answer"
    elif world:
        kind = "world"
    else:
        kind = "unknown"
    return {
        "tests": tests,
        "kind": kind,
        "asserts_no_change": no_change,
        "checks_answer": answer,
    }


def rows(scan: dict) -> list[dict]:
    return scan.get("episodes_with_steps") or []


def main() -> None:
    arguments = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not arguments:
        sys.exit("usage: analyze_passes.py <scan.json> [--all]")
    path = pathlib.Path(arguments[0])
    if not path.exists():
        sys.exit(f"{path} does not exist. A scan that was not published cannot be read.")
    scan = json.loads(path.read_text(encoding="utf-8"))
    everything = "--all" in sys.argv

    episodes = rows(scan)
    chosen = episodes if everything else [e for e in episodes if e.get("passed")]
    model = scan.get("model", "?")
    print(f"scan   : {path.name}")
    print(f"model  : {model}")
    print(f"episodes: {len(episodes)}, passed: {sum(1 for e in episodes if e.get('passed'))}")
    print()

    header = (
        f"{'task':12} {'band':7} {'anchor':>6} {'steps':>6} {'tests':>5} "
        f"{'mean':>7} {'noop':>4} {'triv':>4}  {'kind':12} termination"
    )
    print(header)
    print("-" * len(header))
    for episode in sorted(chosen, key=lambda e: (e["band"], e["task"])):
        shape = task_shape(episode["task"])
        meaningful = f"{episode.get('meaningful_passed')}/{episode.get('meaningful_total')}"
        # Tests a do-nothing agent would pass: the total minus the meaningful.
        total = episode.get("tests_total") or shape["tests"]
        noop = (
            (total - episode["meaningful_total"])
            if (total and episode.get("meaningful_total") is not None)
            else "?"
        )
        print(
            f"{episode['task']:12} {episode['band']:7} {episode['anchor']:6} "
            f"{episode['step']:6} {str(shape['tests']):>5} {meaningful:>7} "
            f"{str(noop):>4} {str(episode.get('trivial_passed')):>4}  "
            f"{shape['kind']:12} {episode['termination']}"
        )

    print()
    kinds: dict[str, list[dict]] = {}
    for episode in episodes:
        kinds.setdefault(task_shape(episode["task"])["kind"], []).append(episode)
    print("task kind over the whole set (what the evaluation asks for):")
    for kind, group in sorted(kinds.items()):
        passed = sum(1 for e in group if e.get("passed"))
        anchors = [e["anchor"] for e in group]
        print(
            f"  {kind:12} {len(group):2} task(s), {passed} passed, "
            f"anchor {min(anchors)}-{max(anchors)}"
        )

    print()
    print(
        "The anchor is the reference solution's call count, not the task's\n"
        "requirement (S-62). A low step count on a high anchor is not by itself\n"
        "evidence of anything; the test counts beside it are what the pass rests on."
    )


if __name__ == "__main__":
    main()
