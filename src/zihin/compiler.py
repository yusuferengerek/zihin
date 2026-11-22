"""Compiler v0: mines skills out of the recorded passing episodes.

`docs/06-skill-language.tr.md` fixes the rules; `SKILL_SPEC.md` fixes the record
this produces. This module is the mechanism between them.

**Offline, deterministic, no model** (`03-architecture.tr.md`). Nothing here calls
a model, reads the clock or samples. The same recording produces the same
library, and that is what makes the library a derived projection rather than a
second source of truth.

**No silent thresholds.** The value threshold, the constant threshold and the
gap size are required arguments. Their numbers belong to the setup phase, not
to the design (K-50), and a default here would quietly become the number. The
runner sweeps them and reports the sensitivity.

**The alphabet is the route template, not the concrete path.** `notes/3084` and
`notes/3085` are the same call with a different argument. Mining over concrete
paths would give every pattern support 1 and the compiler would return nothing —
which would look like "there is nothing to find" rather than "the alphabet is
wrong".

**Support counts distinct tasks, never episodes.** Ten episodes of one task are
one task. Otherwise a single task's repetitions push a pattern into the library.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from zihin.api_routes import path_parameters, route_template, split_endpoint

# Argument names that carry no information about the task: the session token
# changes on every login and appears in almost every call body. Left in, it
# would be classified as a free parameter in every skill and every signature
# would start with it.
IGNORED_ARGUMENTS = frozenset({"access_token"})


@dataclass(frozen=True)
class RecordedCall:
    """One recorded call, in the shape the miner and the classifier need."""

    app: str
    template: str
    method: str
    arguments: dict[str, Any]

    @property
    def element(self) -> str:
        """The alphabet symbol. Two calls are the same symbol iff this matches."""
        return f"{self.method} {self.app}.{self.template}"


@dataclass(frozen=True)
class EpisodeSequence:
    episode_id: int
    task_id: str
    calls: tuple[RecordedCall, ...]
    # Parallel to `calls`: which step each call was made in, and how many calls
    # that step made. Both are needed for attribution — the postcondition is
    # only read off steps that made exactly one call (K-79).
    step_ids: tuple[int, ...] = ()
    step_call_counts: tuple[int, ...] = ()
    # step_id -> the state delta recorded for it. Empty dict means "measured, no
    # change"; a missing key means "not measured", and the two are different.
    step_deltas: dict[int, dict[str, int]] = field(default_factory=dict)
    # step_id -> the observation text, in order. Binding is looked for here.
    observations: tuple[tuple[int, str], ...] = ()

    @property
    def elements(self) -> tuple[str, ...]:
        return tuple(c.element for c in self.calls)


@dataclass
class Pattern:
    """A mined sequence of alphabet symbols, with where it can end.

    **End positions, not full occurrence tuples.** The first version kept every
    matching tuple of positions and did not finish: a pattern with many
    occurrences per sequence multiplies its tuples at every extension, and one
    recorded episode makes 255 calls. Only the end position matters for
    extension and for support, and there are at most as many of those as there
    are calls in the sequence, so the state is bounded by the corpus rather than
    by the pattern.
    """

    elements: tuple[str, ...]
    # episode_id -> the positions at which a match of this pattern can end
    ends: dict[int, set[int]] = field(default_factory=dict)
    tasks: set[str] = field(default_factory=set)

    @property
    def support(self) -> int:
        return len(self.tasks)

    @property
    def length(self) -> int:
        return len(self.elements)


def call_from_action(app: str, api: str, method: str | None, raw_parameters: str) -> RecordedCall:
    """Builds the miner's view of a recorded action row.

    `api` is the concrete path as `actions` stores it; the template and the path
    parameters both come from the production resolver, method included (S-36).
    """
    http = (method or "GET").upper()
    template = route_template(app, api, http)
    arguments = dict(path_parameters(app, api, http))
    body = json.loads(raw_parameters) if raw_parameters else {}
    if isinstance(body, dict):
        arguments.update(body)
    for name in IGNORED_ARGUMENTS:
        arguments.pop(name, None)
    return RecordedCall(app=app, template=template or api, method=http, arguments=arguments)


def call_from_log(row: dict[str, Any]) -> RecordedCall:
    """Same, from a raw `api_calls.jsonl` line."""
    app, path = split_endpoint(row["url"])
    http = (row["method"] or "GET").upper()
    template = route_template(app, path, http)
    arguments = dict(path_parameters(app, path, http))
    if isinstance(row.get("data"), dict):
        arguments.update(row["data"])
    for name in IGNORED_ARGUMENTS:
        arguments.pop(name, None)
    return RecordedCall(app=app, template=template or path, method=http, arguments=arguments)


# --- mining -----------------------------------------------------------------


@dataclass
class MiningResult:
    """What was mined, and whether any guard bound while mining it.

    When a guard binds the result carries **which** one, the value it saw, the
    limit it compared against, and where in the search it happened. "The search
    hit a guard" was the whole message once, and it left the reader with no way
    to tell a node budget from a length cap, or a near miss from an explosion -
    the two call for different responses (K-125, K-158).
    """

    patterns: list[Pattern]
    hit_max_length: bool = False
    hit_max_patterns: bool = False
    guard: str | None = None
    observed: int = 0
    limit: int = 0
    level: int = 0
    frontier: int = 0

    @property
    def guarded(self) -> bool:
        return self.hit_max_length or self.hit_max_patterns

    def guard_report(self) -> str:
        """The guard's own sentence: name, value seen, limit, and where."""
        if not self.guarded:
            return "no guard bound; the search completed"
        if self.guard == "max_length":
            return (
                f"guard max_length bound: {self.frontier} frequent pattern(s) of length "
                f"{self.observed} still had frequent extensions and the limit is "
                f"{self.limit}. This is a depth cap: raising --max-length continues the "
                "search deeper, and a corpus where it binds shares call sequences at least "
                f"{self.limit} long across {self.frontier} pattern(s)."
            )
        return (
            f"guard max_patterns bound: growing length {self.level - 1} to {self.level} "
            f"would bring the pattern count to {self.observed} and the limit is "
            f"{self.limit} ({self.frontier} pattern(s) at the new level). This is a node "
            "budget: raising --max-patterns continues the search, and the search is only "
            "complete when it finishes without this guard binding again."
        )


def _extensions(
    pattern: Pattern,
    sequences: dict[int, EpisodeSequence],
    max_gap: int,
    excluded: frozenset[str] = frozenset(),
) -> dict[str, Pattern]:
    """Every one-symbol extension of `pattern`, built in a single pass.

    Candidate-driven: the symbols tried are the ones that actually occur inside
    the gap window, not the whole frequent alphabet. Trying the alphabet was the
    first version and it did not finish.

    The gap is the number of calls skipped **between** two consecutive pattern
    elements, so `max_gap=0` means strictly adjacent.
    """
    grown: dict[str, Pattern] = {}
    for episode_id, ends in pattern.ends.items():
        sequence = sequences[episode_id]
        elements = sequence.elements
        for end in ends:
            limit = min(len(elements), end + max_gap + 2)
            for index in range(end + 1, limit):
                symbol = elements[index]
                if symbol in excluded:
                    # The call stays in the sequence so that gaps are measured
                    # over what really happened; it just cannot be part of a
                    # skill.
                    continue
                candidate = grown.get(symbol)
                if candidate is None:
                    candidate = Pattern(elements=pattern.elements + (symbol,))
                    grown[symbol] = candidate
                candidate.ends.setdefault(episode_id, set()).add(index)
                candidate.tasks.add(sequence.task_id)
    return grown


def mine_patterns(
    sequences: list[EpisodeSequence],
    *,
    min_support: int,
    max_gap: int,
    min_length: int = 2,
    max_length: int = 12,
    max_patterns: int = 200_000,
    excluded_elements: frozenset[str] = frozenset(),
) -> MiningResult:
    """Closed sequential patterns, support counted by distinct task.

    Level-wise growth with support pruning, then a closure filter. Closure is
    the rule from `06-skill-language.tr.md`: a pattern that has an extension with
    the same support is not reported, because the longer one says everything the
    shorter one says and more.

    `excluded_elements` never appear **inside** a pattern but stay in the
    sequence, so gaps are still counted over the calls that really happened. The
    scaffold's completion call is excluded that way (K-80): a skill whose body
    contained it would end the episode when invoked, so it would carry control
    flow and not just work.

    `max_length` and `max_patterns` are guards, not rules. One recorded episode
    makes 255 calls and repeats a login sequence; without a bound the search
    does not terminate in useful time. When a guard binds the result says so, so
    that a truncated search is never reported as a complete one.
    """
    by_id = {s.episode_id: s for s in sequences}

    seeds: dict[str, Pattern] = {}
    for sequence in sequences:
        for index, symbol in enumerate(sequence.elements):
            if symbol in excluded_elements:
                continue
            pattern = seeds.get(symbol)
            if pattern is None:
                pattern = Pattern(elements=(symbol,))
                seeds[symbol] = pattern
            pattern.ends.setdefault(sequence.episode_id, set()).add(index)
            pattern.tasks.add(sequence.task_id)

    level = [p for p in seeds.values() if p.support >= min_support]
    every_pattern: list[Pattern] = list(level)
    result = MiningResult(patterns=[])

    while level:
        if len(level[0].elements) >= max_length:
            result.hit_max_length = True
            result.guard = "max_length"
            result.observed = len(level[0].elements)
            result.limit = max_length
            result.level = len(level[0].elements)
            result.frontier = len(level)
            break
        following: list[Pattern] = []
        for pattern in level:
            for grown in _extensions(pattern, by_id, max_gap, excluded_elements).values():
                if grown.support >= min_support:
                    following.append(grown)
        if not following:
            break
        if len(every_pattern) + len(following) > max_patterns:
            result.hit_max_patterns = True
            result.guard = "max_patterns"
            result.observed = len(every_pattern) + len(following)
            result.limit = max_patterns
            result.level = len(following[0].elements)
            result.frontier = len(following)
            break
        every_pattern.extend(following)
        level = following

    result.patterns = _closed_only([p for p in every_pattern if p.length >= min_length])
    return result


def _closed_only(patterns: list[Pattern]) -> list[Pattern]:
    """Drops a pattern when a strict superpattern has the same support."""
    by_support: dict[int, list[Pattern]] = defaultdict(list)
    for pattern in patterns:
        by_support[pattern.support].append(pattern)

    closed: list[Pattern] = []
    for support, group in by_support.items():
        for pattern in group:
            if not any(
                other is not pattern
                and other.length > pattern.length
                and _is_subsequence(pattern.elements, other.elements)
                for other in by_support[support]
            ):
                closed.append(pattern)
    return sorted(closed, key=lambda p: (-p.support, -p.length, p.elements))


def _is_subsequence(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    iterator = iter(long)
    return all(any(item == candidate for candidate in iterator) for item in short)


# --- what counts as an effect --------------------------------------------


# The scaffold's control channel. `POST supervisor.message` is `complete_task`:
# it ends the episode and sends an answer, and it changes nothing in the world.
# Every episode ends with it, it is app-independent, and it has no irrelevant
# version — so an irrelevant-retrieval control cannot separate the gain it would
# be credited with. That is K-75's third argument, and this call was its leak
# (K-78).
#
# Keyed by (app, template, method) rather than by app: `admin` also carries real
# environment actions, and every endpoint that writes into `admin` was measured
# to write into its own app as well, so no rule about infrastructure apps is
# needed. The category is "scaffold control channel", and this is its only
# member today.
SCAFFOLD_CONTROL_CALLS = frozenset({("supervisor", "message", "POST")})


def scaffold_control_elements(sequences: list[EpisodeSequence]) -> frozenset[str]:
    """The alphabet symbols that are scaffold control, not work (K-80).

    Excluded from skill bodies as well as from effect suffixes. A skill whose
    body contained `complete_task` would end the episode the moment it was
    invoked: the agent would finish the task by calling the skill, and calling
    it early would file a wrong completion. A skill carries work, not control
    flow, and the distinction is the same one that kept the call out of the
    effect suffix.
    """
    return frozenset(
        call.element
        for sequence in sequences
        for call in sequence.calls
        if (call.app, call.template, call.method) in SCAFFOLD_CONTROL_CALLS
    )


def effect_elements(
    sequences: list[EpisodeSequence],
    write_set: dict,
    session_endpoints: set[tuple[str, str, str]],
) -> set[str]:
    """Alphabet symbols whose call is an effect, for the compiler.

    **Not the same question the shield asks** (K-78). The shield asks "is this
    permitted"; the compiler asks "did this achieve something". The two diverge
    on exactly one family: the shield exempts `login` and `logout` from its
    write set because reading is unconditionally free and logging in is the
    precondition of reading (K-69, K-74). That is a permission statement. For
    the compiler, logging in achieves something concrete — it produces the token
    the following calls need — so it counts as an effect.

    The exemption on the shield's side is unchanged. The same recording answers
    two questions and gives two answers, which is correct, because they are two
    questions.
    """
    effects: set[str] = set()
    for sequence in sequences:
        for call in sequence.calls:
            key = (call.app, call.template, call.method)
            if key in SCAFFOLD_CONTROL_CALLS:
                continue
            if key in session_endpoints or write_set.get(key):
                effects.add(call.element)
    return effects


def session_endpoint_keys(write_set_path: str) -> set[tuple[str, str, str]]:
    """The session endpoints the write set exempted, read from its own output.

    Read rather than re-derived: the derivation names them (`session_endpoints`)
    precisely so that nothing downstream has to guess which path string means
    "login".
    """
    import pathlib

    raw = json.loads(pathlib.Path(write_set_path).read_text(encoding="utf-8"))
    names = set(raw.get("session_endpoints", ()))
    keys = set()
    for record in raw["endpoints"].values():
        if f"{record['app']}.{record['api']}" in names:
            for method in record["methods"]:
                keys.add((record["app"], record["path"].lstrip("/"), method))
    return keys


def effect_suffix(elements: tuple[str, ...], effects: set[str]) -> tuple[int, ...]:
    """Indices of the pattern's elements that are effects."""
    return tuple(i for i, e in enumerate(elements) if e in effects)


# --- occurrences, recovered for the reported patterns only ----------------


def occurrences_of(
    elements: tuple[str, ...],
    sequence: EpisodeSequence,
    max_gap: int,
    max_occurrences: int = 2000,
) -> list[tuple[int, ...]]:
    """Every position tuple at which `elements` occurs in `sequence`.

    The miner deliberately keeps only end positions, because full tuples do not
    terminate at corpus scale. Attribution needs the tuples, so they are
    recovered here — but only for the patterns that survived closure, which is a
    small set.

    `max_occurrences` bounds the recovery on a pathological episode; one
    recorded episode makes 255 calls and repeats a login sequence.
    """
    found: list[tuple[int, ...]] = []
    symbols = sequence.elements

    def walk(prefix: tuple[int, ...], depth: int) -> None:
        if len(found) >= max_occurrences:
            return
        if depth == len(elements):
            found.append(prefix)
            return
        start = 0 if not prefix else prefix[-1] + 1
        limit = len(symbols) if not prefix else min(len(symbols), prefix[-1] + max_gap + 2)
        for index in range(start, limit):
            if symbols[index] == elements[depth]:
                walk((*prefix, index), depth + 1)

    walk((), 0)
    return found


# --- postcondition --------------------------------------------------------


def occurrence_postcondition(
    positions: tuple[int, ...],
    sequence: EpisodeSequence,
    effect_indices: tuple[int, ...],
) -> dict[str, str] | None:
    """The shape of the state change one occurrence produced.

    **Only steps that made exactly one call are used** (K-79). Attribution needs
    isolation: in a step that made eleven calls, which call produced the delta is
    not knowable. Attributing it to all of them over-attributes; splitting it
    proportionally invents data. Of the sixteen delta-bearing steps in the
    recorded corpus, eight made a single call.

    **An occurrence counts as measured only when every one of its effect calls
    was isolated.** The first version required only that *some* step in the
    occurrence be isolated, and it was wrong in a way this project has met
    before: in one supporting episode the effect call sat in a three-call step
    while the scaffold's completion call sat alone, so the occurrence was ruled
    measurable, contributed an empty shape, and emptied the intersection. Four
    other occurrences had observed the same effect identically. That is reading
    "could not attribute" as "measured, nothing happened" — zero difference on
    its own is not evidence.

    Returns None for "not attributable here", `{}` for "attributable and
    nothing changed". The two are different and the caller must not merge them.
    """
    if not sequence.step_ids:
        return None
    for depth in effect_indices:
        index = positions[depth]
        if sequence.step_call_counts[index] != 1:
            return None
        if sequence.step_ids[index] not in sequence.step_deltas:
            return None

    shape: dict[str, str] = {}
    contradicted: set[str] = set()
    for index in positions:
        if sequence.step_call_counts[index] != 1:
            continue
        delta = sequence.step_deltas.get(sequence.step_ids[index])
        if delta is None:
            continue
        for model, amount in delta.items():
            sign = "+" if amount > 0 else "-"
            if model in shape and shape[model] != sign:
                # The same model moved both ways inside one occurrence: no
                # constant shape can be claimed for it.
                contradicted.add(model)
            shape.setdefault(model, sign)
    for model in contradicted:
        shape.pop(model, None)
    return shape


def pattern_postcondition(
    elements: tuple[str, ...],
    sequences: list[EpisodeSequence],
    supporting_episodes: set[int],
    max_gap: int,
    effect_indices: tuple[int, ...] = (),
) -> dict[str, str] | None:
    """The intersection of the shapes over every supporting occurrence.

    The definition is "what changed in every supporting episode", read at the
    level of shape rather than magnitude (`SKILL_SPEC.md`). It is applied to
    occurrences as well as episodes: a pattern that occurs twice in an episode
    has to produce the same shape both times, or the shape is not a property of
    the pattern.

    Returns None when nothing was measurable, `{}` when the occurrences were
    measurable and agreed on nothing.
    """
    shapes: list[dict[str, str]] = []
    for sequence in sequences:
        if sequence.episode_id not in supporting_episodes:
            continue
        for positions in occurrences_of(elements, sequence, max_gap):
            shape = occurrence_postcondition(positions, sequence, effect_indices)
            if shape is not None:
                shapes.append(shape)
    if not shapes:
        return None
    common = dict(shapes[0])
    for shape in shapes[1:]:
        common = {k: v for k, v in common.items() if shape.get(k) == v}
    return common


# --- argument classification ---------------------------------------------

# Below this length a textual match means nothing: `1` and `on` occur in every
# observation. The bound is on the printed representation, and it is the reason
# the classifier under-detects rather than over-detects.
MINIMUM_BINDABLE_LENGTH = 3


@dataclass(frozen=True)
class ArgumentClasses:
    """One classification per position in the pattern."""

    bound: dict[int, set[str]]
    free: set[str]
    constants: dict[str, tuple[Any, int]]
    inspected: int = 0


def _looks_bound(value: Any, earlier_text: str, minimum_length: int) -> bool:
    rendered = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return len(rendered) >= minimum_length and rendered in earlier_text


def classify_arguments(
    elements: tuple[str, ...],
    sequences: list[EpisodeSequence],
    supporting_episodes: set[int],
    max_gap: int,
    constant_threshold: int,
    minimum_bindable_length: int = MINIMUM_BINDABLE_LENGTH,
) -> ArgumentClasses:
    """Binding first, then variability (`06-skill-language.tr.md`).

    The order is the rule and not a preference: classify by variability first
    and a bound argument looks like a free parameter, so the caller would have
    to know half the answer before calling the skill and the skill would be
    worth nothing.

    **Binding is looked for in the observation text, not in the response body.**
    The body is captured at run time but not persisted: `actions` keeps the
    status code and the error class only. What survives is what the agent
    printed, and the reference scaffold's pattern is
    `print(apis.<app>.<api>(...))`, so the values the agent went on to use are
    in it. This is weaker than the structural path matching the design asks for
    — a value used without being printed looks free. The error runs one way,
    under-detection and never over-detection, and it is recorded as a
    limitation. Re-running with the body persisted is the v1 path and cannot be
    applied to this corpus without replacing it (S-16).

    **And it is looked for inside the body only.** `06-skill-language.tr.md` says a
    bound argument's value appears in the output of an earlier call *in the
    sequence*, and the sequence is the skill's own body. A value the episode
    produced elsewhere is not available at execution time, so treating it as
    bound would embed something the skill can neither obtain nor be handed.
    """
    bound: dict[int, set[str]] = defaultdict(set)
    values_by_position: dict[int, list[tuple[str, Any]]] = defaultdict(list)
    tasks_by_position: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    inspected = 0

    for sequence in sequences:
        if sequence.episode_id not in supporting_episodes:
            continue
        for positions in occurrences_of(elements, sequence, max_gap):
            body_steps = {sequence.step_ids[i] for i in positions} if sequence.step_ids else set()
            for depth, index in enumerate(positions):
                call = sequence.calls[index]
                step_id = sequence.step_ids[index] if sequence.step_ids else None
                # **Only the body's own earlier output counts.** A value the
                # episode produced outside the pattern is not available to the
                # compiled skill: the body executes atomically and the calls the
                # gap skipped never run. Searching the whole episode prefix was
                # the first version, and it was measured to call every argument
                # of the venmo login skill bound — including the password, which
                # comes from `supervisor.account_passwords`, a call that skill
                # does not contain. Those arguments belong in the signature.
                earlier = ""
                if step_id is not None:
                    parts = []
                    for observed_step, text in sequence.observations:
                        if observed_step == step_id:
                            break
                        if observed_step in body_steps:
                            parts.append(text)
                    earlier = "\n".join(parts)
                for name, value in call.arguments.items():
                    inspected += 1
                    values_by_position[depth].append((name, value))
                    tasks_by_position[depth][name].add(sequence.task_id)
                    if _looks_bound(value, earlier, minimum_bindable_length):
                        bound[depth].add(name)

    free: set[str] = set()
    constants: dict[str, tuple[Any, int]] = {}
    for depth, pairs in values_by_position.items():
        distinct_by_name: dict[str, set[str]] = defaultdict(set)
        example: dict[str, Any] = {}
        for name, value in pairs:
            distinct_by_name[name].add(repr(value))
            example[name] = value
        for name, distinct in distinct_by_name.items():
            if name in bound.get(depth, set()):
                continue
            tasks = tasks_by_position[depth][name]
            if len(distinct) == 1 and len(tasks) >= constant_threshold:
                constants[f"{depth}.{name}"] = (example[name], len(tasks))
            else:
                free.add(f"{depth}.{name}")
    return ArgumentClasses(bound=dict(bound), free=free, constants=constants, inspected=inspected)


# --- merging --------------------------------------------------------------


@dataclass
class MergedSkill:
    """One skill, after patterns sharing an effect suffix were merged.

    `06-skill-language.tr.md`: a skill splits into a search prefix and an effect
    suffix, and **the same effect suffix means the same skill**. The prefix is
    how the skill is found, not what it is.

    Without the merge the count is an artefact of how many prefixes happened to
    be recorded. It was measured: forty mined patterns, thirty-nine of them the
    same handful of logins reached through different documentation reads.
    """

    effect_suffix: tuple[str, ...]
    body: tuple[str, ...]
    tasks: set[str]
    members: list[Pattern] = field(default_factory=list)

    @property
    def support(self) -> int:
        return len(self.tasks)


def effect_sequence(elements: tuple[str, ...], effects: set[str]) -> tuple[str, ...]:
    """The effect suffix as a sequence of symbols, in order.

    The identity is the effects themselves, not the span from the first effect
    to the end of the pattern. A trailing read is part of how the pattern was
    recorded, not part of what it achieves, and two patterns that differ only by
    one would otherwise stay separate skills.
    """
    return tuple(e for e in elements if e in effects)


def merge_by_effect_suffix(patterns: list[Pattern], effects: set[str]) -> list[MergedSkill]:
    """Groups the mined patterns into skills.

    **The body is the member with the widest support**, ties broken by length
    and then lexicographically. Something has to be the body — a skill has one
    call sequence — and the widest-support member is the variant seen in the
    most tasks, so it is the least specialised to any one of them. The tie-break
    is spelled out because the compiler has to be deterministic: the same
    recording must produce the same library.

    **Support is the union of the members' task sets**, not the maximum. The
    claim being made is that the effect suffix occurred in that many tasks, and
    two prefixes covering different tasks both count towards it.
    """
    grouped: dict[tuple[str, ...], MergedSkill] = {}
    for pattern in patterns:
        suffix = effect_sequence(pattern.elements, effects)
        if not suffix:
            continue
        skill = grouped.get(suffix)
        if skill is None:
            skill = MergedSkill(effect_suffix=suffix, body=pattern.elements, tasks=set())
            grouped[suffix] = skill
        skill.members.append(pattern)
        skill.tasks |= pattern.tasks

    for skill in grouped.values():
        skill.body = max(
            (p.elements for p in skill.members),
            key=lambda elements: (
                len(_tasks_of(skill.members, elements)),
                len(elements),
                tuple(-ord(c) for c in "".join(elements)),
            ),
        )
    return sorted(grouped.values(), key=lambda s: (-s.support, -len(s.body), s.effect_suffix))


def _tasks_of(members: list[Pattern], elements: tuple[str, ...]) -> set[str]:
    for pattern in members:
        if pattern.elements == elements:
            return pattern.tasks
    return set()
