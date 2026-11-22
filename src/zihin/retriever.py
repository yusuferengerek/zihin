"""Retriever v0: picks the skills and failure cards a task should see.

**Symbolic matching, no embedding** (`03-architecture.tr.md`). The rejection is
part of the design, not a shortcut: an embedding adds a second rented component
and a second confounder at run time, and the share of the gain coming from the
mechanism could no longer be separated from the share coming from the embedding
model.

The symbol is the **app**. A task instruction names its apps, and every card is
about one app. The inference is the one the shield already uses
(`allowed_apps.py`) — the same specification serving two mechanisms, so a change
to it moves both and neither drifts from the other.

**Every filter is an argument with no default** (K-50, K-85). The thresholds
belong to the setup phase and none of them has been chosen; a default here would
quietly become the number. The runner sweeps them and reports the sensitivity,
exactly as the support and value thresholds are reported.

**Coverage is the output, not a by-product.** The falsification gates make it a
finding in its own right: below 25% is not "we could not test it" but "the
symbolic retriever finds no relevant experience in this environment"
(`05-experiment-design.tr.md`).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from zihin.allowed_apps import INFRASTRUCTURE_APPS, infer_allowed_apps


@dataclass(frozen=True)
class SkillCard:
    skill_id: str
    apps: tuple[str, ...]
    effect_suffix: tuple[str, ...]
    body: tuple[str, ...]
    support: int
    expected_saving: int | None
    free_parameters: tuple[str, ...]


@dataclass(frozen=True)
class FailureCard:
    pattern_id: str
    app: str
    api: str
    http_method: str
    label: str
    argument_shape: tuple[str, ...]
    condition: dict[str, Any] | None
    no_known_success: bool
    discriminating_count: int | None
    own_app_condition: bool | None
    failure_count: int


@dataclass
class Retrieved:
    task_id: str
    apps: frozenset[str]
    skills: list[SkillCard] = field(default_factory=list)
    failures: list[FailureCard] = field(default_factory=list)

    @property
    def card_count(self) -> int:
        return len(self.skills) + len(self.failures)

    @property
    def covered(self) -> bool:
        return self.card_count > 0


@dataclass(frozen=True)
class Matched:
    """A pool cut to another arm's card count, and whether it could be."""

    retrieved: Retrieved
    # One line per kind the pool could not match; empty when it matched.
    shortfall: tuple[str, ...]

    @property
    def defined(self) -> bool:
        return not self.shortfall


def matched_to(
    reference: Retrieved, pool: Retrieved, *, skill_slots: int, failure_slots: int
) -> Matched:
    """The pool, cut to the number of cards the reference arm reaches the slot with.

    Preregistration A.4: the number of cards is set per task by the retrieval, and
    every card-carrying condition gets that number. So the control arm takes, kind
    by kind, exactly as many as the carded arm puts in the slot - no more, no
    fewer; none if the carded arm gets none. Where the pool holds fewer than that,
    the cut carries what there is and the caller is told which kind fell short:
    the arm runs short and its episodes say so (A.4's correction of 26 September
    2026, K-181; until then it was not run, K-179).
    """
    want_skills = min(len(reference.skills), skill_slots)
    want_failures = min(len(reference.failures), failure_slots)
    shortfall = []
    if len(pool.skills) < want_skills:
        shortfall.append(f"skills: {want_skills} wanted, {len(pool.skills)} available")
    if len(pool.failures) < want_failures:
        shortfall.append(f"failures: {want_failures} wanted, {len(pool.failures)} available")
    cut = Retrieved(
        task_id=pool.task_id,
        apps=pool.apps,
        skills=pool.skills[:want_skills],
        failures=pool.failures[:want_failures],
    )
    return Matched(cut, tuple(shortfall))


def task_apps(instruction: str) -> frozenset[str]:
    """The apps a task names, infrastructure removed.

    Infrastructure is dropped **here but not in the shield**, and the difference
    is not an inconsistency. The shield must let the agent reach `supervisor`
    and `api_docs` or no task can start; the retriever matching on them would
    hand every task the same `api_docs` card, which is the card measured to rest
    on a coincidence (S-45). One inference, two uses, and the difference is
    written down rather than left to be rediscovered.
    """
    return frozenset(infer_allowed_apps(instruction) - INFRASTRUCTURE_APPS)


def _apps_of_skill(row: sqlite3.Row) -> tuple[str, ...]:
    """The apps a skill acts on, read off its effect suffix.

    The body's other calls are how the skill was found, not what it does, so a
    task that merely reads `api_docs` does not thereby match every skill.
    """
    effects = json.loads(row["effect_suffix"])
    return tuple(sorted({e.split(" ", 1)[1].split(".", 1)[0] for e in effects}))


def retrieve_irrelevant(
    connection: sqlite3.Connection,
    instruction: str,
    *,
    library_id: str,
    index_id: str,
    min_expected_saving: int,
    max_discriminating_conditions: int | None,
    include_unverified_cards: bool,
    task_id: str = "",
) -> Retrieved:
    """The cards this task would **not** get: the control arm's pool.

    **It differs from `retrieve` in relevance and in nothing else** (K-176). The
    same library, the same index, the same value floor, the same failure-card
    filters, the same order; only the test on the task's apps is inverted. Both
    go through `_select`, so a filter cannot be added to one arm and forgotten in
    the other. Until 25 September 2026 this arm took no value floor and carried
    no failure cards at all, so its slot differed from the carded arm's in kind
    as well as in relevance.

    A card no task could ever retrieve - one whose apps are all infrastructure -
    is left out here too: it is not an irrelevant card of the kind the mechanism
    delivers, it is a card the mechanism never delivers.
    """
    return _select(
        connection,
        instruction,
        relevant=False,
        library_id=library_id,
        index_id=index_id,
        min_expected_saving=min_expected_saving,
        max_discriminating_conditions=max_discriminating_conditions,
        include_unverified_cards=include_unverified_cards,
        task_id=task_id,
    )


def retrieve(
    connection: sqlite3.Connection,
    instruction: str,
    *,
    library_id: str,
    index_id: str,
    min_expected_saving: int,
    max_discriminating_conditions: int | None,
    include_unverified_cards: bool,
    task_id: str = "",
) -> Retrieved:
    """The cards one task gets.

    `max_discriminating_conditions=None` means "do not filter on it". The
    counter exists because the condition search compares ninety-two candidates
    against small failure groups, so a high count means the choice among
    separating conditions was arbitrary (S-45). Whether to act on it is a setup
    parameter and is swept, not decided here.

    `include_unverified_cards` covers the patterns with no contrasting success.
    They carry no condition at all (K-85) and the taxonomy counts them
    separately, so whether they reach the agent is a separate switch.
    """
    return _select(
        connection,
        instruction,
        relevant=True,
        library_id=library_id,
        index_id=index_id,
        min_expected_saving=min_expected_saving,
        max_discriminating_conditions=max_discriminating_conditions,
        include_unverified_cards=include_unverified_cards,
        task_id=task_id,
    )


def _select(
    connection: sqlite3.Connection,
    instruction: str,
    *,
    relevant: bool,
    library_id: str,
    index_id: str,
    min_expected_saving: int,
    max_discriminating_conditions: int | None,
    include_unverified_cards: bool,
    task_id: str,
) -> Retrieved:
    """One selection for both arms; `relevant` is the only thing that differs."""
    apps = task_apps(instruction)
    found = Retrieved(task_id=task_id, apps=apps)
    if not apps:
        return found

    def wanted(card_apps: set[str]) -> bool:
        if not card_apps - INFRASTRUCTURE_APPS:
            return False
        return bool(card_apps & apps) == relevant

    for row in connection.execute(
        "SELECT * FROM skills WHERE library_id = ? ORDER BY support DESC, skill_id",
        (library_id,),
    ):
        skill_apps = _apps_of_skill(row)
        if not wanted(set(skill_apps)):
            continue
        saving = row["expected_saving"]
        # An unmeasurable saving is not a small one. A skill whose steps could
        # not be attributed has NULL here, and dropping it silently would treat
        # "not measured" as "not worth it".
        if saving is not None and saving < min_expected_saving:
            continue
        found.skills.append(
            SkillCard(
                skill_id=row["skill_id"],
                apps=skill_apps,
                effect_suffix=tuple(json.loads(row["effect_suffix"])),
                body=tuple(json.loads(row["body"])),
                support=row["support"],
                expected_saving=saving,
                free_parameters=tuple(json.loads(row["free_parameters"])),
            )
        )

    for row in connection.execute(
        "SELECT * FROM failure_patterns WHERE index_id = ? ORDER BY failure_count DESC, pattern_id",
        (index_id,),
    ):
        if not wanted({row["app"]}):
            continue
        unverified = bool(row["no_known_success"])
        if unverified and not include_unverified_cards:
            continue
        count = row["discriminating_count"]
        if (
            max_discriminating_conditions is not None
            and count is not None
            and count > max_discriminating_conditions
        ):
            continue
        found.failures.append(
            FailureCard(
                pattern_id=row["pattern_id"],
                app=row["app"],
                api=row["api"],
                http_method=row["http_method"],
                label=row["failure_label"],
                argument_shape=tuple(json.loads(row["argument_shape"])),
                condition=json.loads(row["condition"]) if row["condition"] else None,
                no_known_success=unverified,
                discriminating_count=count,
                own_app_condition=(
                    None if row["own_app_condition"] is None else bool(row["own_app_condition"])
                ),
                failure_count=row["failure_count"],
            )
        )
    return found
