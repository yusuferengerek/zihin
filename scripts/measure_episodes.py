"""Stage 2's measurement run.

Runs a fixed number of tasks under the reference scaffold and writes the raw
numbers for every episode into a JSON file. The fourth and seventh questions in
the facts report are computed from this output.

Whether the model was loaded in memory before the episode started is recorded as
well. The reason is a measured fact: the first inference after a cold load gives
output that differs from the warm state but is stable within itself. Without that
distinction recorded, the difference between episodes looks like randomness.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/measure_episodes.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
import warnings

warnings.filterwarnings("ignore")

from appworld import load_task_ids  # noqa: E402
from appworld.common.path_store import path_store  # noqa: E402
from appworld_agents.code.simplified.react_code_agent import (  # noqa: E402
    SimplifiedReActCodeAgent,
)

MODEL_ETIKETI = "qwen2.5-coder:1.5b-instruct-q4_K_M"
SPLIT = "train"
EXPERIMENT_PREFIX = "asama-2-olcum"
TASK_COUNT = int(os.environ.get("ZIHIN_TASK_COUNT", "12"))
MAX_STEPS = 20
SEED = 123
OUTPUT = "experiments/outputs/asama-2-olcum-ozet.json"


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


def model_yuklu_mu(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base}/api/ps", timeout=30) as response:
            return bool(json.load(response).get("models"))
    except Exception:
        return False


def effective_context(base: str) -> int | None:
    """The effective context window of the model on the server.

    This is A-05's verification condition. If the server restarts without the
    environment variable the value falls silently back to 4096, so it is checked
    once per run.
    """
    try:
        with urllib.request.urlopen(f"{base}/api/ps", timeout=30) as response:
            models = json.load(response).get("models") or []
    except Exception:
        return None
    for m in models:
        if m.get("name", "").startswith(MODEL_ETIKETI.split(":")[0]):
            return m.get("context_length")
    return None


def agent_config(base: str) -> dict:
    import appworld_agents

    instruction = os.path.join(
        os.path.dirname(appworld_agents.__file__),
        "prompts",
        "react_code_agent",
        "instructions.txt",
    )
    return {
        "model_config": {
            "name": f"ollama_chat/{MODEL_ETIKETI}",
            "base_url": base,
            "temperature": 0.2,
            "seed": SEED,
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
        "appworld_config": {"random_seed": SEED},
        "logger_config": {"color": False, "verbose": False},
        "prompt_file_path": instruction,
        "max_prompt_length": 50000,
        "max_output_length": 20000,
        "max_steps": MAX_STEPS,
    }


def episode_measurement(experiment: str, task_id: str) -> dict:
    root = os.path.join(path_store.experiment_outputs, experiment, "tasks", task_id)

    call_log_path = os.path.join(root, "logs", "api_calls.jsonl")
    calls = []
    if os.path.exists(call_log_path):
        with open(call_log_path, encoding="utf-8") as handle:
            for row in handle:
                row = row.strip()
                if row:
                    calls.append(json.loads(row))

    # The step count comes from the interaction headings inside environment_io.md.
    io_yolu = os.path.join(root, "logs", "environment_io.md")
    step = 0
    if os.path.exists(io_yolu):
        with open(io_yolu, encoding="utf-8") as handle:
            step = sum(1 for s in handle if s.startswith("### Environment Interaction"))

    kullanim_yolu = os.path.join(root, "misc", "usage.json")
    kullanim = {}
    if os.path.exists(kullanim_yolu):
        with open(kullanim_yolu, encoding="utf-8") as handle:
            kullanim = json.load(handle)

    return {
        "task_id": task_id,
        "step_count": step,
        "api_cagrisi": len(calls),
        "farkli_api": len({(c.get("method"), c.get("url")) for c in calls}),
        "tokenlar": kullanim.get("tokens", {}),
    }


def main() -> None:
    os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")
    base = base_url()

    tasks = load_task_ids(SPLIT)[:TASK_COUNT]
    print(f"split={SPLIT}  episodes={len(tasks)}  model={MODEL_ETIKETI}")
    print(f"effective context window: {effective_context(base)}")

    measurements = []
    for index, task_id in enumerate(tasks, 1):
        experiment = f"{EXPERIMENT_PREFIX}-{task_id}"
        soguk = not model_yuklu_mu(base)
        basla = time.monotonic()

        agent = SimplifiedReActCodeAgent(**agent_config(base))
        agent.solve_tasks(task_ids=[task_id], experiment_name=experiment)

        measurement = episode_measurement(experiment, task_id)
        measurement["index"] = index
        measurement["soguk_baslangic"] = soguk
        measurement["sure_saniye"] = round(time.monotonic() - basla, 1)
        measurements.append(measurement)

        print(
            f"  {index:2}/{len(tasks)}  {task_id:12}  "
            f"steps={measurement['step_count']:2}  API={measurement['api_cagrisi']:3}  "
            f"cold={'yes' if soguk else 'no'}  {measurement['sure_saniye']}s"
        )

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "model": MODEL_ETIKETI,
                "bolme": SPLIT,
                "seed": SEED,
                "max_adim": MAX_STEPS,
                "effective_context": effective_context(base),
                "episodes_with_steps": measurements,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nsummary written: {OUTPUT}")


if __name__ == "__main__":
    main()
