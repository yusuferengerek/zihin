"""Every recorded episode of the task preregistration A.5 takes its example from.

**Why it exists.** A.5 says the graded score is a diagnostic, not a result, and
gives one observation for it: on `0de03ea_1` the carded arm acted, failed a test a
do-nothing agent passes, and so lost a free pass. That observation came from one
episode. The same task was run eleven more times - three conditions, a
comparability run and three repeats of each arm - and this asks whether the
observation came back (S-77).

**What it reads.** The record for the episodes, and AppWorld's labelled evaluation
file of each (`zihin.verification.graded_detail`) for which tests passed. The
evaluation files are under `experiments/outputs`, which is not in git, so this
runs where the episodes ran and declines elsewhere.

Usage:

    uv run python scripts/setup/measure_no_op_example.py
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.touched import RECORD_SERIES  # noqa: E402
from zihin.verification import graded_detail  # noqa: E402

OUTPUT = REPOSITORY / "results/no-op-example.json"
TASK = "0de03ea_1"
# The episode A.5's sentence was written from.
CITED = "demo-0de03ea_1-kart-0de03ea_1-7b"


def episodes() -> list[dict]:
    rows = []
    for name in RECORD_SERIES:
        path = REPOSITORY / name
        if not path.exists():
            continue
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        for run_id, condition, model, detail in connection.execute(
            "SELECT e.run_id, e.condition, e.model_ref, v.detail_path FROM episodes e "
            "JOIN verifier_results v ON v.episode_id = e.episode_id WHERE e.task_id = ? "
            "ORDER BY e.run_id",
            (TASK,),
        ):
            rows.append(
                {
                    "series": path.name,
                    "run": run_id,
                    "condition": condition,
                    "model": model,
                    "detail": detail,
                }
            )
        connection.close()
    return rows


def main() -> None:
    found = episodes()
    if not found:
        sys.exit(f"the record holds no episode of {TASK}; nothing to measure")
    measured = []
    for row in found:
        detail = row.pop("detail")
        if not detail:
            sys.exit(f"{row['run']} has no evaluation path; this measurement declines")
        # .../experiments/outputs/<experiment>/tasks/<task>/evaluation/report.md
        experiment = pathlib.Path(detail).parents[3].name
        graded = graded_detail(experiment, TASK)
        if not graded:
            sys.exit(
                f"no labelled evaluation for {experiment}; experiments/outputs is not in "
                "git, so this runs only where the episodes ran"
            )
        graded["trivial_lost"] = graded["trivial_total"] - graded["trivial_passed"]
        measured.append({**row, "experiment": experiment, **graded})

    carded = [m for m in measured if m["condition"] == "skills_failures"]
    report = {
        "what": f"every recorded episode of {TASK}, graded against the no-op baseline",
        "limitation": "S-77",
        "cited_by_a5": CITED,
        "episodes": measured,
        "carded_episodes": len(carded),
        "carded_episodes_that_lost_a_free_test": [m["run"] for m in carded if m["trivial_lost"]],
        "carded_meaningful_scores": {
            m["run"]: f"{m['meaningful_passed']}/{m['meaningful_total']}" for m in carded
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for m in measured:
        print(
            f"{m['run']:52} {m['condition']:27} meaningful {m['meaningful_passed']}/"
            f"{m['meaningful_total']}  free tests lost {m['trivial_lost']}"
        )
    print(
        f"\ncarded episodes: {len(carded)}; lost a free test: "
        f"{report['carded_episodes_that_lost_a_free_test']}"
    )
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
