"""How the library grows with the corpus, and where the growth flattens.

**Why it exists.** "Run 32B over the train split until the library saturates" is
not a plan until saturation has a shape. This measures the shape from the corpus
that already exists: mine the library from k distinct passing tasks, for every k,
and see what the curve does.

**The x-axis is distinct passing tasks, not episodes.** Support is counted by
distinct task (`mine_patterns`, min_support 3), so a second episode on a task
already in the corpus adds nothing to support. Episodes are what a run spends;
distinct passing tasks are what the library is paid in. The conversion between
them is the pass rate, and it is a separate measured number.

**Deterministic, no model calls.** The corpus is read from the record and the
miner is a pure function of it. The order tasks enter in does matter, so several
orders are drawn from a fixed seed and the curve is reported as a mean with a
range rather than as one line.

Usage:

    uv run python scripts/setup/measure_accumulation.py
    uv run python scripts/setup/measure_accumulation.py --orders 20
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import statistics
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))
sys.path.insert(0, str(REPOSITORY / "scripts/setup"))

import sqlite3  # noqa: E402

from build_failure_index import every_observed_episode  # noqa: E402
from mine_skills import CALIBRATION_MODEL_TAG, CALIBRATION_SPLIT, passing_sequences  # noqa: E402

from zihin.compiler import mine_patterns  # noqa: E402
from zihin.failure_index import mine_failure_patterns  # noqa: E402
from zihin.records import LIBRARY_SERIES  # noqa: E402

OUTPUT = REPOSITORY / "results/accumulation.json"
# The library's own configuration, so the curve is the curve of *this* library
# and not of a different one that happens to be cheaper to draw.
MIN_SUPPORT = 3
MAX_GAP = 2
# The failure index's own configuration.
FAILURE_SUPPORT = 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=LIBRARY_SERIES)
    parser.add_argument("--orders", type=int, default=12)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument(
        "--scan",
        default="results/b32c-taramasi.json",
        help="the run whose pass rate converts episodes into distinct passing tasks",
    )
    parser.add_argument("--train-tasks", type=int, default=90)
    options = parser.parse_args()

    path = REPOSITORY / options.database
    if not path.exists():
        sys.exit(f"{options.database} does not exist; the curve is read from a corpus.")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    sequences = passing_sequences(
        connection, model_tag=CALIBRATION_MODEL_TAG, split=CALIBRATION_SPLIT
    )
    by_task: dict[str, list] = collections.defaultdict(list)
    for sequence in sequences:
        by_task[sequence.task_id].append(sequence)
    tasks = sorted(by_task)
    if len(tasks) < MIN_SUPPORT:
        sys.exit(
            f"the corpus holds {len(tasks)} distinct passing task(s) and support is "
            f"{MIN_SUPPORT}. There is no curve to draw; this declines rather than "
            "reporting a flat line."
        )

    print(f"corpus: {len(sequences)} passing episodes over {len(tasks)} distinct tasks")
    print(f"mining at min_support={MIN_SUPPORT}, max_gap={MAX_GAP}, {options.orders} orders")
    print()

    rng = random.Random(options.seed)
    curve: dict[int, list[int]] = collections.defaultdict(list)
    for _ in range(options.orders):
        order = tasks[:]
        rng.shuffle(order)
        for k in range(MIN_SUPPORT, len(order) + 1):
            subset = [s for task in order[:k] for s in by_task[task]]
            result = mine_patterns(subset, min_support=MIN_SUPPORT, max_gap=MAX_GAP)
            curve[k].append(len(result.patterns))

    print(f"{'tasks':>5} {'patterns mean':>14} {'min':>5} {'max':>5} {'marginal':>9}")
    print("-" * 44)
    rows = []
    previous = None
    for k in sorted(curve):
        values = curve[k]
        mean = statistics.mean(values)
        marginal = None if previous is None else mean - previous
        rows.append(
            {
                "tasks": k,
                "patterns_mean": round(mean, 2),
                "patterns_min": min(values),
                "patterns_max": max(values),
                "marginal": None if marginal is None else round(marginal, 2),
            }
        )
        print(
            f"{k:5d} {mean:14.2f} {min(values):5d} {max(values):5d} "
            f"{'' if marginal is None else f'{marginal:+9.2f}'}"
        )
        previous = mean

    # --- the failure index: its substrate is every episode, not the passing ones
    observed = every_observed_episode(connection)
    episode_to_task = {
        row["episode_id"]: row["task_id"]
        for row in connection.execute("SELECT episode_id, task_id FROM episodes")
    }
    failure_by_task: dict[str, dict[int, list]] = collections.defaultdict(dict)
    for episode_id, actions in observed.items():
        failure_by_task[episode_to_task.get(episode_id, str(episode_id))][episode_id] = actions
    failure_tasks = sorted(failure_by_task)

    print()
    print(f"failure substrate: {len(observed)} episodes over {len(failure_tasks)} distinct tasks")
    failure_curve: dict[int, list[int]] = collections.defaultdict(list)
    steps = sorted({max(1, round(len(failure_tasks) * f / 10)) for f in range(1, 11)})
    for _ in range(options.orders):
        order = failure_tasks[:]
        rng.shuffle(order)
        for k in steps:
            subset = {}
            for task in order[:k]:
                subset.update(failure_by_task[task])
            found, _ = mine_failure_patterns(subset, min_support=FAILURE_SUPPORT)
            failure_curve[k].append(len(found))

    print(f"{'tasks':>5} {'cards mean':>11} {'min':>5} {'max':>5} {'marginal':>9}")
    print("-" * 40)
    failure_rows = []
    previous_f = None
    for k in sorted(failure_curve):
        values = failure_curve[k]
        mean = statistics.mean(values)
        marginal = None if previous_f is None else mean - previous_f
        failure_rows.append(
            {
                "tasks": k,
                "cards_mean": round(mean, 2),
                "cards_min": min(values),
                "cards_max": max(values),
                "marginal": None if marginal is None else round(marginal, 2),
            }
        )
        print(
            f"{k:5d} {mean:11.2f} {min(values):5d} {max(values):5d} "
            f"{'' if marginal is None else f'{marginal:+9.2f}'}"
        )
        previous_f = mean

    full = rows[-1]["patterns_mean"]

    # Where the curve first reaches a share of what the whole corpus yields.
    def first_at(share: float) -> int | None:
        for row in rows:
            if row["patterns_mean"] >= share * full:
                return row["tasks"]
        return None

    # --- the conversion: episodes are spent, distinct passing tasks are earned
    scan_path = REPOSITORY / options.scan
    projection = None
    if scan_path.exists():
        scan = json.loads(scan_path.read_text(encoding="utf-8"))
        episodes = scan.get("episodes_with_steps") or []
        passed_tasks = {e["task"] for e in episodes if e.get("passed")}
        attempted = {e["task"] for e in episodes}
        if attempted:
            rate = len(passed_tasks) / len(attempted)
            train = options.train_tasks
            projection = {
                "scan": options.scan,
                "model": scan.get("model"),
                "tasks_attempted": len(attempted),
                "tasks_passed": len(passed_tasks),
                "pass_rate": round(rate, 4),
                "train_tasks": train,
                "episodes_for_one_sweep": train,
                "expected_new_passing_tasks": round(train * rate, 1),
                "corpus_after_one_sweep": round(len(tasks) + train * rate, 1),
                # What one sweep buys, read off the measured curve's slope at its
                # end rather than off a fitted shape: the curve is still convex,
                # so a fit would be a guess dressed as a projection.
                "marginal_patterns_per_task_at_corpus_end": rows[-1]["marginal"],
            }

    report = {
        "what": "how many patterns the miner finds from k distinct passing tasks",
        "database": options.database,
        "min_support": MIN_SUPPORT,
        "max_gap": MAX_GAP,
        "orders": options.orders,
        "seed": options.seed,
        "passing_episodes": len(sequences),
        "distinct_passing_tasks": len(tasks),
        "curve": rows,
        "patterns_at_full_corpus": full,
        "tasks_for_half": first_at(0.5),
        "tasks_for_eighty_percent": first_at(0.8),
        "tasks_for_ninety_percent": first_at(0.9),
        "projection": projection,
        "failure_index": {
            "min_support": FAILURE_SUPPORT,
            "substrate_episodes": len(observed),
            "substrate_tasks": len(failure_tasks),
            "curve": failure_rows,
            "cards_at_full_substrate": failure_rows[-1]["cards_mean"] if failure_rows else None,
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"patterns at the full corpus ({len(tasks)} tasks): {full:.2f}")
    print(f"  half of that reached at   : {first_at(0.5)} tasks")
    print(f"  80% of that reached at    : {first_at(0.8)} tasks")
    print(f"  90% of that reached at    : {first_at(0.9)} tasks")
    if projection:
        print()
        print(f"conversion, from {projection['scan']}:")
        print(
            f"  pass rate                 : {projection['tasks_passed']}/"
            f"{projection['tasks_attempted']} = {projection['pass_rate']:.1%}"
        )
        print(f"  one sweep of train        : {projection['episodes_for_one_sweep']} episodes")
        print(f"  expected new passing tasks: {projection['expected_new_passing_tasks']}")
        print(
            f"  corpus after one sweep    : {projection['corpus_after_one_sweep']} distinct tasks"
        )
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
