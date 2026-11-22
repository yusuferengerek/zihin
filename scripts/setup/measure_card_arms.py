"""Three arms, five tasks, three repeats: 45 episodes at one commit.

**What this adds to the demo, and what it cannot add.** The demo had two arms and
one episode per arm, so it could not say whether "carded 2 pairs, card-free 0"
was a result or a coin toss. This run repeats every cell three times and adds a
third arm whose slot carries cards the retriever would **not** give the task.

**The third arm's limit was written before the run** (setup protocol, 12.2):
every skill in the library ends in an `auth/token` POST and the bodies carry the
same skeleton, so a card from another app teaches the same lesson. In this
library the control separates card-shaped text from text that is not
card-shaped, not content from template. Expecting the control to succeed as well
is the pre-registered expectation, and if it does, the finding is that the
library is too homogeneous for content attribution.

**The interpretation is pre-registered too** (12.3), including what makes the
original demo claim retract.

Every episode goes through `scripts/record_run.py`, so the manifest, the shield,
the stopping rule and the recording path are production's. This script only
drives and skips what is already written.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 \\
      uv run python scripts/setup/measure_card_arms.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sqlite3
import subprocess
import sys

sys.path.insert(0, "src")

from zihin.records import ACTIVE_SERIES, load_model_config  # noqa: E402

# The demo's five: three chosen by the corrected criterion plus the two
# within-scenario variants that ran before the criterion was fixed. Both groups
# are in the record and both are re-run here, so the comparison covers exactly
# what the demo reported.
TASKS = ["0de03ea_1", "1150ed6_2", "0a9d82a_1", "0a9d82a_2", "0a9d82a_3"]
ARMS = {"cards": ["--cards"], "baseline": [], "irrelevant": ["--irrelevant-cards"]}
REPEATS = 3
PREFIX = os.environ.get("ZIHIN_PREFIX", "uckol")
SPLIT = "test_normal"
MAX_STEPS = 20
OUTPUT = "results/card-arms.json"


def run_id_for(task: str, arm: str, repeat: int, tag: str) -> str:
    short = tag.split(":")[1].split("-")[0]
    return f"{PREFIX}-{arm}-{repeat}-{task}-{task}-{short}"


def experiment_for(task: str, arm: str, repeat: int) -> str:
    return f"{PREFIX}-{arm}-{repeat}-{task}"


def already_written(connection: sqlite3.Connection, run_id: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM episodes WHERE run_id = ? LIMIT 1", (run_id,)
    ).fetchone()
    return row is not None


def run_episode(task: str, arm: str, repeat: int, tag: str) -> int:
    environment = {
        **os.environ,
        "ZIHIN_TASK_ID": task,
        "ZIHIN_SPLIT": SPLIT,
        "ZIHIN_MODEL": tag,
        "ZIHIN_MAX_STEPS": str(MAX_STEPS),
        "ZIHIN_EXPERIMENT": experiment_for(task, arm, repeat),
        "ZIHIN_SEED_INDEX": str(repeat),
    }
    command = [".venv/bin/python", "scripts/record_run.py", *ARMS[arm]]
    finished = subprocess.run(command, env=environment, capture_output=True, text=True)
    if finished.returncode != 0:
        for line in (finished.stderr.strip().splitlines() or ["<no stderr>"])[-4:]:
            print(f"        {line}")
    return finished.returncode


def collect(connection: sqlite3.Connection, tag: str) -> list[dict]:
    rows = []
    for task in TASKS:
        for arm in ARMS:
            for repeat in range(REPEATS):
                run_id = run_id_for(task, arm, repeat, tag)
                row = connection.execute(
                    "SELECT e.run_id, e.task_id, e.seed, e.total_model_calls, "
                    "e.termination_reason, e.distinct_endpoints, e.duration_seconds, "
                    "m.instruction_file_digest, m.code_commit "
                    "FROM episodes e JOIN run_manifests m USING(run_id) WHERE e.run_id = ?",
                    (run_id,),
                ).fetchone()
                if row is None:
                    rows.append({"task": task, "arm": arm, "repeat": repeat, "missing": True})
                    continue
                steps = connection.execute(
                    "SELECT COUNT(*) FROM steps s JOIN episodes e USING(episode_id) "
                    "WHERE e.run_id = ?",
                    (run_id,),
                ).fetchone()[0]
                verdict = connection.execute(
                    "SELECT passed FROM verifier_results v JOIN episodes e USING(episode_id) "
                    "WHERE e.run_id = ?",
                    (run_id,),
                ).fetchone()
                rows.append(
                    {
                        "task": task,
                        "arm": arm,
                        "repeat": repeat,
                        "run_id": run_id,
                        "seed": row["seed"],
                        "step": steps,
                        "termination": row["termination_reason"],
                        "model_calls": row["total_model_calls"],
                        "distinct_endpoints": row["distinct_endpoints"],
                        "duration_seconds": row["duration_seconds"],
                        "prompt_digest": row["instruction_file_digest"],
                        "code_commit": row["code_commit"],
                        "passed": verdict["passed"] if verdict else None,
                    }
                )
    return rows


def main() -> None:
    if not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not set.")
    tag = load_model_config("config/models.yaml").models[-1]
    connection = sqlite3.connect(f"file:{ACTIVE_SERIES}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    total = len(TASKS) * len(ARMS) * REPEATS
    print(f"model={tag}  prefix={PREFIX}  episodes={total}")
    print(f"tasks={TASKS}")
    print(f"arms={list(ARMS)}  repeats={REPEATS}")
    print()

    index = 0
    for task in TASKS:
        for arm in ARMS:
            for repeat in range(REPEATS):
                index += 1
                run_id = run_id_for(task, arm, repeat, tag)
                head = f"[{index:2}/{total}] {task} {arm} r{repeat}"
                if already_written(connection, run_id):
                    print(f"{head}  already in the record, skipped", flush=True)
                    continue
                print(f"{head}  running", flush=True)
                run_episode(task, arm, repeat, tag)

    rows = collect(connection, tag)
    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {
                "what": "three arms, five tasks, three repeats, one commit",
                "prefix": PREFIX,
                "model": tag,
                "tasks": TASKS,
                "arms": list(ARMS),
                "repeats": REPEATS,
                "episodes": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    written = [r for r in rows if not r.get("missing")]
    print()
    print(f"written: {OUTPUT}  ({len(written)}/{total} episodes in the record)")


if __name__ == "__main__":
    main()
