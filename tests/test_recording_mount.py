"""Is the recorder really mounted — in both modes.

**Why this test exists.** The whole project record rested on an implementation
detail nobody knew about. The reference agent calls `world.batch_execute`, not
`world.execute`; in in-process mode `batch_execute` calls `self.execute` for
every code block, so wrapping `execute` was enough. As long as the coincidence
held, nobody noticed.

In remote-environment mode the coincidence broke: `batch_execute` diverts
straight to an HTTP call and `self.execute` is never called. The first sandbox
episode ran, produced a 32 KB trajectory, wrote **zero steps** to the record and
raised no alarm anywhere (S-53).

**What this test pins.** Which method the wrapper attaches to, and that the
method is really called. It runs against a fake world object: no AppWorld
installation, no container and no model are needed, so this part of the
recording path is checked on every run.

**Checked by mutation, and the result is written here.** The two wrappings in
the production code were removed one at a time and the suite was run:

| Mutation | Failing tests |
|---|---|
| `batch_execute` not wrapped in remote mode | 3 |
| `execute` not wrapped in in-process mode | 2 |
| Reverted | 0, all seven pass |

Failing under the remote mutation: `..._wraps_batch_execute`,
`..._refuses_a_multi_code_batch`, `..._captured_calls_reach_the_step...`.
Under the in-process mutation: `..._wraps_execute`,
`..._records_one_step_per_code`.

On top of that, `test_the_mount_is_not_vacuous` checks the never-wrapped state
directly. Without these tests a green suite would stay green with a recorder
that is never mounted at all — which is exactly what happened in S-53.
"""

from __future__ import annotations

from typing import Any

import pytest

from zihin.api_capture import ApiCapture, CapturedCall
from zihin.recording_agent import RecordingAgent


class FakeWorld:
    """As much of AppWorld as the recorder touches.

    It carries both modes: when `remote_environment_url` is set, `batch_execute`
    answers directly and never falls through to `execute` — the behaviour of real
    remote mode. When it is empty, `batch_execute` calls `execute` for every code
    block — the behaviour of real in-process mode.
    """

    def __init__(self, remote: str | None = None) -> None:
        self.remote_environment_url = remote
        self.task_id = "0de03ea_1"
        self.models = None
        self.execute_cagrildi = 0
        self.batch_cagrildi = 0
        self.seen_codes: list[str] = []

    def execute(self, code: str, *args: Any, **kwargs: Any) -> str:
        self.execute_cagrildi += 1
        self.seen_codes.append(code)
        return f"output: {code}"

    def batch_execute(self, codes: list[str], *args: Any, **kwargs: Any) -> list[str]:
        self.batch_cagrildi += 1
        if self.remote_environment_url:
            # Real remote mode: `self.execute` is never called.
            self.seen_codes.extend(codes)
            return [f"output: {code}" for code in codes]
        return [self.execute(code) for code in codes]


def _kaydedici(capture: ApiCapture | None = None) -> RecordingAgent:
    """A `RecordingAgent` built without calling the superclass constructor.

    Constructing the reference scaffold needs a model configuration and a prompt
    file; what is checked here is only the mount, so the object is built directly
    and the recorder's own fields are supplied by hand.
    """
    agent = RecordingAgent.__new__(RecordingAgent)
    agent.experiment_name = "montaj-testi"
    agent.capture = capture
    agent.probe_state = False
    agent.no_progress_limit = None
    agent.log_source = False
    agent.steps = []
    agent.count_divergences = []
    agent.stop_reason = None
    agent._call_log_path = None
    agent._calls_read = 0
    agent.messages = []
    return agent


def _tak(agent: RecordingAgent, world: FakeWorld) -> None:
    """Runs only the wrapping part of `initialize`.

    The superclass `initialize` and the log-path setup are meaningless against a
    fake world; the wrapping itself is what is checked.
    """
    RecordingAgent.initialize(agent, world)


@pytest.fixture(autouse=True)
def _ust_sinifi_ve_yolu_sustur(monkeypatch):
    monkeypatch.setattr(
        "appworld_agents.code.simplified.react_code_agent.SimplifiedReActCodeAgent.initialize",
        lambda self, world: None,
    )
    fake_path = type("FakePath", (), {"experiment_outputs": "/tmp"})()
    monkeypatch.setattr("zihin.recording_agent.path_store", fake_path)


# --- in-process mode ---


def test_the_in_process_mode_wraps_execute():
    world = FakeWorld(remote=None)
    agent = _kaydedici()
    _tak(agent, world)

    world.batch_execute(["print(1)"])

    assert len(agent.steps) == 1
    assert agent.steps[0]["code"] == "print(1)"
    assert world.execute_cagrildi == 1


def test_the_in_process_mode_records_one_step_per_code():
    """In in-process mode `batch_execute` sends each code block to its own
    `execute`, so three blocks are three steps."""
    world = FakeWorld(remote=None)
    agent = _kaydedici()
    _tak(agent, world)

    world.batch_execute(["a", "b", "c"])

    assert len(agent.steps) == 3
    assert [s["code"] for s in agent.steps] == ["a", "b", "c"]


# --- uzak kip ---


def test_the_remote_mode_wraps_batch_execute():
    """The real fault was here: in remote mode `execute` is never called."""
    world = FakeWorld(remote="http://127.0.0.1:8124")
    agent = _kaydedici()
    _tak(agent, world)

    output = world.batch_execute(["print(1)"])

    assert output == ["output: print(1)"]
    assert len(agent.steps) == 1, "no step was recorded in remote mode"
    assert agent.steps[0]["code"] == "print(1)"
    assert world.execute_cagrildi == 0, "execute must not be called in remote mode"


def test_the_remote_mode_refuses_a_multi_code_batch():
    """With more than one code block, which block a call belongs to cannot be
    told apart; failing is right and attributing it wrongly is not."""
    world = FakeWorld(remote="http://127.0.0.1:8124")
    agent = _kaydedici()
    _tak(agent, world)

    with pytest.raises(RuntimeError, match="cannot be told apart"):
        world.batch_execute(["a", "b"])


def test_the_remote_mode_does_not_wrap_execute_as_well():
    """Wrapping both would record every step twice in in-process mode."""
    world = FakeWorld(remote="http://127.0.0.1:8124")
    agent = _kaydedici()
    _tak(agent, world)

    world.execute("dogrudan")

    assert agent.steps == [], "execute must not be wrapped in remote mode"


# --- eylemler kaydediliyor mu ---


def test_the_captured_calls_reach_the_step_in_remote_mode():
    """The second-layer fault: steps arrived but actions stayed at zero, because
    the absence of the second source was being read as "zero calls"."""
    capture = ApiCapture()
    world = FakeWorld(remote="http://127.0.0.1:8124")
    agent = _kaydedici(capture)
    _tak(agent, world)

    capture.calls.append(
        CapturedCall(
            method="get",
            url="/spotify/songs",
            data={"page_index": 2},
            status_code=200,
            response={},
        )
    )
    world.batch_execute(["print(1)"])

    step = agent.steps[0]
    assert len(step["captured"]) == 1
    assert len(step["actions"]) == 1, "the captured call did not reach the step actions"
    assert step["progress_identities"] == {'spotify.songs|{"page_index": 2}'}


# --- mutation: showing that the test fires ---


def test_the_mount_is_not_vacuous():
    """If the wrapping is removed the claims above must fail.

    Without this test a green suite would stay green with a recorder that is
    never mounted at all — which is exactly what happened in S-53.
    """
    world = FakeWorld(remote="http://127.0.0.1:8124")
    agent = _kaydedici()
    # No wrapping: `initialize` is never called.

    world.batch_execute(["print(1)"])

    assert agent.steps == [], "no step must be recorded without the wrapping"

    world_ici = FakeWorld(remote=None)
    agent_ici = _kaydedici()
    world_ici.batch_execute(["print(1)"])
    assert agent_ici.steps == [], (
        "without the wrapping there must be no step in in-process mode either"
    )
