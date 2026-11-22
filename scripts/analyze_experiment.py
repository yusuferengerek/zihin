"""What may be read of the experiment before it is finished, and whether its slices pool (K-186).

**Before the full set: descriptive only.** Tasks finished, episodes written, the
mean duration over every condition together. No pass rate, no model-call count,
nothing by condition, no interval: the preregistration's partial-reading rule
(A.7's addendum of 26 September 2026). `--confirmatory` is refused until every
planned episode is written.

**Whether the slices pool.** Every experiment episode carries its commit in its
manifest. Each commit is compared with the experiment's first one on the
measurement-defining paths (`zihin.records.MEASUREMENT_DEFINING_PATHS`): episodes
whose code differs there from the first episode's in the same way form one
comparability group. A slice that spans two groups, or two consecutive slices in
different groups, cannot be pooled across that change, and the change needs a
dated addendum. A commit git cannot read is a break too - an unreadable
comparison is not an agreement. The script exits non-zero when anything does not
pool, so nothing downstream pools it silently.

Usage:

    uv run python scripts/analyze_experiment.py
    uv run python scripts/analyze_experiment.py --confirmatory
"""

from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys
from collections.abc import Callable

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.declared import EXPERIMENT_PREFIX, declared_model  # noqa: E402
from zihin.experiment import descriptive, load_sets  # noqa: E402
from zihin.records import ACTIVE_SERIES, changed_files  # noqa: E402


def comparability(
    rows: list[tuple[int, int, str]], defining_between: Callable[[str, str], list[str]]
) -> dict:
    """(episode id, slice, commit) in episode order -> the groups and the breaks."""
    if not rows:
        return {"groups": [], "breaks": [], "poolable": True}
    first = rows[0][2]
    key_of: dict[str, tuple[str, ...]] = {}
    for _, _, commit in rows:
        if commit not in key_of:
            key_of[commit] = (
                () if commit == first else tuple(sorted(defining_between(first, commit)))
            )
    groups: list[tuple[str, ...]] = []
    for _, _, commit in rows:
        if key_of[commit] not in groups:
            groups.append(key_of[commit])
    by_slice: dict[int, list[int]] = {}
    for _, number, commit in rows:
        index = groups.index(key_of[commit])
        if index not in by_slice.setdefault(number, []):
            by_slice[number].append(index)
    breaks = []
    for number, indices in sorted(by_slice.items()):
        if len(indices) > 1:
            breaks.append(f"slice {number} spans comparability groups {sorted(indices)}")
    numbers = sorted(by_slice)
    for a, b in zip(numbers, numbers[1:], strict=False):
        if sorted(by_slice[a]) != sorted(by_slice[b]):
            breaks.append(
                f"slices {a} and {b} ran on code that differs on measurement-defining paths"
            )
    return {
        "groups": [list(key) for key in groups],
        "breaks": breaks,
        "poolable": len(groups) == 1,
    }


def experiment_rows(connection: sqlite3.Connection, prefix: str) -> list[tuple[int, int, str]]:
    return [
        tuple(row)
        for row in connection.execute(
            "SELECT e.episode_id, x.slice, m.code_commit FROM episodes e "
            "JOIN experiment_episodes x ON x.episode_id = e.episode_id "
            "JOIN run_manifests m ON m.run_id = e.run_id "
            "WHERE e.run_id LIKE ? ORDER BY e.episode_id",
            (prefix + "-%",),
        )
    ]


def complete(summary: dict) -> bool:
    """Every planned episode written, on every task of the order."""
    return (
        summary["tasks_finished"] == summary["tasks"]
        and summary["episodes"] >= summary["episodes_planned"]
    )


def report(summary: dict, pooling: dict) -> list[str]:
    """The lines that may be printed before the full set: nothing else."""
    mean = summary["mean_duration_seconds"]
    lines = [
        f"tasks finished : {summary['tasks_finished']} of {summary['tasks']}",
        f"episodes       : {summary['episodes']} of {summary['episodes_planned']}",
        f"mean duration  : {'-' if mean is None else f'{mean} s'}, every condition together",
        f"comparability  : {len(pooling['groups'])} group(s)",
    ]
    for index, key in enumerate(pooling["groups"]):
        changed = ", ".join(key) if key else "the first episode's code"
        lines.append(f"  group {index}: {changed}")
    lines += [f"  BREAK: {line}" for line in pooling["breaks"]]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirmatory", action="store_true", help="refused until the full set is written"
    )
    options = parser.parse_args()
    short = declared_model(EXPERIMENT_PREFIX).split(":")[1].split("-")[0]
    sets = load_sets()
    path = REPOSITORY / ACTIVE_SERIES
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        summary = descriptive(connection, sets, EXPERIMENT_PREFIX, short)
        rows = experiment_rows(connection, EXPERIMENT_PREFIX)
    finally:
        connection.close()
    pooling = comparability(rows, lambda a, b: changed_files(a, b)[1])
    for line in report(summary, pooling):
        print(line)
    if options.confirmatory:
        if not complete(summary):
            sys.exit(
                "REFUSED: the full set is not written. Before it, the experiment is read "
                "descriptively only (preregistration A.7, K-186)."
            )
        sys.exit(
            "the full set is written; the confirmatory analysis is not part of this script yet"
        )
    if not pooling["poolable"]:
        sys.exit("the slices do not pool across a measurement-defining change; see the breaks")


if __name__ == "__main__":
    main()
