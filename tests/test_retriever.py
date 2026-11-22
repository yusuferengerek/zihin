"""Retriever v0: symbolic matching, and every filter an explicit argument.

Three things carry it and each can fail without saying so.

**It matches on the app the card acts on, not on the calls it happens to
contain.** Every skill body starts with an `api_docs` read, so matching on the
body would hand every skill to every task that mentions documentation — which is
every task.

**Infrastructure is dropped here but not in the shield.** The same inference
serves both and the difference is deliberate: the shield must let the agent
reach `supervisor`, the retriever matching on it would hand every task the same
card.

**Filters are arguments, not defaults.** Their numbers belong to the setup phase
and none has been chosen (K-50, K-85). A default here would quietly become the
number, and it would do so in the component whose output the pilot measures.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from zihin.records import insert_failure_pattern, insert_skill, open_database
from zihin.retriever import Retrieved, matched_to, retrieve, retrieve_irrelevant, task_apps

REPOSITORY = Path(__file__).resolve().parents[1]


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        _skill(connection, "venmo", saving=8)
        _skill(connection, "spotify", saving=30)
        _card(connection, "venmo", "transactions", count=5)
        _card(connection, "phone", "contacts", count=3, discriminating=40)
        _card(connection, "todoist", "projects", count=1, unverified=True)
        yield connection


def _skill(connection, app: str, saving: int) -> None:
    insert_skill(
        connection,
        skill_id=f"skill-{app}",
        library_id="kutuphane",
        effect_suffix=[f"POST {app}.auth/token"],
        # The body deliberately opens with an api_docs read, as every mined
        # skill in the corpus does.
        body=["GET api_docs.api_doc", f"POST {app}.auth/token"],
        body_length=2,
        support=5,
        supporting_tasks=["g1"],
        supporting_episodes=[1],
        merged_from=3,
        bound_arguments={},
        free_parameters=["1.password"],
        constants={},
        postcondition={},
        expected_saving=saving,
        expected_saving_calls=saving,
        observed_steps=2,
        max_gap=2,
        min_support=3,
        constant_threshold=3,
        compiler_commit="deadbeef",
        write_set_digest="a" * 64,
    )


def _card(
    connection,
    app: str,
    api: str,
    count: int,
    discriminating: int | None = 2,
    unverified: bool = False,
) -> None:
    insert_failure_pattern(
        connection,
        pattern_id=f"card-{app}-{api}",
        index_id="indeks",
        app=app,
        api=api,
        http_method="GET",
        argument_shape=[],
        status_code="401",
        failure_label="authorization_denied",
        condition=None
        if unverified
        else {"kind": "prior_successful_call", "call": f"POST {app}.auth/token", "present": False},
        discriminator=None if unverified else "condition",
        support=1,
        supporting_tasks=["g1"],
        failure_count=count,
        contrast_successes=0 if unverified else 4,
        no_known_success=int(unverified),
        discriminating_count=None if unverified else discriminating,
        own_app_condition=None if unverified else 1,
        min_support=1,
        compiler_commit="deadbeef",
    )


def _retrieve(db, instruction, **overrides):
    options = {
        "library_id": "kutuphane",
        "index_id": "indeks",
        "min_expected_saving": 0,
        "max_discriminating_conditions": None,
        "include_unverified_cards": True,
    }
    options.update(overrides)
    return retrieve(db, instruction, **options)


# --- matching ---


def test_a_task_gets_the_cards_of_the_apps_it_names(db):
    found = _retrieve(db, "Send $20 to Nancy on Venmo.")
    assert [s.skill_id for s in found.skills] == ["skill-venmo"]
    assert [f.pattern_id for f in found.failures] == ["card-venmo-transactions"]


def test_an_unnamed_app_gives_nothing(db):
    found = _retrieve(db, "Send $20 to Nancy on Venmo.")
    assert "spotify" not in {a for s in found.skills for a in s.apps}


def test_matching_uses_the_effect_suffix_not_the_body(db):
    """Every mined body opens with an `api_docs` read.

    Mutation: matching on the body's calls. `api_docs` is documentation and
    infrastructure, so every task would match every skill and coverage would be
    100% while meaning nothing.
    """
    found = _retrieve(db, "Read the API documentation.")
    assert found.skills == []


def test_infrastructure_apps_do_not_match(db):
    """The shield allows them unconditionally; the retriever ignores them.

    One inference, two uses. Mutation: reusing `infer_allowed_apps` unchanged.
    Every task names `supervisor` implicitly, so every task would draw whatever
    card `supervisor` had.
    """
    assert task_apps("Ask my supervisor for the address.") == frozenset()


def test_a_task_naming_two_apps_gets_both(db):
    found = _retrieve(db, "Play the song on Spotify and pay for it on Venmo.")
    assert {s.skill_id for s in found.skills} == {"skill-venmo", "skill-spotify"}


def test_a_task_naming_nothing_is_uncovered(db):
    found = _retrieve(db, "Do the thing.")
    assert not found.covered
    assert found.card_count == 0


# --- the filters ---


def test_the_saving_threshold_drops_the_cheaper_skill(db):
    found = _retrieve(db, "Play on Spotify and pay on Venmo.", min_expected_saving=20)
    assert {s.skill_id for s in found.skills} == {"skill-spotify"}


def test_an_unmeasurable_saving_is_not_treated_as_a_small_one(db):
    """NULL means "could not attribute", not "worth nothing".

    Mutation: comparing NULL as zero. The skill would vanish at any positive
    threshold, and a missing measurement would read as a negative one — the
    same confusion K-79 had to be corrected for.
    """
    _skill_null = dict(
        skill_id="skill-todoist",
        library_id="kutuphane",
        effect_suffix=["POST todoist.auth/token"],
        body=["GET api_docs.api_doc", "POST todoist.auth/token"],
        body_length=2,
        support=5,
        supporting_tasks=["g1"],
        supporting_episodes=[1],
        merged_from=1,
        bound_arguments={},
        free_parameters=[],
        constants={},
        postcondition=None,
        expected_saving=None,
        expected_saving_calls=5,
        observed_steps=None,
        max_gap=2,
        min_support=3,
        constant_threshold=3,
        compiler_commit="deadbeef",
        write_set_digest="a" * 64,
    )
    insert_skill(db, **_skill_null)
    found = _retrieve(db, "Add a todoist task.", min_expected_saving=1000)
    assert [s.skill_id for s in found.skills] == ["skill-todoist"]


def test_the_condition_cap_drops_a_card_that_separated_too_easily(db):
    """A high count means the choice among separating conditions was arbitrary.

    Not a rule in the index — the index stores everything with its provenance
    and the reader decides (K-85).
    """
    wide = _retrieve(db, "Call a contact on my phone.")
    assert [f.pattern_id for f in wide.failures] == ["card-phone-contacts"]

    narrow = _retrieve(db, "Call a contact on my phone.", max_discriminating_conditions=10)
    assert narrow.failures == []


def test_unverified_cards_are_a_separate_switch(db):
    """Patterns with no contrasting success carry no condition at all (K-85).

    They still exist — a failure seen once but real does not vanish — but
    whether they reach the agent is its own decision.
    """
    with_them = _retrieve(db, "Add a todoist task.")
    assert [f.pattern_id for f in with_them.failures] == ["card-todoist-projects"]
    assert with_them.failures[0].condition is None
    assert with_them.failures[0].no_known_success

    without = _retrieve(db, "Add a todoist task.", include_unverified_cards=False)
    assert without.failures == []


def test_every_filter_has_to_be_given(db):
    """No default may slip in: the numbers define what the pilot measures."""
    with pytest.raises(TypeError):
        retrieve(db, "Venmo.", library_id="kutuphane", index_id="indeks")


# --- provenance travels with the card ---


def test_the_card_carries_what_the_reader_needs_to_judge_it(db):
    found = _retrieve(db, "Call a contact on my phone.")
    card = found.failures[0]
    assert card.discriminating_count == 40
    assert card.own_app_condition is True
    assert card.condition == {
        "kind": "prior_successful_call",
        "call": "POST phone.auth/token",
        "present": False,
    }


def test_a_skill_card_carries_its_free_parameters(db):
    """The caller has to know what it must supply.

    For the login skills that is the credentials, because the body does not
    contain the call that reads them (S-42).
    """
    found = _retrieve(db, "Pay on Venmo.")
    assert found.skills[0].free_parameters == ("1.password",)


def test_two_libraries_do_not_bleed_into_each_other(db):
    insert_skill(
        db,
        **{
            **json.loads(json.dumps({})),
            "skill_id": "other",
            "library_id": "other-library",
            "effect_suffix": ["POST venmo.auth/token"],
            "body": ["GET api_docs.api_doc", "POST venmo.auth/token"],
            "body_length": 2,
            "support": 9,
            "supporting_tasks": ["g9"],
            "supporting_episodes": [9],
            "merged_from": 1,
            "bound_arguments": {},
            "free_parameters": [],
            "constants": {},
            "postcondition": {},
            "expected_saving": 9,
            "expected_saving_calls": 9,
            "observed_steps": 2,
            "max_gap": 5,
            "min_support": 2,
            "constant_threshold": 3,
            "compiler_commit": "cafe",
            "write_set_digest": "b" * 64,
        },
    )
    found = _retrieve(db, "Pay on Venmo.")
    assert [s.skill_id for s in found.skills] == ["skill-venmo"]


# --- the control arm's pool ---


def _irrelevant(db, instruction, **overrides):
    options = {
        "library_id": "kutuphane",
        "index_id": "indeks",
        "min_expected_saving": 0,
        "max_discriminating_conditions": None,
        "include_unverified_cards": True,
    }
    options.update(overrides)
    return retrieve_irrelevant(db, instruction, **options)


def _both(db, instruction, **overrides):
    return _retrieve(db, instruction, **overrides), _irrelevant(db, instruction, **overrides)


def test_the_irrelevant_pool_is_disjoint_from_what_the_task_would_get(db):
    """The control arm must not hand back the card the task actually matches.

    If the two overlapped, the arm would be a weaker copy of the carded arm and
    the comparison would mean nothing.
    """
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    got = {card.skill_id for card in relevant.skills}
    control = {card.skill_id for card in irrelevant.skills}
    assert got, "the fixture task should match at least one skill"
    assert control, "the control arm needs a non-empty pool"
    assert not (got & control)


def test_the_irrelevant_pool_carries_the_failure_cards_of_other_apps(db):
    """The control arm differs from the carded arm in relevance alone (K-176).

    It used to carry skills only, on the reasoning that a failure card for another
    app and no failure card are the same slot content. The declaration of 25
    September 2026 reversed that: a slot without failure cards differs from the
    carded slot in kind and in volume, not only in relevance.
    """
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    assert {card.app for card in relevant.failures} == {"venmo"}
    assert {card.app for card in irrelevant.failures} == {"phone", "todoist"}


def test_the_two_arms_take_the_same_filters():
    """A filter cannot exist in one arm and not the other."""
    assert (
        inspect.signature(retrieve).parameters == inspect.signature(retrieve_irrelevant).parameters
    )


def _names(found) -> set[str]:
    return {c.skill_id for c in found.skills} | {c.pattern_id for c in found.failures}


@pytest.mark.parametrize(
    "overrides, gone",
    [
        ({"min_expected_saving": 31}, "skill-spotify"),
        ({"max_discriminating_conditions": 10}, "card-phone-contacts"),
        ({"include_unverified_cards": False}, "card-todoist-projects"),
    ],
    ids=["value-floor", "condition-cap", "unverified-switch"],
)
def test_every_filter_applies_to_the_control_arm(db, overrides, gone):
    _, before = _both(db, "Send $20 to Nancy on Venmo.")
    _, after = _both(db, "Send $20 to Nancy on Venmo.", **overrides)
    assert gone in _names(before)
    assert gone not in _names(after)


def test_the_two_arms_partition_what_the_filters_let_through(db):
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    everything, _ = _both(db, "Venmo, Spotify, phone contacts and Todoist.")
    left = {c.skill_id for c in relevant.skills + irrelevant.skills}
    left |= {c.pattern_id for c in relevant.failures + irrelevant.failures}
    whole = {c.skill_id for c in everything.skills} | {c.pattern_id for c in everything.failures}
    assert left == whole


def test_a_card_no_task_can_retrieve_is_not_an_irrelevant_card(db):
    _card(db, "api_docs", "api_descriptions", count=150)
    _, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    assert "api_docs" not in {card.app for card in irrelevant.failures}


def test_the_irrelevant_pool_is_empty_when_the_task_names_no_app(db):
    """No apps means no basis for "not matching" either.

    `retrieve` returns nothing here, and so must the control: an arm that filled
    the slot where the carded arm could not would compare two different things.
    """
    relevant, irrelevant = _both(db, "Do something vague.")
    assert relevant.skills == []
    assert irrelevant.skills == []


def test_the_irrelevant_pool_is_deterministic(db):
    """Three repeats must receive the same cards.

    The ordering is `support DESC, skill_id`, the same as `retrieve`; without it
    the repeats would differ in their slot and the stability analysis would be
    measuring the selection rather than the model.
    """
    first = _irrelevant(db, "Send $20 to Nancy on Venmo.")
    second = _irrelevant(db, "Send $20 to Nancy on Venmo.")
    assert [c.skill_id for c in first.skills] == [c.skill_id for c in second.skills]


# --- equal card counts (A.4, K-179) ---


@pytest.mark.parametrize("slots", [(5, 5), (1, 1), (0, 2)])
def test_the_control_arm_gets_the_carded_arms_count_kind_by_kind(db, slots):
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    matched = matched_to(relevant, irrelevant, skill_slots=slots[0], failure_slots=slots[1])
    assert len(matched.retrieved.skills) == min(len(relevant.skills), slots[0])
    assert len(matched.retrieved.failures) == min(len(relevant.failures), slots[1])
    assert matched.defined


def test_nothing_for_the_carded_arm_means_nothing_for_the_control(db):
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    empty = Retrieved(task_id="t", apps=relevant.apps)
    matched = matched_to(empty, irrelevant, skill_slots=5, failure_slots=5)
    assert matched.retrieved.skills == [] and matched.retrieved.failures == []
    assert matched.defined


def test_a_pool_that_falls_short_is_named_and_the_cut_carries_what_there_is(db):
    """K-181: the arm runs short rather than not at all, so the cut keeps the cards
    the pool has and the shortfall names what it lacks."""
    relevant, irrelevant = _both(db, "Send $20 to Nancy on Venmo.")
    bigger = Retrieved(
        task_id="t", apps=relevant.apps, skills=relevant.skills * 3, failures=relevant.failures
    )
    matched = matched_to(bigger, irrelevant, skill_slots=5, failure_slots=5)
    assert not matched.defined
    assert matched.shortfall == ("skills: 3 wanted, 1 available",)
    assert len(matched.retrieved.skills) == 1
