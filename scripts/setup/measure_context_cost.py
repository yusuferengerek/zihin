"""What does one step's context cost, with the cards on top of it?

Stage 2 measured 5958 input tokens per step and `03-architecture.tr.md` claims the
fixed block is "roughly a fifth of the 32K budget, a quarter with the cards".
Neither number had been checked against a real card block, and the cards are the
part this project adds.

**Three numbers come out of here and all three feed the context assembler.** How
much the fixed block eats, how much the slot adds at k = 5+5, and how much window
is left for the episode's own turns. The third is the one that decides whether a
long episode survives: what the cards take, the history cannot have.

**The measurement goes through the production path.** The prompt file is written
by `scaffold.write_rendered_prompt`, read by the reference agent itself, rendered
by the agent's own template and split into messages by the agent's own
`text_to_messages`. The only line this script writes for itself is the three
template parameters, and that line is checked against a real opened world before
anything is measured: if `Task.load` and `AppWorld` disagree, the run aborts.

**Counted on the chat form, not the raw text.** The wrapper the chat template
puts around each message costs tokens too, and the window is spent on the wrapped
form.

**The sweep runs on the smallest model of the axis.** Measured in
`measure_card_tokens.py`: the three models give identical counts for every card,
so the tokenizer is a property of the family. The headline numbers are then
re-measured on the 7B for a sample, and the two are reported side by side.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/setup/measure_context_cost.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sqlite3
import statistics
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.task import Task, load_task_ids  # noqa: E402
from appworld_agents.code.simplified.react_code_agent import (  # noqa: E402
    SimplifiedReActCodeAgent,
)
from jinja2 import Template  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.cards import render_card_block  # noqa: E402
from zihin.config import load_condition_config  # noqa: E402
from zihin.model_server import count_chat_tokens, count_tokens  # noqa: E402
from zihin.records import load_model_config, open_library  # noqa: E402
from zihin.retriever import retrieve  # noqa: E402
from zihin.scaffold import write_rendered_prompt  # noqa: E402

OUTPUT = "results/context-cost.json"
FULL_CONDITION = "config/skills_failures.yaml"
SPLITS = ("train", "dev", "test_normal")
# Deterministic sample per split: every task of `dev`, and a fixed stride through
# the other two. The fixed block varies only with the task instruction, so a
# stride sample carries its spread; the size is reported with the numbers.
SAMPLE_STRIDE = {"train": 4, "dev": 1, "test_normal": 8}
# How many recorded steps are tokenised for the per-turn cost. A stride over the
# whole record rather than the first N: the first steps of an episode are the
# short ones.
TURN_SAMPLE = 240
VERIFY_TASK = "82e2fac_1"
SCRATCH_RUN = "jeton-olcumu"


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


def production_agent_config() -> object:
    """The agent configuration the recording runs use, imported not retyped."""
    path = pathlib.Path("scripts/record_run.py")
    spec = importlib.util.spec_from_file_location("record_run", path)
    if spec is None or spec.loader is None:
        sys.exit(f"{path} could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def template_parameters(task: Task) -> dict:
    """The three parameters the reference agent renders the prompt with.

    Copied from `react_code_agent.initialize`, and the copy is the reason
    `verify_against_world` exists: this is the one place where the measurement
    is not literally the production call.
    """
    app_descriptions = json.dumps(
        [{"name": k, "description": v} for (k, v) in task.app_descriptions.items()],
        indent=1,
    )
    return {
        "instruction": task.instruction,
        "main_user": task.supervisor,
        "app_descriptions": app_descriptions,
    }


def build_agent(module, base: str, tag: str, prompt_path: str) -> SimplifiedReActCodeAgent:
    config = module.agent_config(base, tag, 0, 0.2, prompt_path, 400)
    return SimplifiedReActCodeAgent(**config)


def messages_for(agent: SimplifiedReActCodeAgent, task: Task) -> list[dict[str, str]]:
    """The messages the agent would start the episode with."""
    text = Template(agent.prompt_template).render(template_parameters(task))
    text = agent.truncate_input(text) + "\n\n"
    return agent.text_to_messages(text)


def verify_against_world(module, base: str, tag: str) -> None:
    """Does the shortcut produce exactly what an opened world produces?

    The agent's own `initialize` is run against a real world and its messages are
    compared to ours. Without this the measurement would rest on a three-line
    copy of production, and this repository has already had a correction that
    never reached the caller.
    """
    from appworld import AppWorld

    prompt = str(write_rendered_prompt(f"results/prompts/{SCRATCH_RUN}__verify__seed0.txt", ""))
    agent = build_agent(module, base, tag, prompt)
    ours = messages_for(agent, Task.load(VERIFY_TASK))
    with AppWorld(task_id=VERIFY_TASK, experiment_name=SCRATCH_RUN) as world:
        agent.initialize(world)
        theirs = agent.messages
    if ours != theirs:
        sys.exit(
            "The shortcut does not produce what the agent produces; the measurement "
            f"was stopped. ours {len(ours)} messages, the agent {len(theirs)}."
        )
    print(f"production path verified: {VERIFY_TASK}, {len(ours)} messages, byte-identical")


def sampled_tasks(split: str) -> list[str]:
    every = list(load_task_ids(split))
    return every[:: SAMPLE_STRIDE[split]]


def turn_costs(connection: sqlite3.Connection, base: str, tag: str) -> dict:
    """What one recorded turn adds to the context, measured on the record.

    A turn is the model's own code plus the observation that comes back, and the
    observation is the truncated text that actually entered the context (K-17),
    not the full output on disk.
    """
    rows = list(
        connection.execute(
            "SELECT s.generated_code, o.truncated_text FROM steps s "
            "LEFT JOIN observations o ON o.step_id = s.step_id ORDER BY s.step_id"
        )
    )
    stride = max(1, len(rows) // TURN_SAMPLE)
    sample = rows[::stride]
    costs = []
    for row in sample:
        code = row[0] or ""
        observation = row[1] or ""
        costs.append(
            count_tokens(base, tag, code) + count_tokens(base, tag, observation)
            if (code or observation)
            else 0
        )
    return {
        "recorded_steps": len(rows),
        "sampled_steps": len(sample),
        "stride": stride,
        "tokens_median": statistics.median(costs),
        "tokens_mean": round(statistics.mean(costs), 1),
        "tokens_max": max(costs),
        "tokens_p90": sorted(costs)[int(0.9 * (len(costs) - 1))],
    }


def character_cap_in_tokens(connection: sqlite3.Connection, base: str, tag: str, cap: int) -> dict:
    """What the scaffold's own character cap is worth in tokens.

    The reference agent trims by **characters**, not tokens: `max_prompt_length`
    is 50000 in `scripts/record_run.py` and the trimming happens inside the
    scaffold (S-07, K-26). So the binding limit on the context may not be the
    model's window at all, and the two are in different units — which is exactly
    why the conversion has to be measured rather than assumed.

    Real recorded content is concatenated in record order until the cap is
    reached: code and observations, the mix that actually fills a context. A
    ratio taken from the instruction prompt would be the wrong text type, since
    prose and JSON tokenise differently.
    """
    text = ""
    for code, observation in connection.execute(
        "SELECT s.generated_code, o.truncated_text FROM steps s "
        "LEFT JOIN observations o ON o.step_id = s.step_id ORDER BY s.step_id"
    ):
        text += (code or "") + (observation or "")
        if len(text) >= cap:
            break
    text = text[:cap]
    tokens = count_tokens(base, tag, text)
    return {
        "character_cap": cap,
        "characters_measured": len(text),
        "tokens": tokens,
        "characters_per_token": round(len(text) / tokens, 2),
    }


def main() -> None:
    base = base_url()
    module = production_agent_config()
    models = load_model_config("config/models.yaml")
    window = models.num_ctx
    small, big = models.models[0], models.models[-1]
    condition = load_condition_config(FULL_CONDITION)

    # The library is read from the series it was mined from, not from
    # whichever series runs are being written to (K-143).
    connection, library_id, index_id = open_library()

    print(f"window {window} tokens, sweep model {small}, control model {big}")
    print(f"slots {condition.skill_slots}+{condition.failure_slots}, library {library_id}")
    verify_against_world(module, base, small)
    print()

    per_split: dict[str, dict] = {}
    for split in SPLITS:
        rows = []
        for task_id in sampled_tasks(split):
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
            task = Task.load(task_id)

            empty_path = str(
                write_rendered_prompt(f"results/prompts/{SCRATCH_RUN}__{task_id}__empty.txt", "")
            )
            card_path = str(
                write_rendered_prompt(f"results/prompts/{SCRATCH_RUN}__{task_id}__cards.txt", block)
            )
            fixed = count_chat_tokens(
                base, small, messages_for(build_agent(module, base, small, empty_path), task)
            )
            with_cards = count_chat_tokens(
                base, small, messages_for(build_agent(module, base, small, card_path), task)
            )
            rows.append(
                {
                    "task_id": task_id,
                    "cards": (
                        min(len(found.skills), condition.skill_slots)
                        + min(len(found.failures), condition.failure_slots)
                    ),
                    "fixed_block_tokens": fixed,
                    "with_cards_tokens": with_cards,
                    "card_tokens": with_cards - fixed,
                }
            )
        fixed_all = [r["fixed_block_tokens"] for r in rows]
        cards_all = [r["card_tokens"] for r in rows]
        total_all = [r["with_cards_tokens"] for r in rows]
        per_split[split] = {
            "sampled_tasks": len(rows),
            "stride": SAMPLE_STRIDE[split],
            "fixed_block": {
                "min": min(fixed_all),
                "median": statistics.median(fixed_all),
                "max": max(fixed_all),
            },
            "cards": {
                "min": min(cards_all),
                "median": statistics.median(cards_all),
                "max": max(cards_all),
            },
            "with_cards": {
                "min": min(total_all),
                "median": statistics.median(total_all),
                "max": max(total_all),
            },
            "fixed_share_of_window_median": round(statistics.median(fixed_all) / window, 4),
            "with_cards_share_of_window_median": round(statistics.median(total_all) / window, 4),
            "with_cards_share_of_window_max": round(max(total_all) / window, 4),
            "per_task": rows,
        }
        print(
            f"   {split:<12} fixed block median {statistics.median(fixed_all):>6.0f}, "
            f"card median {statistics.median(cards_all):>5.0f}, "
            f"total median {statistics.median(total_all):>6.0f} "
            f"({statistics.median(total_all) / window:.1%} of the window), max {max(total_all)}"
        )
    print()

    # Control on the largest model: the sweep's claim is that the family shares a
    # tokenizer, and a claim used to justify a shortcut gets checked.
    control = []
    for split in SPLITS:
        first = per_split[split]["per_task"][0]
        task = Task.load(first["task_id"])
        path = f"results/prompts/{SCRATCH_RUN}__{first['task_id']}__cards.txt"
        agent = build_agent(module, base, big, path)
        control.append(
            {
                "task_id": first["task_id"],
                "small_model_tokens": first["with_cards_tokens"],
                "big_model_tokens": count_chat_tokens(base, big, messages_for(agent, task)),
            }
        )
    agree = all(c["small_model_tokens"] == c["big_model_tokens"] for c in control)
    print(f"do the two models give the same count: {agree}")
    for c in control:
        print(
            f"   {c['task_id']:<12} {small.split(':')[1]}: {c['small_model_tokens']}, "
            f"{big.split(':')[1]}: {c['big_model_tokens']}"
        )
    print()

    print("--- per-turn cost from the record ---")
    turns = turn_costs(connection, base, small)
    print(
        f"   {turns['sampled_steps']}/{turns['recorded_steps']} steps sampled "
        f"(stride {turns['stride']}): median {turns['tokens_median']:.0f}, "
        f"ortalama {turns['tokens_mean']}, p90 {turns['tokens_p90']}, "
        f"max {turns['tokens_max']} tokens"
    )

    # How many turns the remaining window holds. Three turn sizes, because the
    # median hides the case that actually overflows: observation size is heavily
    # skewed (K-17 truncates at 8192 bytes) and one p90 turn costs six median
    # ones. Both the empty-slot and the full-slot case are given, because the
    # difference is exactly what the cards cost the history.
    headroom = {}
    for split in SPLITS:
        fixed = per_split[split]["fixed_block"]["median"]
        full = per_split[split]["with_cards"]["median"]
        sizes = {
            "median_turn": turns["tokens_median"] or 1,
            "mean_turn": turns["tokens_mean"] or 1,
            "p90_turn": turns["tokens_p90"] or 1,
        }
        headroom[split] = {
            "window": window,
            "free_without_cards": window - fixed,
            "free_with_cards": window - full,
            "turns": {
                name: {
                    "turn_tokens": size,
                    "without_cards": int((window - fixed) / size),
                    "with_cards": int((window - full) / size),
                }
                for name, size in sizes.items()
            },
        }
        row = ", ".join(
            f"{name.replace('_turn', '')} turnde "
            f"{headroom[split]['turns'][name]['without_cards']}→"
            f"{headroom[split]['turns'][name]['with_cards']}"
            for name in ("median_turn", "mean_turn", "p90_turn")
        )
        print(f"   {split:<12} turns that fit, no cards -> cards: {row}")
    print()

    print("--- the scaffold own character ceiling ---")
    cap = character_cap_in_tokens(
        connection,
        base,
        small,
        module.agent_config(base, small, 0, 0.2, "x", 400)["max_prompt_length"],
    )
    print(
        f"   {cap['character_cap']} characters = {cap['tokens']} tokens "
        f"({cap['characters_per_token']} characters/token), "
        f"{100 * cap['tokens'] / window:.1f}% of the window"
    )

    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {
                "window": window,
                "sweep_model": small,
                "control_model": big,
                "library_id": library_id,
                "index_id": index_id,
                "skill_slots": condition.skill_slots,
                "failure_slots": condition.failure_slots,
                "verified_against_world": VERIFY_TASK,
                "splits": per_split,
                "model_control": control,
                "models_agree": agree,
                "turn_cost": turns,
                "headroom": headroom,
                "scaffold_character_cap": cap,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nwritten: {OUTPUT}")


if __name__ == "__main__":
    main()
