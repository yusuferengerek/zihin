"""Stage 5's acceptance criterion: does an empty slot change the trajectory?

Same task, same seed, same model. One episode runs with the reference prompt and
one with the slotted prompt, and the whole trajectories are compared. If there is
a difference, where it sits is printed.

Both run in the cold regime. The reason was measured: the load state changes the
trajectory (S-13). Without the regime pinned, this check would measure the load
state rather than the slot.

The per-model load time is measured here too; K-21's final decision rests on that
bakacak.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/verify_slot.py
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import statistics
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402
from appworld_agents.code.simplified.react_code_agent import (  # noqa: E402
    SimplifiedReActCodeAgent,
)

from zihin.model_server import (  # noqa: E402
    kernel_clock,
    load_model,
    unload_model,
    vram_footprint,
)
from zihin.records import load_model_config, load_recording_limits  # noqa: E402
from zihin.scaffold import (  # noqa: E402
    REFERENCE_PROMPT,
    load_scaffold_config,
    write_rendered_prompt,
)

TASK = os.environ.get("ZIHIN_TASK_ID", "82e2fac_1")
MAX_STEPS = 20
OUTPUT = "results/asama-5-slot-dogrulamasi.json"
MAX_PROMPT_CHARACTERS = load_recording_limits("config/recording.yaml").max_prompt_characters


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


BASE = base_url()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def agent_config(tag: str, seed: int, temperature: float, instruction: str) -> dict:
    return {
        "model_config": {
            "name": f"ollama_chat/{tag}",
            "base_url": BASE,
            "temperature": temperature,
            "seed": seed,
            "max_tokens": 400,
            "stop": ["```\n"],
            "use_cache": False,
            "retry_after_n_seconds": 5,
            "max_retries": 3,
            "cost_per_token": {
                "input_cache_miss": 0.0,
                "input_cache_hit": 0.0,
                "input_cache_write": 0.0,
                "output": 0.0,
            },
        },
        "appworld_config": {"random_seed": seed % (2**31)},
        "logger_config": {"color": False, "verbose": False},
        "prompt_file_path": instruction,
        # The character ceiling comes from the configuration (S-47): this check
        # claims the two prompts give the same trajectory, and with a different
        # ceiling the claim would be made for a different regime.
        "max_prompt_length": (None if MAX_PROMPT_CHARACTERS == -1 else MAX_PROMPT_CHARACTERS),
        "max_output_length": 20000,
        "max_steps": MAX_STEPS,
    }


def run(experiment: str, tag: str, seed: int, temperature: float, instruction: str) -> dict:
    unload_model(BASE, tag)
    load = load_model(BASE, tag)
    unload_model(BASE, tag)

    started = kernel_clock()
    agent = SimplifiedReActCodeAgent(**agent_config(tag, seed, temperature, instruction))
    agent.solve_tasks(task_ids=[TASK], experiment_name=experiment)
    elapsed = kernel_clock() - started

    root = os.path.join(path_store.experiment_outputs, experiment, "tasks", TASK, "logs")
    with open(os.path.join(root, "environment_io.md"), encoding="utf-8") as handle:
        trajectory = handle.read()
    call = 0
    call_log_path = os.path.join(root, "api_calls.jsonl")
    if os.path.exists(call_log_path):
        with open(call_log_path, encoding="utf-8") as handle:
            call = sum(1 for s in handle if s.strip())
    return {
        "trajectory": trajectory,
        "digest": digest(trajectory),
        "api_cagrisi": call,
        "sure_saniye": round(elapsed, 1),
        "yukleme_saniye": round(load, 2),
    }


def main() -> None:
    config = load_model_config("config/models.yaml")
    iskele = load_scaffold_config("config/scaffold.yaml")
    tag = config.models[0]
    seed = config.seed_for(TASK, 0)

    os.makedirs("results", exist_ok=True)
    slotted_path = write_rendered_prompt("results/asama-5-slotlu-instructions.txt", "")

    print(f"task={TASK}  model={tag}  seed={seed}  slot={iskele.slot_position}")
    print(f"referans prompt: {REFERENCE_PROMPT}")
    print(f"empty-slot prompt: {slotted_path}")

    with open(REFERENCE_PROMPT, encoding="utf-8") as handle:
        reference_text = handle.read()
    slotted_text = slotted_path.read_text(encoding="utf-8")
    bytes_identical = reference_text == slotted_text
    print(f"\nis the prompt byte-identical: {bytes_identical}")
    if not bytes_identical:
        sys.exit(
            "The empty-slot prompt diverges from the reference; the behaviour check is not run."
        )

    for experiment in ("asama-5-referans", "asama-5-slotlu"):
        path = os.path.join(path_store.experiment_outputs, experiment)
        if os.path.isdir(path):
            import shutil

            shutil.rmtree(path)

    reference = run("asama-5-referans", tag, seed, config.temperature, str(REFERENCE_PROMPT))
    slotlu = run("asama-5-slotlu", tag, seed, config.temperature, str(slotted_path))

    print(f"\nreference : {reference['api_cagrisi']} API calls, trajectory {reference['digest']}")
    print(f"slotted   : {slotlu['api_cagrisi']} API calls, trajectory {slotlu['digest']}")

    identical = reference["trajectory"] == slotlu["trajectory"]
    print(f"\nare the trajectories identical: {identical}")
    if not identical:
        print("\n=== fark ===")
        difference = list(
            difflib.unified_diff(
                reference["trajectory"].splitlines(),
                slotlu["trajectory"].splitlines(),
                fromfile="referans",
                tofile="slotlu",
                lineterm="",
                n=2,
            )
        )
        for line in difference[:60]:
            print(" ", line)
        print(f"  (total {len(difference)} differing lines)")

    print("\n=== load time per model ===")
    load_times = {}
    for m in config.models:
        measurements = []
        for _ in range(3):
            unload_model(BASE, m)
            measurements.append(load_model(BASE, m))
        footprint = vram_footprint(BASE, m)
        unload_model(BASE, m)
        load_times[m] = {
            "medyan_saniye": round(statistics.median(measurements), 2),
            "olcumler": [round(o, 2) for o in measurements],
            "vram_gib": footprint.get("vram_gib"),
        }
        print(
            f"  {m:38} median={load_times[m]['medyan_saniye']:5.2f}s  "
            f"measurements={load_times[m]['olcumler']}  VRAM={footprint.get('vram_gib')} GiB"
        )

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "task": TASK,
                "model": tag,
                "seed": seed,
                "slot_position": iskele.slot_position,
                "prompt_bayt_ayni": bytes_identical,
                "yorungeler_ayni": identical,
                "referans": {k: v for k, v in reference.items() if k != "trajectory"},
                "slotlu": {k: v for k, v in slotlu.items() if k != "trajectory"},
                "yukleme_sureleri": load_times,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nsummary written: {OUTPUT}")
    if not identical:
        sys.exit(1)


if __name__ == "__main__":
    main()
