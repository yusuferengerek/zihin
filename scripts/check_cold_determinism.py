"""Measures residual variance in the cold regime and classifies the steps.

This started out as a pass/fail gate: if uniformity did not hold, determinism was
to be abandoned. The rule changed (K-51). Determinism is not an analysis
assumption; the analysis's only real dependency is the noise rule in regression
detection. Rather than picking one of two binary assumptions, residual variance
is now measured per model and added to the noise floor.

Two things are measured.

The first is residual variance: the same (task, seed, condition, model) quadruple
is repeated N times and the number of distinct trajectories is counted. If 1.5B
and 3B come out at zero, their contribution is zero by itself; whatever 7B
produces enters the arithmetic.

The second is a step taxonomy: the steps of zero-call episodes are distributed
over K-36's five categories. "The model is weak" and "the model makes one
specific mistake systematically on this scaffold" are different diagnoses, and
the second one may be fixable.

The difference between seeds has to remain, because that is where the variance
estimate comes from. That is why one more episode is run with a second seed.

The model is unloaded before every episode and the unload is verified (K-21's
second condition).

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/check_cold_determinism.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import warnings
from collections import Counter

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402

from zihin.api_capture import capturing  # noqa: E402
from zihin.model_server import is_loaded, kernel_clock, unload_model  # noqa: E402
from zihin.recording_agent import NoProgress, RecordingAgent, step_category  # noqa: E402
from zihin.records import load_model_config, load_recording_limits  # noqa: E402
from zihin.scaffold import write_rendered_prompt  # noqa: E402

TASK = os.environ.get("ZIHIN_TASK_ID", "82e2fac_1")
REPEATS = int(os.environ.get("ZIHIN_REPEATS", "10"))
# The models can be run one at a time. The reason is practical: all three
# together run past half an hour, and a single-piece run hits session limits. The
# results are written to one file per model and merged at the end.
MODEL_FILTER = os.environ.get("ZIHIN_MODEL", "")
MAX_STEPS = 20
OUTPUT_DIR = "results/determinizm"
# The measurement is taken in the regime the experiment will run in: stopping
# rule on. Measured with the rule off, the resulting noise floor would describe
# longer episodes that spin up to the ceiling, not the episodes to be analysed.
NO_PROGRESS_LIMIT = load_recording_limits("config/recording.yaml").no_progress_limit
# The scaffold's character ceiling comes from the configuration too (S-47). Had
# a number stayed written here, this diagnostic would run with the old context
# length once the ceiling changed, and the noise floor it produced would not
# describe the regime the experiment runs in.
MAX_PROMPT_CHARACTERS = load_recording_limits("config/recording.yaml").max_prompt_characters


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not set.")
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
        "max_prompt_length": None if MAX_PROMPT_CHARACTERS == -1 else MAX_PROMPT_CHARACTERS,
        "max_output_length": 20000,
        "max_steps": MAX_STEPS,
    }


def one_episode(tag: str, seed: int, temperature: float, experiment: str, instruction: str) -> dict:
    path = os.path.join(path_store.experiment_outputs, experiment)
    if os.path.isdir(path):
        shutil.rmtree(path)

    unload_model(BASE, tag)
    unloaded = not is_loaded(BASE, tag)

    started = kernel_clock()
    with capturing() as capture:
        agent = RecordingAgent(
            experiment_name=experiment,
            capture=capture,
            probe_state=True,
            no_progress_limit=NO_PROGRESS_LIMIT,
            **agent_config(tag, seed, temperature, instruction),
        )
        try:
            agent.solve_tasks(task_ids=[TASK], experiment_name=experiment)
        except NoProgress:
            pass
    elapsed = kernel_clock() - started

    root = os.path.join(path_store.experiment_outputs, experiment, "tasks", TASK, "logs")
    with open(os.path.join(root, "environment_io.md"), encoding="utf-8") as handle:
        trajectory = handle.read()

    captured = sum(len(a["captured"] or []) for a in agent.steps)
    from_log = sum(len(a["actions"]) for a in agent.steps)
    statuses = Counter(c.status_code for a in agent.steps for c in (a["captured"] or []))
    categories = Counter(step_category(a) or "eylem_uretti" for a in agent.steps)

    # One sample from the zero-call steps: the diagnosis needs the code and the
    # output themselves, the category name alone is not enough.
    sample = None
    for a in agent.steps:
        if step_category(a) in {"execution_error_no_action", "execution_ok_no_action"}:
            sample = {
                "kategori": step_category(a),
                "code": a["code"][:600],
                "output": a["output"][:400],
            }
            break

    return {
        "digest": digest(trajectory),
        "step": len(agent.steps),
        "yakalanan_cagri": captured,
        "gunlukteki_cagri": from_log,
        "count_divergences": agent.count_divergences,
        "durum_kodlari": {str(k): v for k, v in statuses.items()},
        "adim_kategorileri": dict(categories),
        "sifir_cagri_ornegi": sample,
        "bosaltma_dogrulandi": unloaded,
        "sure_saniye": round(elapsed, 1),
    }


def main() -> None:
    config = load_model_config("config/models.yaml")
    instruction = str(write_rendered_prompt("results/determinizm-instructions.txt", ""))
    seed = config.seed_for(TASK, 0)
    other_seed = config.seed_for(TASK, 1)

    print(f"task={TASK}  repeats={REPEATS}  seed={seed}  second seed={other_seed}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    models = [m for m in config.models if MODEL_FILTER in m]
    if not models:
        sys.exit(f"ZIHIN_MODEL={MODEL_FILTER!r} matches no model")

    all_passed = True

    for tag in models:
        print(f"\n=== {tag} ===")
        runs = []
        for i in range(REPEATS):
            result = one_episode(tag, seed, config.temperature, f"determinizm-{i}", instruction)
            runs.append(result)
            print(
                f"  {i + 1:2}/{REPEATS}  trajectory={result['digest']}  step={result['step']:2}  "
                f"calls={result['yakalanan_cagri']:3}  unloaded={result['bosaltma_dogrulandi']}  "
                f"{result['sure_saniye']}s"
            )

        summary_distribution = Counter(k["digest"] for k in runs)
        uniform = len(summary_distribution) == 1
        unloading = all(k["bosaltma_dogrulandi"] for k in runs)
        divergence = [k["count_divergences"] for k in runs if k["count_divergences"]]
        category_totals = Counter()
        for k in runs:
            category_totals.update(k["adim_kategorileri"])

        second = one_episode(tag, other_seed, config.temperature, "determinizm-tohum2", instruction)
        seed_differs = second["digest"] not in summary_distribution

        print(f"  residual variance         : {len(summary_distribution)} distinct trajectories")
        print(f"  trajectory distribution   : {dict(summary_distribution)}")
        print(f"  unload always verified    : {unloading}")
        print(f"  second seed differs       : {seed_differs}  ({second['digest']})")
        print(f"  step categories           : {dict(category_totals)}")
        sample = next((k["sifir_cagri_ornegi"] for k in runs if k["sifir_cagri_ornegi"]), None)
        if sample:
            print(f"  zero-call step sample     : {sample['kategori']}")
            print(f"    output: {sample['output'][:160]!r}")
        if divergence:
            print(f"  WARNING: capture and log counts diverged: {divergence}")

        result = {
            "model": tag,
            "task": TASK,
            "tekrar": REPEATS,
            "seed": seed,
            "tekduze": uniform,
            "farkli_yorunge_sayisi": len(summary_distribution),
            "yorunge_dagilimi": dict(summary_distribution),
            "bosaltma_hep_dogrulandi": unloading,
            "ikinci_tohum_farkli": seed_differs,
            "ikinci_tohum_ozeti": second["digest"],
            "count_divergences": divergence,
            "adim_kategorileri": dict(category_totals),
            "sifir_cagri_ornegi": sample,
            "kosular": runs,
        }
        file_name = f"{tag.replace(':', '-').replace('.', '_')}--{TASK}.json"
        with open(os.path.join(OUTPUT_DIR, file_name), "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
        print(f"  written: {os.path.join(OUTPUT_DIR, file_name)}")

        # Uniformity is no longer a pass/fail criterion but a measured quantity
        # (K-51). The run fails only if the unload cannot be verified or the seed
        # axis dies; both of those invalidate the measurement.
        all_passed = all_passed and unloading and seed_differs

    print(f"\nMEASUREMENT VALID: {all_passed}")
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
