"""What the evaluation sample asks for: an answer, or a change in the world.

**Why it exists.** This pilot's mechanisms are about *doing*: the skill library
holds API call sequences, the failure index holds call failures. A task whose
evaluation only compares a string can be passed without either. So "how many of
the sample can the mechanisms possibly help with" is a property of the sample,
and it is readable before a single episode runs.

**One classifier, not a second one.** The shape of a task is read by
`scripts/analyze_passes.py`'s `task_shape`, imported rather than re-implemented.
Two copies would drift and the drift would be silent — the same defect the
declared-conditions check exists to catch (K-136).

**What the sample is.** `test_normal` minus the tasks setup touched
(read through `zihin.touched`, protocol §3). Excluded tasks stay in the
accumulation pool; they are out of the evaluation only.

Usage:

    uv run python scripts/setup/measure_task_types.py
    uv run python scripts/setup/measure_task_types.py --split train
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import pathlib
import statistics
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from appworld.task import load_task_ids  # noqa: E402

from zihin.touched import TouchedListError, load_touched  # noqa: E402

OUTPUT = REPOSITORY / "results/task-types.json"


def classifier():
    """`task_shape` from the pass analysis, so there is one definition of a kind."""
    path = REPOSITORY / "scripts/analyze_passes.py"
    spec = importlib.util.spec_from_file_location("analyze_passes", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_passes"] = module
    spec.loader.exec_module(module)
    return module.task_shape


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="test_normal")
    parser.add_argument(
        "--keep-touched",
        action="store_true",
        help="do not remove the tasks setup touched",
    )
    options = parser.parse_args()

    task_shape = classifier()
    everything = list(load_task_ids(options.split))
    touched: list[str] = []
    if not options.keep_touched:
        try:
            listed = load_touched()
        except TouchedListError as error:
            sys.exit(str(error))
        print(f"touched list: {listed.basis}")
        touched = listed.tasks(options.split)
    sample = [t for t in everything if t not in set(touched)]

    kinds: collections.Counter[str] = collections.Counter()
    tests: collections.Counter[str] = collections.Counter()
    # A task whose evaluation asserts that nothing changed hands a do-nothing agent
    # one passing test for free. With few tests in the file, that one test is a
    # large share of the verdict, so the two strata are not equally strict and the
    # numbers that show it belong in the artefact rather than in prose.
    free_test: collections.Counter[str] = collections.Counter()
    test_counts: dict[str, list[int]] = collections.defaultdict(list)
    unreadable = []
    per_task = {}
    for task in sample:
        shape = task_shape(task)
        if shape["kind"] == "unknown" and shape.get("tests") is None:
            unreadable.append(task)
            continue
        kinds[shape["kind"]] += 1
        tests[shape["kind"]] += shape["tests"] or 0
        test_counts[shape["kind"]].append(shape["tests"] or 0)
        if shape.get("asserts_no_change"):
            free_test[shape["kind"]] += 1
        per_task[task] = {
            "kind": shape["kind"],
            "tests": shape["tests"],
            "asserts_no_change": bool(shape.get("asserts_no_change")),
        }

    readable = sum(kinds.values())
    if not readable:
        sys.exit(
            f"none of the {len(sample)} tasks could be read. `data/tasks` is probably "
            "not installed; the measurement declines rather than reporting a "
            "distribution over nothing."
        )
    # The axis the pilot cares about: does passing require changing the world.
    answer_only = kinds["answer"]
    needs_world = kinds["answer+world"] + kinds["world"]

    report = {
        "what": "what the evaluation sample's tasks ask for: an answer, or a changed world",
        "split": options.split,
        "tasks_in_split": len(everything),
        "touched_and_removed": len(touched),
        "sample": len(sample),
        "readable": readable,
        "unreadable": unreadable,
        "kinds": dict(kinds),
        "tests_per_kind": dict(tests),
        "median_tests_per_kind": {
            kind: statistics.median(values) for kind, values in test_counts.items()
        },
        "asserts_no_change_per_kind": dict(free_test),
        "answer_only": answer_only,
        "needs_world_change": needs_world,
        "needs_world_change_share": round(needs_world / readable, 4),
        "per_task": per_task,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"split {options.split}: {len(everything)} tasks, "
        f"{len(touched)} touched by setup and removed, sample {len(sample)}"
    )
    if unreadable:
        print(f"  unreadable: {len(unreadable)}")
    print()
    width = max(len(k) for k in kinds)
    for kind, count in kinds.most_common():
        print(f"  {kind.ljust(width)}  {count:3d}  {count / readable:6.1%}  ({tests[kind]} tests)")
    print()
    print()
    for kind in sorted(test_counts):
        print(
            f"  {kind.ljust(width)}  median {statistics.median(test_counts[kind]):.0f} test(s), "
            f"{free_test[kind]} of {kinds[kind]} hand a do-nothing agent a free pass"
        )
    print()
    print(f"  answer only          : {answer_only:3d}  {answer_only / readable:6.1%}")
    print(f"  requires a world change: {needs_world:3d}  {needs_world / readable:6.1%}")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
