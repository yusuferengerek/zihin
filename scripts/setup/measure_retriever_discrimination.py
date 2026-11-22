"""Does the retriever give different tasks different cards, or the same ones.

**Why it exists.** Coverage says how many tasks get a card. It does not say
whether the cards differ: a retriever that handed every task the same card would
score full coverage. The sentence "test_normal carries 21 distinct card sets and
the most common set covers 20.8% of the tasks" was quoted in three documents and
stored in no artefact — a number with no source is a number nobody can check
(K-135, in its document form).

**It needs no model.** The retriever is deterministic: the card set for a task is
a function of the task's text, the library and the index. So this is a
measurement that can be re-run at any time and must produce the same numbers.

**Which database.** The library and the index live in the series they were mined
from, which is not the active series. The path is a parameter rather than a
constant for exactly that reason.

Usage:

    uv run python scripts/setup/measure_retriever_discrimination.py
    uv run python scripts/setup/measure_retriever_discrimination.py
        --database results/zihin-2.sqlite
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.records import LIBRARY_SERIES, open_library  # noqa: E402
from zihin.retriever import retrieve  # noqa: E402

OUTPUT = REPOSITORY / "results/retriever-discrimination.json"
# The setting the pilot reports under: no saving floor, no condition cap, and
# unverified cards included. Named here rather than swept, because the claim
# being checked is about that setting.
SAVING = 0
CAP = None
UNVERIFIED = True


def card_set(found) -> tuple[str, ...]:
    """The identity of what a task received, as an ordered tuple of card ids."""
    ids = [
        str(getattr(card, "skill_id", None) or getattr(card, "card_id", card))
        for card in found.skills
    ]
    ids += [
        str(getattr(card, "pattern_id", None) or getattr(card, "card_id", card))
        for card in found.failures
    ]
    return tuple(sorted(ids))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=LIBRARY_SERIES)
    parser.add_argument("--split", default="test_normal")
    options = parser.parse_args()

    connection, library_id, index_id = open_library(str(REPOSITORY / options.database))

    sets: list[tuple[str, tuple[str, ...]]] = []
    without = 0
    for task_id in load_task_ids(options.split):
        try:
            instruction = task_instruction(task_id)
        except FileNotFoundError:
            continue
        found = retrieve(
            connection,
            instruction,
            library_id=library_id,
            index_id=index_id,
            min_expected_saving=SAVING,
            max_discriminating_conditions=CAP,
            include_unverified_cards=UNVERIFIED,
            task_id=task_id,
        )
        identity = card_set(found)
        if not identity:
            without += 1
            continue
        sets.append((task_id, identity))

    counts = collections.Counter(identity for _, identity in sets)
    covered = len(sets)
    most_common, most_common_count = counts.most_common(1)[0] if counts else ((), 0)

    report = {
        "what": (
            "how many distinct card sets the retriever produces on a split, and "
            "how concentrated they are"
        ),
        "database": options.database,
        "library_id": library_id,
        "index_id": index_id,
        "split": options.split,
        "setting": {
            "min_expected_saving": SAVING,
            "max_discriminating_conditions": CAP,
            "include_unverified_cards": UNVERIFIED,
        },
        "tasks_with_cards": covered,
        "tasks_without_cards": without,
        "distinct_card_sets": len(counts),
        "most_common_set_tasks": most_common_count,
        "most_common_set_share": round(most_common_count / covered, 4) if covered else None,
        "most_common_set": list(most_common),
        "set_sizes": dict(collections.Counter(len(i) for _, i in sets)),
        "distribution": sorted(counts.values(), reverse=True),
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"library {library_id}, index {index_id}")
    print(f"split {options.split}: {covered} task(s) with cards, {without} without")
    print(f"distinct card sets   : {report['distinct_card_sets']}")
    print(
        f"most common set      : {most_common_count} task(s) = "
        f"{report['most_common_set_share']:.1%}"
        if covered
        else "most common set      : -"
    )
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
