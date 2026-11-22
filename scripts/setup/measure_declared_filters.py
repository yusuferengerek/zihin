"""What the declared retrieval filters take away, measured with the retriever itself.

**Why it exists.** Preregistration A.4 carries two declarations of 25 September
2026: a skill card must be expected to save at least one model call
(`min_expected_saving = 1`, K-175), and the irrelevant arm passes through the same
filters as the carded arm, failure cards included (K-176). A declaration has to
say what it drops, and "what it drops" is a measurement: which skills, on which
of the primary sample's tasks, and what reaches the slot.

**The production code is called, not re-implemented.** Cards come from
`zihin.retriever` against the delivered library and index, the slot counts from
the condition configuration, the sample from the threshold derivation's
`action_stratum`, and a skill's steps per occurrence from the compiler's own
`occurrences_of` over the corpus the library was mined from.

Usage:

    uv run python scripts/setup/measure_declared_filters.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))
sys.path.insert(0, str(REPOSITORY / "scripts/setup"))

from mine_skills import passing_sequences  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.compiler import occurrences_of  # noqa: E402
from zihin.config import load_condition_config  # noqa: E402
from zihin.declared import declared_field, declared_model  # noqa: E402
from zihin.records import LIBRARY_SERIES  # noqa: E402
from zihin.retriever import Retrieved, matched_to, retrieve, retrieve_irrelevant  # noqa: E402

OUTPUT = REPOSITORY / "results/declared-filters.json"
CONDITION = REPOSITORY / "config/skills_failures.yaml"
DELIVERED_BY = "bir1"
# The rule before the declaration: the literal the runner passed.
BEFORE = 0


def primary_sample() -> list[str]:
    path = REPOSITORY / "scripts/setup/derive_pass_threshold.py"
    spec = importlib.util.spec_from_file_location("derive_pass_threshold", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["derive_pass_threshold"] = module
    spec.loader.exec_module(module)
    return [task for task, _ in module.action_stratum()]


def cards(connection, instruction, task, *, library_id, index_id, floor, relevant=True):
    return (retrieve if relevant else retrieve_irrelevant)(
        connection,
        instruction,
        library_id=library_id,
        index_id=index_id,
        min_expected_saving=floor,
        max_discriminating_conditions=None,
        include_unverified_cards=True,
        task_id=task,
    )


def cut(reference: Retrieved, pool: Retrieved, slots) -> dict:
    """The production cut (K-179), as a row of the report."""
    matched = matched_to(
        reference, pool, skill_slots=slots.skill_slots, failure_slots=slots.failure_slots
    )
    return {
        "slot": [len(matched.retrieved.skills), len(matched.retrieved.failures)],
        "defined": matched.defined,
        "shortfall": list(matched.shortfall),
    }


def steps_per_occurrence(connection, rows) -> dict[str, dict[int, int]]:
    """For each skill, how many steps each of its occurrences took."""
    sequences = passing_sequences(connection, model_tag=declared_model(DELIVERED_BY), split="train")
    by_id = {sequence.episode_id: sequence for sequence in sequences}
    out = {}
    for row in rows:
        counts: collections.Counter[int] = collections.Counter()
        for episode_id in json.loads(row["supporting_episodes"]):
            sequence = by_id.get(episode_id)
            if sequence is None:
                continue
            for positions in occurrences_of(
                tuple(json.loads(row["body"])), sequence, row["max_gap"]
            ):
                counts[len({sequence.step_ids[i] for i in positions})] += 1
        out[row["skill_id"]] = dict(sorted(counts.items()))
    return out


def main() -> None:
    library_id = declared_field("delivered_library_id", DELIVERED_BY)
    index_id = declared_field("delivered_index_id", DELIVERED_BY)
    slots = load_condition_config(CONDITION)
    declared = slots.min_expected_saving
    connection = sqlite3.connect(f"file:{REPOSITORY / LIBRARY_SERIES}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    tasks = primary_sample()

    dropped_rows = connection.execute(
        "SELECT * FROM skills WHERE library_id = ? AND expected_saving IS NOT NULL "
        "AND expected_saving < ? AND expected_saving >= ? ORDER BY support DESC, skill_id",
        (library_id, declared, BEFORE),
    ).fetchall()
    dropped_ids = {row["skill_id"] for row in dropped_rows}
    occurrences = steps_per_occurrence(connection, dropped_rows)

    per_task = {}
    reached_by = collections.Counter()
    retrievable = {"before": set(), "after": set()}
    control = {}
    equal = {}
    for task in tasks:
        instruction = task_instruction(task, REPOSITORY / "data/tasks")
        before = cards(
            connection, instruction, task, library_id=library_id, index_id=index_id, floor=BEFORE
        )
        after = cards(
            connection, instruction, task, library_id=library_id, index_id=index_id, floor=declared
        )
        slotted_before = {c.skill_id for c in before.skills[: slots.skill_slots]}
        retrievable["before"] |= {c.skill_id for c in before.skills}
        retrievable["after"] |= {c.skill_id for c in after.skills}
        for card in before.skills:
            if card.skill_id in dropped_ids:
                reached_by[card.skill_id] += 1
        # The control arm, the old rule against the declared one. The old arm took
        # no value floor and carried no failure card; with no floor below zero the
        # floor-0 skills are exactly the skills it gave.
        old_arm = cards(
            connection,
            instruction,
            task,
            library_id=library_id,
            index_id=index_id,
            floor=BEFORE,
            relevant=False,
        )
        new_arm = cards(
            connection,
            instruction,
            task,
            library_id=library_id,
            index_id=index_id,
            floor=declared,
            relevant=False,
        )

        # A.4's equal count, with the production cut (K-179). The two single-
        # mechanism conditions fill their other kind from the same pool, so they
        # are held to the same count and can fall short the same way.
        carded = [
            min(len(after.skills), slots.skill_slots),
            min(len(after.failures), slots.failure_slots),
        ]
        equal[task] = {
            "carded_slot": carded,
            "irrelevant_retrieval": cut(after, new_arm, slots),
            "skills_fills_failures": cut(
                Retrieved(task_id=task, apps=after.apps, failures=after.failures), new_arm, slots
            ),
            "failures_fills_skills": cut(
                Retrieved(task_id=task, apps=after.apps, skills=after.skills), new_arm, slots
            ),
        }
        control[task] = {
            "carded_slot": [
                min(len(after.skills), slots.skill_slots),
                min(len(after.failures), slots.failure_slots),
            ],
            "control_slot_before": [min(len(old_arm.skills), slots.skill_slots), 0],
            "control_slot_after": [
                min(len(new_arm.skills), slots.skill_slots),
                min(len(new_arm.failures), slots.failure_slots),
            ],
        }
        per_task[task] = {
            "skill_cards_before": len(before.skills),
            "skill_cards_after": len(after.skills),
            "failure_cards": len(after.failures),
            "lost_a_slotted_skill_card": bool(slotted_before & dropped_ids),
        }
    connection.close()

    def count(predicate):
        return sum(1 for values in per_task.values() if predicate(values))

    report = {
        "what": "what the declared retrieval filters take away, on the primary sample",
        "library_id": library_id,
        "index_id": index_id,
        "primary_sample": len(tasks),
        "skill_slots": slots.skill_slots,
        "min_expected_saving": {
            "before": BEFORE,
            "declared": declared,
            "decision": "K-175",
            "dropped_skills": [
                {
                    "skill_id": row["skill_id"],
                    "effect_suffix": json.loads(row["effect_suffix"]),
                    "body": json.loads(row["body"]),
                    "support": row["support"],
                    "observed_steps": row["observed_steps"],
                    "expected_saving": row["expected_saving"],
                    "expected_saving_calls": row["expected_saving_calls"],
                    "steps_per_occurrence": occurrences[row["skill_id"]],
                    "primary_tasks_it_reached": reached_by[row["skill_id"]],
                }
                for row in dropped_rows
            ],
            # A.8: a library's size is the number of skills some task can retrieve.
            "retrievable_skills": {k: len(v) for k, v in retrievable.items()},
            "tasks_that_lose_a_skill_card": count(
                lambda v: v["skill_cards_after"] < v["skill_cards_before"]
            ),
            "tasks_that_lose_a_slotted_skill_card": count(lambda v: v["lost_a_slotted_skill_card"]),
            "tasks_left_with_no_skill_card": {
                "before": count(lambda v: v["skill_cards_before"] == 0),
                "after": count(lambda v: v["skill_cards_after"] == 0),
            },
            "tasks_with_any_card": {
                "before": count(lambda v: v["skill_cards_before"] + v["failure_cards"] > 0),
                "after": count(lambda v: v["skill_cards_after"] + v["failure_cards"] > 0),
            },
        },
        "irrelevant_arm": {
            "decision": "K-176",
            "rule_before": "skills only, from the apps the task does not name, no value floor",
            "rule_after": "the carded arm's filters, skills and failure cards, relevance inverted",
            "slot_is": "[skill cards, failure cards] after the slot caps",
            "tasks_where_the_control_slot_is_smaller_than_the_carded_slot": {
                "before": sum(
                    1
                    for v in control.values()
                    if sum(v["control_slot_before"]) < sum(v["carded_slot"])
                ),
                "after": sum(
                    1
                    for v in control.values()
                    if sum(v["control_slot_after"]) < sum(v["carded_slot"])
                ),
            },
            "tasks_where_the_control_arm_cannot_match_a_kind": {
                "skills": sum(
                    1 for v in control.values() if v["control_slot_after"][0] < v["carded_slot"][0]
                ),
                "failures": sum(
                    1 for v in control.values() if v["control_slot_after"][1] < v["carded_slot"][1]
                ),
            },
            "failure_cards_in_the_control_slot": {
                "before": 0,
                "after": sum(v["control_slot_after"][1] for v in control.values()),
            },
            "per_task": control,
        },
        "equal_counts": {
            "decision": "K-179",
            "rule": "the control takes the carded arm's slot count, kind by kind; zero for zero",
            "tasks_with_no_card_in_the_carded_arm": [
                t for t, v in equal.items() if sum(v["carded_slot"]) == 0
            ],
            "irrelevant_retrieval_equal_to_the_carded_arm": sum(
                1
                for v in equal.values()
                if v["irrelevant_retrieval"]["defined"]
                and v["irrelevant_retrieval"]["slot"] == v["carded_slot"]
            ),
            "undefined": {
                arm: {t: v[arm]["shortfall"] for t, v in equal.items() if not v[arm]["defined"]}
                for arm in (
                    "irrelevant_retrieval",
                    "skills_fills_failures",
                    "failures_fills_skills",
                )
            },
            "per_task": equal,
        },
        "per_task": per_task,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    section = report["min_expected_saving"]
    for skill in section["dropped_skills"]:
        print(
            f"dropped {skill['skill_id']} support {skill['support']:>2} steps "
            f"{skill['steps_per_occurrence']} reached {skill['primary_tasks_it_reached']} tasks: "
            f"{' > '.join(skill['effect_suffix'])[:60]}"
        )
    for key in (
        "retrievable_skills",
        "tasks_that_lose_a_skill_card",
        "tasks_that_lose_a_slotted_skill_card",
        "tasks_left_with_no_skill_card",
        "tasks_with_any_card",
    ):
        print(f"{key}: {section[key]}")
    arm = report["irrelevant_arm"]
    for key in (
        "tasks_where_the_control_slot_is_smaller_than_the_carded_slot",
        "tasks_where_the_control_arm_cannot_match_a_kind",
        "failure_cards_in_the_control_slot",
    ):
        print(f"irrelevant arm, {key}: {arm[key]}")
    counts = report["equal_counts"]
    print(
        f"equal counts: irrelevant arm equal to the carded arm on "
        f"{counts['irrelevant_retrieval_equal_to_the_carded_arm']} of {len(tasks)} tasks; "
        f"no card in the carded arm: {counts['tasks_with_no_card_in_the_carded_arm']}"
    )
    for arm, where in counts["undefined"].items():
        print(f"  undefined, {arm}: {len(where)} {where}")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
