"""Mines the failure index out of the recorded failing actions.

`docs/07-failure-taxonomy.tr.md` fixes the rules. Like the compiler this is
offline, deterministic and uses no model, and like the skill library the index
is a derived projection: delete it and it rebuilds from the record.

**Every card carries a context condition.** An unconditional prohibition makes
the agent worse — a card that says "do not make this call" without saying when
also blocks the call in the cases where it is required. So a pattern with no
expressible condition does not enter the index, and the count of those is
reported rather than hidden.

**The condition language is closed and stays closed** (K-83). Three forms are
allowed: object existence, object field values, and whether a given call was
made earlier in the sequence. Only the third is recorded here, because the
response body is not persisted (S-40) and object state is therefore not
observable per call. That was measured to be enough: all 498 of the corpus's
401s are expressible with the third form alone, once the argument shape is read
as part of the pattern rather than as a fourth condition form.

**The argument component is shape, not value** (K-83). Which argument names the
call carried, never what was in them. Keying on values would explode the pattern
space and collapse support, the same way keying skills on concrete paths would
have.

**The action label is read from the status code.** `actions.error_class` is
uniformly `Exception`: AppWorld raises on every failed response and the code is
parsed out of the exception text, so the column carries no signal (S-44).

**Shield violations do not create cards.** A card needs a real failure. In
shadow mode a flagged call still executes and, if it fails, enters through the
ordinary path — from its failure, not from the shield's opinion. The shield only
reinforces, and the count is kept beside the card for that.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from zihin.api_routes import route_template

# The action-level labels of `07-failure-taxonomy.tr.md` that this corpus reaches,
# keyed by the status code the exception text carried. The priority order the
# taxonomy fixes — shield, then runtime exception, then API code — does not bite
# here: every failure in the record is an API code, and the shield blocks
# nothing in shadow mode.
STATUS_LABELS = {
    "401": "authorization_denied",
    "403": "authorization_denied",
    "404": "object_not_found",
    "409": "conflicting_state",
    "422": "invalid_parameter",
}

# Argument names dropped from the shape. `access_token` is **not** among them:
# its absence is precisely what distinguishes a third of the corpus's 401s, so
# dropping it would erase the pattern.
IGNORED_IN_SHAPE: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ObservedAction:
    """One recorded action, in the shape the miner needs."""

    episode_id: int
    task_id: str
    order: int
    app: str
    api: str
    method: str
    status: str | None
    error_class: str | None
    arguments: dict[str, Any]

    @property
    def element(self) -> str:
        return f"{self.method} {self.app}.{self.api}"

    @property
    def failed(self) -> bool:
        if self.error_class:
            return True
        return self.status is not None and self.status != "200"

    @property
    def succeeded(self) -> bool:
        return self.status == "200" and not self.error_class

    @property
    def shape(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.arguments) - IGNORED_IN_SHAPE))


@dataclass(frozen=True)
class Condition:
    """A predicate in the closed language, third form only.

    `present=False` is as much a condition as `present=True`: "no successful
    login to this app earlier in the sequence" is what two thirds of the
    corpus's 401s have in common.
    """

    kind: str
    call: str
    present: bool

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "call": self.call, "present": self.present}


@dataclass
class FailurePattern:
    app: str
    api: str
    method: str
    shape: tuple[str, ...]
    status: str
    label: str
    condition: Condition | None = None
    discriminator: str = ""
    failures: list[ObservedAction] = field(default_factory=list)
    contrast_successes: int = 0
    no_known_success: bool = False
    # How many conditions separated this pattern, and whether any of them was
    # about the failing call's own app. Both are recorded on the card because
    # they say how much to trust it: with ninety-two candidates and a small
    # group, a condition can separate by coincidence. A card whose only
    # separating conditions are about unrelated apps is a correlation, not a
    # cause, and the reader has to be able to see that without re-deriving it.
    discriminating_count: int = 0
    own_app_condition: bool = False

    @property
    def tasks(self) -> set[str]:
        return {a.task_id for a in self.failures}

    @property
    def support(self) -> int:
        return len(self.tasks)

    @property
    def key(self) -> tuple[str, str, str, tuple[str, ...], str]:
        return (self.app, self.api, self.method, self.shape, self.status)


def action_from_row(row: Any, order: int) -> ObservedAction:
    """Builds the miner's view of an `actions` row.

    The template comes from the production resolver with the method, as
    everywhere else (S-36).
    """
    method = (row["http_method"] or "GET").upper()
    template = route_template(row["app"], row["api"], method)
    try:
        arguments = json.loads(row["raw_parameters"]) if row["raw_parameters"] else {}
    except json.JSONDecodeError:
        arguments = {}
    return ObservedAction(
        episode_id=row["episode_id"],
        task_id=row["task_id"],
        order=order,
        app=row["app"],
        api=template or row["api"],
        method=method,
        status=row["result_status"],
        error_class=row["error_class"],
        arguments=arguments if isinstance(arguments, dict) else {},
    )


def facts_before(actions: list[ObservedAction]) -> list[frozenset[str]]:
    """For each position, the set of calls that had already succeeded.

    This is the whole of the condition language that the record supports: what
    the sequence had already done. Only **successful** calls count — a login
    that was refused did not log anyone in, and treating it as a fact would put
    the wrong condition on the card.
    """
    seen: set[str] = set()
    per_position: list[frozenset[str]] = []
    for action in actions:
        per_position.append(frozenset(seen))
        if action.succeeded:
            seen.add(action.element)
    return per_position


def _candidate_conditions(alphabet: set[str]) -> list[Condition]:
    return [
        Condition("prior_successful_call", call, present)
        for call in sorted(alphabet)
        for present in (True, False)
    ]


def _holds(condition: Condition, facts: frozenset[str]) -> bool:
    return (condition.call in facts) is condition.present


def mine_failure_patterns(
    episodes: dict[int, list[ObservedAction]],
    *,
    min_support: int,
) -> tuple[list[FailurePattern], dict[str, int]]:
    """Groups failures and attaches a condition to each group.

    The grouping key is the endpoint, the argument **shape** and the status
    code. The contrast set is every success of the same endpoint, whatever its
    shape — because the shape is one of the two things that can discriminate,
    and restricting the contrast to the same shape would hide it.

    A group enters the index when it has a condition that holds in **every** one
    of its failures, and is discriminating in one of two ways:

      * `condition` — the condition holds in no contrasting success;
      * `argument_shape` — no contrasting success carries this shape.

    Both are recorded so the report can tell them apart. A group with neither is
    left out and counted: the language cannot say when to avoid that call, and a
    card that cannot say when is a card that makes the agent worse.

    No purity threshold is chosen. "Holds in every failure and no success" is a
    rule, not a number, and this corpus is too small to calibrate a number on.
    """
    alphabet = {a.element for calls in episodes.values() for a in calls}

    grouped: dict[tuple, FailurePattern] = {}
    facts_by_action: dict[tuple[int, int], frozenset[str]] = {}
    successes_by_endpoint: dict[tuple[str, str, str], list[ObservedAction]] = defaultdict(list)
    shapes_by_endpoint: dict[tuple[str, str, str], set[tuple[str, ...]]] = defaultdict(set)

    for episode_id, calls in episodes.items():
        for position, facts in enumerate(facts_before(calls)):
            facts_by_action[(episode_id, position)] = facts
        for action in calls:
            endpoint = (action.app, action.api, action.method)
            if action.succeeded:
                successes_by_endpoint[endpoint].append(action)
                shapes_by_endpoint[endpoint].add(action.shape)

    for calls in episodes.values():
        for action in calls:
            if not action.failed or action.status is None:
                continue
            label = STATUS_LABELS.get(action.status)
            if label is None:
                continue
            pattern = grouped.setdefault(
                (action.app, action.api, action.method, action.shape, action.status),
                FailurePattern(
                    app=action.app,
                    api=action.api,
                    method=action.method,
                    shape=action.shape,
                    status=action.status,
                    label=label,
                ),
            )
            pattern.failures.append(action)

    kept: list[FailurePattern] = []
    tally = {
        "groups": len(grouped),
        "below_support": 0,
        "no_expressible_condition": 0,
        "discriminated_by_condition": 0,
        "discriminated_by_shape": 0,
        "no_known_success": 0,
        # The split that says how far to trust the index. A card whose only
        # separating conditions are about other apps separated by coincidence.
        "own_app_condition": 0,
        "unrelated_app_condition": 0,
    }

    for pattern in grouped.values():
        if pattern.support < min_support:
            tally["below_support"] += 1
            continue
        endpoint = (pattern.app, pattern.api, pattern.method)
        successes = successes_by_endpoint.get(endpoint, [])
        pattern.contrast_successes = len(successes)
        pattern.no_known_success = not successes

        if pattern.no_known_success:
            # **No contrast, no condition** (K-85). The condition is derived
            # contrastively; with nothing to separate from, every admissible
            # condition separates trivially and none of them is a finding.
            # Measured: one such pattern admitted 59. The card still enters —
            # a failure seen once but real does not vanish — carrying only its
            # mark, and retrieval counts it separately
            # (`07-failure-taxonomy.tr.md`).
            tally["no_known_success"] += 1
            kept.append(pattern)
            continue

        failure_facts = [facts_by_action[(a.episode_id, a.order)] for a in pattern.failures]
        success_facts = [facts_by_action[(a.episode_id, a.order)] for a in successes]

        admissible = [
            condition
            for condition in _candidate_conditions(alphabet)
            if all(_holds(condition, facts) for facts in failure_facts)
        ]
        if not admissible:
            tally["no_expressible_condition"] += 1
            continue

        discriminating = [
            condition
            for condition in admissible
            if not any(_holds(condition, facts) for facts in success_facts)
        ]
        shape_is_unique = pattern.shape not in shapes_by_endpoint.get(endpoint, set())

        prefix = f"{pattern.app}."

        def _on_own_app(conditions: list[Condition], prefix: str = prefix) -> list[Condition]:
            return [c for c in conditions if c.call.split(" ", 1)[1].startswith(prefix)]

        if discriminating:
            # Deterministic choice: the same corpus must give the same index
            # twice. A condition about the failing call's own app is preferred,
            # because "log in to phone first" is a cause and "someone called an
            # unrelated endpoint" is a coincidence that happened to separate.
            own_app = _on_own_app(discriminating)
            pattern.condition = sorted(
                own_app or discriminating, key=lambda c: (c.call, not c.present)
            )[0]
            pattern.discriminator = "condition"
            pattern.discriminating_count = len(discriminating)
            pattern.own_app_condition = bool(own_app)
            tally["discriminated_by_condition"] += 1
            tally["own_app_condition" if own_app else "unrelated_app_condition"] += 1
        elif shape_is_unique:
            own_app = _on_own_app(admissible)
            pattern.condition = sorted(
                own_app or admissible, key=lambda c: (c.call, not c.present)
            )[0]
            pattern.discriminator = "argument_shape"
            pattern.discriminating_count = len(admissible)
            pattern.own_app_condition = bool(own_app)
            tally["discriminated_by_shape"] += 1
        else:
            tally["no_expressible_condition"] += 1
            continue

        kept.append(pattern)

    kept.sort(key=lambda p: (-p.support, -len(p.failures), p.app, p.api))
    return kept, tally
