"""The stopping rule and the state fingerprint.

The rule was born from two measured faults, and the second broke the first one's
fix.

First fault: the 1.5B repeats the same login with the wrong password for twenty
steps and gets a 401 every time. A criterion that looked at the call count would
take that for progress.

Second fault: one episode made 736 calls over 150 steps, every one returned 200,
the database never changed once, and the rule saying "a successful call is
progress" never fired (S-25). That episode went to the same three endpoints on
every step.

The new criterion runs over the concrete call set: if verifiable state did not
change and no call was made that had not been made before, the step made no
progress.

The identity is the concrete call, not the route template. The template was tried
and eliminated by measurement: episode `8ce6779_2` reads comments 117 times under
different ids and writes them all at the end, and it passes; under template
identity it looked stalled for 107 steps.

A third fault came out of these tests themselves and shaped them (S-32). The rule
read `app` and `api` keys off the actions; `api_calls.jsonl` rows carry no such
keys, only `method`, `url` and `data`. The fake steps here used the same invented
shape, so the tests passed and the criterion never worked. That is why the steps
are now built in the real log shape and the endpoint set is computed with the
production function itself. That the shape matches reality is checked against
recorded logs in `tests/test_api_routes.py`.

The tests run on fake steps; they need neither a model nor AppWorld.
"""

from __future__ import annotations

import pytest

from zihin.recording_agent import (
    NoProgress,
    RecordingAgent,
    step_endpoints,
    step_progress_identities,
    step_raw_urls,
    step_resources,
)
from zihin.state_probe import diff, snapshot


def _agent(limit: int | None = 3) -> RecordingAgent:
    agent = RecordingAgent.__new__(RecordingAgent)
    agent.no_progress_limit = limit
    agent.steps = []
    agent.stop_reason = None
    return agent


def _step(*, state=None, calls=(), data=None) -> dict:
    """A step. `calls` is a URL list in the real `api_calls.jsonl` shape.

    `captured` is None so the capture-less branch is exercised. The identity set
    is computed with the production `step_progress_identities`, not with the
    test's own arithmetic.
    """
    step = {
        "state_delta": state,
        "captured": None,
        "actions": [{"method": "get", "url": u, "data": data or {}} for u in calls],
    }
    step["progress_identities"] = step_progress_identities(step)
    step["endpoints"] = step_endpoints(step)
    step["resources"] = step_resources(step)
    step["raw_urls"] = step_raw_urls(step)
    return step


def _run(agent: RecordingAgent, steps: list[dict]) -> None:
    for step in steps:
        agent.steps.append(step)
        agent._check_progress()


def test_state_change_counts_as_progress():
    agent = _agent()
    assert not agent._made_no_progress(_step(state={"spotify.Song": 1}), set())


def _identity(*calls, data=None) -> set[str]:
    """The set seen: the identity production makes, not a string the test wrote by hand."""
    return step_progress_identities(_step(calls=calls, data=data))


def test_new_call_counts_as_progress():
    agent = _agent()
    step = _step(calls=["/spotify/library/playlists"])
    assert not agent._made_no_progress(step, _identity("/spotify/auth/token"))


def test_already_made_call_is_not_progress():
    agent = _agent()
    step = _step(calls=["/spotify/library/playlists"])
    assert agent._made_no_progress(step, _identity("/spotify/library/playlists"))


def test_no_action_and_no_change_is_not_progress():
    agent = _agent()
    assert agent._made_no_progress(_step(), set())


def test_repeated_failing_login_is_caught():
    """The first fault: the same wrong login, over and over."""
    agent = _agent(limit=3)
    steps = [_step(calls=["/venmo/auth/token"]) for _ in range(4)]
    with pytest.raises(NoProgress):
        _run(agent, steps)
    assert agent.stop_reason == "no_progress"


def test_successful_reads_of_the_same_endpoints_are_caught():
    """The second fault: 736 successful calls, zero state change, three endpoints.

    The old rule did not fire here, because every step had a successful call.
    """
    agent = _agent(limit=3)
    endpoints = [
        "/spotify/auth/token",
        "/supervisor/account_passwords",
        "/spotify/library/playlists",
    ]
    with pytest.raises(NoProgress):
        _run(agent, [_step(calls=endpoints) for _ in range(5)])


def test_genuine_exploration_is_not_caught():
    """An episode that reaches a new endpoint on every step is not cut."""
    agent = _agent(limit=3)
    real_endpoints = [
        "/spotify/auth/token",
        "/spotify/library/playlists",
        "/spotify/library/songs",
        "/spotify/albums",
        "/spotify/artists",
        "/spotify/genres",
        "/spotify/liked_songs",
        "/spotify/downloaded_songs",
        "/spotify/following_artists",
        "/spotify/payment_cards",
    ]
    _run(agent, [_step(calls=[u]) for u in real_endpoints])
    assert agent.stop_reason is None


def test_pagination_survives_a_generous_threshold():
    """Legitimate pagination completes under a generous threshold.

    Five pagination steps against the same endpoint are not cut when the threshold
    is fifteen.
    """
    agent = _agent(limit=15)
    steps = [_step(calls=["/spotify/library/playlists"]) for _ in range(6)]
    _run(agent, steps)
    assert agent.stop_reason is None


def test_threshold_spares_the_longest_successful_stagnation():
    """False-positive calibration, against a measured case.

    Among the boundary control's 30 complete trajectories, the longest stall of
    the 20 that passed is 36 (`8ce6779_2`). The threshold in the configuration is
    40; the lowest safe value is 37. If the threshold drops to 36 or below that
    episode is cut and this test fails.
    """
    agent = _agent(limit=40)
    fixed = ["/todoist/tasks/2851/comments"]
    _run(agent, [_step(calls=fixed) for _ in range(37)])
    assert agent.stop_reason is None, "a 36-step stall must not cut a success"

    agent = _agent(limit=36)
    with pytest.raises(NoProgress):
        _run(agent, [_step(calls=fixed) for _ in range(37)])


def test_progress_resets_the_window():
    agent = _agent(limit=3)
    steps = [
        _step(calls=["/venmo/auth/token"]),
        _step(calls=["/venmo/auth/token"]),
        _step(state={"spotify.Song": 1}, calls=["/venmo/auth/token"]),
        _step(calls=["/venmo/auth/token"]),
    ]
    _run(agent, steps)
    assert agent.stop_reason is None, "an intervening progress step must reset the window"


def test_rule_fires_only_after_the_limit():
    """The first step reaches a new endpoint so it is progress; the stall starts at the second."""
    steps = [_step(calls=["/venmo/auth/token"]) for _ in range(4)]

    agent = _agent(limit=3)
    _run(agent, steps[:3])
    assert agent.stop_reason is None, "there are only two stalled steps in three"

    agent = _agent(limit=3)
    with pytest.raises(NoProgress):
        _run(agent, steps)


def test_rule_is_off_when_limit_is_none():
    agent = _agent(limit=None)
    _run(agent, [_step() for _ in range(10)])
    assert agent.stop_reason is None


def test_long_read_only_enumeration_is_not_cut():
    """The measured case: `8ce6779_2`. It reads under different ids and writes at
    the end.

    The mutation this test kills is going back to the route template. Under
    template identity the ten steps below collapse to one endpoint and a threshold
    of three cuts them; under concrete identity every step is a new call, so
    nothing is cut.
    """
    agent = _agent(limit=3)
    steps = [_step(calls=[f"/todoist/tasks/{2851 + i}/comments"]) for i in range(10)]
    _run(agent, steps)
    assert agent.stop_reason is None, "reading a different resource is progress"


def test_repeating_the_same_concrete_call_is_still_caught():
    """What separates the S-25 case: the same three **concrete** calls, always.

    Measured: that episode makes all 736 calls to the same three concrete paths
    and its stall is 146. So the concrete identity still catches the pathology.
    """
    agent = _agent(limit=3)
    fixed = ["/todoist/tasks/2851/comments", "/todoist/projects/9/tasks"]
    with pytest.raises(NoProgress):
        _run(agent, [_step(calls=fixed) for _ in range(5)])


def test_parameters_are_part_of_the_identity():
    """Same path, different parameters: a different call.

    Going to the same endpoint with a different query brings back new information.
    The mutation this test kills is dropping the parameters from the identity.
    """
    agent = _agent(limit=3)
    first = _step(calls=["/todoist/tasks"], data={"project_id": 1})
    second = _step(calls=["/todoist/tasks"], data={"project_id": 2})
    assert agent._progress_identities(first) != agent._progress_identities(second)
    assert not agent._made_no_progress(second, agent._progress_identities(first))


def test_identity_serialisation_is_order_independent():
    """Parameter order must not change the identity.

    `insert_action` writes with `sort_keys=True`; the identity has to be produced
    the same way, otherwise the calibration tool builds a different identity from
    the database and the two paths drift apart in silence.
    """
    a = _step(calls=["/todoist/tasks"], data={"a": 1, "b": 2})
    b = _step(calls=["/todoist/tasks"], data={"b": 2, "a": 1})
    assert step_progress_identities(a) == step_progress_identities(b)


def test_operation_and_object_counts_separate_exploration_from_repetition():
    """The ratio of object count to operation count is diagnostic, and it is
    recorded per episode.

    Two measured cases: `8ce6779_2` at 27 objects / 9 operations = 3.0 is
    exploration; S-25's episode at 3 objects / 3 operations = 1.0 is repetition.
    Choosing the concrete call as the identity rests on this distinction (K-63).
    """
    agent = _agent()
    agent.steps = [_step(calls=[f"/todoist/tasks/{2851 + i}/comments"]) for i in range(6)]
    assert len(agent.endpoints) == 1, "every row is the same operation"
    assert len(agent.resources) == 6, "six distinct objects"

    agent = _agent()
    agent.steps = [_step(calls=["/todoist/tasks/2851/comments"]) for _ in range(6)]
    assert len(agent.endpoints) == 1
    assert len(agent.resources) == 1, "yineleme: tek resource"


def test_collapse_detector_needs_no_call_count():
    """The health check: with distinct raw URLs but a single identity left,
    something has collapsed.

    A check that looked at the call count would never fire on the preflight
    episode; that episode makes only two calls in three steps.
    """
    agent = _agent(limit=3)
    agent.steps = [_step(calls=["/venmo/friends/a@x.com", "/venmo/transactions/7"])]
    assert not agent.identity_collapsed

    agent.steps[0]["progress_identities"] = {"None.None|{}"}
    assert agent.identity_collapsed, "13 distinct URLs had collapsed to one identity (S-32)"


def test_rule_reads_the_same_actions_the_database_records():
    """S-32's direct sentry.

    The identity set the rule sees has to derive from the action rows written to
    the database. If the two paths separate, the rule can fall idle in silence.
    The identity's shape is pinned here as well, because the calibration tool
    rebuilds the same shape from the database.
    """
    from zihin.recording_agent import _action_rows

    agent = _agent(limit=3)
    step = _step(calls=["/venmo/transactions/42", "/spotify/library/playlists"])
    rows = _action_rows(step)
    assert [s["app"] for s in rows] == ["venmo", "spotify"]
    assert [s["api"] for s in rows] == ["transactions/42", "library/playlists"]
    assert agent._progress_identities(step) == {
        "venmo.transactions/42|{}",
        "spotify.library/playlists|{}",
    }


def test_missing_mandatory_key_raises():
    """A missing mandatory field must raise, not become None in silence.

    That was S-32's class: `.get()` turned a missing key into None and the
    criterion ran idle for months.
    """
    from zihin.recording_agent import _action_rows

    with pytest.raises(KeyError):
        _action_rows({"captured": None, "actions": [{"method": "get", "data": {}}]})


class FakeModel:
    def __init__(self, count: int):
        self._count = count

    def count(self) -> int:
        return self._count


class FakeApp:
    def __init__(self, **models):
        for name, count in models.items():
            setattr(self, name, FakeModel(count))


class FakeCollection:
    def __init__(self, **apps):
        for name, uyg in apps.items():
            setattr(self, name, uyg)


class FakeWorld:
    def __init__(self, collection):
        self.models = collection


def test_snapshot_counts_rows_per_model():
    world = FakeWorld(FakeCollection(spotify=FakeApp(Song=10, Album=3)))
    assert snapshot(world) == {"spotify.Song": 10, "spotify.Album": 3}


def test_snapshot_skips_infrastructure_apps():
    """`admin` and `api_docs` are used by the framework on every task."""
    world = FakeWorld(FakeCollection(spotify=FakeApp(Song=1), admin=FakeApp(User=5)))
    assert snapshot(world) == {"spotify.Song": 1}


def test_diff_reports_only_changed_models():
    assert diff({"a.B": 1, "a.C": 2}, {"a.B": 2, "a.C": 2}) == {"a.B": 1}


def test_diff_reports_deletions_as_negative():
    assert diff({"a.B": 5}, {"a.B": 3}) == {"a.B": -2}


def test_diff_ignores_unmeasurable_models():
    """An uncountable model is marked with -1; it must not be taken for unchanged."""
    assert diff({"a.B": -1}, {"a.B": -1}) == {}
    assert diff({"a.B": -1}, {"a.B": 5}) == {}
