"""Runs a single AppWorld task end to end under the reference agent scaffold.

It exists for stage 1's acceptance criterion: does the task start, does the agent
call the API, does the verifier return a verdict. The scaffold is untouched —
`SimplifiedReActCodeAgent` is constructed as-is and we only supply the
configuration.

Model serving is stage 4's subject. Here the smallest model is used, only to see
that the environment is up.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/run_single_task.py

`MODEL_SERVER_URL` is the scaffold's own variable; it fills the template in the
`base_url` field. We do not define a second variable of our own.
"""

from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")

from appworld import load_task_ids  # noqa: E402
from appworld.common.path_store import path_store  # noqa: E402
from appworld.evaluator import evaluate_dataset  # noqa: E402
from appworld_agents.code.simplified.react_code_agent import (  # noqa: E402
    SimplifiedReActCodeAgent,
)

# The smallest of stage 4's three models. Stage 1 wants the fastest, so rather
# than pulling a separate model the small one from the target set is used.
MODEL_ETIKETI = "qwen2.5-coder:1.5b-instruct-q4_K_M"

EXPERIMENT_NAME = "asama-1-tek-gorev"
SPLIT = "train"


def ollama_base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit(
            "MODEL_SERVER_URL is not defined. Under WSL mirrored networking, Ollama on "
            "Windows is visible at http://127.0.0.1:11434."
        )
    return address.rstrip("/")


def agent_config(base_url: str) -> dict:
    instruction_file = os.path.join(
        os.path.dirname(__import__("appworld_agents").__file__),
        "prompts",
        "react_code_agent",
        "instructions.txt",
    )
    return {
        "model_config": {
            # litellm's ollama_chat provider; the scaffold uses the litellm
            # client by default.
            #
            # The scaffold derives which keys may pass from the
            # `litellm.completion` signature and applies a whitelist. `base_url`
            # is on the list, `api_base` is not. `num_ctx` is not on it either —
            # so K-19's first route cannot pass the context window through. That
            # is for stage 4 to solve; stage 1 only sees that the environment is
            # up.
            "name": f"ollama_chat/{MODEL_ETIKETI}",
            "base_url": base_url,
            "temperature": 0.2,
            "seed": 123,
            "max_tokens": 400,
            "stop": ["```\n"],
            "use_cache": False,
            "retry_after_n_seconds": 5,
            "max_retries": 3,
            # A local model, we are not measuring money; the field is mandatory
            # so it is zeroed.
            "cost_per_token": {
                "input_cache_miss": 0.0,
                "input_cache_hit": 0.0,
                "input_cache_write": 0.0,
                "output": 0.0,
            },
        },
        "appworld_config": {"random_seed": 123},
        "logger_config": {"color": False, "verbose": True},
        "prompt_file_path": instruction_file,
        "max_prompt_length": 50000,
        "max_output_length": 20000,
        "max_steps": 20,
    }


def _row_count(path: str) -> int | str:
    if not os.path.exists(path):
        return "no file"
    with open(path, encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def main() -> None:
    # The scaffold constructs an `OpenAI()` object in its constructor even when
    # the client is litellm, and that object does not open without a key. On a
    # local model no key is used, so a placeholder is enough; no call goes to a
    # real provider.
    os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

    base_url = ollama_base_url()
    task_id = os.environ.get("ZIHIN_TASK_ID") or load_task_ids(SPLIT)[0]

    print(f"task       : {task_id}")
    print(f"model      : {MODEL_ETIKETI}")
    print(f"server     : {base_url}")
    print(f"experiment name : {EXPERIMENT_NAME}")

    agent = SimplifiedReActCodeAgent(**agent_config(base_url))
    agent.solve_tasks(task_ids=[task_id], experiment_name=EXPERIMENT_NAME)

    # `solve_tasks` does not run the evaluation; the CLI's `appworld evaluate`
    # command calls the same function.
    evaluate_dataset(
        experiment_name=EXPERIMENT_NAME,
        dataset_name=None,
        task_id=task_id,
        suppress_errors=True,
        include_details=True,
        aggregate_only=False,
        save_reports=True,
        print_report=True,
    )

    rapor = os.path.join(
        path_store.experiment_outputs, EXPERIMENT_NAME, "tasks", task_id, "evaluation", "report.md"
    )
    calls = os.path.join(
        path_store.experiment_outputs, EXPERIMENT_NAME, "tasks", task_id, "logs", "api_calls.jsonl"
    )

    print(f"\nAPI call count     : {_row_count(calls)}")
    print(f"verifier report    : {rapor}")
    print("verdict file       : " + ("present" if os.path.exists(rapor) else "ABSENT"))


if __name__ == "__main__":
    main()
