"""Boundary control: does the apparatus work.

**This is not a search for a band but a verification of the apparatus.** The
published baselines are not zero on this benchmark. If a strong model also scores
zero on our apparatus, the fault is ours, and no path can be chosen before it is
found. If it scores a reasonable ratio, the apparatus is sound and the question is
plain model capacity.

**It writes into the manifest.** It used not to: the manifest contract required
four locally specific fields unconditionally, and a hosted model has no
counterparts for them. That obstacle disappeared once the contract was narrowed by
serving mode — `serving_mode='hosted'` frees those four fields and **forbids**
writing `context_verified=1`, because that would present something unverifiable as
verified.

The reason it started writing is S-29: the measurement we cite most often had no
manifest row, and because hosted mode had never been tried, that half of the
contract had never been tested.

**What it holds fixed.** The same thirty tasks, the same per-task ceiling, the
same stopping rule, the same capture, the same verifier, the same instruction
file. The only things that change are the model and the layer serving it.

Usage:

    OPENROUTER_API_KEY=... uv run python scripts/setup/measure_boundary_control.py sinir2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402

from zihin.api_capture import capturing  # noqa: E402
from zihin.model_server import kernel_clock  # noqa: E402
from zihin.recording_agent import (  # noqa: E402
    NoProgress,
    RecordingAgent,
    step_category,
    write_steps,
)
from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    boot_id,
    completed_runs,
    insert_episode,
    insert_run_manifest,
    insert_verifier_result,
    load_model_config,
    load_recording_limits,
    missing_manifest_constraints,
    open_database,
    os_environment_text,
    resume_check,
    working_tree,
)
from zihin.scaffold import write_rendered_prompt  # noqa: E402
from zihin.shield import load_write_set  # noqa: E402
from zihin.shield_mount import config_digest, mount_for_task  # noqa: E402
from zihin.verification import graded_detail, verdict  # noqa: E402

APPWORLD_COMMIT = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"

# Served through OpenRouter. litellm separates the provider prefix from the
# model's own id: `openrouter/` + the slug on OpenRouter.
MODEL = os.environ.get("ZIHIN_API_MODEL", "openrouter/deepseek/deepseek-v4-flash-0731")
KEY_ENV_NAME = os.environ.get("ZIHIN_API_KEY_ENV", "OPENROUTER_API_KEY")
BASE_URL = os.environ.get("ZIHIN_API_BASE_URL") or None
# The price read from OpenRouter's /models endpoint is dollars per token, not
# dollars per million tokens. It is written into the JSON output rather than the
# manifest.
INPUT_COST = float(os.environ.get("ZIHIN_INPUT_COST", "0.00000008"))
OUTPUT_COST = float(os.environ.get("ZIHIN_OUTPUT_COST", "0.00000018"))
# The output budget lives in `config/recording.yaml` and is not read from the
# environment. This model produces reasoning and the reasoning eats from the same
# budget; if the budget runs short the content comes back empty and the step
# counts as codeless. The value is part of the measurement's definition and has no
# silent default.

ADET = int(os.environ.get("ZIHIN_COUNT", "0"))  # 0 = every_row
TASKS = [g for g in os.environ.get("ZIHIN_TASKS", "").split(",") if g]
# The task list and the per-task ceiling come from the first band scan and stay
# that way: the value of the boundary control comes from being comparable **on the
# same thirty tasks**. The selection is deterministic anyway, and a fresh scan
# picks the same thirty.
SCAN_FILE = os.environ.get("ZIHIN_SCAN", "results/bant-taramasi.json")
SPLIT = "test_normal"
WRITE_SET_PATH = "inputs/write-set-static.json"


def parse_options(argv: list[str]) -> argparse.Namespace:
    """The prefix is positional; the threshold and the dirty tree are flags.

    The threshold is the same flag as in `record_run.py` and it is here for the
    same reason: a value that determines the measurement, put into the
    environment, silently hangs over the following runs. argparse rather than
    scanning the arguments by hand: written as `--stop-threshold 0`, the `0` would
    fall into the positional prefix.
    """
    parser = argparse.ArgumentParser(description="Boundary control runner.")
    parser.add_argument("prefix", nargs="?", default="sinir", help="Run prefix.")
    parser.add_argument(
        "--stop-threshold",
        type=int,
        default=None,
        help="Stopping-rule threshold; overrides the configuration. 0 = rule off.",
    )
    parser.add_argument(
        "--allow-dirty-tree",
        action="store_true",
        help="Allows running with uncommitted changes; the manifest records dirty.",
    )
    return parser.parse_args(argv)


# The run prefix comes from the command line. It goes into the manifest's primary
# key, so running the same control a second time requires a separate prefix.
_OPTIONS = parse_options(sys.argv[1:])
PREFIX = _OPTIONS.prefix
ALLOW_DIRTY = _OPTIONS.allow_dirty_tree
OUTPUT = os.environ.get("ZIHIN_OUTPUT") or (
    "results/sinir-kontrolu.json" if PREFIX == "sinir" else f"results/{PREFIX}-kontrolu.json"
)


def code_commit() -> str:
    # The same as in `scripts/record_run.py`; because `zihin.records` cannot be
    # edited while the scan is running, it sits in both for now and moves there
    # once the scan finishes.
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


def agent_config(
    seed: int,
    temperature: float,
    instruction: str,
    ceiling: int,
    max_tokens: int,
    max_prompt_characters: int,
) -> dict:
    """The same as in the band scan, only the model and the transport layer
    differ.

    The character ceiling is an argument with no default and comes from the
    configuration (S-47); its value is written into the manifest as well, so the
    number the agent sees and the number that enters the record come from a single
    source.
    """
    model_config: dict = {
        "name": MODEL,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "stop": ["```\n"],
        "use_cache": False,
        "retry_after_n_seconds": 5,
        "max_retries": 3,
        "cost_per_token": {
            "input_cache_miss": INPUT_COST,
            "input_cache_hit": INPUT_COST,
            "input_cache_write": 0.0,
            "output": OUTPUT_COST,
        },
    }
    # The key is optional: candidate families served through local Ollama run with
    # the same script and do not ask for a key.
    if os.environ.get(KEY_ENV_NAME):
        model_config["api_key"] = os.environ[KEY_ENV_NAME]
    if BASE_URL:
        model_config["base_url"] = BASE_URL
    return {
        "model_config": model_config,
        "appworld_config": {"random_seed": seed % (2**31)},
        "logger_config": {"color": False, "verbose": False},
        "prompt_file_path": instruction,
        "max_prompt_length": None if max_prompt_characters == -1 else max_prompt_characters,
        "max_output_length": 20000,
        "max_steps": ceiling,
    }


PIN_STATE = os.environ.get("ZIHIN_PIN_STATE")
PINNED_PROVIDER = os.environ.get("ZIHIN_PINNED_PROVIDER")
DECLARED_QUANTISATION = os.environ.get("ZIHIN_DECLARED_QUANTISATION")
DECLARED_MAX_CONTEXT = os.environ.get("ZIHIN_DECLARED_MAX_CONTEXT")


def pin_observations() -> dict:
    """What the forwarder saw, read from its state file.

    The pinned provider is written twice on purpose: once as what we asked for and
    once as what actually served the calls. Protocol §14.3 requires the second,
    because a pin that is only declared is not a pin — and the two disagreeing is
    exactly the failure the pin exists to prevent.
    """
    if not PIN_STATE or not os.path.exists(PIN_STATE):
        return {}
    try:
        with open(PIN_STATE, encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "pin_calls": state.get("calls"),
        "providers_observed": state.get("providers"),
        "cost_usd_so_far": state.get("cost_usd"),
    }


def server_environment() -> dict:
    """What `model_server_env` carries in a hosted run.

    In local mode the server's settings dump went in; here the provider and the
    transport layer go in. Not the key itself but its **name** is written.

    Fields prefixed `declared_` are the provider's claim, not our measurement. In
    hosted mode nothing here is verified — the schema already forbids
    `context_verified = 1` — and the prefix keeps a declaration from being read
    later as an observation (protocol §14.2).
    """
    environment = {
        "provider": "openrouter",
        "model": MODEL,
        "base_url": BASE_URL or "https://openrouter.ai/api/v1",
        "api_key_env": KEY_ENV_NAME,
    }
    if PINNED_PROVIDER:
        environment["provider_pinned_to"] = PINNED_PROVIDER
        environment["allow_fallbacks"] = False
    if DECLARED_QUANTISATION:
        environment["declared_quantisation"] = DECLARED_QUANTISATION
    if DECLARED_MAX_CONTEXT:
        environment["declared_max_context"] = DECLARED_MAX_CONTEXT
    environment.update(pin_observations())
    return environment


def cost_so_far() -> float:
    """Accumulated spending, from the forwarder rather than from our own estimate.

    Our `cost_per_token` figures are an estimate written into the scaffold's
    config; the forwarder reads what OpenRouter actually charged. The ceiling is
    checked against the second (protocol §14.5).
    """
    return float(pin_observations().get("cost_usd_so_far") or 0.0)


def run_id_for(task: str, prefix: str = "") -> str:
    return f"{prefix or PREFIX}-{task}-{MODEL.split('/')[-1]}"


def one_episode(
    connection,
    task: str,
    ceiling: int,
    seed: int,
    model_config,
    limits,
    instruction: str,
    instruction_digest: str,
    threshold: int,
    prefix: str = "",
) -> dict:
    # `prefix` is only for the preflight: the preflight episode runs under its own
    # prefix and does not mix into the measured set.
    experiment = f"{prefix or PREFIX}-{task}"
    run_id = run_id_for(task, prefix)
    # The clock comes from `/proc/uptime`: episode durations have to be measured
    # the same way across a series.
    started = kernel_clock()
    # The shield is open in all five conditions, so it is not a condition variable
    # and has no flag. Shadow mode blocks nothing and therefore does not change
    # this measurement's numbers; what it records is what the shield would do.
    shield = mount_for_task(task, load_write_set(WRITE_SET_PATH))
    with capturing(shield=shield) as capture:
        agent = RecordingAgent(
            experiment_name=experiment,
            capture=capture,
            probe_state=True,
            no_progress_limit=threshold,
            **agent_config(
                seed,
                model_config.temperature,
                instruction,
                ceiling,
                limits.max_output_tokens,
                limits.max_prompt_characters,
            ),
        )
        try:
            agent.solve_tasks(task_ids=[task], experiment_name=experiment)
        except NoProgress:
            pass
    elapsed = kernel_clock() - started

    kullanim_yolu = os.path.join(
        path_store.experiment_outputs, experiment, "tasks", task, "misc", "usage.json"
    )
    kullanim = {}
    if os.path.exists(kullanim_yolu):
        with open(kullanim_yolu, encoding="utf-8") as handle:
            kullanim = json.load(handle)

    episode_verdict = verdict(experiment, task)
    categories: dict[str, int] = {}
    for step in agent.steps:
        name = step_category(step) or "eylem_uretti"
        categories[name] = categories.get(name, 0) + 1
    termination = agent.stop_reason or (
        "step_ceiling" if len(agent.steps) >= ceiling else "agent_finished"
    )

    with connection:
        insert_run_manifest(
            connection,
            allow_dirty_tree=ALLOW_DIRTY,
            run_id=run_id,
            created_at=f"uptime:{started:.3f}",
            # The four locally specific fields are empty: a hosted model has no
            # counterparts for them. context_verified cannot be 1; the contract
            # rejects that separately.
            serving_mode="hosted",
            model_tag=MODEL,
            num_ctx_requested=None,
            num_ctx_effective=None,
            context_verified=0,
            kv_cache_type=None,
            flash_attention=None,
            temperature=model_config.temperature,
            base_seed=model_config.base_seed,
            keep_alive=None,
            # 0 means "rule off" and a 0 goes into the manifest: which episode ran
            # with the rule off has to be readable from the record afterwards.
            no_progress_limit=threshold,
            max_output_tokens=limits.max_output_tokens,
            max_prompt_characters=limits.max_prompt_characters,
            library_id=None,
            shield_mode=str(shield.mode),
            shield_config_digest=config_digest(WRITE_SET_PATH),
            model_server_env=server_environment(),
            appworld_version="0.2.0.dev0",
            appworld_commit=APPWORLD_COMMIT,
            code_commit=code_commit(),
            instruction_file_digest=instruction_digest,
            os_environment=os_environment_text(),
        )
        episode_id = insert_episode(
            connection,
            run_id=run_id,
            task_id=task,
            split=SPLIT,
            condition="baseline",
            model_ref=MODEL,
            seed=seed,
            sequence_in_run=1,
            # On a hosted model the load state is not our concept.
            model_load_state="unknown",
            step_ceiling=ceiling,
            started_at=f"uptime:{started:.3f}",
            ended_at=f"uptime:{started + elapsed:.3f}",
            termination_reason=termination,
            total_model_calls=len(agent.steps),
            distinct_endpoints=len(agent.endpoints),
            distinct_resources=len(agent.resources),
            input_tokens=(kullanim.get("tokens") or {}).get("input_cache_miss"),
            output_tokens=(kullanim.get("tokens") or {}).get("output"),
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
                task,
                "logs",
                "environment_io.md",
            ),
        )
        insert_verifier_result(connection, episode_id=episode_id, **episode_verdict)

    return {
        "task": task,
        "ceiling": ceiling,
        "episode": episode_id,
        "step": len(agent.steps),
        "action": agent.total_actions,
        # The action and resource counts; their ratio is diagnostic (K-63).
        "distinct_endpoints": len(agent.endpoints),
        "distinct_resources": len(agent.resources),
        # The set the stopping rule sees, and the basis of the health check
        # (S-32).
        "distinct_calls": len(agent.progress_identities),
        "raw_urls": len(agent.raw_urls),
        "identity_collapsed": agent.identity_collapsed,
        "termination": termination,
        "passed": episode_verdict["passed"],
        "duration_seconds": round(elapsed, 1),
        "usage": kullanim,
        "step_categories": categories,
        # The seam is in the data: in a run that was interrupted and resumed,
        # which episode ran under which commit and boot is read from here.
        "code_commit": code_commit(),
        "boot_id": boot_id(),
        **graded_detail(experiment, task),
    }


# The preflight task and its ceiling. The task is among the measured thirty but
# the preflight runs under its own prefix, so it does not mix into the set. The
# ceiling is three: the preflight does not have to solve the task, it has to show
# that the write path works from beginning to end.
PREFLIGHT_TASK = "024c982_1"
PREFLIGHT_CEILING = 3


def preflight(
    connection, model_config, limits, instruction: str, instruction_digest: str, threshold: int
) -> None:
    """Verifies the write path with a single episode before starting thirty.

    The band scan already had this rule; the runner did not. The rationale was
    measured twice: while a field was being added to the manifest it was written at
    the wrong call site and thirty episodes failed while the agent was being
    constructed (S-28); during the language migration the same class was
    reproduced, with the call site saying `allow_dirty_tree=` while the definition
    was still spelled in Turkish.

    **Why the test suite is not enough.** The tests do not run the runner, and the
    verification tool covers the calibration path. The write path is the region
    neither of them sees, and a fault came out there twice. A static signature
    check catches the keyword mismatch but does not replace actually running the
    path.

    The preflight episode carries its own prefix: it does not mix into the measured
    set, does not enter the summaries, and produces no `run_id` collision.
    """
    prefix = f"{PREFIX}-preflight"
    print(f"preflight: {PREFLIGHT_TASK}  ceiling={PREFLIGHT_CEILING}  prefix={prefix}")
    try:
        row = one_episode(
            connection,
            PREFLIGHT_TASK,
            PREFLIGHT_CEILING,
            model_config.seed_for(PREFLIGHT_TASK, 0),
            model_config,
            limits,
            instruction,
            instruction_digest,
            threshold,
            prefix=prefix,
        )
    except Exception as error:
        sys.exit(f"The preflight failed: {type(error).__name__}: {error}. The run was not started.")

    written = connection.execute(
        "SELECT e.total_model_calls, e.distinct_endpoints, e.distinct_resources, m.serving_mode "
        "FROM run_manifests m JOIN episodes e USING(run_id) WHERE m.run_id = ?",
        (run_id_for(PREFLIGHT_TASK, prefix),),
    ).fetchone()
    if written is None:
        sys.exit(
            "The preflight ran but there is no manifest or episode row. The run was not started."
        )
    if not written["total_model_calls"]:
        sys.exit("The preflight episode wrote no model call at all. The run was not started.")
    if row.get("identity_collapsed"):
        sys.exit(
            f"identity generation collapsed in the preflight: {row['raw_urls']} raw "
            f"URLs, {row['distinct_calls']} identities. The run was not started."
        )
    print("  " + "  ".join(f"{k}={written[k]}" for k in written.keys()))
    print()


def main() -> None:
    local = MODEL.startswith("ollama")
    if not local and not os.environ.get(KEY_ENV_NAME):
        sys.exit(f"{KEY_ENV_NAME} is not set. A hosted model asks for an API key.")
    if not os.path.exists(SCAN_FILE):
        sys.exit(f"{SCAN_FILE} does not exist. The band scan has to be run first.")

    with open(SCAN_FILE, encoding="utf-8") as handle:
        scan = json.load(handle)["episodes_with_steps"]
    if TASKS:
        scan = [s for s in scan if s["task"] in TASKS]
    if ADET:
        scan = scan[:ADET]

    model_config = load_model_config("config/models.yaml")
    limits = load_recording_limits("config/recording.yaml")
    threshold = (
        limits.no_progress_limit if _OPTIONS.stop_threshold is None else _OPTIONS.stop_threshold
    )
    instruction = str(write_rendered_prompt(f"results/{PREFIX}-instructions.txt", ""))
    instruction_digest = hashlib.sha256(
        open(instruction, encoding="utf-8").read().encode("utf-8")
    ).hexdigest()

    connection = open_database(ACTIVE_SERIES)
    missing = missing_manifest_constraints(connection)
    if missing:
        sys.exit(
            f"{ACTIVE_SERIES} does not carry the manifest constraints: {missing}. "
            "The run was not started."
        )

    print(f"model={MODEL}  tasks={len(scan)}  split={SPLIT}  max_tokens={limits.max_output_tokens}")
    print(
        f"database={ACTIVE_SERIES}  prefix={PREFIX}  threshold={threshold}"
        + (" (rule off)" if not threshold else "")
    )

    # Resume: episodes already written completely are skipped. Interruption is a
    # measured fact in this environment, and here every episode spends money.
    identity = {s["task"]: run_id_for(s["task"]) for s in scan}
    tamam = completed_runs(connection, identity.values())
    remaining = [s for s in scan if identity[s["task"]] not in tamam]
    if len(remaining) < len(scan):
        print(f"resume: {len(scan) - len(remaining)} episodes already written, skipping")
        # Is the condition of what was written the same as what will be run now.
        # If not, the set becomes a mixture of two different measurements, and the
        # manifest records that but does not prevent it.
        expected = {
            identity[s["task"]]: {
                "model_tag": MODEL,
                "serving_mode": "hosted",
                "temperature": model_config.temperature,
                "base_seed": model_config.base_seed,
                "max_output_tokens": limits.max_output_tokens,
                "no_progress_limit": threshold,
                "appworld_commit": APPWORLD_COMMIT,
                "instruction_file_digest": instruction_digest,
                "library_id": None,
                "shield_mode": "shadow",
                "shield_config_digest": config_digest(WRITE_SET_PATH),
                "working_tree": working_tree(),
                "condition": "baseline",
                "split": SPLIT,
                "step_ceiling": s["ceiling"],
                "model_server_env": server_environment(),
            }
            for s in scan
            if identity[s["task"]] in tamam
        }
        check = resume_check(connection, expected, code_commit())
        for row in check.uyar:
            print(f"  warning: {row}")
        if not check.passed:
            for row in check.reddet:
                print(f"  RET: {row}")
            sys.exit(
                "The condition of the written episodes does not match the current "
                "one. Resuming would make the set a mixture of two different "
                "measurements. It has to be run from scratch under a new prefix."
            )

    rows = []
    ceiling_usd = float(os.environ.get("ZIHIN_COST_CEILING", "0") or 0)
    for index, s in enumerate(remaining, 1):
        if ceiling_usd:
            spent = cost_so_far()
            if spent >= ceiling_usd:
                print(
                    f"\ncost ceiling reached: {spent:.4f} >= {ceiling_usd:.4f} USD. "
                    f"Stopped after {index - 1} of {len(remaining)} episodes. "
                    "This is a result, not a fault (protocol §14.5)."
                )
                break
        task, ceiling = s["task"], s["ceiling"]
        seed = model_config.seed_for(task, 0)
        print(f"[{index}/{len(remaining)}] {task}  ceiling={ceiling}", flush=True)
        try:
            row = one_episode(
                connection,
                task,
                ceiling,
                seed,
                model_config,
                limits,
                instruction,
                instruction_digest,
                threshold,
            )
        except Exception as error:  # one episode must not bring the run down
            print(f"  episode failed: {type(error).__name__}: {error}")
            row = {"task": task, "ceiling": ceiling, "error": f"{type(error).__name__}: {error}"}
            # If the first episode tried fails, carrying on means thirty failed
            # calls. S-28's fault would be repeated here while spending money.
            if index == 1:
                rows.append(row)
                sys.exit(
                    "The first episode failed, the run was stopped. A configuration "
                    "or key error must not be repeated across thirty episodes."
                )
        rows.append(row)
        print(
            f"  step={row.get('step')} action={row.get('action')} "
            f"endpoint={row.get('distinct_endpoints')} call={row.get('distinct_calls')} "
            f"termination={row.get('termination')} verdict={row.get('passed')} "
            f"meaningful={row.get('meaningful_passed')}/{row.get('meaningful_total')}",
            flush=True,
        )
        # The health check runs on the first episode. If identity generation has
        # collapsed, the stopping rule silently falls back to the state criterion
        # alone and thirty episodes are wasted.
        if index == 1 and row.get("identity_collapsed"):
            sys.exit(
                f"health check failed: {row['raw_urls']} distinct raw URLs but "
                f"{row['distinct_calls']} identity. The run was stopped."
            )

    # The summary is built over the whole set. In a resumed run, summarizing only
    # the newly run ones would mean citing an incomplete set.
    fresh = {s["task"]: s for s in rows}
    complete = []
    for s in scan:
        task = s["task"]
        if task in fresh:
            complete.append(fresh[task])
            continue
        record = connection.execute(
            "SELECT e.total_model_calls, e.termination_reason, e.duration_seconds, v.passed, "
            "m.code_commit, m.boot_id "
            "FROM episodes e JOIN run_manifests m USING(run_id) "
            "JOIN verifier_results v USING(episode_id) WHERE e.run_id = ?",
            (identity[task],),
        ).fetchone()
        row = {"task": task, "ceiling": s["ceiling"]}
        if record:
            row.update(
                {
                    "step": record[0],
                    "termination": record[1],
                    "duration_seconds": record[2],
                    "passed": record[3],
                    "code_commit": record[4],
                    "boot_id": record[5],
                }
            )
            row.update(graded_detail(f"{PREFIX}-{task}", task))
        complete.append(row)
    rows = complete

    passing = sum(1 for s in rows if s.get("passed") == 1)
    numerator = sum(s.get("meaningful_passed", 0) or 0 for s in rows)
    denominator = sum(s.get("meaningful_total", 0) or 0 for s in rows)
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                # Which series a number came from stands next to it.
                "database": ACTIVE_SERIES,
                "prefix": PREFIX,
                "model": MODEL,
                "split": SPLIT,
                "passing": passing,
                "episodes_with_steps": rows,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(f"passing tasks: {passing}/{len(rows)}")
    if denominator:
        print(f"meaningful tests: {numerator}/{denominator} = {100 * numerator / denominator:.1f}%")
    reasons: dict[str, int] = {}
    for s in rows:
        reasons[str(s.get("termination"))] = reasons.get(str(s.get("termination")), 0) + 1
    print(f"termination: {reasons}")
    durations = [s["duration_seconds"] for s in rows if s.get("duration_seconds")]
    if durations:
        print(
            f"time: {sum(durations) / 3600:.2f} hours in total, "
            f"{sum(durations) / len(durations):.0f} s per episode"
        )
    commits = sorted({s["code_commit"][:7] for s in rows if s.get("code_commit")})
    boots = sorted({s["boot_id"][:8] for s in rows if s.get("boot_id")})
    print(f"code_commit: {commits}   boot_id: {boots}")
    if len(commits) > 1 or len(boots) > 1:
        print("  the set ran under more than one commit or boot; to be flagged in the report")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
