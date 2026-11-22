"""The two distinctions that carry the demo usage measurement.

Both come from a fact found during the measurement and both can give a wrong
answer in silence.

**A successful effect and an effect are not the same thing.** In the baseline
run `POST simple_note.auth/token` occurs twice and both are `401`: same endpoint,
same method, no token. Counted as "reached the effect", the place where the card
helped and the place where it did not look identical.

**The body match is searched under the gap constraint the card was produced
with.** The search is the compiler's `occurrences_of`; the tests here pin that
the demo **calls** it correctly, not the search itself (`test_compiler.py`
checks that).

The script is not a module, so it is loaded by path. The logic that carries the
measurement comes from production code and only the demo own wrappers are
checked here.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "measure_card_demo", pathlib.Path("scripts/setup/measure_card_demo.py")
)
demo = importlib.util.module_from_spec(_SPEC)
sys.modules["measure_card_demo"] = demo
_SPEC.loader.exec_module(demo)

from zihin.compiler import EpisodeSequence, RecordedCall  # noqa: E402


def _calls(*rows: tuple[int, str, str | None]) -> list[dict]:
    return [{"step": step, "call": call, "status": status} for step, call, status in rows]


def _sequence(*elements: str) -> EpisodeSequence:
    calls = tuple(
        RecordedCall(
            app=e.split(" ", 1)[1].split(".", 1)[0],
            template=e.split(".", 1)[1],
            method=e.split(" ", 1)[0],
            arguments=(),
        )
        for e in elements
    )
    return EpisodeSequence(
        episode_id=0,
        task_id="",
        calls=calls,
        step_ids=tuple(range(1, len(calls) + 1)),
        step_call_counts=tuple(1 for _ in calls),
        step_deltas={},
        observations=(),
    )


# --- the successful-effect distinction ---


def test_a_failed_call_does_not_count_as_reaching_the_effect():
    """The measured case: the baseline tried to log in twice and both were 401."""
    calls = _calls(
        (3, "GET simple_note.notes", "401"),
        (9, "POST simple_note.auth/token", "401"),
        (10, "POST simple_note.auth/token", "401"),
    )
    assert demo.first_step_of(calls, "POST simple_note.auth/token") == 9
    assert demo.first_step_of(calls, "POST simple_note.auth/token", only_successful=True) is None


def test_the_successful_call_is_found_even_when_a_failed_one_comes_first():
    calls = _calls(
        (4, "POST simple_note.auth/token", "401"),
        (6, "POST simple_note.auth/token", "200"),
    )
    assert demo.first_step_of(calls, "POST simple_note.auth/token") == 4
    assert demo.first_step_of(calls, "POST simple_note.auth/token", only_successful=True) == 6


def test_an_unrecorded_status_is_not_treated_as_success():
    """A NULL status means "not read", not "200"."""
    calls = _calls((2, "POST venmo.auth/token", None))
    assert demo.first_step_of(calls, "POST venmo.auth/token") == 2
    assert demo.first_step_of(calls, "POST venmo.auth/token", only_successful=True) is None


def test_a_call_that_never_happened_has_no_step():
    assert (
        demo.first_step_of(_calls((1, "GET spotify.songs", "200")), "POST spotify.auth/token")
        is None
    )


# --- body matching ---


def test_the_body_matches_when_the_calls_follow_it():
    sequence = _sequence("GET supervisor.account_passwords", "POST spotify.auth/token")
    result = demo.body_appears(
        sequence, ["GET supervisor.account_passwords", "POST spotify.auth/token"], max_gap=2
    )
    assert result["matched"]
    assert result["longest_prefix"] == 2
    assert result["first_occurrence"] == [0, 1]


def test_the_gap_constraint_is_the_compilers_own():
    """The gap is 2, so at most two foreign calls may come in between (K-81)."""
    yakin = _sequence("GET a.x", "GET b.y", "GET c.z", "POST d.w")
    assert demo.body_appears(yakin, ["GET a.x", "POST d.w"], max_gap=2)["matched"]
    uzak = _sequence("GET a.x", "GET b.y", "GET c.z", "GET e.v", "POST d.w")
    assert not demo.body_appears(uzak, ["GET a.x", "POST d.w"], max_gap=2)["matched"]


def test_a_partial_match_is_reported_as_a_prefix_length():
    """Six of a seven-call body matching is not the same as none of it matching."""
    sequence = _sequence("GET supervisor.account_passwords", "GET spotify.songs")
    result = demo.body_appears(
        sequence,
        ["GET supervisor.account_passwords", "POST spotify.auth/token", "GET spotify.songs"],
        max_gap=2,
    )
    assert not result["matched"]
    assert result["longest_prefix"] == 1
    assert result["body_length"] == 3


def test_an_episode_without_calls_matches_nothing():
    """The measured case: on the demo first task both runs produced zero calls."""
    result = demo.body_appears(_sequence(), ["POST simple_note.auth/token"], max_gap=2)
    assert not result["matched"]
    assert result["longest_prefix"] == 0


# --- task selection ---


def test_the_scenario_is_the_task_id_without_its_variant():
    """The selection criterion rests on this: `0a9d82a_1` and `0a9d82a_2` are one scenario."""
    assert "0a9d82a_1".rsplit("_", 1)[0] == "0a9d82a_2".rsplit("_", 1)[0]
    assert "0a9d82a_1".rsplit("_", 1)[0] != "0de03ea_1".rsplit("_", 1)[0]


def test_the_demo_declares_how_many_tasks_it_runs():
    assert demo.TASK_COUNT == 3
    assert demo.MAX_STEPS == 20


@pytest.mark.parametrize("field", ["OUTPUT", "SPLIT", "FULL_CONDITION"])
def test_the_demo_names_its_own_configuration(field):
    assert getattr(demo, field)
