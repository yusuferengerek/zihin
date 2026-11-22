"""Renders retrieved cards into the text the model reads.

The retriever decides **which** cards a task gets (`retriever.py`); this module
decides **how** they are printed. The two are separate because the token budget
is a property of the printed form alone, and it is the printed form that the
pilot's context assembler has to fit into 32K.

**One line per field, and nothing that is not a stored field.** The renderer
adds no prose, no advice and no framing. Anything it added would be content the
compiler did not derive from the record, and the mechanism's gain could no
longer be attributed to the mined experience (`03-architecture.tr.md`: the
compiler is offline, deterministic and model-free).

**The skill card has seven fields and the failure card five**, which is the
field count of `SkillCard` and of the failure pattern's identity plus its
condition and its count. The provenance columns the index also stores —
`discriminating_count`, `own_app_condition` — are inputs to the retriever's
filters, not card content (K-85): the index keeps everything with its origin
and the reader filters at read time.

**Text is English.** It enters the reference scaffold's prompt, which is
English, and it is read by the model, not by us.

**A missing saving is not a zero.** `expected_saving` is NULL when the skill's
steps could not be attributed, and printing `0` there would turn "not measured"
into "not worth it" — the confusion K-79 had to be corrected for.
"""

from __future__ import annotations

from zihin.retriever import FailureCard, Retrieved, SkillCard

# The budgets the card format has to hold, in tokens of the model that reads
# them. Measured against the real cards by
# `scripts/setup/measure_card_tokens.py`; a card over budget means the format is
# wrong, not that the budget is.
SKILL_CARD_TOKEN_BUDGET = 180
FAILURE_CARD_TOKEN_BUDGET = 120

SKILL_CARD_FIELDS = 7
FAILURE_CARD_FIELDS = 5

NO_ARGUMENTS = "none"
UNATTRIBUTED_SAVING = "unknown"


def render_skill_card(card: SkillCard) -> str:
    """One skill card: seven lines, the seven fields of `SkillCard`."""
    saving = UNATTRIBUTED_SAVING if card.expected_saving is None else str(card.expected_saving)
    return "\n".join(
        (
            f"SKILL {card.skill_id}",
            f"  apps: {', '.join(card.apps)}",
            f"  effect: {'; '.join(card.effect_suffix)}",
            f"  calls: {' -> '.join(card.body)}",
            f"  parameters: {', '.join(card.free_parameters) or NO_ARGUMENTS}",
            f"  support: {card.support} tasks",
            f"  saves: {saving} model calls",
        )
    )


def render_condition(card: FailureCard) -> str:
    """The condition, in the closed language's own terms.

    Only the third form occurs in the record — "a prior successful call" —
    because response bodies are not persisted (K-83), so the other two forms
    have no rendering yet and would be dead text.

    A pattern with no contrasting success carries **no condition at all**
    (K-85). It still says so: a card that silently omitted the condition would
    read as an unconditional prohibition, and an unconditional prohibition makes
    the agent worse (`07-failure-taxonomy.tr.md`).
    """
    if card.condition is None:
        return "unknown, no successful contrast recorded"
    kind = card.condition.get("kind")
    if kind != "prior_successful_call":
        raise ValueError(f"unrenderable condition kind: {kind!r}")
    call = card.condition.get("call", "")
    state = "has succeeded" if card.condition.get("present") else "has not succeeded"
    return f"{call} {state} earlier in this episode"


def render_failure_card(card: FailureCard) -> str:
    """One failure card: five lines, the pattern's identity plus condition and count."""
    return "\n".join(
        (
            f"FAILURE {card.http_method} {card.app}.{card.api}",
            f"  fails with: {card.label}",
            f"  when: {render_condition(card)}",
            f"  arguments: {', '.join(card.argument_shape) or NO_ARGUMENTS}",
            f"  seen: {card.failure_count} times",
        )
    )


def render_card_block(
    retrieved: Retrieved,
    *,
    skill_slots: int,
    failure_slots: int,
) -> str:
    """The block that goes into the scaffold's slot.

    `skill_slots` and `failure_slots` have no defaults. They come from the
    condition configuration (`config/*.yaml`, `cards.skill_slots`), they define
    what the run measures, and a default here would quietly become the number
    (K-50, the same rule the retriever's filters follow).

    The cap keeps the retriever's own order — skills by support, failures by
    failure count — so truncation drops the weakest evidence, not an arbitrary
    tail.

    An empty block renders as the empty string: the slot then leaves no trace at
    all and the prompt stays byte-for-byte the reference prompt (K-25). A
    non-empty block carries its own trailing blank line, because
    `scaffold.render_prompt` adds nothing.
    """
    if skill_slots < 0 or failure_slots < 0:
        raise ValueError("slot counts cannot be negative")
    cards = [render_skill_card(s) for s in retrieved.skills[:skill_slots]]
    cards += [render_failure_card(f) for f in retrieved.failures[:failure_slots]]
    if not cards:
        return ""
    return "\n\n".join(cards) + "\n\n"
