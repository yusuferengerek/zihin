"""Runs a single task and writes it into the record schema.

The runner for phase 3's acceptance criterion. The recorder itself lives in
`zihin.recording_agent`; only the configuration and the manifest are here.

The scaffold is not touched. `SimplifiedReActCodeAgent` is used as it is; for
recording, only the environment's `execute` method is wrapped from outside
(K-19).

The episode row is written last, in a single transaction. The reason is the
append-only rule: the end time and the totals are known only once the episode
finishes, and UPDATE is forbidden.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/record_run.py
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.common.path_store import path_store  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.api_capture import capturing  # noqa: E402
from zihin.cards import render_card_block  # noqa: E402
from zihin.declared import experiment_run_problems  # noqa: E402
from zihin.model_server import (  # noqa: E402
    is_loaded,
    kernel_clock,
    load_model,
    server_settings,
    setting_flag,
    unload_model,
)
from zihin.recording_agent import (  # noqa: E402
    NoProgress,
    RecordingAgent,
    write_steps,
)
from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    AlreadyRecorded,
    insert_episode,
    insert_experiment_episode,
    insert_run_manifest,
    insert_verifier_result,
    load_model_config,
    load_recording_limits,
    open_database,
    open_library,
    os_environment_text,
)
from zihin.scaffold import episode_prompt_path, write_rendered_prompt  # noqa: E402
from zihin.shield import load_write_set  # noqa: E402
from zihin.shield_mount import config_digest, mount_for_task  # noqa: E402
from zihin.slots import compose, condition_config  # noqa: E402
from zihin.verification import verdict  # noqa: E402

TASK = os.environ.get("ZIHIN_TASK_ID", "82e2fac_1")
SEED_INDEX = int(os.environ.get("ZIHIN_SEED_INDEX", "0"))
SPLIT = os.environ.get("ZIHIN_SPLIT", "train")
# The card-free run is the baseline condition; a card flag or `--condition`
# names another, and the record says which condition ran.
CONDITION = "baseline"
# The ceiling is computed per task (K-43): the anchor is
# `metadata.num_api_calls`, the multiplier is swept. The fixed 20 is only phase
# 3's single-task default; on a task whose anchor is 195, a fixed ceiling does
# not measure the task, it measures the ceiling.
MAX_STEPS = int(os.environ.get("ZIHIN_MAX_STEPS", "20"))
APIS_PORT = int(os.environ.get("ZIHIN_APIS_PORT", "8123"))
APPWORLD_COMMIT = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"
# The experiment directory is where the task outputs go. It is overwritten when
# the same task is run with another model, so it has to be separable per model.
EXPERIMENT_NAME = os.environ.get("ZIHIN_EXPERIMENT", "phase-3-record")
DATABASE = ACTIVE_SERIES
WRITE_SET_PATH = "inputs/write-set-static.json"


def parse_options() -> argparse.Namespace:
    """Two flags from the command line, not from the environment.

    Both affect the measurement, and the environment carries only secrets and
    values read back from the server. Both are also single-run decisions: put
    into the environment, they would silently hang over the following runs.
    """
    # Imported here as well as at the top: the parser is also built on its own, by
    # the test that reads every invoked script's required arguments.
    from zihin.slots import EXPERIMENT_CONDITIONS  # noqa: PLC0415

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stop-threshold",
        type=int,
        default=None,
        help=(
            "Takes the stopping-rule threshold from here instead of the "
            "configuration. 0 = rule off."
        ),
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=None,
        help=(
            "Takes the output budget from here instead of the configuration. "
            "A declared condition has to be settable where it is declared; "
            "otherwise the protocol names one number and the run uses another."
        ),
    )
    parser.add_argument(
        "--allow-dirty-tree",
        action="store_true",
        help="Allows running with uncommitted changes; the manifest records dirty.",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Makes the exit status non-zero if endpoint resolution has broken (S-32).",
    )
    parser.add_argument(
        "--cards",
        action="store_true",
        help=(
            "Puts the cards the retriever found for this task into the slot. Without "
            "it the slot stays empty and the prompt is byte-identical to the "
            "reference (K-25)."
        ),
    )
    parser.add_argument(
        "--irrelevant-cards",
        action="store_true",
        help=(
            "Puts cards the retriever would NOT give this task into the slot: the "
            "control arm. Same library, no new mining."
        ),
    )
    parser.add_argument(
        "--condition",
        choices=EXPERIMENT_CONDITIONS,
        default=None,
        help=(
            "Runs one of the experiment's five conditions by name and records it under "
            "that name. Every card-carrying condition gets the carded arm's card count "
            "on the task, kind by kind (A.4, K-181)."
        ),
    )
    parser.add_argument(
        "--slice",
        type=int,
        default=None,
        help="The experiment slice this episode belongs to. Experiment runs only.",
    )
    parser.add_argument(
        "--session",
        default=None,
        help="The driver session that runs this episode. Experiment runs only.",
    )
    parser.add_argument(
        "--path-change-accepted",
        action="store_true",
        help=(
            "Written into the experiment's table when the driver was told to go on "
            "after a measurement-defining path changed. Experiment runs only."
        ),
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help=(
            "Runs the agent's code in the container and takes the record from the "
            "loopback proxy. Needs a running `appworld serve apis` server and a "
            "built image."
        ),
    )
    options = parser.parse_args()
    chosen = [bool(options.cards), bool(options.irrelevant_cards), bool(options.condition)]
    if sum(chosen) > 1:
        parser.error("--cards, --irrelevant-cards and --condition name one arm; give one")
    return options


def arm(options: argparse.Namespace) -> tuple[str, str]:
    """(the condition whose slot is built, the name the record gives it).

    `--cards` and `--irrelevant-cards` are the flags the runs before the
    experiment used. The second one's episodes were recorded as
    `skills_failures_irrelevant` (section 12's three-arm run); a run made with it
    keeps that name, so an old row and a new one made the same way do not part
    over a label. The experiment names its conditions with `--condition`.
    """
    if options.condition:
        return options.condition, options.condition
    if options.cards:
        return "skills_failures", "skills_failures"
    if options.irrelevant_cards:
        return "irrelevant_retrieval", "skills_failures_irrelevant"
    return CONDITION, CONDITION


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not set.")
    return address.rstrip("/")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def code_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


def effective_context(base: str, tag: str) -> int | None:
    """The effective context window on the server (K-37).

    `/api/ps` reports only the loaded model, so reading it means loading the
    model. The verification warms the model up; that is why the episode is
    unloaded after the verification and started in the cold regime.
    """
    load_model(base, tag)
    with urllib.request.urlopen(f"{base}/api/ps", timeout=30) as response:
        for m in json.load(response).get("models") or []:
            if m.get("name") == tag:
                return m.get("context_length")
    return None


def sandbox_kur(is_open: bool, shield, seed: int) -> dict:
    """Sets up the sandbox layer and returns four things.

    With it off, today's path stays exactly as it is: `ApiCapture` wraps the
    `Requester`, nothing is added to `appworld_config`, and the sandbox fields in
    the manifest stay NULL. So without the flag nothing changes.

    With it on, the recording path moves to the proxy. The order matters: the
    proxy has to come up **before** the container, because the bridge inside the
    container tries to connect to the socket as its first action.
    """
    if not is_open:
        return {
            "capture_context": capturing(shield=shield),
            "appworld_extras": {},
            "manifest": {},
            "teardown": lambda: None,
        }

    from zihin.recording_proxy import (  # noqa: PLC0415
        PROXY_VERSION,
        policy_for_episode,
        proxy_for_episode,
    )
    from zihin.sandbox import (  # noqa: PLC0415
        Sandbox,
        image_digest,
        image_exists,
        load_sandbox_config,
    )

    config = load_sandbox_config("config/sandbox.yaml")
    if not image_exists(config):
        sys.exit(
            f"{config.image} image is not built. Build it with: podman build "
            f"-t {config.image} -f Containerfile ."
        )
    policy = policy_for_episode(
        experiment_name=EXPERIMENT_NAME, task_id=TASK, random_seed=seed % (2**31)
    )
    proxy = proxy_for_episode(
        socket_path=config.apis_socket,
        upstream_port=APIS_PORT,
        shield=shield,
        policy=policy,
    )
    # The task output tree is born inside the container, not on the host. The
    # agent's own `log_usage`, however, writes on the host side — the token
    # counts come from the host's model calls — and with no directory it fails
    # **after** the episode ends, which wastes the whole run. That is why the
    # directories are created in advance.
    for alt in ("misc", "logs", "evaluation"):
        os.makedirs(
            os.path.join(path_store.experiment_outputs, EXPERIMENT_NAME, "tasks", TASK, alt),
            exist_ok=True,
        )

    proxy.start()
    container = Sandbox(config=config, name=f"zihin-{EXPERIMENT_NAME}-{TASK}")
    container.start()
    container.wait_until_ready(timeout_seconds=300)
    # The rule: a run does not count until it has verified that it is talking to
    # the thing it started (K-98). `wait_until_ready` does the confirming itself;
    # here it only goes into the record.
    identity = container.verify_identity()
    container.sample_usage()
    print(
        f"sandbox: {config.image}, network {config.network_mode}, proxy {config.apis_socket}, "
        f"container pid {identity['container_pid']}"
    )

    def teardown() -> None:
        # The logs are copied after the episode ends (K-94): there is no
        # writable mount for the duration of the run.
        container.copy_out(
            f"/zihin/experiments/outputs/{EXPERIMENT_NAME}/tasks/{TASK}/logs",
            os.path.join(path_store.experiment_outputs, EXPERIMENT_NAME, "tasks", TASK, "logs"),
        )
        peak = container.stop_sampling()
        if peak:
            print(f"container peak usage: {json.dumps(peak, ensure_ascii=False)}")
            with open("results/sandbox-tepe.json", "w", encoding="utf-8") as peak_file:
                json.dump(
                    {"gorev": TASK, "deney": EXPERIMENT_NAME, "tepe": peak},
                    peak_file,
                    ensure_ascii=False,
                    indent=2,
                )
        limit = container.exited_at_limit()
        if limit:
            print(f"WARNING: the container finished by hitting a limit: {limit}")
        print(f"proxy: {proxy.request_count} requests, {len(proxy.refusals)} refused")
        for refusal in proxy.refusals:
            print(f"  RED: {refusal.method} {refusal.path} -> {refusal.reason}")
        container.stop()
        proxy.stop()

    return {
        "capture_context": contextlib.nullcontext(proxy.capture),
        "appworld_extras": {
            "remote_environment_url": container.environment_url,
            "remote_apis_url": f"http://127.0.0.1:{config.bridge_port}",
            "remote_docker": True,
        },
        "manifest": {
            **config.manifest_fields(),
            "sandbox_image": f"{config.image}@{image_digest(config)}",
            "sandbox_version": PROXY_VERSION,
            "sandbox_proxy_digest": policy.digest(),
        },
        "teardown": teardown,
    }


def agent_config(
    base: str,
    tag: str,
    seed: int,
    temperature: float,
    instruction: str,
    max_tokens: int,
    max_prompt_characters: int,
    appworld_extras: dict,
) -> dict:
    """The agent's configuration. The character ceiling is an argument with no
    default (S-47).

    The ceiling comes from `config/recording.yaml` and is written into the
    manifest. Had a number been written here, there would be two sources of
    truth: whoever changed the config would think they had not changed the run's
    behaviour.
    """
    return {
        "model_config": {
            "name": f"ollama_chat/{tag}",
            "base_url": base,
            "temperature": temperature,
            "seed": seed,
            "max_tokens": max_tokens,
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
        "appworld_config": {"random_seed": seed % (2**31), **appworld_extras},
        "logger_config": {"color": False, "verbose": False},
        "prompt_file_path": instruction,
        # The agent never truncates with `None`; -1 is our spelling of "no
        # ceiling".
        "max_prompt_length": None if max_prompt_characters == -1 else max_prompt_characters,
        # The character ceiling on the observation text. Our own limit (K-17,
        # 8192 bytes) is tighter than this, so this value never binds; it is
        # still left at the reference's value, because there is no reason to
        # change it.
        "max_output_length": 20000,
        "max_steps": MAX_STEPS,
    }


def main() -> None:
    options = parse_options()
    base = base_url()
    model_config = load_model_config("config/models.yaml")
    limits = load_recording_limits("config/recording.yaml")
    # 0 means "rule off" and a 0 goes into the manifest as well: which episode
    # ran with the rule off has to be readable from the record afterwards.
    stop_threshold = (
        limits.no_progress_limit if options.stop_threshold is None else options.stop_threshold
    )
    max_output_tokens = (
        limits.max_output_tokens if options.max_output_tokens is None else options.max_output_tokens
    )
    # No silent fallback. `models[0]` is 1.5B, so a missing variable used to run
    # the smallest model on the axis and record it as if it had been asked for.
    tag = os.environ.get("ZIHIN_MODEL")
    if not tag:
        sys.exit(
            "ZIHIN_MODEL is not set. This runner does not choose a model: the "
            "caller names it, and a default here would be a second place the "
            "name lives (K-138)."
        )
    if tag not in model_config.models:
        sys.exit(f"{tag} is not in config/models.yaml.")
    # The repeat index. Zero is the single-episode default, so nothing changes
    # for a run that does not ask for repeats; 1 and 2 are the second and third
    # repeats of the three-arm run. The derivation itself is the existing one —
    # no new machinery, and the manifest keeps recording the seed it used.
    seed = model_config.seed_for(TASK, SEED_INDEX)
    # The manifest key carries the task and the model together; with the
    # experiment name in front as well, there is no collision when the same pair
    # is run again in another measurement.
    run_id = f"{EXPERIMENT_NAME}-{TASK}-{tag.split(':')[1].split('-')[0]}"
    # An experiment run is refused here, before anything is spent, if it could not
    # be recorded as one - whether or not the check before it ran (K-180, K-182).
    refused = experiment_run_problems(
        run_id,
        allow_dirty_tree=options.allow_dirty_tree,
        named_condition=options.condition,
        split=SPLIT,
        slice_number=options.slice,
        session_id=options.session,
        path_change_accepted=options.path_change_accepted,
    )
    if refused:
        sys.exit(f"{run_id} is not started:\n  " + "\n  ".join(refused))

    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    connection = open_database(DATABASE)

    # The card block. When empty the slot leaves no trace and the prompt stays
    # byte-identical to the reference (K-25); when full the only difference is
    # the block itself, and that difference goes into the record through the
    # manifest's `instruction_file_digest`.
    card_block = ""
    library_id = None
    slot = None
    condition, label = arm(options)
    if condition != CONDITION:
        # Two databases, two questions. Episodes are written to the active
        # series; the library is read from the series it was mined from. They
        # were the same file until series 3 opened, and asking the writing
        # connection for the library would now refuse mid-run (K-143).
        library, library_id, index_id = open_library()
        config = condition_config(condition)
        # One selection for every condition, the same one the analysis sets are
        # counted from (`zihin.slots`, K-181): the same filters in all five, and
        # every kind taken from the irrelevant pool cut to the carded arm's count.
        slot = compose(
            library,
            task_instruction(TASK),
            condition,
            library_id=library_id,
            index_id=index_id,
            task_id=TASK,
        )
        library.close()
        if not slot.covered:
            sys.exit(
                f"the carded arm reaches {TASK} with no card, so {label} is not run "
                "here: a card-carrying run with an empty slot is the baseline under "
                "another name (A.3's covered tasks)."
            )
        card_block = render_card_block(
            slot.cards, skill_slots=config.skill_slots, failure_slots=config.failure_slots
        )
        print(
            f"cards: {len(slot.cards.skills)} skills, {len(slot.cards.failures)} failures; "
            f"into the slot {card_block.count('SKILL ')}+{card_block.count('FAILURE ')}, "
            f"{len(card_block)} characters"
        )
        if slot.shortfall:
            # It runs short and the record says so (A.4's correction, K-181): a
            # control that carried less volume than the arm it controls is left out
            # of every confirmatory analysis that involves it.
            print(f"volume: not matched on {TASK} ({'; '.join(slot.shortfall)})")
        if not card_block:
            sys.exit(
                f"no card at all reaches the slot for {label} on {TASK}. A card-carrying "
                "run is not run with an empty slot: it would leave an episode in the "
                "record that looks carded but ran card-free."
            )

    instruction_path = str(write_rendered_prompt(episode_prompt_path(run_id, TASK, 0), card_block))
    instruction_digest = digest(open(instruction_path, encoding="utf-8").read())

    effective = effective_context(base, tag)
    print(f"effective context window: {effective}  (requested {model_config.num_ctx})")
    if effective != model_config.num_ctx:
        sys.exit(
            f"Effective context window {effective}, requested {model_config.num_ctx}. "
            "The server may have been started without OLLAMA_CONTEXT_LENGTH. Run "
            "stopped (K-37)."
        )

    server = server_settings(base)
    unload_model(base, tag)
    print(f"model loaded before episode: {is_loaded(base, tag)}")

    # The shield is open in all five conditions, so it is not a condition
    # variable and takes no flag: every run carries it. Shadow mode is the only
    # mode that exists (K-71), so it records and blocks nothing.
    shield = mount_for_task(TASK, load_write_set(WRITE_SET_PATH))
    print(f"shield: {shield.mode}, allowed apps: {sorted(shield.allowed_apps)}")

    # With the sandbox on, the record comes from the proxy rather than from the
    # `Requester` wrapper. The two are not set up at the same time and cannot be:
    # in served mode there is no host-side `Requester` left to wrap (measured).
    kum = sandbox_kur(options.sandbox, shield, seed)

    started = kernel_clock()
    with kum["capture_context"] as capture:
        agent = RecordingAgent(
            experiment_name=EXPERIMENT_NAME,
            capture=capture,
            # In served mode the row-count probe does not work: `world.models`
            # is None and the probe returns an empty dict, which in the record
            # reads as "measured, unchanged". The probe is off in that mode and
            # a digest-based measurement takes its place (K-93).
            probe_state=not options.sandbox,
            # Sandbox kipinde  konteynerin icinde, yani host
            # side there is no second source. Its absence is not read as "zero calls".
            log_source=not options.sandbox,
            no_progress_limit=stop_threshold,
            **agent_config(
                base,
                tag,
                seed,
                model_config.temperature,
                instruction_path,
                limits.max_output_tokens,
                limits.max_prompt_characters,
                kum["appworld_extras"],
            ),
        )
        try:
            agent.solve_tasks(task_ids=[TASK], experiment_name=EXPERIMENT_NAME)
        except NoProgress as error:
            print(f"episode ended early: {error}")
    elapsed = kernel_clock() - started

    # Did a record actually come out. A run does not count until it has verified
    # that it is talking to the thing it started (K-98), and this is that rule on
    # the record side: if the proxy saw app calls and not a single step was
    # recorded, the recorder was never attached. Exactly this happened in the
    # first sandbox episode — a 32 KB trajectory was produced, zero steps were
    # written, and it stayed silent because the episode row was written anyway.
    # It now fails before the episode row is written.
    if not agent.steps and capture.calls:
        sys.exit(
            f"recorder not attached: {len(capture.calls)} calls were seen but zero "
            "steps were recorded. The episode row was not written."
        )
    kum["teardown"]()

    kullanim_yolu = os.path.join(
        path_store.experiment_outputs, EXPERIMENT_NAME, "tasks", TASK, "misc", "usage.json"
    )
    kullanim = {}
    if os.path.exists(kullanim_yolu):
        with open(kullanim_yolu, encoding="utf-8") as handle:
            kullanim = json.load(handle).get("tokens", {})

    # The manifest, the episode, the steps and the verdict are one transaction.
    # `insert_episode` raises when this identity is already in the record under
    # the same conditions, and raising inside the block rolls the manifest write
    # back with it - which is what should happen, because that manifest was
    # already there too. The alternative is letting sqlite refuse with
    # `UNIQUE constraint failed`, which is the message the third restart got
    # (K-157).
    try:
        with connection:
            insert_run_manifest(
                connection,
                allow_dirty_tree=options.allow_dirty_tree,
                run_id=run_id,
                created_at=f"uptime:{started:.3f}",
                serving_mode="local",
                model_tag=tag,
                num_ctx_requested=model_config.num_ctx,
                num_ctx_effective=effective,
                context_verified=1,
                kv_cache_type=server.get("OLLAMA_KV_CACHE_TYPE"),
                flash_attention=setting_flag(server, "OLLAMA_FLASH_ATTENTION"),
                temperature=model_config.temperature,
                base_seed=model_config.base_seed,
                keep_alive=server.get("OLLAMA_KEEP_ALIVE"),
                no_progress_limit=stop_threshold,
                max_output_tokens=max_output_tokens,
                # The number that determines the effective context (S-47). The same
                # value that goes to the agent, because both are read from a single
                # source.
                max_prompt_characters=limits.max_prompt_characters,
                **kum["manifest"],
                # NULL in a card-free run: that episode saw no card from any
                # library.
                library_id=library_id,
                shield_mode=str(shield.mode),
                shield_config_digest=config_digest(WRITE_SET_PATH),
                model_server_env=server,
                appworld_version="0.2.0.dev0",
                appworld_commit=APPWORLD_COMMIT,
                code_commit=code_commit(),
                instruction_file_digest=instruction_digest,
                os_environment=os_environment_text(),
            )

            episode_id = insert_episode(
                connection,
                run_id=run_id,
                task_id=TASK,
                split=SPLIT,
                condition=label,
                model_ref=tag,
                seed=seed,
                sequence_in_run=1,
                model_load_state="cold",
                step_ceiling=MAX_STEPS,
                started_at=f"uptime:{started:.3f}",
                ended_at=f"uptime:{started + elapsed:.3f}",
                termination_reason=(
                    agent.stop_reason
                    or ("step_ceiling" if len(agent.steps) >= MAX_STEPS else "agent_finished")
                ),
                total_model_calls=len(agent.steps),
                distinct_endpoints=len(agent.endpoints),
                distinct_resources=len(agent.resources),
                input_tokens=kullanim.get("input_cache_miss"),
                output_tokens=kullanim.get("output"),
                duration_seconds=round(elapsed, 3),
            )
            write_steps(
                connection,
                episode_id,
                agent,
                limits,
                os.path.join(
                    path_store.experiment_outputs,
                    EXPERIMENT_NAME,
                    "tasks",
                    TASK,
                    "logs",
                    "environment_io.md",
                ),
            )

            episode_verdict = verdict(EXPERIMENT_NAME, TASK)
            insert_verifier_result(connection, episode_id=episode_id, **episode_verdict)
            if options.slice is not None:
                # What the experiment episode belongs to, in the same transaction:
                # an episode without its row would be one the per-slice analysis
                # cannot place (K-182).
                insert_experiment_episode(
                    connection,
                    task_id=TASK,
                    episode_id=episode_id,
                    slice=options.slice,
                    session_id=options.session,
                    volume_matched=None if slot is None else int(slot.volume_matched),
                    path_change_accepted=int(options.path_change_accepted),
                )
    except AlreadyRecorded as already:
        print(f"episode          : {already.episode_id} (already recorded; nothing written)")
        print(f"run id           : {run_id}")
        raise SystemExit(0) from None

    state_measured = sum(1 for a in agent.steps if a["state_delta"] is not None)
    print(f"episode          : {episode_id}")
    print(f"step             : {len(agent.steps)}")
    print(f"action           : {agent.total_actions}")
    operation, resource = len(agent.endpoints), len(agent.resources)
    print(f"distinct action  : {operation}")
    print(
        f"distinct resource: {resource}"
        + (f"  (ratio {resource / operation:.1f})" if operation else "")
    )
    print(f"distinct call    : {len(agent.progress_identities)}  (the set the rule sees)")
    print(f"state measured   : {state_measured}")
    print(f"stop reason      : {agent.stop_reason or 'ceiling or agent'}")
    print(
        "verdict         : "
        + {1: "passed", 0: "failed", None: "unreadable"}[episode_verdict["passed"]]
        + f"  ({episode_verdict['num_passed_tests']} passed"
        + f" / {episode_verdict['num_failed_tests']} failed tests)"
    )
    print(f"database         : {DATABASE}")

    # A health check. With broken resolution the identity set had a single
    # element in every episode and the stopping rule silently fell back to the
    # state criterion alone (S-32). It is checked after the episode row is
    # written: keep the record, stop the scan.
    if options.health_check and agent.identity_collapsed:
        sys.exit(
            f"health check failed: {len(agent.raw_urls)} distinct raw URLs but "
            f"{len(agent.progress_identities)} identity. Identity generation may "
            "have broken."
        )


if __name__ == "__main__":
    main()
