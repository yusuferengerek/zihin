"""Is there seed control, and what does the trajectory vary with?

The measurement that closes S-11. It looks at two layers.

The first layer is token level: the same prompt, the same seed, one call with the
model unloaded and two with it warm. If the cold call diverges from the warm ones
but is stable within itself, what we have is not randomness but two separate
deterministic regimes.

The second layer is episode level: the same task is run twice in the cold regime
and twice in the warm one, and the digest of the whole trajectory is compared.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/check_determinism.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402
from appworld_agents.code.simplified.react_code_agent import (  # noqa: E402
    SimplifiedReActCodeAgent,
)

TAG = "qwen2.5-coder:1.5b-instruct-q4_K_M"
TASK = "82e2fac_1"
SEED = 123
ISTEM = (
    "Write a short Python function that returns the three most common words in "
    "a string. Explain your choice of data structure in two sentences."
)


def base() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


BASE = base()


def request(body: dict, path: str) -> dict:
    ham = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        f"{BASE}{path}", data=ham, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(r, timeout=600) as response:
        return json.load(response)


def unload() -> None:
    request({"model": TAG, "messages": [], "keep_alive": 0}, "/api/chat")
    time.sleep(3)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def single_call() -> str:
    response = request(
        {
            "model": TAG,
            "messages": [{"role": "user", "content": ISTEM}],
            "stream": False,
            "options": {"temperature": 0.2, "seed": SEED, "num_predict": 300},
        },
        "/api/chat",
    )
    return digest(response["message"]["content"])


def agent_config() -> dict:
    import appworld_agents

    instruction = os.path.join(
        os.path.dirname(appworld_agents.__file__),
        "prompts",
        "react_code_agent",
        "instructions.txt",
    )
    return {
        "model_config": {
            "name": f"ollama_chat/{TAG}",
            "base_url": BASE,
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
        "max_steps": 20,
    }


def episode(experiment: str) -> tuple[int, str]:
    agent = SimplifiedReActCodeAgent(**agent_config())
    agent.solve_tasks(task_ids=[TASK], experiment_name=experiment)
    root = os.path.join(path_store.experiment_outputs, experiment, "tasks", TASK)
    with open(os.path.join(root, "logs", "api_calls.jsonl"), encoding="utf-8") as f:
        call = sum(1 for s in f if s.strip())
    with open(os.path.join(root, "logs", "environment_io.md"), encoding="utf-8") as f:
        trajectory = f.read()
    return call, digest(trajectory)


def main() -> None:
    print("=== first layer: token level ===")
    unload()
    soguk = single_call()
    isinmis_1 = single_call()
    isinmis_2 = single_call()
    print(f"  cold     {soguk}")
    print(f"  warm     {isinmis_1}")
    print(f"  warm     {isinmis_2}")
    print(f"  are the two warm calls equal   : {isinmis_1 == isinmis_2}")
    print(f"  does cold diverge from warm    : {soguk != isinmis_1}")

    print("\n=== second layer: episode level ===")
    result = {}
    for kind, rejim in enumerate(["soguk", "isinmis", "soguk", "isinmis"], 1):
        if rejim == "soguk":
            unload()
        call, trace = episode(f"determinizm-{kind}")
        result.setdefault(rejim, []).append((call, trace))
        print(f"  {kind}. {rejim:8} API={call:3}  trajectory={trace}")

    soguklar = result["soguk"]
    isinmislar = result["isinmis"]
    print(f"\n  are the two cold runs equal : {soguklar[0] == soguklar[1]}")
    print(f"  are the two warm runs equal : {isinmislar[0] == isinmislar[1]}")
    print(f"  do the regimes differ       : {soguklar[0] != isinmislar[0]}")

    tutarli = soguklar[0] == soguklar[1] and isinmislar[0] == isinmislar[1]
    if tutarli and soguklar[0] != isinmislar[0]:
        print(
            "\nVERDICT: seed control exists, the episode is deterministic, two regimes are present."
        )
    elif tutarli:
        print("\nVERDICT: seed control exists, the regime difference does not reach the episode.")
    else:
        print("\nVERDICT: the episode is not deterministic, there is an unexplained source.")
        sys.exit(1)


if __name__ == "__main__":
    main()
