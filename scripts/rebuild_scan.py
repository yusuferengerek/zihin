"""Rebuilds a scan's JSON summary from the record, when the JSON was lost.

**Why from the record.** The Colab session that produced `b32c` closed and took
its JSON with it. The episodes survived in the database, which is the append-only
record; the JSON is a projection of it. A projection can be rebuilt, and a number
that was pasted into a chat cannot be checked, so it is rebuilt rather than
retyped.

**What is exact and what is not, stated per field.** Everything the database
holds — the task, the termination, the steps, the durations, the verifier's pass
and its test counts — is exact. Two fields are not in the database:

*`meaningful_total`*, the number of a task's tests that an agent doing nothing
would fail. It is a property of the task, not of the run, and that was checked
rather than assumed: across every scan that recorded it, the value agrees for
every one of the thirty tasks. It is taken from a reference scan, and the
reference is named in the output.

*`meaningful_passed`*, how many of those the episode passed. This is determined
only at the ends: when no test failed, all of them passed; when none passed, none
did. In between the database records how many tests passed but not which, so the
field is left null and a bound is written beside it. Guessing a number there
would be inventing a measurement.

Usage:

    uv run python scripts/rebuild_scan.py <database> <prefix> <reference-scan> [-o out.json]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.declared import conditions  # noqa: E402

# The band scan's own numbers, and they are repeated here rather than imported
# because `measure_band.py` parses arguments at import time. They are checked
# against the scan being rebuilt: if the rebuilt bands disagree with the
# reference scan's `band_size`, the rebuild says so instead of publishing.
BANDS = ((1, 10), (11, 20), (21, 40), (41, 89), (90, 10**9))
MULTIPLIER = 2.0
FLOOR_CEILING = 20
CEILING_CAP = 150


def band_name(low: int, high: int) -> str:
    return f"{low}-{high}" if high < 10**9 else f"{low}+"


def band_of(anchor: int) -> str:
    for low, high in BANDS:
        if low <= anchor <= high:
            return band_name(low, high)
    return "?"


def anchor_of(task: str) -> int:
    path = REPOSITORY / "data/tasks" / task / "ground_truth/metadata.json"
    return int(json.loads(path.read_text(encoding="utf-8"))["num_api_calls"])


def ceiling_of(anchor: int) -> int:
    return min(max(int(MULTIPLIER * anchor), FLOOR_CEILING), CEILING_CAP)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("prefix")
    parser.add_argument("reference", help="a scan that recorded meaningful_total")
    parser.add_argument("-o", "--output", default=None)
    options = parser.parse_args()

    reference = json.loads(pathlib.Path(options.reference).read_text(encoding="utf-8"))
    key = "episodes_with_steps" if "episodes_with_steps" in reference else "episodes"
    meaningful_total = {row["task"]: row.get("meaningful_total") for row in reference.get(key, [])}

    connection = sqlite3.connect(f"file:{options.database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT e.task_id, e.split, e.termination_reason, e.total_model_calls, "
        "e.duration_seconds, e.step_ceiling, "
        "COALESCE(v.passed, 0) passed, v.num_passed_tests, v.num_failed_tests "
        "FROM episodes e LEFT JOIN verifier_results v USING(episode_id) "
        "WHERE e.run_id LIKE ? AND e.run_id NOT LIKE '%onkontrol%' ORDER BY e.task_id",
        (options.prefix + "-%",),
    ).fetchall()
    if not rows:
        sys.exit(f"no episode carries the prefix {options.prefix!r}")

    _, declared = conditions(options.prefix)
    episodes = []
    for row in rows:
        task = row["task_id"]
        anchor = anchor_of(task)
        total_tests = (row["num_passed_tests"] or 0) + (row["num_failed_tests"] or 0)
        meaningful = meaningful_total.get(task)
        entry = {
            "task": task,
            "band": band_of(anchor),
            "anchor": anchor,
            "ceiling": ceiling_of(anchor),
            "ceiling_at_cap": ceiling_of(anchor) == CEILING_CAP,
            "step": row["total_model_calls"],
            "termination": row["termination_reason"],
            "elapsed": row["duration_seconds"],
            "passed": row["passed"],
            "tests_total": total_tests,
            "tests_passed": row["num_passed_tests"],
            "tests_failed": row["num_failed_tests"],
            "meaningful_total": meaningful,
        }
        if meaningful is None:
            entry["meaningful_passed"] = None
            entry["meaningful_passed_bound"] = "the reference scan records no total"
        elif row["num_failed_tests"] == 0:
            entry["meaningful_passed"] = meaningful
            entry["trivial_passed"] = total_tests - meaningful
        elif row["num_passed_tests"] == 0:
            entry["meaningful_passed"] = 0
            entry["trivial_passed"] = 0
        else:
            passed = row["num_passed_tests"]
            low = max(0, passed - (total_tests - meaningful))
            entry["meaningful_passed"] = None
            entry["meaningful_passed_bound"] = [low, min(passed, meaningful)]
        episodes.append(entry)

    if row["step_ceiling"] and any(
        e["ceiling"] != r["step_ceiling"] for e, r in zip(episodes, rows, strict=True)
    ):
        print("note: a rebuilt ceiling disagrees with the recorded step_ceiling", file=sys.stderr)

    band_size = reference.get("band_size")
    summary = {
        "database": options.database,
        "prefix": options.prefix,
        "split": rows[0]["split"],
        "model": declared["model_tag"],
        "multiplier": MULTIPLIER,
        "floor_ceiling": FLOOR_CEILING,
        "ceiling_cap": CEILING_CAP,
        "band_size": band_size,
        "rebuilt_from_the_record": {
            "why": (
                "the Colab session closed and took the scan's JSON with it; the "
                "episodes survived in the append-only record"
            ),
            "exact": [
                "task",
                "band",
                "anchor",
                "ceiling",
                "step",
                "termination",
                "elapsed",
                "passed",
                "tests_total",
                "tests_passed",
                "tests_failed",
            ],
            "from_reference": {
                "meaningful_total": options.reference,
                "checked": (
                    "meaningful_total agrees for every task across every scan that "
                    "recorded it, so it is a property of the task rather than of the run"
                ),
            },
            "not_reconstructable": (
                "meaningful_passed is determined only when no test failed or none "
                "passed; otherwise a bound is written and the field is null"
            ),
            "band_size": "copied from the reference scan; it describes the split, not the run",
        },
        "episodes_with_steps": episodes,
    }

    out = pathlib.Path(options.output or f"results/{options.prefix}-taramasi.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    passed = sum(e["passed"] for e in episodes)
    graded_n = sum(
        e["meaningful_passed"] or 0 for e in episodes if e["meaningful_passed"] is not None
    )
    graded_d = sum(e["meaningful_total"] or 0 for e in episodes)
    ceiling_hits = sum(1 for e in episodes if e["termination"] == "step_ceiling")
    print(f"written : {out}")
    print(f"episodes: {len(episodes)}   passed: {passed}")
    print(f"graded  : {graded_n}/{graded_d}  (numerator counts only determined episodes)")
    print(f"ceiling : {ceiling_hits}/{len(episodes)} = {ceiling_hits / len(episodes):.1%}")
    reasons: dict[str, int] = {}
    for entry in episodes:
        reasons[entry["termination"]] = reasons.get(entry["termination"], 0) + 1
    print(f"endings : {reasons}")


if __name__ == "__main__":
    main()
