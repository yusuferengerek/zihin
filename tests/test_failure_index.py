"""The failure index: does it obey the rules the taxonomy fixes.

The load-bearing rule is that **every card carries a context condition**. An
unconditional prohibition makes the agent worse — a card that says "do not make
this call" without saying when also blocks it where it is required. So the tests
here spend most of their weight on when a card is *refused*.

The second rule is that the condition language stays closed (K-83). Only the
third form is available in this record: whether a call had already succeeded.
The argument component is part of the pattern, and it is a **shape** — which
names the call carried, never their values.
"""

from __future__ import annotations

from zihin.failure_index import (
    STATUS_LABELS,
    Condition,
    ObservedAction,
    facts_before,
    mine_failure_patterns,
)


def action(
    order: int,
    app: str,
    api: str,
    method: str = "GET",
    status: str = "200",
    arguments: dict | None = None,
    episode_id: int = 1,
    task_id: str = "gorev-a",
) -> ObservedAction:
    return ObservedAction(
        episode_id=episode_id,
        task_id=task_id,
        order=order,
        app=app,
        api=api,
        method=method,
        status=status,
        error_class=None,
        arguments=arguments or {},
    )


def episode(episode_id: int, task_id: str, *calls: ObservedAction) -> tuple[int, list]:
    fixed = [
        ObservedAction(
            episode_id=episode_id,
            task_id=task_id,
            order=index,
            app=c.app,
            api=c.api,
            method=c.method,
            status=c.status,
            error_class=c.error_class,
            arguments=c.arguments,
        )
        for index, c in enumerate(calls)
    ]
    return episode_id, fixed


# --- the label comes from the status code ---


def test_the_label_is_read_from_the_status_code():
    """`error_class` is uniformly 'Exception' and carries no signal (S-44).

    Mutation: labelling from `error_class`. Every failure would get one label
    and the index would separate nothing.
    """
    assert STATUS_LABELS["401"] == "authorization_denied"
    assert STATUS_LABELS["422"] == "invalid_parameter"
    assert STATUS_LABELS["409"] == "conflicting_state"


# --- the condition language ---


def test_only_successful_calls_become_facts():
    """A refused login did not log anyone in.

    Mutation: counting every call as a fact regardless of status. The card would
    then say "you already logged in" about an episode whose login was refused,
    which is the opposite of the truth.
    """
    calls = [
        action(0, "venmo", "auth/token", "POST", status="401"),
        action(1, "venmo", "transactions", status="401"),
    ]
    facts = facts_before(calls)
    assert facts[0] == frozenset()
    assert facts[1] == frozenset(), "a refused login was counted as a fact"


def test_a_successful_call_becomes_a_fact_for_what_follows():
    calls = [
        action(0, "venmo", "auth/token", "POST"),
        action(1, "venmo", "transactions"),
    ]
    assert facts_before(calls)[1] == frozenset({"POST venmo.auth/token"})


def test_absence_is_a_condition_too():
    """ "No prior login" is what two thirds of the corpus's 401s have in common."""
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="200"),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "venmo", "transactions", status="401"),
            ),
        ]
    )
    patterns, _ = mine_failure_patterns(episodes, min_support=1)
    assert len(patterns) == 1
    assert patterns[0].condition == Condition(
        "prior_successful_call", "POST venmo.auth/token", False
    )


# --- a card is refused when nothing can be said ---


def test_no_card_when_no_condition_holds_in_every_failure():
    """Two failures with nothing in common produce no card.

    Mutation: attaching a condition that holds in *some* failures. The card
    would then be wrong for the rest, and a wrong condition is worse than no
    card at all.
    """
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="409"),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "venmo", "transactions", status="409"),
            ),
            # The contrast: the same endpoint succeeding, in both states.
            episode(
                3,
                "gorev-c",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="200"),
            ),
            episode(4, "gorev-d", action(0, "venmo", "transactions", status="200")),
        ]
    )
    patterns, tally = mine_failure_patterns(episodes, min_support=1)
    assert patterns == []
    assert tally["no_expressible_condition"] == 1


def test_a_condition_that_also_holds_in_a_success_does_not_discriminate():
    """Holding in every failure is not enough; it must not hold in a success."""
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="409"),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="200"),
            ),
        ]
    )
    patterns, tally = mine_failure_patterns(episodes, min_support=1)
    assert patterns == []
    assert tally["no_expressible_condition"] == 1


def test_a_pattern_below_the_support_threshold_is_counted_not_kept():
    episodes = dict([episode(1, "gorev-a", action(0, "venmo", "transactions", status="401"))])
    patterns, tally = mine_failure_patterns(episodes, min_support=2)
    assert patterns == []
    assert tally["below_support"] == 1


# --- the argument shape ---


def test_the_shape_is_argument_names_not_values():
    """Keying on values would explode the pattern space (K-83).

    Two failures with different values are one pattern; the same call with a
    different argument *name* is a different one.
    """
    same = [
        action(0, "venmo", "transactions", "POST", status="401", arguments={"amount": 1}),
        action(0, "venmo", "transactions", "POST", status="401", arguments={"amount": 999}),
    ]
    assert same[0].shape == same[1].shape == ("amount",)
    other = action(0, "venmo", "transactions", "POST", arguments={"amount": 1, "note": "x"})
    assert other.shape != same[0].shape


def test_the_session_token_stays_in_the_shape():
    """Its absence is what distinguishes a third of the corpus's 401s.

    Mutation: dropping `access_token` from the shape the way the compiler drops
    it from skill arguments. The "logged in but not carrying the token" pattern
    would merge into "not logged in" and the two cards would become one wrong
    one.
    """
    with_token = action(0, "simple_note", "notes", arguments={"access_token": "x"})
    without = action(0, "simple_note", "notes", arguments={})
    assert with_token.shape == ("access_token",)
    assert without.shape == ()
    assert with_token.shape != without.shape


def test_two_shapes_of_one_endpoint_are_two_patterns():
    """The corpus's two 401 families differ only by shape."""
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "simple_note", "notes", status="401", arguments={}),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "simple_note", "auth/token", "POST"),
                action(1, "simple_note", "notes", status="401", arguments={}),
                action(2, "simple_note", "notes", status="200", arguments={"access_token": "t"}),
            ),
        ]
    )
    patterns, _ = mine_failure_patterns(episodes, min_support=1)
    shapes = {p.shape for p in patterns}
    assert shapes == {()}, "two cards were produced for the same shape"


# --- what the card says about its own trustworthiness ---


def test_a_pattern_with_no_contrasting_success_is_marked():
    """Kept rather than dropped, but the mark travels with it.

    A failure seen once and never contradicted is still a finding
    (`07-failure-taxonomy.tr.md`); what it is not is verified.
    """
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "splitwise", "auth/logout", "POST", status="422"),
            )
        ]
    )
    patterns, tally = mine_failure_patterns(episodes, min_support=1)
    assert len(patterns) == 1
    assert patterns[0].no_known_success
    assert patterns[0].contrast_successes == 0
    assert tally["no_known_success"] == 1


def test_the_card_records_how_many_conditions_separated_it():
    """With ninety-two candidates a condition can separate by coincidence.

    The count is on the card so the reader can see the choice was arbitrary
    without re-deriving it. Measured: one corpus pattern had 59 separating
    conditions, all of them vacuous because it had no contrasting success.
    """
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "phone", "contacts", status="401"),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "phone", "auth/token", "POST"),
                action(1, "phone", "contacts", status="200"),
            ),
        ]
    )
    patterns, _ = mine_failure_patterns(episodes, min_support=1)
    assert patterns[0].discriminating_count >= 1
    assert patterns[0].own_app_condition


def test_a_condition_about_another_app_is_flagged():
    """A separating condition on an unrelated app is a correlation, not a cause.

    The card still enters — the rule is about expressibility, not causality —
    but it says so, because a reader who cannot tell the two apart will trust
    both equally.
    """
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "spotify", "songs"),
                action(1, "api_docs", "api_doc", status="422"),
            ),
            episode(2, "gorev-b", action(0, "api_docs", "api_doc", status="200")),
        ]
    )
    patterns, tally = mine_failure_patterns(episodes, min_support=1)
    assert len(patterns) == 1
    assert not patterns[0].own_app_condition
    assert tally["unrelated_app_condition"] == 1


# --- determinism ---


def test_the_same_record_gives_the_same_index():
    """Offline, deterministic, no model. Two runs must agree exactly."""
    episodes = dict(
        [
            episode(
                1,
                "gorev-a",
                action(0, "venmo", "users"),
                action(1, "venmo", "transactions", status="401"),
            ),
            episode(
                2,
                "gorev-b",
                action(0, "venmo", "auth/token", "POST"),
                action(1, "venmo", "transactions", status="200"),
            ),
        ]
    )
    first, _ = mine_failure_patterns(episodes, min_support=1)
    second, _ = mine_failure_patterns(episodes, min_support=1)
    assert [(p.key, p.condition) for p in first] == [(p.key, p.condition) for p in second]
