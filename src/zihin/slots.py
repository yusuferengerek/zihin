"""What each condition puts in the slot, from one selection.

**Five conditions, one rule.** Preregistration A.4 gives every card-carrying
condition the carded arm's card count on a task, kind by kind: a kind taken from
the task's own cards comes from `retrieve`, a kind taken from the irrelevant pool
comes from `retrieve_irrelevant` and is cut to what the carded arm
(`skills_failures`) puts in the slot. So `skills` carries the task's skill cards
and irrelevant failure cards, `failures` the reverse, and `irrelevant_retrieval`
irrelevant cards of both kinds - each at the carded arm's count.

**A pool that falls short runs short and says so** (A.4's correction of
26 September 2026, K-181). The control arm on `d194965_1` and `d194965_3` gets
three skill cards where the carded arm gets five; it runs with three and its
episodes carry `volume_matched = 0`. Every confirmatory analysis that involves
such an arm leaves those tasks out. Until K-181 the arm was not run there at all.

**A task the carded arm reaches with no card is not run under any card-carrying
condition** (K1 of the phase design). The carded arm's slot is the reference for
every other one, so where it is empty every other slot is cut to empty too, and a
card-carrying run with an empty slot is the baseline under another name.

**Why a module of its own.** The runner and the measurement that counts the
analysis sets must make the same selection, or the counts in the protocol describe
a slot no episode saw. Both call `compose`; neither writes the rule again. It is a
measurement-defining path: it decides what a condition is given.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from zihin.config import ConditionConfig, FailureSource, SkillSource, load_condition_config
from zihin.retriever import Retrieved, matched_to, retrieve, retrieve_irrelevant

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

# The experiment's conditions (preregistration A.4). `naive_compiler` is not among
# them: K-145 did not write it.
EXPERIMENT_CONDITIONS = (
    "baseline",
    "skills_failures",
    "skills",
    "failures",
    "irrelevant_retrieval",
)
# The carded arm: every other card-carrying condition is matched to its slot.
REFERENCE_CONDITION = "skills_failures"


def condition_config(name: str) -> ConditionConfig:
    """One experiment condition's configuration, read from `config/<name>.yaml`."""
    if name not in EXPERIMENT_CONDITIONS:
        raise ValueError(f"{name!r} is not an experiment condition: {EXPERIMENT_CONDITIONS}")
    config = load_condition_config(CONFIG_DIR / f"{name}.yaml")
    if config.condition != name:
        raise ValueError(f"config/{name}.yaml names its condition {config.condition!r}")
    return config


def carries_cards(config: ConditionConfig) -> bool:
    return not (
        config.skills_source is SkillSource.NONE and config.failures_source is FailureSource.NONE
    )


@dataclass(frozen=True)
class Slot:
    """The cards one condition gets on one task, and how they relate to the carded arm."""

    condition: str
    # What goes into the slot, already cut to the carded arm's counts.
    cards: Retrieved
    # The carded arm's slot on this task. None for the baseline, which reads no
    # library.
    reference: Retrieved | None
    # One line per kind the irrelevant pool could not match; empty when it did.
    shortfall: tuple[str, ...]

    @property
    def carries_cards(self) -> bool:
        return self.reference is not None

    @property
    def covered(self) -> bool:
        """The carded arm reaches the slot with at least one card (A.3's covered task)."""
        return self.reference is not None and self.reference.covered

    @property
    def runnable(self) -> bool:
        """The baseline always; a card-carrying condition only on a covered task (K1)."""
        return not self.carries_cards or self.covered

    @property
    def volume_matched(self) -> bool | None:
        """Whether the slot carries the carded arm's count. None for the baseline."""
        return None if not self.carries_cards else not self.shortfall


def compose(
    connection: sqlite3.Connection | None,
    instruction: str,
    condition: str,
    *,
    library_id: str | None,
    index_id: str | None,
    task_id: str,
) -> Slot:
    """The slot `condition` gets on this task.

    The filters are the condition's own and they are the same in all five
    configurations (K-175, K-176); the slot counts likewise. The baseline reads
    nothing and needs no connection.
    """
    config = condition_config(condition)
    if not carries_cards(config):
        return Slot(condition, Retrieved(task_id=task_id, apps=frozenset()), None, ())
    if connection is None or library_id is None or index_id is None:
        raise ValueError(f"{condition} carries cards and needs the library and the index")
    kinds = (config.skills_source, config.failures_source)
    unsupported = [k for k in kinds if k.value not in ("standard", "irrelevant")]
    if unsupported:
        raise ValueError(f"{condition}: a card source the experiment does not run: {unsupported}")

    filters = {
        "library_id": library_id,
        "index_id": index_id,
        "min_expected_saving": config.min_expected_saving,
        "max_discriminating_conditions": None,
        "include_unverified_cards": True,
        "task_id": task_id,
    }
    relevant = retrieve(connection, instruction, **filters)
    irrelevant = retrieve_irrelevant(connection, instruction, **filters)
    counts = {"skill_slots": config.skill_slots, "failure_slots": config.failure_slots}
    reference = matched_to(relevant, relevant, **counts).retrieved
    pool = Retrieved(
        task_id=task_id,
        apps=relevant.apps,
        skills=relevant.skills
        if config.skills_source is SkillSource.STANDARD
        else irrelevant.skills,
        failures=(
            relevant.failures
            if config.failures_source is FailureSource.STANDARD
            else irrelevant.failures
        ),
    )
    matched = matched_to(relevant, pool, **counts)
    return Slot(condition, matched.retrieved, reference, matched.shortfall)
