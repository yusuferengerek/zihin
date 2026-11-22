"""The tasks each confirmatory contrast is read on, from the runner's own selection (K-184).

**Derived, not written.** The counts in the protocol come from `zihin.slots.compose`,
the function the runner builds every slot with, opened on the library the
runner opens (`open_library`). It spends no episode. For every task in the declared order and every
card-carrying condition this records the slot's two counts, whether it matched the
carded arm's volume, and whether the carded arm reached the task at all; the sets
follow from those by one rule (`zihin.experiment.analysis_sets`).

Usage:

    uv run python scripts/setup/measure_experiment_sets.py           # write
    uv run python scripts/setup/measure_experiment_sets.py --check   # compare
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.experiment import (  # noqa: E402
    ANALYSES,
    PHASE_ONE,
    SETS,
    analysis_sets,
    load_order,
    phase_one_episodes,
    render,
)
from zihin.records import LIBRARY_SERIES, load_model_config, open_library  # noqa: E402
from zihin.slots import EXPERIMENT_CONDITIONS, compose  # noqa: E402


def measure() -> dict:
    if not (REPOSITORY / LIBRARY_SERIES).exists():
        sys.exit(f"{LIBRARY_SERIES} is not here; the slots cannot be built without the library")
    order = load_order()["order"]
    connection, library_id, index_id = open_library()
    per_task: dict[str, dict[str, dict]] = {}
    try:
        for task in order:
            instruction = task_instruction(task)
            per_task[task] = {}
            for condition in EXPERIMENT_CONDITIONS:
                if condition == "baseline":
                    continue
                slot = compose(
                    connection,
                    instruction,
                    condition,
                    library_id=library_id,
                    index_id=index_id,
                    task_id=task,
                )
                per_task[task][condition] = {
                    "skills": len(slot.cards.skills),
                    "failures": len(slot.cards.failures),
                    "covered": slot.covered,
                    "volume_matched": slot.volume_matched,
                    "shortfall": list(slot.shortfall),
                }
    finally:
        connection.close()
    sets = analysis_sets(per_task)
    seeds = load_model_config(REPOSITORY / "config/models.yaml").seed_count
    return {
        "what": "the tasks each confirmatory contrast is read on, from the runner's own slots",
        "decision": "K-184",
        "library_id": library_id,
        "index_id": index_id,
        "tasks": len(order),
        "covered": sum(1 for slots in per_task.values() if slots["skills_failures"]["covered"]),
        "uncovered": sorted(t for t, s in per_task.items() if not s["skills_failures"]["covered"]),
        "volume_not_matched": {
            condition: sorted(
                t for t, s in per_task.items() if s[condition]["volume_matched"] is False
            )
            for condition in EXPERIMENT_CONDITIONS
            if condition != "baseline"
        },
        "sets": {
            name: {"compares": list(ANALYSES[name]), "tasks": len(tasks), "task_ids": tasks}
            for name, tasks in sets.items()
        },
        "phase_one": {
            "conditions": list(PHASE_ONE),
            "seeds": seeds,
            "episodes": phase_one_episodes(per_task, seeds),
        },
        "per_task": per_task,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    options = parser.parse_args()
    text = render(measure())
    path = REPOSITORY / SETS
    if options.check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            sys.exit(f"{SETS} is not what the runner's slots give; regenerate it")
        print(f"{SETS} matches the runner's slots")
        return
    path.write_text(text, encoding="utf-8")
    document = json.loads(text)
    for name, entry in document["sets"].items():
        print(f"{name:24} {entry['tasks']:4}  {' vs '.join(entry['compares'])}")
    print(f"phase 1 episodes: {document['phase_one']['episodes']}")
    print(f"wrote {SETS}")


if __name__ == "__main__":
    main()
