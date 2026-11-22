"""Calibrates the stopping rule's threshold over the recorded episodes.

There is a single criterion: **the corrected rule must not cut an episode that
passed.** The threshold is chosen from that condition, not set by hand.

The rule itself is not rewritten here. The steps are rebuilt from the database in
the production form and `RecordingAgent._check_progress` is called. The reason is
S-32: because the rule and the code testing it walked separate paths, the
criterion never ran and nobody noticed. A calibration tool reinterpreting the rule
would be a mistake of the same class.

**Complete trajectories only.** An episode with `termination_reason =
'no_progress'` was cut; what it would have done past the cut is unknown, so its
real stall length cannot be measured. Such episodes do not enter the calibration
set, and how many were dropped is printed: no silent filtering.

**More than one prefix.** Cut episodes are re-run with the rule off and written
under a separate prefix. If the same task appears under two prefixes, the one with
a complete trajectory is taken; if both are complete, the later prefix wins.
Merging the two prefixes is legitimate because a rule that never fires has no
effect on the episode, but which episode came from which prefix and under which
threshold is written both to the screen and to the JSON.

Usage:

    uv run python scripts/setup/calibrate_stopping_rule.py sinir3 sinir3-kapali
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys

from zihin.recording_agent import NoProgress, RecordingAgent
from zihin.records import ACTIVE_SERIES


def parse_options(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("onekler", nargs="+", help="Run prefixes, in order.")
    parser.add_argument("--database", default=ACTIVE_SERIES)
    parser.add_argument(
        "--thresholds",
        default="4,6,8,10,12,15,20,25,30",
        help="Thresholds to try, comma separated.",
    )
    parser.add_argument("--output", default=None, help="JSON output path.")
    return parser.parse_args(argv)


def episodes_with_steps(connection: sqlite3.Connection, prefix: str) -> list[dict]:
    """The episodes matching the prefix, with their steps and identity sets.

    The identity set is derived from the action rows: what enters the rule and
    what enters the record should come from the same source.

    The prefix match is tested together with the task id. A bare `LIKE 'x-%'`
    also catches `x-off-...` rows; because the run id has the form
    `prefix-task-model`, requiring the row to start with `prefix-task-` cuts
    those off.
    """
    rows = connection.execute(
        "SELECT e.episode_id, e.run_id, e.task_id, e.termination_reason, "
        "       e.total_model_calls, e.step_ceiling, v.passed, m.no_progress_limit "
        "FROM episodes e JOIN run_manifests m USING(run_id) "
        "LEFT JOIN verifier_results v USING(episode_id) "
        "WHERE e.run_id LIKE ? ORDER BY e.episode_id",
        (f"{prefix}-%",),
    ).fetchall()

    result = []
    for episode_id, run_id, task, termination, step_count, ceiling, passed, threshold in rows:
        if not run_id.startswith(f"{prefix}-{task}-"):
            continue
        steps = []
        for step_id, state in connection.execute(
            "SELECT step_id, state_change FROM steps WHERE episode_id = ? ORDER BY step_index",
            (episode_id,),
        ).fetchall():
            # The identity is built in exactly the form the live path uses:
            # `insert_action` writes the parameters with `sort_keys=True`, and
            # `step_progress_identities` produces them the same way.
            kimlikler = {
                f"{app}.{api}|{prm if prm is not None else '{}'}"
                for app, api, prm in connection.execute(
                    "SELECT app, api, raw_parameters FROM actions WHERE step_id = ? "
                    "ORDER BY action_index",
                    (step_id,),
                ).fetchall()
            }
            steps.append(
                {
                    "state_delta": None if state is None else json.loads(state),
                    "progress_identities": kimlikler,
                }
            )
        result.append(
            {
                "task": task,
                "run_id": run_id,
                "prefix": prefix,
                "sonlanma": termination,
                "step_count": step_count,
                "ceiling": ceiling,
                "passed": passed,
                "kosu_esigi": threshold,
                "steps": steps,
            }
        )
    return result


def merge(sets: list[list[dict]]) -> list[dict]:
    """One episode per task: the one with a complete trajectory wins.

    If both are complete, the prefix that comes later in the list wins. A rule
    that never fired has no effect on the episode, so merging the two prefixes is
    legitimate; which one was chosen stays in the record.
    """
    secili: dict[str, dict] = {}
    for identifiers in sets:
        for e in identifiers:
            previous = secili.get(e["task"])
            if previous is None:
                secili[e["task"]] = e
                continue
            if previous["sonlanma"] == "no_progress" or e["sonlanma"] != "no_progress":
                secili[e["task"]] = e
    return list(secili.values())


def longest_stall(steps: list[dict]) -> int:
    """The longest run of consecutive steps without progress in the episode.

    With the rule's own criterion: `_made_no_progress` and the cumulative set of
    endpoints seen.
    """
    agent = RecordingAgent.__new__(RecordingAgent)
    agent.no_progress_limit = None
    seen: set[str] = set()
    longest = 0
    stalled = 0
    for step in steps:
        if agent._made_no_progress(step, seen):
            stalled += 1
            longest = max(longest, stalled)
        else:
            stalled = 0
        seen |= step["progress_identities"]
    return longest


def cut_step(steps: list[dict], threshold: int) -> int | None:
    """At which step the rule would have cut had it run with `threshold`. None if
    it would not have cut.

    The production check itself is called.
    """
    agent = RecordingAgent.__new__(RecordingAgent)
    agent.no_progress_limit = threshold
    agent.steps = []
    agent.stop_reason = None
    for index, step in enumerate(steps, 1):
        agent.steps.append(step)
        try:
            agent._check_progress()
        except NoProgress:
            return index
    return None


def main() -> None:
    options = parse_options(sys.argv[1:])
    connection = sqlite3.connect(options.database)
    sets = []
    for prefix in options.prefixes:
        identifiers = episodes_with_steps(connection, prefix)
        print(f"{prefix}: {len(identifiers)} episode")
        sets.append(identifiers)
    every_row = merge(sets)
    if not every_row:
        sys.exit(f"no episode with the prefixes {options.prefixes} ({options.database}).")

    excluded_episodes = [e for e in every_row if e["sonlanma"] == "no_progress"]
    complete = [e for e in every_row if e["sonlanma"] != "no_progress"]
    print(f"database={options.database}  prefixes={options.prefixes}")
    print(
        f"episodes: {len(every_row)}  complete: {len(complete)}  "
        f"cut (excluded): {len(excluded_episodes)}"
    )
    if excluded_episodes:
        print(f"  left out: {[e['task'] for e in excluded_episodes]}")
    source: dict[str, int] = {}
    for e in complete:
        key = f"{e['prefix']}(threshold={e['kosu_esigi']})"
        source[key] = source.get(key, 0) + 1
    print(f"  where the complete trajectories come from: {source}")

    passing = [e for e in complete if e["passed"] == 1]
    print(f"  passing: {len(passing)}/{len(complete)}")
    print()

    print("--- longest stall in the passing episodes ---")
    for e in sorted(passing, key=lambda x: -longest_stall(x["steps"])):
        print(
            f"  {e['task']:12s} step={e['step_count']:3d} "
            f"ceiling={e['ceiling']:3d} "
            f"longest_stall={longest_stall(e['steps']):3d}"
        )
    print()

    thresholds = [int(s) for s in options.thresholds.split(",") if s.strip()]
    print("--- threshold sweep ---")
    print(
        f"  {'threshold':>9s}  {'cuts passing':>12s}  {'cuts failing':>12s}  {'steps saved':>14s}"
    )
    table = []
    for threshold in thresholds:
        passing_cut = []
        failing_cut = 0
        kazanc = 0
        for e in complete:
            nerede = cut_step(e["steps"], threshold)
            if nerede is None:
                continue
            kazanc += e["step_count"] - nerede
            if e["passed"] == 1:
                passing_cut.append(e["task"])
            else:
                failing_cut += 1
        table.append(
            {
                "threshold": threshold,
                "kesilen_gecen": passing_cut,
                "kesilen_dusen": failing_cut,
                "kazanilan_adim": kazanc,
            }
        )
        print(f"  {threshold:5d}  {len(passing_cut):12d}  {failing_cut:12d}  {kazanc:14d}")

    safe = [t for t in table if not t["kesilen_gecen"]]
    print()
    if safe:
        lowest = min(safe, key=lambda t: t["threshold"])
        print(
            f"lowest threshold that cuts no passing episode: {lowest['threshold']}  "
            f"(cuts {lowest['kesilen_dusen']} of the failing ones, "
            f"saves {lowest['kazanilan_adim']} steps)"
        )
    else:
        print("none of the thresholds tried is safe; widen the range upwards.")
    for t in table:
        if t["kesilen_gecen"]:
            print(f"  threshold {t['threshold']} would cut: {t['kesilen_gecen']}")

    output = options.output or f"results/{options.prefixes[-1]}-kalibrasyon.json"
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "veritabani": options.database,
                "onekler": options.prefixes,
                "tam_yorunge": len(complete),
                "disarida_kalan": [e["task"] for e in excluded_episodes],
                "passing": len(passing),
                "episodes_with_steps": [
                    {
                        "task": e["task"],
                        "prefix": e["prefix"],
                        "kosu_esigi": e["kosu_esigi"],
                        "passed": e["passed"],
                        "step_count": e["step_count"],
                        "ceiling": e["ceiling"],
                        "sonlanma": e["sonlanma"],
                        "longest_stall": longest_stall(e["steps"]),
                    }
                    for e in complete
                ],
                "esik_taramasi": table,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print(f"written: {output}")


if __name__ == "__main__":
    main()
