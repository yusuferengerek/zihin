"""Do the real cards fit their declared token budgets?

The format claims a skill card is seven fields and at most 180 tokens, and a
failure card five fields and at most 120. Both numbers were written before a
single card existed, and neither had ever been checked against one.

**A card over budget means the format is wrong, not the budget.** The budget is
the context assembler's input: the slot has `skill_slots + failure_slots` places
and the fixed block already eats a fifth of the window
(`03-architecture.tr.md`). A format that overflows would silently take that space
from the episode's own history.

**Counted by the model's own tokenizer**, through the server that will serve the
pilot (`model_server.count_tokens`). Bytes divided by four would be an estimate,
and the thing being tested is a token budget.

**All three models on the scale axis are measured**, not to compare them but to
show the count is a property of the family: if the three disagree, "180 tokens"
does not name one number and the budget has to say which model it means.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/setup/measure_card_tokens.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sqlite3
import statistics
import sys
import warnings

warnings.filterwarnings("ignore")

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.cards import (  # noqa: E402
    FAILURE_CARD_FIELDS,
    FAILURE_CARD_TOKEN_BUDGET,
    SKILL_CARD_FIELDS,
    SKILL_CARD_TOKEN_BUDGET,
    render_card_block,
    render_failure_card,
    render_skill_card,
)
from zihin.config import load_condition_config  # noqa: E402
from zihin.model_server import count_tokens  # noqa: E402
from zihin.records import load_model_config, open_library  # noqa: E402
from zihin.retriever import retrieve  # noqa: E402

OUTPUT = "results/card-tokens.json"
SPLITS = ("train", "dev", "test_normal")
FULL_CONDITION = "config/skills_failures.yaml"


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


def every_card(connection: sqlite3.Connection, library_id: str, index_id: str) -> tuple[dict, dict]:
    """Every card the retriever can hand to any task, collected once.

    Retrieval is the production path and it is task-scoped, so the union over all
    tasks is taken rather than the tables read directly. A card no task retrieves
    cannot reach a model, and the count of those is reported: a budget check that
    silently skipped cards would be measuring the wrong set.
    """
    skills: dict[str, object] = {}
    failures: dict[str, object] = {}
    for split in SPLITS:
        for task_id in load_task_ids(split):
            try:
                instruction = task_instruction(task_id)
            except FileNotFoundError:
                continue
            found = retrieve(
                connection,
                instruction,
                library_id=library_id,
                index_id=index_id,
                min_expected_saving=0,
                max_discriminating_conditions=None,
                include_unverified_cards=True,
                task_id=task_id,
            )
            for card in found.skills:
                skills.setdefault(card.skill_id, card)
            for card in found.failures:
                failures.setdefault(card.pattern_id, card)
    return skills, failures


def unreachable(connection: sqlite3.Connection, library_id: str, index_id: str, seen) -> dict:
    """Rows in the projections that no task retrieved."""
    skills_seen, failures_seen = seen
    all_skills = {
        r[0]
        for r in connection.execute(
            "SELECT skill_id FROM skills WHERE library_id = ?", (library_id,)
        )
    }
    all_failures = {
        r[0]
        for r in connection.execute(
            "SELECT pattern_id FROM failure_patterns WHERE index_id = ?", (index_id,)
        )
    }
    return {
        "skills": sorted(all_skills - set(skills_seen)),
        "failures": sorted(all_failures - set(failures_seen)),
    }


def measure(base: str, tags: list[str], texts: dict[str, str]) -> dict[str, dict[str, int]]:
    """Token count of every text, under every model on the axis."""
    counts: dict[str, dict[str, int]] = {}
    for tag in tags:
        counts[tag] = {name: count_tokens(base, tag, text) for name, text in texts.items()}
        print(f"   {tag}: {len(counts[tag])} texts measured")
    return counts


def main() -> None:
    base = base_url()
    models = load_model_config("config/models.yaml").models
    condition = load_condition_config(FULL_CONDITION)
    # The library is read from the series it was mined from, not from
    # whichever series runs are being written to (K-143).
    connection, library_id, index_id = open_library()

    skills, failures = every_card(connection, library_id, index_id)
    missed = unreachable(connection, library_id, index_id, (skills, failures))
    print(f"library {library_id}, index {index_id}")
    print(f"retrievable cards: {len(skills)} skills, {len(failures)} failures")
    print(f"rows no task retrieves: {len(missed['skills'])} skills, {len(missed['failures'])} hata")
    print(
        f"slot: {condition.skill_slots} beceri + {condition.failure_slots} hata ({FULL_CONDITION})"
    )
    print()

    texts = {f"skill:{k}": render_skill_card(v) for k, v in skills.items()}
    texts.update({f"failure:{k}": render_failure_card(v) for k, v in failures.items()})

    print("--- token counts ---")
    counts = measure(base, list(models), texts)
    print()

    # The budget is per card type. The largest model on the axis carries the
    # headline number, and the disagreement across models is reported next to it.
    biggest = models[-1]
    rows = []
    for name, text in sorted(texts.items()):
        kind, _, card_id = name.partition(":")
        budget = SKILL_CARD_TOKEN_BUDGET if kind == "skill" else FAILURE_CARD_TOKEN_BUDGET
        expected_fields = SKILL_CARD_FIELDS if kind == "skill" else FAILURE_CARD_FIELDS
        per_model = {tag: counts[tag][name] for tag in models}
        rows.append(
            {
                "kind": kind,
                "card_id": card_id,
                "fields": len(text.splitlines()),
                "expected_fields": expected_fields,
                "bytes": len(text.encode("utf-8")),
                "tokens": per_model[biggest],
                "tokens_per_model": per_model,
                "budget": budget,
                "over_budget": per_model[biggest] > budget,
                "models_agree": len(set(per_model.values())) == 1,
            }
        )

    for kind, budget in (
        ("skill", SKILL_CARD_TOKEN_BUDGET),
        ("failure", FAILURE_CARD_TOKEN_BUDGET),
    ):
        subset = [r for r in rows if r["kind"] == kind]
        tokens = [r["tokens"] for r in subset]
        over = [r for r in subset if r["over_budget"]]
        print(f"--- {kind} card, budget <={budget} tokens ---")
        print(f"   cards       : {len(subset)}")
        print(
            f"   tokens      : at least {min(tokens)}, median "
            f"{statistics.median(tokens):.0f}, max {max(tokens)}"
        )
        print(f"   field count : {sorted({r['fields'] for r in subset})}")
        print(
            f"   over budget : {len(over)}" + (f" → {[r['card_id'] for r in over]}" if over else "")
        )
        print()

    disagreeing = [r["card_id"] for r in rows if not r["models_agree"]]
    print(
        f"do the three models give the same count: {not disagreeing}"
        + (f" (disagreeing: {disagreeing})" if disagreeing else "")
    )
    print()

    # The block: what one task's slot actually costs at k = skill_slots +
    # failure_slots, measured over the real retrieved sets rather than a
    # constructed worst case.
    print(f"--- k = {condition.skill_slots}+{condition.failure_slots} ile blok maliyeti ---")
    blocks: dict[str, dict] = {}
    for split in SPLITS:
        per_task = []
        for task_id in load_task_ids(split):
            try:
                instruction = task_instruction(task_id)
            except FileNotFoundError:
                continue
            found = retrieve(
                connection,
                instruction,
                library_id=library_id,
                index_id=index_id,
                min_expected_saving=0,
                max_discriminating_conditions=None,
                include_unverified_cards=True,
                task_id=task_id,
            )
            block = render_card_block(
                found, skill_slots=condition.skill_slots, failure_slots=condition.failure_slots
            )
            per_task.append(
                {
                    "task_id": task_id,
                    "skill_cards": min(len(found.skills), condition.skill_slots),
                    "failure_cards": min(len(found.failures), condition.failure_slots),
                    "tokens": count_tokens(base, biggest, block),
                    "bytes": len(block.encode("utf-8")),
                }
            )
        tokens = [t["tokens"] for t in per_task]
        filled = [t for t in per_task if t["tokens"] > 0]
        blocks[split] = {
            "tasks": len(per_task),
            "tokens_min": min(tokens),
            "tokens_median": statistics.median(tokens),
            "tokens_max": max(tokens),
            "empty_blocks": len(per_task) - len(filled),
            "per_task": per_task,
        }
        print(
            f"   {split:<12} en az {min(tokens):>4}, median {statistics.median(tokens):>6.0f}, "
            f"max {max(tokens):>4} tokens; empty blocks {len(per_task) - len(filled)}"
        )
    print()

    # Additivity: does the block cost the sum of its cards, or does joining them
    # cost something? The answer decides whether a per-card budget bounds a block.
    worst_split = max(blocks, key=lambda s: blocks[s]["tokens_max"])
    worst = max(blocks[worst_split]["per_task"], key=lambda t: t["tokens"])
    print(
        f"most expensive block: {worst['task_id']} ({worst_split}), {worst['tokens']} tokens, "
        f"{worst['skill_cards']} skill + {worst['failure_cards']} failure cards"
    )
    ceiling = (
        condition.skill_slots * SKILL_CARD_TOKEN_BUDGET
        + condition.failure_slots * FAILURE_CARD_TOKEN_BUDGET
    )
    print(f"combined ceiling of the budgets: {ceiling} tokens")

    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {
                "library_id": library_id,
                "index_id": index_id,
                "condition_config": FULL_CONDITION,
                "skill_slots": condition.skill_slots,
                "failure_slots": condition.failure_slots,
                "models": list(models),
                "headline_model": biggest,
                "budgets": {
                    "skill": SKILL_CARD_TOKEN_BUDGET,
                    "failure": FAILURE_CARD_TOKEN_BUDGET,
                },
                "block_budget_ceiling": ceiling,
                "cards": rows,
                "unreachable_rows": missed,
                "blocks": blocks,
                "rendered": {name: text for name, text in sorted(texts.items())},
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nwritten: {OUTPUT}")

    over = [r for r in rows if r["over_budget"]]
    if over:
        sys.exit(
            f"{len(over)} cards are over budget: {[r['card_id'] for r in over]}. "
            "That means the format is wrong; the fix belongs to item 6."
        )


if __name__ == "__main__":
    main()
