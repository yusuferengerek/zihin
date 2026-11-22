"""Runs the shield in shadow mode over every recorded episode.

**What this measures is the block rate, not the false-positive rate.** The two
answer different questions and only one of them is answerable here.

  * The *false-positive rate* is how often a block would have been **wrong**.
    Answering it needs ground truth: the reference solution has to show that the
    blocked write was one the task legitimately required. Only `train` and `dev`
    carry reference solutions, and that measurement is
    `measure_shield_cost.py`'s first section — 4.1% of tasks.

  * The *block rate* is how often the shield would have **fired**, right or
    wrong. That is what this script measures, over the corpus this project
    actually ran. Most of that corpus is `test_normal`, which has no
    `required_apps.json`, so whether any individual block there was correct is
    not knowable.

Reporting one as the other would be a category error in both directions: a high
block rate is not evidence of harm, and a low false-positive rate on train/dev
does not bound what enforcement would do here.

**It goes through the mount, not around it.** `ShieldMount.check` does the
resolution and the recording; this script only feeds it the recorded calls. A
script that resolved the URL itself would be measuring a second implementation,
and this project has already had a correction that never reached the caller.

Usage:

    uv run python scripts/setup/measure_shadow_mode.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import warnings

warnings.filterwarnings("ignore")

from zihin.allowed_apps import infer_allowed_apps, task_instruction  # noqa: E402
from zihin.shield import load_write_set  # noqa: E402
from zihin.shield_mount import ShieldMount  # noqa: E402

WRITE_SET_PATH = "inputs/write-set-static.json"
CORPUS = pathlib.Path("experiments/outputs")
OUTPUT = "results/shadow-mode.json"


def episode_logs() -> list[pathlib.Path]:
    """Every recorded episode's call log.

    `legacy_` is excluded the same way the route tests exclude it: those runs
    predate the current recording format.
    """
    return sorted(
        p for p in CORPUS.glob("*/tasks/*/logs/api_calls.jsonl") if "legacy_" not in str(p)
    )


def calls_of(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    write_set = load_write_set(WRITE_SET_PATH)
    logs = episode_logs()
    if not logs:
        raise SystemExit(f"no episodes under {CORPUS}")

    predicates: collections.Counter[str] = collections.Counter()
    per_experiment: dict[str, dict] = {}
    blocked_episodes: list[dict] = []
    blocked_apis: collections.Counter[str] = collections.Counter()
    total_calls = 0
    episodes = 0
    tasks_seen: set[str] = set()
    tasks_blocked: set[str] = set()
    skipped: list[str] = []

    for path in logs:
        task_id = path.parent.parent.name
        experiment = path.parents[3].name
        try:
            instruction = task_instruction(task_id)
        except FileNotFoundError:
            # A task whose spec is not on this machine cannot have an allowed
            # set derived, and guessing one would fabricate a decision. Counted
            # and reported: a silent skip would make the coverage look total.
            skipped.append(f"{experiment}/{task_id}")
            continue

        mount = ShieldMount(
            allowed_apps=infer_allowed_apps(instruction),
            write_set=write_set,
        )
        calls = calls_of(path)
        for call in calls:
            mount.check(call["method"], call["url"], call["data"])

        episodes += 1
        total_calls += len(calls)
        tasks_seen.add(task_id)
        predicates.update(mount.predicate_counts)

        bucket = per_experiment.setdefault(
            experiment, {"episodes": 0, "calls": 0, "blocked_episodes": 0, "blocked_calls": 0}
        )
        bucket["episodes"] += 1
        bucket["calls"] += len(calls)

        if mount.violations:
            tasks_blocked.add(task_id)
            bucket["blocked_episodes"] += 1
            bucket["blocked_calls"] += len(mount.violations)
            for violation in mount.violations:
                blocked_apis[f"{violation.app}.{violation.api}"] += 1
            blocked_episodes.append(
                {
                    "experiment": experiment,
                    "task_id": task_id,
                    "allowed_apps": sorted(mount.allowed_apps),
                    "calls": len(calls),
                    "blocked": len(mount.violations),
                    "reasons": sorted({v.reason for v in mount.violations}),
                }
            )

    denied_calls = sum(e["blocked"] for e in blocked_episodes)
    report = {
        "episodes": episodes,
        "episode_logs_found": len(logs),
        "skipped_no_spec": len(skipped),
        "skipped_examples": skipped[:10],
        "distinct_tasks": len(tasks_seen),
        "calls": total_calls,
        "predicates": dict(predicates.most_common()),
        "blocked_calls": denied_calls,
        "blocked_episodes": len(blocked_episodes),
        "blocked_tasks": len(tasks_blocked),
        "call_block_rate": round(denied_calls / total_calls, 4) if total_calls else 0.0,
        "episode_block_rate": round(len(blocked_episodes) / episodes, 4) if episodes else 0.0,
        "task_block_rate": round(len(tasks_blocked) / len(tasks_seen), 4) if tasks_seen else 0.0,
        "per_experiment": per_experiment,
        "most_blocked_endpoints": blocked_apis.most_common(15),
        "blocked_episode_detail": blocked_episodes,
    }
    pathlib.Path(OUTPUT).write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(
        f"episodes: {episodes}/{len(logs)}  distinct tasks: {len(tasks_seen)}  calls: {total_calls}"
    )
    if skipped:
        print(f"  skipped, no task spec on this machine: {len(skipped)} ({skipped[:3]})")
    print("\n--- predicate distribution ---")
    for name, count in predicates.most_common():
        print(f"  {name:<42} {count:>6}  {count / total_calls:6.2%}")
    print("\n--- block rate (NOT the false-positive rate) ---")
    print(
        f"  calls blocked    {denied_calls:>5} / {total_calls:<5} = {report['call_block_rate']:.2%}"
    )
    print(
        f"  episodes hit     {len(blocked_episodes):>5} / {episodes:<5} = "
        f"{report['episode_block_rate']:.2%}"
    )
    print(
        f"  tasks hit        {len(tasks_blocked):>5} / {len(tasks_seen):<5} = "
        f"{report['task_block_rate']:.2%}"
    )
    if blocked_apis:
        print("\n--- endpoints most often blocked ---")
        for name, count in blocked_apis.most_common(10):
            print(f"  {name:<52} {count:>5}")
    print(f"\nwritten: {OUTPUT}")


if __name__ == "__main__":
    main()
