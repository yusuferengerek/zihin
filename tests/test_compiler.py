"""Compiler v0's miner: does it mine what the design says it mines.

Four properties carry the whole thing and each has a way of failing silently.

**Support counts tasks.** Ten episodes of one task are one task. A miner that
counted episodes would put a single task's repetitions into the library, and the
number would look healthier for it.

**The gap constraint is a distance, not a suggestion.** `max_gap=0` means
strictly adjacent. Off by one here changes every support in the corpus and
nothing announces it.

**Closure drops the shorter pattern only at equal support.** Dropping it at
lower support would delete real findings; never dropping it floods the report
with prefixes of one pattern.

**End positions, not occurrence tuples.** The first version kept every matching
tuple and did not terminate on a 255-call episode. The optimisation has to give
the same answer as the definition, so the tests state the answer directly rather
than comparing two implementations.

Sequences here are hand-written and tiny. The corpus-scale run is
`scripts/setup/mine_skills.py`, and its numbers are a measurement, not a test.
"""

from __future__ import annotations

import json

from zihin.compiler import (
    EpisodeSequence,
    Pattern,
    RecordedCall,
    call_from_action,
    call_from_log,
    classify_arguments,
    effect_elements,
    merge_by_effect_suffix,
    mine_patterns,
    occurrence_postcondition,
    pattern_postcondition,
    scaffold_control_elements,
)


def call(app: str, template: str, method: str = "GET") -> RecordedCall:
    return RecordedCall(app=app, template=template, method=method, arguments={})


def sequence(episode_id: int, task_id: str, *templates: str) -> EpisodeSequence:
    return EpisodeSequence(
        episode_id=episode_id,
        task_id=task_id,
        calls=tuple(call("app", t) for t in templates),
    )


def elements_of(result) -> set[tuple[str, ...]]:
    return {p.elements for p in result.patterns}


# --- support ---


def test_support_counts_distinct_tasks_not_episodes():
    """Three episodes of one task give support 1.

    Mutation: counting episodes. The pattern would show support 3 and clear a
    threshold of 3 on the strength of one task repeated.
    """
    sequences = [
        sequence(1, "gorev-a", "x", "y"),
        sequence(2, "gorev-a", "x", "y"),
        sequence(3, "gorev-a", "x", "y"),
    ]
    assert mine_patterns(sequences, min_support=2, max_gap=0).patterns == []

    result = mine_patterns(sequences, min_support=1, max_gap=0)
    assert ("GET app.x", "GET app.y") in elements_of(result)
    assert next(p for p in result.patterns if p.length == 2).support == 1


def test_two_tasks_reach_support_two():
    sequences = [sequence(1, "gorev-a", "x", "y"), sequence(2, "gorev-b", "x", "y")]
    result = mine_patterns(sequences, min_support=2, max_gap=0)
    assert ("GET app.x", "GET app.y") in elements_of(result)


# --- the gap constraint ---


def test_zero_gap_means_strictly_adjacent():
    """`x ? y` does not contain the pattern `x y` when the gap is zero.

    Mutation: an off-by-one in the window bound. Every support in the corpus
    moves and no test but this one notices.

    The skipped symbol differs between the two sequences on purpose. With the
    same symbol in both, `x z y` would itself be a pattern of equal support and
    the closure filter would drop `x y` — a correct result that would look like
    a gap failure. The first version of this test made exactly that mistake.
    """
    sequences = [sequence(1, "gorev-a", "x", "p", "y"), sequence(2, "gorev-b", "x", "q", "y")]
    assert ("GET app.x", "GET app.y") not in elements_of(
        mine_patterns(sequences, min_support=2, max_gap=0)
    )
    assert ("GET app.x", "GET app.y") in elements_of(
        mine_patterns(sequences, min_support=2, max_gap=1)
    )


def test_the_gap_is_counted_between_elements_not_from_the_start():
    """Two skipped calls need `max_gap=2`, not `max_gap=1`."""
    sequences = [
        sequence(1, "gorev-a", "x", "p", "p", "y"),
        sequence(2, "gorev-b", "x", "q", "q", "y"),
    ]
    assert ("GET app.x", "GET app.y") not in elements_of(
        mine_patterns(sequences, min_support=2, max_gap=1)
    )
    assert ("GET app.x", "GET app.y") in elements_of(
        mine_patterns(sequences, min_support=2, max_gap=2)
    )


# --- closure ---


def test_a_prefix_with_the_same_support_is_dropped():
    """`x y` and `x y z` both have support 2, so only the longer is reported.

    Mutation: skipping the closure filter. The report fills with prefixes of one
    finding and the skill count looks several times larger than it is.
    """
    sequences = [
        sequence(1, "gorev-a", "x", "y", "z"),
        sequence(2, "gorev-b", "x", "y", "z"),
    ]
    found = elements_of(mine_patterns(sequences, min_support=2, max_gap=0))
    assert ("GET app.x", "GET app.y", "GET app.z") in found
    assert ("GET app.x", "GET app.y") not in found


def test_a_prefix_with_higher_support_is_kept():
    """Closure drops at equal support only.

    Here `x y` holds in both tasks but `x y z` only in one, so the short pattern
    is a finding in its own right. Mutation: dropping any pattern that has a
    superpattern, regardless of support — that deletes real findings.
    """
    sequences = [
        sequence(1, "gorev-a", "x", "y", "z"),
        sequence(2, "gorev-b", "x", "y"),
    ]
    found = elements_of(mine_patterns(sequences, min_support=2, max_gap=0))
    assert ("GET app.x", "GET app.y") in found


# --- length ---


def test_single_calls_are_not_patterns():
    """The minimum length is two (`06-skill-language.tr.md`)."""
    sequences = [sequence(1, "gorev-a", "x"), sequence(2, "gorev-b", "x")]
    assert mine_patterns(sequences, min_support=2, max_gap=0).patterns == []


def test_a_repeated_symbol_can_form_a_pattern_with_itself():
    """`x x` is a legitimate pattern; the alphabet has no uniqueness rule.

    It matters because the recorded corpus has episodes that call the same
    endpoint repeatedly, and the miner must not silently collapse them.
    """
    sequences = [sequence(1, "gorev-a", "x", "x"), sequence(2, "gorev-b", "x", "x")]
    assert ("GET app.x", "GET app.x") in elements_of(
        mine_patterns(sequences, min_support=2, max_gap=0)
    )


# --- the guards report themselves ---


def test_a_bound_that_binds_is_reported():
    """A truncated search must never be reported as a complete one."""
    sequences = [
        sequence(1, "gorev-a", *(["x"] * 30)),
        sequence(2, "gorev-b", *(["x"] * 30)),
    ]
    result = mine_patterns(sequences, min_support=2, max_gap=0, max_length=4)
    assert result.hit_max_length
    assert result.guarded


def test_an_unbounded_search_says_so():
    sequences = [sequence(1, "gorev-a", "x", "y"), sequence(2, "gorev-b", "x", "y")]
    result = mine_patterns(sequences, min_support=2, max_gap=0)
    assert not result.guarded


# --- the alphabet ---


def test_the_alphabet_element_carries_method_app_and_template():
    """Three calls that differ only in method are three symbols.

    `GET messages/text/{id}` and `POST messages/text/{phone}` are different
    operations on the same path (S-36). Collapsing them would merge a read and a
    write into one pattern element.
    """
    assert call("phone", "messages/text/{id}", "GET").element != (
        call("phone", "messages/text/{id}", "POST").element
    )
    assert call("venmo", "transactions").element != call("spotify", "transactions").element


def test_a_path_parameter_becomes_an_argument_not_a_new_symbol():
    """`notes/3084` and `notes/3085` are one symbol with different arguments.

    Mutation: mining over concrete paths. Every pattern would have support 1 and
    the compiler would return nothing, which reads as "there is nothing here"
    rather than "the alphabet is wrong".
    """
    first = call_from_action("simple_note", "notes/3084", "PATCH", json.dumps({"title": "a"}))
    second = call_from_action("simple_note", "notes/3085", "PATCH", json.dumps({"title": "b"}))
    assert first.element == second.element == "PATCH simple_note.notes/{note_id}"
    assert first.arguments == {"note_id": "3084", "title": "a"}
    assert second.arguments == {"note_id": "3085", "title": "b"}


def test_the_session_token_is_not_an_argument():
    """`access_token` changes on every login and appears in nearly every body.

    Left in, it is a free parameter in every skill and every signature starts
    with it.
    """
    recorded = call_from_action(
        "venmo", "transactions", "POST", json.dumps({"access_token": "abc", "amount": 20})
    )
    assert recorded.arguments == {"amount": 20}


def test_the_log_and_the_database_produce_the_same_call():
    """Two entry points, one answer.

    The miner reads the database; other tools read `api_calls.jsonl`. If the two
    disagreed, a measurement taken from the log would not describe the library
    built from the database.
    """
    from_db = call_from_action(
        "simple_note", "notes/3084", "PATCH", json.dumps({"title": "a", "access_token": "x"})
    )
    from_log = call_from_log(
        {
            "method": "patch",
            "url": "/simple_note/notes/3084",
            "data": {"title": "a", "access_token": "x"},
        }
    )
    assert from_db == from_log


# --- what counts as an effect ---


def sequence_with_steps(episode_id, task_id, templates, step_ids, deltas, observations=()):
    return EpisodeSequence(
        episode_id=episode_id,
        task_id=task_id,
        calls=tuple(call("app", t, "POST") for t in templates),
        step_ids=tuple(step_ids),
        step_call_counts=tuple(step_ids.count(s) for s in step_ids),
        step_deltas=deltas,
        observations=tuple(observations),
    )


def test_the_scaffolds_completion_call_is_not_an_effect():
    """`POST supervisor.message` is `complete_task` (K-78).

    It ends the episode and changes nothing in the world. Every episode has it,
    it is app-independent, and it has no irrelevant version — so an
    irrelevant-retrieval control could not separate the gain credited to it.

    Mutation: dropping it from `SCAFFOLD_CONTROL_CALLS`. Measured consequence:
    at gap 2 / support 3, five of six mined skills were patterns whose only
    effect was this call.
    """
    sequences = [
        EpisodeSequence(
            episode_id=1,
            task_id="g",
            calls=(RecordedCall("supervisor", "message", "POST", {}),),
        )
    ]
    write_set = {("supervisor", "message", "POST"): ("supervisor",)}
    assert effect_elements(sequences, write_set, set()) == set()


def test_login_is_an_effect_for_the_compiler_though_not_a_write_for_the_shield():
    """The two ask different questions and get different answers (K-78).

    The shield exempts session endpoints because reading is unconditionally free
    and logging in is the precondition of reading — a permission statement. The
    compiler asks whether a call achieved something, and logging in produces the
    token the following calls need.

    Mutation: reusing the shield's write set unchanged. Measured consequence:
    the whole login family drops out of the library and lands among the
    discovery prefixes, which is the family the corpus most supports.
    """
    sequences = [
        EpisodeSequence(
            episode_id=1,
            task_id="g",
            calls=(RecordedCall("venmo", "auth/token", "POST", {}),),
        )
    ]
    write_set: dict = {}  # the shield does not call it a write
    session = {("venmo", "auth/token", "POST")}
    assert effect_elements(sequences, write_set, session) == {"POST venmo.auth/token"}


def test_a_plain_read_is_not_an_effect():
    sequences = [
        EpisodeSequence(
            episode_id=1, task_id="g", calls=(RecordedCall("venmo", "transactions", "GET", {}),)
        )
    ]
    assert effect_elements(sequences, {}, set()) == set()


# --- postcondition attribution ---


def test_only_single_call_steps_are_attributed():
    """A delta from a step that made several calls cannot be assigned (K-79)."""
    sequence = sequence_with_steps(
        1, "g", ["write"], step_ids=[10, 10], deltas={10: {"app.Model": 1}}
    )
    # Both calls sit in step 10, so nothing is attributable.
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(call("app", "write", "POST"), call("app", "other", "POST")),
        step_ids=(10, 10),
        step_call_counts=(2, 2),
        step_deltas={10: {"app.Model": 1}},
    )
    assert occurrence_postcondition((0, 1), sequence, (0,)) is None


def test_an_unattributable_effect_call_is_not_read_as_no_change():
    """The correction that this project has had to make before.

    First version: an occurrence counted as measured if *any* of its steps was
    isolated. Measured consequence — in one supporting episode the effect call
    sat in a three-call step while the scaffold's completion call sat alone, so
    the occurrence was ruled measurable, contributed `{}`, and emptied an
    intersection that four other occurrences agreed on.

    Zero difference on its own is not evidence.
    """
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(call("app", "write", "POST"), call("app", "done", "POST")),
        # The effect call shares its step; the second call is alone and changed
        # nothing.
        step_ids=(10, 11),
        step_call_counts=(3, 1),
        step_deltas={10: {"app.Model": 3}, 11: {}},
    )
    assert occurrence_postcondition((0, 1), sequence, (0,)) is None


def test_an_isolated_effect_call_gives_its_shape():
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(call("app", "write", "POST"), call("app", "done", "POST")),
        step_ids=(10, 11),
        step_call_counts=(1, 1),
        step_deltas={10: {"app.Model": 1, "app.Note": -2}, 11: {}},
    )
    assert occurrence_postcondition((0, 1), sequence, (0,)) == {
        "app.Model": "+",
        "app.Note": "-",
    }


def test_the_shape_carries_direction_not_magnitude():
    """`+1` and `+7` are the same claim (`SKILL_SPEC.md`).

    Magnitude follows a free parameter whenever the skill has one, so a
    magnitude claim would hold in no supporting episode at all.
    """
    one = EpisodeSequence(
        episode_id=1,
        task_id="a",
        calls=(call("app", "write", "POST"),),
        step_ids=(10,),
        step_call_counts=(1,),
        step_deltas={10: {"app.Model": 1}},
    )
    seven = EpisodeSequence(
        episode_id=2,
        task_id="b",
        calls=(call("app", "write", "POST"),),
        step_ids=(20,),
        step_call_counts=(1,),
        step_deltas={20: {"app.Model": 7}},
    )
    assert pattern_postcondition(
        ("POST app.write",), [one, seven], {1, 2}, max_gap=0, effect_indices=(0,)
    ) == {"app.Model": "+"}


def test_an_unmeasured_step_is_not_an_empty_delta():
    """A step with no `state_change` row was not measured.

    Mutation: defaulting a missing delta to `{}`. The postcondition would then
    read "measured, nothing changed" off an episode where the probe never ran.
    """
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(call("app", "write", "POST"),),
        step_ids=(10,),
        step_call_counts=(1,),
        step_deltas={},  # not measured
    )
    assert occurrence_postcondition((0,), sequence, (0,)) is None


# --- binding ---


def test_a_value_printed_by_an_earlier_step_is_bound():
    """Binding is looked for in what the agent saw, because the response body is
    not persisted. Weaker than structural matching, and one-directional."""
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(
            RecordedCall("supervisor", "account_passwords", "GET", {}),
            RecordedCall("venmo", "auth/token", "POST", {"password": "hunter2000"}),
        ),
        step_ids=(10, 11),
        step_call_counts=(1, 1),
        observations=((10, '[{"password": "hunter2000"}]'), (11, "ok")),
    )
    classes = classify_arguments(
        ("GET supervisor.account_passwords", "POST venmo.auth/token"),
        [sequence],
        {1},
        max_gap=0,
        constant_threshold=1,
    )
    assert classes.bound == {1: {"password"}}
    assert "1.password" not in classes.free


def test_a_value_never_printed_looks_free():
    """The declared blind spot, stated as a test so it is not mistaken for a bug.

    A value the agent used without printing is indistinguishable from one it
    invented. The error runs one way — under-detection — and the fix is
    persisting the response body, which is the v1 path (S-40).
    """

    def unprinted(episode_id: int, task_id: str, password: str) -> EpisodeSequence:
        return EpisodeSequence(
            episode_id=episode_id,
            task_id=task_id,
            calls=(
                RecordedCall("supervisor", "account_passwords", "GET", {}),
                RecordedCall("venmo", "auth/token", "POST", {"password": password}),
            ),
            step_ids=(episode_id * 10, episode_id * 10 + 1),
            step_call_counts=(1, 1),
            observations=((episode_id * 10, "(nothing printed)"), (episode_id * 10 + 1, "ok")),
        )

    sequences = [unprinted(1, "gorev-a", "hunter2000"), unprinted(2, "gorev-b", "swordfish9")]
    classes = classify_arguments(
        ("GET supervisor.account_passwords", "POST venmo.auth/token"),
        sequences,
        {1, 2},
        max_gap=0,
        constant_threshold=1,
    )
    assert classes.bound == {}
    assert "1.password" in classes.free


def test_a_short_value_is_never_called_bound():
    """`1` and `on` appear in every observation.

    Without the length floor every small argument would be classified as bound
    and the signatures would come out empty.
    """
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="g",
        calls=(
            RecordedCall("app", "read", "GET", {}),
            RecordedCall("app", "write", "POST", {"count": 1}),
        ),
        step_ids=(10, 11),
        step_call_counts=(1, 1),
        observations=((10, "1 1 1 1 1"), (11, "ok")),
    )
    classes = classify_arguments(
        ("GET app.read", "POST app.write"), [sequence], {1}, max_gap=0, constant_threshold=1
    )
    assert classes.bound == {}


# --- the scaffold's control channel is not a body element either ---


def test_the_completion_call_cannot_appear_inside_a_skill():
    """A skill body carrying `complete_task` would end the episode (K-80).

    Invoking it would finish the task, and invoking it early would file a wrong
    completion. A skill carries work, not control flow.

    Mutation: excluding the call from the effect suffix but leaving it in the
    body. Measured consequence: the one environment-action pattern in the corpus
    was `payment_requests` followed by the completion call, and it would go into
    the library as a skill that ends the episode.
    """
    sequences = [
        EpisodeSequence(
            episode_id=1,
            task_id="gorev-a",
            calls=(
                RecordedCall("venmo", "payment_requests", "POST", {}),
                RecordedCall("supervisor", "message", "POST", {}),
            ),
        ),
        EpisodeSequence(
            episode_id=2,
            task_id="gorev-b",
            calls=(
                RecordedCall("venmo", "payment_requests", "POST", {}),
                RecordedCall("supervisor", "message", "POST", {}),
            ),
        ),
    ]
    excluded = scaffold_control_elements(sequences)
    assert excluded == {"POST supervisor.message"}

    result = mine_patterns(sequences, min_support=2, max_gap=0, excluded_elements=excluded)
    assert all("POST supervisor.message" not in p.elements for p in result.patterns)
    # And with only one call left, nothing reaches the minimum length of two.
    assert result.patterns == []


def test_an_excluded_call_still_counts_towards_the_gap():
    """It is removed from patterns, not from the sequence.

    Mutation: dropping the call from the sequence instead of from the alphabet.
    Then its neighbours become adjacent, and a pattern that really had a call
    between its two elements would be mined at `max_gap=0`. Gaps have to be
    measured over what actually happened.
    """
    sequences = [
        EpisodeSequence(
            episode_id=n,
            task_id=f"gorev-{n}",
            calls=(
                RecordedCall("app", "x", "GET", {}),
                RecordedCall("supervisor", "message", "POST", {}),
                RecordedCall("app", "y", "GET", {}),
            ),
        )
        for n in (1, 2)
    ]
    excluded = scaffold_control_elements(sequences)
    at_zero = mine_patterns(sequences, min_support=2, max_gap=0, excluded_elements=excluded)
    assert at_zero.patterns == [], "the skipped call was not counted towards the gap"

    at_one = mine_patterns(sequences, min_support=2, max_gap=1, excluded_elements=excluded)
    assert ("GET app.x", "GET app.y") in elements_of(at_one)


# --- merging ---


def merged_pattern(elements, tasks) -> Pattern:
    pattern = Pattern(elements=tuple(elements))
    pattern.tasks = set(tasks)
    return pattern


def test_patterns_sharing_an_effect_suffix_become_one_skill():
    """The rule from `06-skill-language.tr.md`: same effect suffix, same skill.

    Mutation: not merging. Measured consequence: forty mined patterns at the
    lead configuration, thirty-nine of them the same four logins reached through
    different documentation reads. The count would be an artefact of how many
    prefixes happened to be recorded.
    """
    effects = {"POST venmo.auth/token"}
    patterns = [
        merged_pattern(["GET api_docs.api_doc", "POST venmo.auth/token"], {"a", "b"}),
        merged_pattern(["GET supervisor.passwords", "POST venmo.auth/token"], {"b", "c"}),
    ]
    skills = merge_by_effect_suffix(patterns, effects)
    assert len(skills) == 1
    assert skills[0].effect_suffix == ("POST venmo.auth/token",)


def test_the_merged_support_is_the_union_of_the_members():
    """Two prefixes covering different tasks both count.

    Mutation: taking the maximum instead. The claim is that the effect suffix
    occurred in that many tasks, and the maximum understates it.
    """
    effects = {"POST venmo.auth/token"}
    patterns = [
        merged_pattern(["GET a", "POST venmo.auth/token"], {"gorev-1", "gorev-2"}),
        merged_pattern(["GET b", "POST venmo.auth/token"], {"gorev-3"}),
    ]
    skills = merge_by_effect_suffix(patterns, effects)
    assert skills[0].support == 3


def test_the_merged_body_is_the_widest_supported_member():
    """Something has to be the body, and it is the least specialised member."""
    effects = {"POST venmo.auth/token"}
    narrow = merged_pattern(["GET rare", "POST venmo.auth/token"], {"gorev-1"})
    wide = merged_pattern(["GET common", "POST venmo.auth/token"], {"a", "b", "c"})
    skills = merge_by_effect_suffix([narrow, wide], effects)
    assert skills[0].body == ("GET common", "POST venmo.auth/token")


def test_merging_is_deterministic_whatever_the_input_order():
    """The compiler must produce the same library from the same recording."""
    effects = {"POST venmo.auth/token"}
    one = merged_pattern(["GET a", "POST venmo.auth/token"], {"g1", "g2"})
    two = merged_pattern(["GET b", "POST venmo.auth/token"], {"g1", "g2"})
    forwards = merge_by_effect_suffix([one, two], effects)
    backwards = merge_by_effect_suffix([two, one], effects)
    assert forwards[0].body == backwards[0].body


def test_different_effect_suffixes_stay_separate():
    """Sequences that reach the same goal by different effects stay apart in v1
    (`06-skill-language.tr.md`)."""
    effects = {"POST venmo.transactions", "POST venmo.payment_requests"}
    patterns = [
        merged_pattern(["GET a", "POST venmo.transactions"], {"g1", "g2"}),
        merged_pattern(["GET a", "POST venmo.payment_requests"], {"g3", "g4"}),
    ]
    assert len(merge_by_effect_suffix(patterns, effects)) == 2


def test_the_effect_suffix_is_the_effects_themselves_not_the_tail():
    """A trailing read is how the pattern was recorded, not what it achieves.

    Mutation: taking the span from the first effect to the end of the pattern.
    Then `[auth, api_doc]` and `[auth]` would be two skills, and the merge would
    barely reduce anything.
    """
    effects = {"POST venmo.auth/token"}
    with_tail = merged_pattern(
        ["GET api_docs.api_doc", "POST venmo.auth/token", "GET api_docs.api_doc"], {"g1"}
    )
    without = merged_pattern(["GET api_docs.api_doc", "POST venmo.auth/token"], {"g2"})
    skills = merge_by_effect_suffix([with_tail, without], effects)
    assert len(skills) == 1
    assert skills[0].support == 2


def test_a_pattern_with_no_effect_is_not_a_skill_at_all():
    """Discovery prefixes never reach the merge (K-75)."""
    patterns = [merged_pattern(["GET a", "GET b"], {"g1", "g2"})]
    assert merge_by_effect_suffix(patterns, set()) == []


# --- binding is looked for inside the body only ---


def test_a_value_produced_outside_the_body_is_not_bound():
    """`06-skill-language.tr.md`: the value appears in an earlier call *in the
    sequence*, and the sequence is the skill's own body (S-42).

    Here the credentials come from a call the pattern skipped. The compiled
    skill executes atomically, so that call never runs and the value is not
    available. It belongs in the signature.

    Mutation: searching the whole episode prefix. Measured consequence: all four
    arguments of the venmo login skill were classified as bound, including the
    password, and the skill would have been compiled with no parameters at all
    while being unable to obtain any of them.
    """
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="gorev-a",
        calls=(
            RecordedCall("supervisor", "account_passwords", "GET", {}),
            RecordedCall("api_docs", "api_doc", "GET", {}),
            RecordedCall("venmo", "auth/token", "POST", {"password": "hunter2000"}),
        ),
        step_ids=(10, 11, 12),
        step_call_counts=(1, 1, 1),
        observations=((10, '{"password": "hunter2000"}'), (11, "docs"), (12, "ok")),
    )
    # The pattern is the last two calls; the credential read is not in it.
    classes = classify_arguments(
        ("GET api_docs.api_doc", "POST venmo.auth/token"),
        [sequence],
        {1},
        max_gap=1,
        constant_threshold=99,
    )
    assert classes.bound == {}
    assert "1.password" in classes.free


def test_a_value_produced_inside_the_body_is_bound():
    """The counterweight: the same value, with the producing call in the body."""
    sequence = EpisodeSequence(
        episode_id=1,
        task_id="gorev-a",
        calls=(
            RecordedCall("supervisor", "account_passwords", "GET", {}),
            RecordedCall("venmo", "auth/token", "POST", {"password": "hunter2000"}),
        ),
        step_ids=(10, 11),
        step_call_counts=(1, 1),
        observations=((10, '{"password": "hunter2000"}'), (11, "ok")),
    )
    classes = classify_arguments(
        ("GET supervisor.account_passwords", "POST venmo.auth/token"),
        [sequence],
        {1},
        max_gap=0,
        constant_threshold=99,
    )
    assert classes.bound == {1: {"password"}}
    assert "1.password" not in classes.free
