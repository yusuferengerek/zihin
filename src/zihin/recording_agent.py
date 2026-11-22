"""Wrapper that records the reference scaffold.

The scaffold is untouched. `SimplifiedReActCodeAgent` is used as-is; only the
environment's `execute` method is wrapped from outside. The agent's prompt,
parser and loop stay the same (K-19 scope note).

Why live recording: AppWorld's `logs/api_calls.jsonl` is a flat list and does
not say which call belongs to which step. Once a run is over, actions can no
longer be attached to steps. So the recording is taken after every `execute()`
call: however much the file grew during that step is that step's actions
(K-14).
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from appworld import AppWorld
from appworld.common.path_store import path_store
from appworld_agents.code.simplified.react_code_agent import SimplifiedReActCodeAgent

from zihin.api_capture import ApiCapture
from zihin.api_routes import endpoint_identity, split_endpoint
from zihin.state_probe import diff as state_diff
from zihin.state_probe import snapshot as state_snapshot


class NoProgress(RuntimeError):
    """The episode was terminated because it produced no progress.

    The stopping rule belongs to the harness layer, not to the agent's logic.
    The scaffold's loop is untouched; termination happens through an exception
    raised from the `execute` wrapper, and the runner catches it. Because the
    world closes through its context manager, the records still reach disk.
    """


def kernel_clock() -> float:
    """freezegun freezes `time.monotonic` process-wide; it does not freeze the
    kernel clock."""
    with open("/proc/uptime", encoding="ascii") as handle:
        return float(handle.read().split()[0])


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def step_category(step: dict[str, Any]) -> str | None:
    """Which of K-36's five categories, or None when an action was produced."""
    if not step["code"].strip():
        return "no_code"
    if step["actions"]:
        return None
    if "Execution failed" in step["output"]:
        return "execution_error_no_action"
    return "execution_ok_no_action"


def _action_rows(step: dict[str, Any]) -> list[dict[str, Any]]:
    """Turns the step's actions into the shape that gets written.

    When the capture is present, the response body and status code come with
    it. Otherwise only the request is written and the status columns stay empty
    (S-05).

    On the log branch the fields are indexed directly, not read with `.get()`.
    The reason is a measured failure: the stopping rule was reading `app` and
    `api` keys that do not exist on those rows, silently getting None, and the
    endpoint criterion never worked (S-32). `method`, `url` and `data` are
    mandatory; if one is missing the run must fail rather than pass silently.
    """
    captured = step.get("captured")
    if captured is not None and len(captured) == len(step["actions"]):
        rows = []
        for call in captured:
            app, endpoint = split_endpoint(call.url)
            rows.append(
                {
                    "app": app,
                    "api": endpoint,
                    "http_method": (call.method or "").upper() or None,
                    "raw_parameters": call.data or {},
                    "result_status": str(call.status_code) if call.status_code else None,
                    "error_class": call.error_class,
                }
            )
        return rows

    rows = []
    for call in step["actions"]:
        app, endpoint = split_endpoint(call["url"])
        rows.append(
            {
                "app": app,
                "api": endpoint,
                "http_method": (call["method"] or "").upper() or None,
                "raw_parameters": call["data"] or {},
                "result_status": None,
                "error_class": None,
            }
        )
    return rows


def step_endpoints(step: dict[str, Any]) -> set[str]:
    """The API endpoints the step touched, reduced to route templates.

    **This is not the rule's criterion, it is a reported diagnostic.** The rule
    looks at concrete call identity (`step_progress_identities`). This count
    answers "how many distinct operations did the episode touch" and is written
    to `episodes.distinct_endpoints`.
    """
    return {
        endpoint_identity(row["app"], row["api"], row["http_method"]) for row in _action_rows(step)
    }


def step_progress_identities(step: dict[str, Any]) -> set[str]:
    """The identity set the stopping rule uses for its progress criterion.

    The identity is the concrete call itself: app, concrete path and request
    parameters. `todoist.tasks/2851/comments|{"access_token": ...}` and
    `todoist.tasks/2854/comments|{...}` are **different** identities.

    Not the route template, because it was measured: episode `8ce6779_2` reads
    comments 117 times with different `task_id`s, writes everything at the end,
    and passes 9 of 9 tests. Under template identity that episode looks
    stagnant for 107 steps and no reasonable threshold saves it. Under concrete
    identity its stall drops to 36.

    S-25's pathology is still caught by this definition and the separation was
    measured: that episode makes all 736 calls to **the same three concrete
    paths**, and its stall is 146.

    The serialisation matches `insert_action` exactly (`sort_keys=True`),
    because the calibration tool rebuilds the same identity from the database.
    Two different serialisations in two places would produce a silent
    divergence.
    """
    return {
        f"{row['app']}.{row['api']}|"
        f"{json.dumps(row['raw_parameters'], ensure_ascii=False, sort_keys=True)}"
        for row in _action_rows(step)
    }


def step_resources(step: dict[str, Any]) -> set[str]:
    """The distinct **objects** the step touched: concrete path, no parameters.

    `tasks/2851/comments` and `tasks/2854/comments` are two objects, `tasks` is
    one operation. The ratio of this count to the endpoint count is diagnostic:
    high means exploration, close to one means repetition.
    """
    return {f"{row['app']}.{row['api']}" for row in _action_rows(step)}


def step_raw_urls(step: dict[str, Any]) -> set[str]:
    """The raw URLs of the step's calls, without going through the parser.

    The basis of the health check: when there is more than one raw URL but the
    identity set collapses to one, identity production has broken. S-32 was
    exactly that — 13 distinct URLs, one identity. Taking the raw URL without
    the parser is essential, otherwise a broken parser breaks the check along
    with it.
    """
    captured = step.get("captured")
    if captured is not None and len(captured) == len(step["actions"]):
        return {call.url for call in captured}
    return {call["url"] for call in step["actions"]}


class RecordingAgent(SimplifiedReActCodeAgent):
    """The reference scaffold with nothing but a recording wrapper on top.

    When `capture` is given, actions come from the API capture and carry the
    response body and status code (S-16). Otherwise the `api_calls.jsonl` delta
    is used; that source carries no response.

    When both sources are in play their counts are compared. A divergence means
    the capture missed a call or counted an extra one, and must not pass
    silently.
    """

    def __init__(
        self,
        *,
        experiment_name: str,
        capture: ApiCapture | None = None,
        probe_state: bool = True,
        no_progress_limit: int | None = None,
        log_source: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.experiment_name = experiment_name
        self.capture = capture
        self.probe_state = probe_state
        self.no_progress_limit = no_progress_limit
        # Whether the second source, `api_calls.jsonl`, can be read. In sandbox
        # mode the file is inside the container, so there is no second source on
        # the host side.
        self.log_source = log_source
        self.steps: list[dict[str, Any]] = []
        self.count_divergences: list[dict[str, int]] = []
        self.stop_reason: str | None = None
        self._call_log_path: str | None = None
        self._calls_read = 0

    @staticmethod
    def _progress_identities(step: dict[str, Any]) -> set[str]:
        """The step's identity set. Computed once, when the step is recorded.

        Indexed directly: if the key is missing, raise. Deriving the set again
        here would mean the rule following a path of its own, separate from
        what is recorded.
        """
        return step["progress_identities"]

    def _made_no_progress(self, step: dict[str, Any], seen_identities: set[str]) -> bool:
        """Did the step produce progress?

        Two things count as progress: changing verifiable state, or making a
        call that has never been made before. With neither, the step made no
        progress.

        **A successful call on its own does not count as progress**, and the
        reason is a measured failure. One episode made 736 calls over 150
        steps, all returned 200, the database never changed once, and that
        episode repeated the same three concrete calls at every step (S-25).
        Because the identity is the concrete call, that pathology is still
        caught: its stall is 146.

        **Why concrete call rather than template.** Long read-only exploration
        is a legitimate way to solve a task: `8ce6779_2` reads comments 117
        times with different ids, writes everything at the end, and passes.
        Under template identity that episode looked stagnant for 107 steps.
        """
        if step["state_delta"]:
            return False
        return self._progress_identities(step) <= seen_identities

    def _check_progress(self) -> None:
        if not self.no_progress_limit:
            return
        if len(self.steps) < self.no_progress_limit:
            return

        # Calls made up to the start of the window are the yardstick for what
        # counts as "new" inside it. The view is cumulative: every call made
        # since the beginning of the episode.
        seen: set[str] = set()
        stalled = 0
        for step in self.steps:
            if self._made_no_progress(step, seen):
                stalled += 1
            else:
                stalled = 0
            seen |= self._progress_identities(step)

        if stalled >= self.no_progress_limit:
            self.stop_reason = "no_progress"
            raise NoProgress(
                f"{self.no_progress_limit} consecutive steps neither changed state nor made a "
                "call that had not been made before; the episode was terminated."
            )

    def initialize(self, world: AppWorld) -> None:
        """Mounts the recorder onto the environment.

        **Which method to wrap depends on the mode, and that was learned by
        measurement.** The reference agent calls `world.batch_execute`, not
        `world.execute`. In in-process mode `batch_execute` calls `self.execute`
        for every code block, so wrapping `execute` was enough — that is how the
        recording worked until now. In remote-environment mode `batch_execute`
        diverts straight to an HTTP call and `self.execute` is never called.

        The difference showed up in the first sandbox episode: the episode ran,
        the trajectory produced 32 KB of text, and **zero steps** were written to
        the record. Silent, because the episode row was still written and the
        verifier still returned a result.

        So remote mode wraps `batch_execute` and in-process mode wraps `execute`.
        Wrapping both would record every step twice in in-process mode.
        """
        super().initialize(world)
        self._call_log_path = os.path.join(
            path_store.experiment_outputs,
            self.experiment_name,
            "tasks",
            world.task_id,
            "logs",
            "api_calls.jsonl",
        )
        self._calls_read = 0
        real_execute = world.execute

        if self.capture is not None:
            self.capture.reset()

        def wrapped(code: str, *args: Any, **kwargs: Any):
            state_before = state_snapshot(world) if self.probe_state else None
            started = kernel_clock()
            output = real_execute(code, *args, **kwargs)
            state_delta = (
                state_diff(state_before, state_snapshot(world))
                if state_before is not None
                else None
            )
            captured = self.capture.drain() if self.capture is not None else None

            # `api_calls.jsonl` is the second source and in sandbox mode it is
            # **absent**: the environment server writes it and that server is
            # inside the container. Reading its absence as "zero calls" would be
            # a silent zeroing — which is exactly what happened in the first
            # sandbox episode: the proxy saw thirty requests and zero actions
            # were written. With no source, actions come from the capture and no
            # count comparison is made: there is no second number to compare.
            if not self.log_source:
                from_log = list(captured or [])
            else:
                from_log = self._new_calls()

            if self.log_source and captured is not None and len(captured) != len(from_log):
                self.count_divergences.append(
                    {
                        "step": len(self.steps) + 1,
                        "captured": len(captured),
                        "from_log": len(from_log),
                    }
                )

            # Drained in the same place as the calls, so a violation attaches to
            # the step whose code produced it.
            shield = (
                self.capture.shield.drain()
                if self.capture is not None and self.capture.shield is not None
                else []
            )

            step = {
                "code": code,
                "output": output,
                "elapsed": kernel_clock() - started,
                "actions": from_log,
                "captured": captured,
                "shield_violations": shield,
                "state_delta": state_delta,
                "instruction_digest": digest(json.dumps(self.messages, ensure_ascii=False)),
            }
            # The only place where the set the rule sees is derived from the
            # rows that get recorded.
            step["progress_identities"] = step_progress_identities(step)
            step["endpoints"] = step_endpoints(step)
            step["resources"] = step_resources(step)
            step["raw_urls"] = step_raw_urls(step)
            self.steps.append(step)

            self._check_progress()
            return output

        if getattr(world, "remote_environment_url", None):
            real_batch = world.batch_execute

            # What runs under the wrapper stays the same route the reference
            # uses: a one-element batch call. Calling `execute` would be
            # equivalent, but the server's counter bookkeeping lives inside
            # `batch_execute` and there is no reason to skip it.
            def single(code: str, *args: Any, **kwargs: Any) -> str:
                return real_batch([code], *args, **kwargs)[0]

            real_execute = single

            def wrapped_batch(codes: list[str], *args: Any, **kwargs: Any):
                # When a batch carries more than one code block, remote mode
                # cannot tell which API call came from which block: all the
                # blocks run inside a single HTTP call. The reference agent sends
                # one block per step; on the day it does not, dropping the
                # episode is right and attributing it wrongly is not.
                if len(codes) != 1:
                    raise RuntimeError(
                        f"a batch in remote-environment mode carries {len(codes)} code "
                        "blocks; which block a call belongs to cannot be told apart and "
                        "the step-level record would be wrong"
                    )
                return [wrapped(codes[0], *args, **kwargs)]

            world.batch_execute = wrapped_batch  # type: ignore[method-assign]
        else:
            world.execute = wrapped  # type: ignore[method-assign]

    def _new_calls(self) -> list[dict[str, Any]]:
        if not self._call_log_path or not os.path.exists(self._call_log_path):
            return []
        with open(self._call_log_path, encoding="utf-8") as handle:
            everything = [json.loads(line) for line in handle if line.strip()]
        fresh = everything[self._calls_read :]
        self._calls_read = len(everything)
        return fresh

    @property
    def total_actions(self) -> int:
        return sum(len(s["actions"]) for s in self.steps)

    def _merge(self, key: str) -> set[str]:
        return set().union(*(s[key] for s in self.steps)) if self.steps else set()

    @property
    def endpoints(self) -> set[str]:
        """Distinct **operations** touched over the episode (route template).
        Diagnostic."""
        return self._merge("endpoints")

    @property
    def resources(self) -> set[str]:
        """Distinct **objects** touched over the episode (concrete path).
        Diagnostic."""
        return self._merge("resources")

    @property
    def progress_identities(self) -> set[str]:
        """The set the rule sees: distinct concrete calls made over the
        episode."""
        return self._merge("progress_identities")

    @property
    def raw_urls(self) -> set[str]:
        """URLs that have not been through the parser; basis of the health
        check."""
        return self._merge("raw_urls")

    @property
    def identity_collapsed(self) -> bool:
        """Has identity production broken?

        When the raw URLs hold more than one distinct value but the identity
        set collapses to one, either parsing or identity production has broken.
        S-32 was exactly that: 13 distinct URLs, one identity (`None.None`).

        It does not look at the call count. A check that did would never fire
        on the preflight episode: that episode makes only two calls in three
        steps.
        """
        return len(self.raw_urls) > 1 and len(self.progress_identities) <= 1


def write_steps(connection, episode_id: int, agent: RecordingAgent, limits, observation_path: str):
    """Writes the agent's accumulated steps, actions and observations to the
    database."""
    from zihin.records import (
        insert_action,
        insert_observation,
        insert_shield_violation,
        insert_step,
    )

    for index, step in enumerate(agent.steps, 1):
        state = step.get("state_delta")
        step_id = insert_step(
            connection,
            episode_id=episode_id,
            step_index=index,
            instruction_digest=step["instruction_digest"],
            context_tokens=None,
            generated_tokens=None,
            latency_seconds=round(step["elapsed"], 3),
            generated_code=step["code"],
            outcome_category=step_category(step),
            # An empty dict means "measured, no change"; None means "not
            # measured".
            state_change=None if state is None else json.dumps(state, sort_keys=True),
        )
        for action_index, row in enumerate(_action_rows(step), 1):
            insert_action(
                connection,
                step_id=step_id,
                action_index=action_index,
                normalized_parameters=None,
                latency_seconds=None,
                **row,
            )
        for violation_index, violation in enumerate(step.get("shield_violations") or [], 1):
            insert_shield_violation(
                connection,
                step_id=step_id,
                violation_index=violation_index,
                app=violation.app,
                api=violation.api,
                http_method=violation.http_method,
                # The dict goes in as a dict: `insert_shield_violation`
                # serialises it the same way `insert_action` serialises the
                # action row for the same call, and the two have to be
                # comparable. Serialising it here would be a second place where
                # the format is decided.
                raw_parameters=violation.raw_parameters,
                predicate=violation.predicate,
                mode=violation.mode,
                reason=violation.reason,
            )
        insert_observation(
            connection,
            step_id=step_id,
            full_text=step["output"],
            limits=limits,
            full_output_path=observation_path,
        )
