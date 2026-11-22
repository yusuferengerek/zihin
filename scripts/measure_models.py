"""Stage 4: measures three models and writes a manifest for every run.

Per model:

1. The model is loaded into memory and the effective context window is read from
   the server. If it differs from the requested value the model is skipped,
   because a silent fallback is the one failure mode we cannot tolerate (K-37).
2. VRAM usage is measured. Ollama's `/api/ps` output gives the model's total size
   and the part that sits in VRAM.
3. A single task is run under the reference scaffold.
4. The manifest is written to the table.

The verification itself warms the model. So after verification the model is
unloaded and the episode starts in the cold regime; the single regime measured in
stage 2
tekrarlanabilir protokol bu (K-21, S-13).

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/measure_models.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402

from zihin.model_server import server_log, setting_flag  # noqa: E402
from zihin.recording_agent import NoProgress, RecordingAgent, write_steps  # noqa: E402
from zihin.records import (  # noqa: E402
    insert_episode,
    insert_run_manifest,
    load_model_config,
    load_recording_limits,
    open_database,
    os_environment_text,
)

TASK = os.environ.get("ZIHIN_TASK_ID", "82e2fac_1")
SPLIT = "train"
CONDITION = "baseline"
MAX_STEPS = 20
APPWORLD_COMMIT = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"
DATABASE = "results/zihin.sqlite"
SUMMARY_FILE = "results/asama-4-model-olcumu.json"
GIB = 1024**3


def saat() -> float:
    with open("/proc/uptime", encoding="ascii") as handle:
        return float(handle.read().split()[0])


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


BASE = base_url()


def request(body: dict, path: str, zaman_asimi: int = 600) -> dict:
    ham = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        f"{BASE}{path}", data=ham, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(r, timeout=zaman_asimi) as response:
        return json.load(response)


def loaded_models() -> list[dict]:
    with urllib.request.urlopen(f"{BASE}/api/ps", timeout=30) as response:
        return json.load(response).get("models") or []


def yukle(tag: str) -> None:
    request(
        {
            "model": tag,
            "messages": [{"role": "user", "content": "ok"}],
            "stream": False,
            "options": {"num_predict": 1},
        },
        "/api/chat",
    )


def unload(tag: str) -> None:
    request({"model": tag, "messages": [], "keep_alive": 0}, "/api/chat", zaman_asimi=120)
    time.sleep(3)


# The server runs on the Windows side, this process inside WSL. Reading the
# environment variables through `os.environ` yields empty values; the server's own
# configuration dump is read instead. The source is the server's declaration, not
# the launcher's claim.
SERVER_LOG = server_log()


def server_settings_row() -> dict:
    """The server's own configuration. This is what goes into the manifest (K-37)."""
    settings: dict = {"source": SERVER_LOG}
    aranan = (
        "OLLAMA_CONTEXT_LENGTH",
        "OLLAMA_KV_CACHE_TYPE",
        "OLLAMA_FLASH_ATTENTION",
        "OLLAMA_KEEP_ALIVE",
        "OLLAMA_HOST",
    )
    try:
        with open(SERVER_LOG, encoding="utf-8", errors="replace") as handle:
            dokum = next((s for s in handle if "server config" in s), "")
        for name in aranan:
            matches = re.search(rf"{name}:(\S*?)[ \]]", dokum)
            settings[name] = matches.group(1) if matches else None
    except OSError as error:
        settings["log_hatasi"] = str(error)[:160]
        for name in aranan:
            settings[name] = None
    try:
        with urllib.request.urlopen(f"{BASE}/api/version", timeout=30) as response:
            settings["ollama_version"] = json.load(response).get("version")
    except Exception as error:
        settings["ollama_version_hatasi"] = str(error)[:120]
    return settings


def vram_measurement(tag: str) -> dict:
    """The model's memory footprint. The source is Ollama's own report."""
    for m in loaded_models():
        if m.get("name") == tag:
            total = m.get("size") or 0
            vram = m.get("size_vram") or 0
            return {
                "toplam_bayt": total,
                "vram_bayt": vram,
                "toplam_gib": round(total / GIB, 3),
                "vram_gib": round(vram / GIB, 3),
                "tamamen_gpuda": bool(total) and vram >= total,
                "baglam_penceresi": m.get("context_length"),
            }
    return {"error": "the model does not appear to be loaded"}


def code_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


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
        "max_prompt_length": 50000,
        "max_output_length": 20000,
        "max_steps": MAX_STEPS,
    }


def episode_counts(experiment: str) -> dict:
    root = os.path.join(path_store.experiment_outputs, experiment, "tasks", TASK)
    call_log_path = os.path.join(root, "logs", "api_calls.jsonl")
    io_yolu = os.path.join(root, "logs", "environment_io.md")
    kullanim_yolu = os.path.join(root, "misc", "usage.json")

    call = 0
    if os.path.exists(call_log_path):
        with open(call_log_path, encoding="utf-8") as handle:
            call = sum(1 for s in handle if s.strip())
    step = 0
    if os.path.exists(io_yolu):
        with open(io_yolu, encoding="utf-8") as handle:
            step = sum(1 for s in handle if s.startswith("### Environment Interaction"))
    kullanim = {}
    if os.path.exists(kullanim_yolu):
        with open(kullanim_yolu, encoding="utf-8") as handle:
            kullanim = json.load(handle).get("tokens", {})
    return {"step": step, "api_cagrisi": call, "tokenlar": kullanim}


def main() -> None:
    import appworld_agents

    config = load_model_config("config/models.yaml")
    instruction_path = os.path.join(
        os.path.dirname(appworld_agents.__file__),
        "prompts",
        "react_code_agent",
        "instructions.txt",
    )
    with open(instruction_path, encoding="utf-8") as handle:
        instruction_digest = hashlib.sha256(handle.read().encode("utf-8")).hexdigest()

    settings = server_settings_row()
    limits = load_recording_limits("config/recording.yaml")
    os.makedirs("results", exist_ok=True)
    connection = open_database(DATABASE)

    measurements = []
    for index, tag in enumerate(config.models, 1):
        print(f"\n=== {index}/{len(config.models)}  {tag} ===")
        run_id = f"asama-4-{tag.split(':')[1].split('-')[0]}"

        yukle(tag)
        vram = vram_measurement(tag)
        effective = vram.get("baglam_penceresi")
        dogrulandi = effective == config.num_ctx
        print(f"  effective context window   : {effective}  (requested {config.num_ctx})")
        print(
            f"  VRAM                   : {vram.get('vram_gib')} GiB / "
            f"total {vram.get('toplam_gib')} GiB  tamamen GPU'da="
            f"{vram.get('tamamen_gpuda')}"
        )

        if not dogrulandi:
            print("  SKIPPED: the context window could not be verified (K-37).")
            measurements.append(
                {"model": tag, "dogrulandi": False, "effective_context": effective, "vram": vram}
            )
            continue

        seed = config.seed_for(TASK, 0)
        unload(tag)

        experiment = f"asama-4-{tag.replace(':', '-').replace('.', '_')}"
        started = saat()
        agent = RecordingAgent(
            experiment_name=experiment,
            probe_state=True,
            no_progress_limit=limits.no_progress_limit,
            **agent_config(tag, seed, config.temperature, instruction_path),
        )
        try:
            agent.solve_tasks(task_ids=[TASK], experiment_name=experiment)
        except NoProgress as error:
            print(f"  episode ended early     : {error}")
        elapsed = saat() - started

        numbers = episode_counts(experiment)
        after_load = vram_measurement(tag)
        print(
            f"  episode                 : {numbers['step']} steps, "
            f"{numbers['api_cagrisi']} API calls, {elapsed:.1f}s"
        )

        with connection:
            insert_run_manifest(
                connection,
                run_id=run_id,
                created_at=f"uptime:{started:.3f}",
                model_tag=tag,
                num_ctx_requested=config.num_ctx,
                num_ctx_effective=effective,
                context_verified=1,
                kv_cache_type=settings.get("OLLAMA_KV_CACHE_TYPE"),
                flash_attention=(setting_flag(settings, "OLLAMA_FLASH_ATTENTION")),
                temperature=config.temperature,
                base_seed=config.base_seed,
                keep_alive=settings.get("OLLAMA_KEEP_ALIVE") or config.keep_alive,
                no_progress_limit=limits.no_progress_limit,
                model_server_env={**settings, "vram": after_load},
                appworld_version="0.2.0.dev0",
                appworld_commit=APPWORLD_COMMIT,
                # The family sweep was cancelled and this script was written
                # before the shield existed; it was never mounted. 'off' is
                # correct for the old rows and correct here too — not an invented
                # value but a fact.
                shield_mode="off",
                code_commit=code_commit(),
                instruction_file_digest=instruction_digest,
                os_environment=os_environment_text(),
            )
            episode_id = insert_episode(
                connection,
                run_id=run_id,
                task_id=TASK,
                split=SPLIT,
                condition=CONDITION,
                model_ref=tag,
                seed=seed,
                sequence_in_run=1,
                model_load_state="cold",
                started_at=f"uptime:{started:.3f}",
                ended_at=f"uptime:{started + elapsed:.3f}",
                termination_reason=(
                    agent.stop_reason
                    or ("step_ceiling" if numbers["step"] >= MAX_STEPS else "agent_finished")
                ),
                total_model_calls=numbers["step"],
                input_tokens=numbers["tokenlar"].get("input_cache_miss"),
                output_tokens=numbers["tokenlar"].get("output"),
                duration_seconds=round(elapsed, 3),
            )
            write_steps(
                connection,
                episode_id,
                agent,
                limits,
                os.path.join(
                    path_store.experiment_outputs,
                    experiment,
                    "tasks",
                    TASK,
                    "logs",
                    "environment_io.md",
                ),
            )

        measurements.append(
            {
                "model": tag,
                "dogrulandi": True,
                "effective_context": effective,
                "seed": seed,
                "vram_yuklemede": vram,
                "vram_epizot_sonrasi": after_load,
                "episode": numbers,
                "sure_saniye": round(elapsed, 1),
            }
        )
        unload(tag)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as handle:
        json.dump(
            {"server": settings, "task": TASK, "olcumler": measurements},
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nsummary written: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
