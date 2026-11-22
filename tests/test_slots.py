"""What each of the five conditions puts in the slot (A.4, K-179, K-181).

Three rules carry it, and each can fail without a visible error.

**Every card-carrying condition gets the carded arm's count, kind by kind.** A
kind that comes from the irrelevant pool is cut to what `skills_failures` puts in
the slot, never to the slot's size.

**A pool that falls short runs short and says so.** The control is not skipped
and not padded: it carries what there is and `volume_matched` is false.

**A task the carded arm reaches with no card runs no card-carrying condition.**
Its reference slot is empty, so every other slot is cut to empty (K1).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zihin.records import insert_failure_pattern, insert_skill, open_database
from zihin.slots import EXPERIMENT_CONDITIONS, compose, condition_config

REPOSITORY = Path(__file__).resolve().parents[1]
VENMO = "Send $20 to Nancy on Venmo."


def _skill(connection, name: str, app: str, support: int = 5) -> None:
    insert_skill(
        connection,
        skill_id=name,
        library_id="library",
        effect_suffix=[f"POST {app}.{name}"],
        body=["GET api_docs.api_doc", f"POST {app}.{name}"],
        body_length=2,
        support=support,
        supporting_tasks=["g1"],
        supporting_episodes=[1],
        merged_from=3,
        bound_arguments={},
        free_parameters=[],
        constants={},
        postcondition={},
        expected_saving=4,
        expected_saving_calls=4,
        observed_steps=5,
        max_gap=2,
        min_support=3,
        constant_threshold=3,
        compiler_commit="deadbeef",
        write_set_digest="a" * 64,
    )


def _card(connection, app: str, api: str, count: int = 3) -> None:
    insert_failure_pattern(
        connection,
        pattern_id=f"card-{app}-{api}",
        index_id="index",
        app=app,
        api=api,
        http_method="GET",
        argument_shape=[],
        status_code="401",
        failure_label="authorization_denied",
        condition={"kind": "prior_successful_call", "call": f"POST {app}.x", "present": False},
        discriminator="condition",
        support=1,
        supporting_tasks=["g1"],
        failure_count=count,
        contrast_successes=4,
        no_known_success=0,
        discriminating_count=2,
        own_app_condition=1,
        min_support=1,
        compiler_commit="deadbeef",
    )


@pytest.fixture
def db(tmp_path):
    """Venmo has two skills and two failure cards; the other apps have one skill
    and three failure cards, so the irrelevant pool is short of skills only."""
    with open_database(tmp_path / "record.sqlite") as connection:
        _skill(connection, "venmo_a", "venmo")
        _skill(connection, "venmo_b", "venmo")
        _skill(connection, "spotify_a", "spotify")
        _card(connection, "venmo", "transactions")
        _card(connection, "venmo", "payment_cards")
        _card(connection, "phone", "contacts")
        _card(connection, "spotify", "songs")
        _card(connection, "todoist", "projects")
        yield connection


def _slot(db, condition: str, instruction: str = VENMO):
    return compose(db, instruction, condition, library_id="library", index_id="index", task_id="t")


def _apps(cards) -> set[str]:
    return {a for s in cards.skills for a in s.apps} | {f.app for f in cards.failures}


def test_the_five_conditions_are_the_experiments() -> None:
    assert EXPERIMENT_CONDITIONS == (
        "baseline",
        "skills_failures",
        "skills",
        "failures",
        "irrelevant_retrieval",
    )
    for name in EXPERIMENT_CONDITIONS:
        assert condition_config(name).condition == name


def test_the_carded_arm_takes_the_tasks_own_cards(db) -> None:
    slot = _slot(db, "skills_failures")
    assert len(slot.cards.skills) == 2 and len(slot.cards.failures) == 2
    assert _apps(slot.cards) == {"venmo"}
    assert slot.volume_matched is True


def test_skills_takes_its_own_skills_and_irrelevant_failures_at_the_carded_count(db) -> None:
    slot = _slot(db, "skills")
    assert {s.skill_id for s in slot.cards.skills} == {"venmo_a", "venmo_b"}
    assert len(slot.cards.failures) == 2
    assert "venmo" not in {f.app for f in slot.cards.failures}
    assert slot.volume_matched is True


def test_failures_takes_its_own_failures_and_runs_short_of_irrelevant_skills(db) -> None:
    slot = _slot(db, "failures")
    assert {f.app for f in slot.cards.failures} == {"venmo"}
    assert [s.skill_id for s in slot.cards.skills] == ["spotify_a"]
    assert slot.volume_matched is False
    assert slot.shortfall == ("skills: 2 wanted, 1 available",)


def test_the_control_takes_irrelevant_cards_of_both_kinds_and_runs_short(db) -> None:
    """The d194965_1 case in miniature: it runs with what there is, flagged."""
    slot = _slot(db, "irrelevant_retrieval")
    assert "venmo" not in _apps(slot.cards)
    assert len(slot.cards.skills) == 1
    assert len(slot.cards.failures) == 2
    assert slot.runnable
    assert slot.volume_matched is False


def test_a_kind_is_cut_to_the_carded_count_not_to_the_slot(db) -> None:
    """Three irrelevant failure cards exist and the slot holds five; the carded
    arm puts two in, so the control gets two."""
    slot = _slot(db, "irrelevant_retrieval")
    assert len(slot.cards.failures) == len(_slot(db, "skills_failures").cards.failures) == 2


def test_the_baseline_reads_nothing(db) -> None:
    slot = compose(None, VENMO, "baseline", library_id=None, index_id=None, task_id="t")
    assert slot.cards.card_count == 0
    assert slot.volume_matched is None
    assert slot.runnable


@pytest.mark.parametrize(
    "condition", ["skills_failures", "skills", "failures", "irrelevant_retrieval"]
)
def test_a_task_the_carded_arm_cannot_reach_runs_no_card_carrying_condition(db, condition) -> None:
    """K1: `8ce6779_3`. The reference is empty, so nothing else may carry a card."""
    slot = _slot(db, condition, "Add a note titled groceries in my Simple Note account.")
    assert not slot.covered
    assert not slot.runnable
    assert slot.cards.card_count == 0


def test_the_runner_builds_every_slot_through_the_one_selection() -> None:
    source = (REPOSITORY / "scripts/record_run.py").read_text(encoding="utf-8")
    assert "compose(" in source
    assert "retrieve(" not in source and "retrieve_irrelevant(" not in source
    assert "if not slot.covered:" in source
