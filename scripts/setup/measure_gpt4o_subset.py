"""Does the 7B get further on the tasks a strong model solves.

**Why this subset.** The band sweep showed that reference length is not a
difficulty signal for this model: zero tasks pass in all five bands. The subset
the published gpt-4o runs solve is a better signal, because it shows solvability
directly. gpt-4o's own per-band solve rate is flat too: 59%, 51%, 42%, 59%, 38%
— so length does not mean difficulty for it either.

**Not cherry-picking.** The subset is chosen before any mechanism runs and
before any result is seen, and it is declared in the preregistration as a scope
restriction. The selection comes from a published run, not from our own
measurement.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/measure_gpt4o_subset.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from zihin.records import open_database  # noqa: E402
from zihin.verification import graded_detail  # noqa: E402

MODEL = os.environ.get("ZIHIN_MODEL", "qwen2.5-coder:7b-instruct-q4_K_M")
ADET = int(os.environ.get("ZIHIN_COUNT", "15"))
MULTIPLIER = float(os.environ.get("ZIHIN_MULTIPLIER", "2"))
FLOOR_CEILING = int(os.environ.get("ZIHIN_FLOOR_CEILING", "20"))
CEILING_CAP = int(os.environ.get("ZIHIN_CEILING_LIMIT", "150"))
SOURCE = "results/gpt4o-cozulen.json"
SCAN_FILE = "results/bant-taramasi.json"
OUTPUT = "results/gpt4o-alt-kume.json"
DATABASE = "results/zihin.sqlite"


def sec() -> list[tuple[str, int, int]]:
    """An evenly spaced selection from the tasks gpt-4o solved and we have not run yet."""
    with open(SOURCE, encoding="utf-8") as handle:
        source = json.load(handle)
    capalar = {g: int(c) for g, c in source["capalar"].items()}
    with open(SCAN_FILE, encoding="utf-8") as handle:
        kosulmus = {s["task"] for s in json.load(handle)["episodes_with_steps"]}

    aday = sorted((c, g) for g, c in capalar.items() if g not in kosulmus)
    step = len(aday) / min(ADET, len(aday))
    selection = [aday[int(i * step)] for i in range(min(ADET, len(aday)))]
    return [(g, c, min(max(int(MULTIPLIER * c), FLOOR_CEILING), CEILING_CAP)) for c, g in selection]


def run_episode(task: str, step_ceiling: int) -> int:
    environment = dict(os.environ)
    environment["ZIHIN_TASK_ID"] = task
    environment["ZIHIN_MODEL"] = MODEL
    environment["ZIHIN_SPLIT"] = "test_normal"
    environment["ZIHIN_MAX_STEPS"] = str(step_ceiling)
    environment["ZIHIN_EXPERIMENT"] = f"gpt4o-{task}"
    result = subprocess.run(
        [sys.executable, "scripts/record_run.py"], env=environment, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  the run failed ({result.returncode}): {result.stderr.strip().splitlines()[-1:]}")
    return result.returncode


def main() -> None:
    if not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not defined.")

    selection = sec()
    print(f"model={MODEL}  tasks={len(selection)}  multiplier={MULTIPLIER}")
    for index, (task, anchor, ceiling) in enumerate(selection, 1):
        print(f"[{index}/{len(selection)}] {task}  anchor={anchor}  ceiling={ceiling}")
        run_episode(task, ceiling)

    connection = open_database(DATABASE)
    short_tag = MODEL.split(":")[1].split("-")[0]
    rows = []
    for task, anchor, ceiling in selection:
        record = connection.execute(
            "SELECT e.total_model_calls, e.termination_reason, v.passed "
            "FROM episodes e JOIN verifier_results v USING(episode_id) WHERE e.run_id = ?",
            (f"gpt4o-{task}-{task}-{short_tag}",),
        ).fetchone()
        row = {
            "task": task,
            "anchor": anchor,
            "ceiling": ceiling,
            "ceiling_at_cap": ceiling == CEILING_CAP,
            "step": record[0] if record else None,
            "termination": record[1] if record else None,
            "passed": record[2] if record else None,
        }
        row.update(graded_detail(f"gpt4o-{task}", task))
        rows.append(row)

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {"model": MODEL, "episodes_with_steps": rows}, handle, ensure_ascii=False, indent=2
        )

    numerator = sum(s.get("meaningful_passed", 0) for s in rows)
    denominator = sum(s.get("meaningful_total", 0) for s in rows)
    passing = sum(1 for s in rows if s["passed"] == 1)
    print()
    print(
        f"the 7B on the {len(rows)} tasks gpt-4o solved: passing={passing}, "
        f"meaningful tests={numerator}/{denominator}"
        + (f" = {100 * numerator / denominator:.1f}%" if denominator else "")
    )
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
