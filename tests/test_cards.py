"""The printed form of a card, which is what the token budget is about.

Three things carry it and each can fail silently.

**The field counts are the spec's, not the renderer's convenience.** Seven for a
skill, five for a failure. A field added here is content the compiler never
derived, and it would enter the measured gain without provenance.

**The empty block has to leave no trace**, or the empty slot stops being
byte-for-byte the reference prompt (K-25) and the "same trajectory" criterion
breaks for a reason that has nothing to do with cards.

**A conditionless failure card would be an unconditional prohibition**, which
`07-failure-taxonomy.tr.md` rejects outright: it blocks the call in the cases where
the call is needed. Patterns with no contrasting success carry no condition
(K-85), so the card has to say that instead of dropping the line.
"""

from __future__ import annotations

import pytest

from zihin.cards import (
    FAILURE_CARD_FIELDS,
    SKILL_CARD_FIELDS,
    render_card_block,
    render_failure_card,
    render_skill_card,
)
from zihin.retriever import FailureCard, Retrieved, SkillCard
from zihin.scaffold import SLOT_MARKER, render_prompt


def _skill(skill_id: str = "134ca318", saving: int | None = 8) -> SkillCard:
    return SkillCard(
        skill_id=skill_id,
        apps=("venmo",),
        effect_suffix=("POST venmo.auth/token",),
        body=("GET api_docs.api_doc", "POST venmo.auth/token"),
        support=8,
        expected_saving=saving,
        free_parameters=("0.app_name", "1.password", "1.username"),
    )


def _failure(
    pattern_id: str = "dce3af97",
    condition: dict | None = None,
    shape: tuple[str, ...] = (),
) -> FailureCard:
    if condition is None:
        condition = {
            "kind": "prior_successful_call",
            "call": "POST todoist.auth/token",
            "present": False,
        }
    return FailureCard(
        pattern_id=pattern_id,
        app="todoist",
        api="projects/{project_id}/tasks",
        http_method="GET",
        label="authorization_denied",
        argument_shape=shape,
        condition=condition,
        no_known_success=condition is None,
        discriminating_count=1,
        own_app_condition=True,
        failure_count=146,
    )


# --- the field counts ---


def test_a_skill_card_has_exactly_seven_fields():
    lines = render_skill_card(_skill()).splitlines()
    assert len(lines) == SKILL_CARD_FIELDS == 7


def test_a_failure_card_has_exactly_five_fields():
    lines = render_failure_card(_failure()).splitlines()
    assert len(lines) == FAILURE_CARD_FIELDS == 5


def test_the_card_prints_no_field_the_reader_filters_on():
    """`discriminating_count` and `own_app_condition` are filter inputs (K-85).

    Mutation: printing them. The agent cannot act on "this condition also
    separated forty other candidates"; the retriever can, and does.
    """
    text = render_failure_card(_failure())
    assert "discriminating" not in text
    assert "own_app" not in text


# --- the slot contract ---


def test_an_empty_block_renders_nothing():
    empty = Retrieved(task_id="g1", apps=frozenset({"venmo"}))
    assert render_card_block(empty, skill_slots=5, failure_slots=5) == ""
    assert render_prompt("") == render_prompt(
        render_card_block(empty, skill_slots=5, failure_slots=5)
    )


def test_a_full_block_lands_before_the_user_block():
    found = Retrieved(
        task_id="g1", apps=frozenset({"venmo"}), skills=[_skill()], failures=[_failure()]
    )
    block = render_card_block(found, skill_slots=5, failure_slots=5)
    assert block.endswith("\n\n")
    prompt = render_prompt(block)
    assert SLOT_MARKER not in prompt
    assert "  saves: 8 model calls\n\nUSER:" in prompt or "  seen: 146 times\n\nUSER:" in prompt


def test_the_slots_cap_and_keep_the_retriever_order():
    found = Retrieved(
        task_id="g1",
        apps=frozenset({"venmo"}),
        skills=[_skill("first"), _skill("second"), _skill("third")],
        failures=[_failure("f1"), _failure("f2")],
    )
    block = render_card_block(found, skill_slots=2, failure_slots=1)
    assert block.count("SKILL ") == 2
    assert block.count("FAILURE ") == 1
    assert "SKILL first" in block and "SKILL second" in block and "SKILL third" not in block


def test_the_slot_counts_have_no_defaults():
    """The numbers come from the condition config; a default would become one."""
    found = Retrieved(task_id="g1", apps=frozenset({"venmo"}), skills=[_skill()])
    with pytest.raises(TypeError):
        render_card_block(found)


# --- what the fields say ---


def test_an_unattributed_saving_is_not_printed_as_zero():
    """NULL means "could not attribute", not "worth nothing" (K-79)."""
    text = render_skill_card(_skill(saving=None))
    assert "  saves: unknown model calls" in text
    assert "saves: 0" not in text


def test_the_two_directions_of_the_condition_read_differently():
    missing = render_failure_card(_failure())
    present = render_failure_card(
        _failure(
            condition={
                "kind": "prior_successful_call",
                "call": "POST todoist.auth/token",
                "present": True,
            }
        )
    )
    assert "has not succeeded" in missing
    assert "has not succeeded" not in present
    assert "has succeeded" in present


def test_a_pattern_with_no_contrast_says_so_instead_of_dropping_the_line():
    card = FailureCard(
        pattern_id="5e4e21c1",
        app="splitwise",
        api="auth/logout",
        http_method="POST",
        label="invalid_parameter",
        argument_shape=(),
        condition=None,
        no_known_success=True,
        discriminating_count=None,
        own_app_condition=None,
        failure_count=64,
    )
    text = render_failure_card(card)
    assert len(text.splitlines()) == FAILURE_CARD_FIELDS
    assert "no successful contrast recorded" in text


def test_an_unknown_condition_kind_is_refused_not_printed():
    """The language is closed (`07-failure-taxonomy.tr.md`).

    A new form has to gain a rendering deliberately; falling back to `str()`
    would put an unreviewed dialect in front of the model.
    """
    with pytest.raises(ValueError):
        render_failure_card(_failure(condition={"kind": "field_value", "call": "x"}))


def test_an_empty_argument_shape_is_named():
    assert "  arguments: none" in render_failure_card(_failure())
    assert "  arguments: access_token" in render_failure_card(_failure(shape=("access_token",)))


def test_a_skill_without_free_parameters_says_none():
    card = SkillCard(
        skill_id="x",
        apps=("venmo",),
        effect_suffix=("POST venmo.auth/token",),
        body=("POST venmo.auth/token",),
        support=3,
        expected_saving=3,
        free_parameters=(),
    )
    assert "  parameters: none" in render_skill_card(card)


def test_rendering_is_deterministic():
    found = Retrieved(
        task_id="g1", apps=frozenset({"venmo"}), skills=[_skill()], failures=[_failure()]
    )
    first = render_card_block(found, skill_slots=5, failure_slots=5)
    second = render_card_block(found, skill_slots=5, failure_slots=5)
    assert first == second
