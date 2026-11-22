"""What a 32B episode actually costs, and what the full design would cost.

**Why it exists.** The design's size is known — 123 evaluation tasks by six
conditions by three seeds — but its price was an estimate, and an estimate is
not a number you can plan a rented A100 around. This reads the one 32B run that
exists (`b32c`) and reports what it consumed.

**Two clocks, and they are not the same.** `episodes.duration_seconds` is the
episode's own time. The session's wall clock is longer: the model loads, the
environment resets, and the gaps between episodes are billed too. Colab bills
the second. Both are reported, and their ratio is the overhead a plan has to
carry.

**The one number the record cannot supply** is the unit rate of the accelerator,
because it is a price and prices are not in the database. It is a parameter,
printed as declared, and everything derived from it is labelled.

Usage:

    uv run python scripts/setup/measure_compute_cost.py
    uv run python scripts/setup/measure_compute_cost.py --prefix b14 --units-per-hour 4.82
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

import sqlite3  # noqa: E402

OUTPUT = REPOSITORY / "results/compute-cost.json"
# The evaluation sample and the design's shape, both from the protocol rather
# than from this script.
#
# **Tasks: all 123.** K-144 stratifies the answer-type tasks, it does not remove
# them: they are run and reported separately. A projection over the 105 action
# tasks alone would be a projection of a design nobody declared.
#
# **Conditions: five, not six.** K-145 did not write the `naive_compiler`
# condition, because the naive miner reached all four of the compiler's skills on
# this corpus. Six was the number before that decision.
EVALUATION_TASKS = 123
CONDITIONS = 5
SEEDS = 3
# What the projection assumes, carried into the artefact so a reader does not
# have to reconstruct it from the arithmetic.
DESIGN_ASSUMPTION = (
    "123 evaluation tasks (test_normal minus the 45 setup touched; answer-type "
    "tasks are stratified by K-144, not removed) x 5 conditions (K-145 did not "
    "write naive_compiler) x 3 seeds. A lower bound: the session clock is "
    "measured from the first episode's start to the last one's end, so "
    "per-session setup -- clone, install, pulling the model -- is outside it, "
    "and 1845 episodes do not fit one session."
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="results/zihin-3.sqlite")
    parser.add_argument("--prefix", default="b32c")
    parser.add_argument(
        "--units-per-hour",
        type=float,
        default=None,
        help="the accelerator's unit rate; declared, not measured",
    )
    options = parser.parse_args()

    path = REPOSITORY / options.database
    if not path.exists():
        sys.exit(f"{options.database} does not exist; a cost is read from the record.")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT e.episode_id, e.run_id, e.duration_seconds, e.input_tokens, "
        "e.output_tokens, m.wall_clock_utc, m.model_tag "
        "FROM episodes e JOIN run_manifests m ON m.run_id = e.run_id "
        "WHERE e.run_id LIKE ? ORDER BY m.wall_clock_utc",
        (options.prefix + "-%",),
    ).fetchall()
    if not rows:
        sys.exit(
            f"no episode carries the prefix {options.prefix!r} in {options.database}. "
            "A cost cannot be read off a run that is not in the record."
        )

    durations = [r["duration_seconds"] for r in rows if r["duration_seconds"] is not None]
    if not durations:
        sys.exit(
            f"{len(rows)} episodes carry the prefix {options.prefix!r} but none has a "
            "duration. This measurement declines rather than reporting a zero cost."
        )

    stamps = sorted(r["wall_clock_utc"] for r in rows if r["wall_clock_utc"])
    import datetime

    first = datetime.datetime.fromisoformat(stamps[0])
    last = datetime.datetime.fromisoformat(stamps[-1])
    # The session runs to the end of the last episode, not to its start.
    last_duration = (
        next((r["duration_seconds"] for r in rows if r["wall_clock_utc"] == stamps[-1]), 0.0) or 0.0
    )
    session_seconds = (last - first).total_seconds() + last_duration

    episode_seconds = sum(durations)
    n = len(durations)
    mean_h = episode_seconds / n / 3600
    session_per_episode_h = session_seconds / n / 3600
    total_episodes = EVALUATION_TASKS * CONDITIONS * SEEDS

    report = {
        "what": "the measured cost of one 32B episode, and the design projected from it",
        "database": options.database,
        "prefix": options.prefix,
        "model_tag": rows[0]["model_tag"],
        "episodes": n,
        "first_episode_utc": stamps[0],
        "last_episode_utc": stamps[-1],
        "episode_clock": {
            "total_seconds": round(episode_seconds, 1),
            "mean_seconds": round(statistics.mean(durations), 1),
            "median_seconds": round(statistics.median(durations), 1),
            "min_seconds": round(min(durations), 1),
            "max_seconds": round(max(durations), 1),
            "hours_per_episode": round(mean_h, 5),
        },
        "session_clock": {
            "total_seconds": round(session_seconds, 1),
            "hours": round(session_seconds / 3600, 3),
            "hours_per_episode": round(session_per_episode_h, 5),
            "overhead_ratio": round(session_seconds / episode_seconds, 3),
        },
        "tokens": {
            "input_total": sum(r["input_tokens"] or 0 for r in rows),
            "output_total": sum(r["output_tokens"] or 0 for r in rows),
            "input_per_episode": round(sum(r["input_tokens"] or 0 for r in rows) / n, 1),
            "output_per_episode": round(sum(r["output_tokens"] or 0 for r in rows) / n, 1),
        },
        "design": {
            "assumption": DESIGN_ASSUMPTION,
            "is_a_lower_bound": True,
            "evaluation_tasks": EVALUATION_TASKS,
            "conditions": CONDITIONS,
            "seeds": SEEDS,
            "episodes": total_episodes,
            "episode_clock_hours": round(total_episodes * mean_h, 1),
            "session_clock_hours": round(total_episodes * session_per_episode_h, 1),
        },
        "units_per_hour": options.units_per_hour,
    }
    if options.units_per_hour:
        report["design"]["units_declared_rate"] = round(
            total_episodes * session_per_episode_h * options.units_per_hour, 1
        )
        report["measured_run_units_declared_rate"] = round(
            session_seconds / 3600 * options.units_per_hour, 2
        )
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"prefix {options.prefix}  model {report['model_tag']}  episodes {n}")
    print(f"  window            : {stamps[0]} -> {stamps[-1]} UTC")
    print(
        f"  episode clock     : {episode_seconds / 3600:.3f} h total, "
        f"mean {statistics.mean(durations):.1f} s, median {statistics.median(durations):.1f} s"
    )
    print(
        f"  session clock     : {session_seconds / 3600:.3f} h, "
        f"overhead x{session_seconds / episode_seconds:.2f}"
    )
    print(f"  hours per episode : {mean_h:.5f} episode-clock, {session_per_episode_h:.5f} session")
    print()
    print(
        f"design: {EVALUATION_TASKS} tasks x {CONDITIONS} conditions x {SEEDS} seeds "
        f"= {total_episodes} episodes  (a lower bound; per-session setup is outside)"
    )
    print(f"  episode clock     : {total_episodes * mean_h:.1f} h")
    print(f"  session clock     : {total_episodes * session_per_episode_h:.1f} h")
    if options.units_per_hour:
        print(
            f"  units at declared {options.units_per_hour}/h : "
            f"{total_episodes * session_per_episode_h * options.units_per_hour:.0f}"
        )
    else:
        print("  units             : pass --units-per-hour; a price is not in the record")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
