"""Re-runs the episodes cut by the stopping rule with the rule off.

**The trigger was written before the result was seen (setup protocol, section
6).** If the scan comes out at zero, the episodes that closed with `no_progress`
are re-run with the rule off. Only the ones that were cut; not the ones that
ended with `agent_finished`.

**Why there is no share threshold.** When the result is zero, every cut episode is
in principle a candidate for "the one that could have succeeded". Putting a
threshold there would tie the answer to the size of the share; the question is not
how large the share is but how clean the zero is.

**Why it cannot be settled on paper.** The threshold was calibrated from both
sides, but the calibration came from the successful episodes of **another model**.
Because the local model has no successful episode at all, no direct calibration is
possible.

The threshold is written as zero and a zero goes into the manifest as well: which
episode ran with the rule off has to be readable from the record afterwards.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 \\
      uv run python scripts/setup/measure_rule_off.py bant3 bant3-kapali
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

import subprocess as _sp  # noqa: E402

from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    completed_runs,
    load_model_config,
    load_recording_limits,
    missing_manifest_constraints,
    open_database,
    resume_check,
    working_tree,
)


def code_commit() -> str:
    try:
        return _sp.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


SPLIT = os.environ.get("ZIHIN_SPLIT", "test_normal")
MODEL = os.environ.get("ZIHIN_MODEL", "qwen2.5-coder:7b-instruct-q4_K_M")


def parse_options(argv: list[str]) -> tuple[str, str, bool]:
    """Command line options. Pure: it does not look at module state, so it can be
    tested."""
    konumsal = [a for a in argv if not a.startswith("-")]
    source = konumsal[0] if konumsal else "bant3"
    prefix = konumsal[1] if len(konumsal) > 1 else f"{source}-kapali"
    return source, prefix, "--allow-dirty-tree" in argv


SOURCE_PREFIX, PREFIX, ALLOW_DIRTY = parse_options(sys.argv[1:])
SOURCE = f"results/{SOURCE_PREFIX}-taramasi.json"
OUTPUT = f"results/{PREFIX}-taramasi.json"


def run_id_for(task: str, prefix: str, model: str = MODEL) -> str:
    """The manifest key `record_run.py` will build, computed in advance."""
    return f"{prefix}-{task}-{task}-{model.split(':')[1].split('-')[0]}"


def episode_command(
    task: str, step_ceiling: int, prefix: str, allow_dirty: bool
) -> tuple[list[str], dict[str, str]]:
    """One episode's command and environment. Pure.

    It is kept apart from the resume logic, and none of its arguments derive from
    the skipped episodes. Skipping can only remove items from the work list; it
    cannot change how a remaining episode runs — a separate test pins that down.
    """
    environment = dict(os.environ)
    environment["ZIHIN_TASK_ID"] = task
    environment["ZIHIN_MODEL"] = MODEL
    environment["ZIHIN_SPLIT"] = SPLIT
    environment["ZIHIN_MAX_STEPS"] = str(step_ceiling)
    environment["ZIHIN_EXPERIMENT"] = f"{prefix}-{task}"
    command = [sys.executable, "scripts/record_run.py", "--stop-threshold", "0"]
    if allow_dirty:
        command.append("--allow-dirty-tree")
    return command, environment


def remaining_tasks(connection, target: list[dict], prefix: str) -> list[dict]:
    """Removes from the target set those already written completely in the
    database.

    The source is the database, not the file system. The order is preserved and
    skipping only removes items.
    """
    identity = {s["task"]: run_id_for(s["task"], prefix) for s in target}
    tamam = completed_runs(connection, identity.values())
    return [s for s in target if identity[s["task"]] not in tamam]


def can_resume(connection, target: list[dict], prefix: str, limits, model_config) -> None:
    """Stops the run if the condition of the written episodes is not the same as
    the current one."""
    identity = {s["task"]: run_id_for(s["task"], prefix) for s in target}
    tamam = completed_runs(connection, identity.values())
    expected = {
        identity[s["task"]]: {
            "model_tag": MODEL,
            "serving_mode": "local",
            "temperature": model_config.temperature,
            "base_seed": model_config.base_seed,
            "max_output_tokens": limits.max_output_tokens,
            # Rule off: the threshold is zero, and the written ones have to be
            # zero as well.
            "no_progress_limit": 0,
            "library_id": None,
            "working_tree": working_tree(),
            "condition": "baseline",
            "split": SPLIT,
            "step_ceiling": s["ceiling"],
        }
        for s in target
        if identity[s["task"]] in tamam
    }
    check = resume_check(connection, expected, code_commit())
    for row in check.uyar:
        print(f"  warning: {row}")
    if not check.passed:
        for row in check.reddet:
            print(f"  RET: {row}")
        sys.exit(
            "The condition of the written episodes does not match the current one. "
            "Resuming would make the set a mixture of two different measurements. It "
            "has to be run from scratch under a new prefix."
        )


def run_episode(task: str, step_ceiling: int, prefix: str = PREFIX) -> int:
    command, environment = episode_command(task, step_ceiling, prefix, ALLOW_DIRTY)
    result = subprocess.run(command, env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  run failed ({result.returncode}): {result.stderr.strip().splitlines()[-1:]}")
    return result.returncode


def preflight(connection, task: str, step_ceiling: int) -> None:
    """Verifies the write path with a single episode before starting the set.

    The band scan and the boundary control already had this; this runner did not.
    The structural count of guards against runners (K-115) found the gap, and it
    did not overlap with the missing resume guard in `measure_band.py`.

    The rationale is the measured one (S-28): a manifest field written at the wrong
    call site made thirty episodes fail during agent construction and the scan
    produced no data at all. The manifest row alone is not enough — the episode row
    is looked for as well, and a zero model call count is a failure, because a
    written-but-empty episode wastes the run the same way.

    The preflight writes under its own prefix so that it never joins the set it is
    checking.
    """
    print(f"preflight: {task}  ceiling={step_ceiling}")
    code = run_episode(task, step_ceiling, prefix=f"{PREFIX}-preflight")
    if code != 0:
        sys.exit(f"The preflight failed (exit {code}). The run was not started.")
    row = connection.execute(
        "SELECT e.total_model_calls, e.termination_reason FROM run_manifests m "
        "JOIN episodes e USING(run_id) WHERE m.run_id LIKE ?",
        (f"{PREFIX}-preflight-%",),
    ).fetchone()
    if row is None:
        sys.exit(
            "The preflight ran but there is no manifest or episode row. The run was not started."
        )
    if not row["total_model_calls"]:
        sys.exit("The preflight episode wrote no model call at all. The run was not started.")
    print(f"  model_calls={row['total_model_calls']}  termination={row['termination_reason']}")
    print()


def verdict_detail(task: str) -> dict[str, int]:
    path = os.path.join(
        "experiments", "outputs", f"{PREFIX}-{task}", "evaluations", f"on_only_{task}.json"
    )
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        entry = (json.load(handle).get("individual") or {}).get(task) or {}
    passing = entry.get("passes") or []
    failing = entry.get("failures") or []
    return {
        "meaningful_passed": sum(1 for t in passing if t.get("label") == "no_op_fail"),
        "meaningful_total": sum(1 for t in passing + failing if t.get("label") == "no_op_fail"),
        "trivial_passed": sum(1 for t in passing if t.get("label") == "no_op_pass"),
    }


def after_cut(connection, run_id: str, cut_step: int) -> dict[str, int]:
    """What the episode did after the step at which the rule cut it.

    This is what separates whether the threshold cut **progress or success**. If
    there is neither a new endpoint nor a state change after the cut point, the
    rule cut nothing and the cut did not affect the outcome. If there is, the rule
    is cutting progress, even when the episode does not pass.

    The endpoint set uses the rule's own criterion: app and API name, parameters
    abstracted away.
    """
    steps = list(
        connection.execute(
            "SELECT s.step_index, s.state_change, ("
            "  SELECT GROUP_CONCAT(a.app || '.' || a.api) FROM actions a "
            "  WHERE a.step_id = s.step_id"
            ") endpoints FROM steps s JOIN episodes e USING(episode_id) "
            "WHERE e.run_id = ? ORDER BY s.step_index",
            (run_id,),
        )
    )
    seen: set[str] = set()
    steps_after = new_endpoints_after = state_changes_after = 0
    for a in steps:
        endpoints = {u for u in (a["endpoints"] or "").split(",") if u}
        if a["step_index"] > cut_step:
            steps_after += 1
            new_endpoints_after += len(endpoints - seen)
            if a["state_change"] and a["state_change"] not in ("{}", ""):
                state_changes_after += 1
        seen |= endpoints
    return {
        "kesim_sonrasi_adim": steps_after,
        "kesim_sonrasi_yeni_uc": new_endpoints_after,
        "kesim_sonrasi_durum_degisikligi": state_changes_after,
    }


def main() -> None:
    if not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not set.")
    if not os.path.exists(SOURCE):
        sys.exit(f"{SOURCE} does not exist.")

    with open(SOURCE, encoding="utf-8") as handle:
        scan = json.load(handle)

    passing_in_source = sum(1 for s in scan["episodes_with_steps"] if s.get("passed") == 1)
    if passing_in_source:
        sys.exit(
            f"{SOURCE} is not zero ({passing_in_source} passing). The trigger fires "
            "only on a zero result; no rule-off run is needed."
        )

    cut_episodes = [s for s in scan["episodes_with_steps"] if s.get("termination") == "no_progress"]
    if not cut_episodes:
        sys.exit(f"no episode in {SOURCE} was cut by the stopping rule.")

    connection = open_database(ACTIVE_SERIES)
    missing = missing_manifest_constraints(connection)
    if missing:
        sys.exit(
            f"{ACTIVE_SERIES} does not carry the manifest constraints: {missing}. "
            "The run was not started."
        )

    preflight(connection, cut_episodes[0]["task"], cut_episodes[0]["ceiling"])
    print(f"source={SOURCE}  cut={len(cut_episodes)}/{len(scan['episodes_with_steps'])}")
    print(f"database={ACTIVE_SERIES}  prefix={PREFIX}  threshold=0 (rule off)")

    # Resume: those already written completely in the database are removed from
    # the target set.
    remaining = remaining_tasks(connection, cut_episodes, PREFIX)
    if len(remaining) < len(cut_episodes):
        print(f"resume: {len(cut_episodes) - len(remaining)} episodes already written, skipping")
        can_resume(
            connection,
            cut_episodes,
            PREFIX,
            load_recording_limits("config/recording.yaml"),
            load_model_config("config/models.yaml"),
        )
    print(
        f"to run: {len(remaining)}  steps up to the ceiling: {sum(s['ceiling'] for s in remaining)}"
    )
    print()

    for index, s in enumerate(remaining, 1):
        print(
            f"[{index}/{len(remaining)}] {s['task']}  band={s['band']}  "
            f"ceiling={s['ceiling']}  (with the rule it was cut at step {s['step']})",
            flush=True,
        )
        run_episode(s["task"], s["ceiling"])

    rows = []
    for s in cut_episodes:
        run_id = run_id_for(s["task"], PREFIX)
        # Which episode ran under which commit and which boot goes into the data,
        # not only into the prose: in a run that was interrupted and resumed, the
        # seam is read from here.
        record = connection.execute(
            "SELECT e.total_model_calls, e.termination_reason, e.duration_seconds, v.passed, "
            "m.code_commit, m.boot_id "
            "FROM episodes e JOIN run_manifests m USING(run_id) "
            "JOIN verifier_results v USING(episode_id) WHERE e.run_id = ?",
            (run_id,),
        ).fetchone()
        row = {
            "task": s["task"],
            "band": s["band"],
            "ceiling": s["ceiling"],
            "kuralli_adim": s["step"],
            "kuralli_anlamli_gecen": s.get("meaningful_passed"),
            "step": record[0] if record else None,
            "termination": record[1] if record else None,
            "elapsed": record[2] if record else None,
            "passed": record[3] if record else None,
            "code_commit": record[4] if record else None,
            "boot_id": record[5] if record else None,
        }
        row.update(verdict_detail(s["task"]))
        if record:
            row.update(after_cut(connection, run_id, s["step"]))
        rows.append(row)

    passing = sum(1 for s in rows if s["passed"] == 1)
    numerator = sum(s.get("meaningful_passed", 0) or 0 for s in rows)
    denominator = sum(s.get("meaningful_total", 0) or 0 for s in rows)
    numerator_with_rule = sum(s.get("kuralli_anlamli_gecen", 0) or 0 for s in rows)

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "database": ACTIVE_SERIES,
                "prefix": PREFIX,
                "kaynak_onek": SOURCE_PREFIX,
                "stop_threshold": 0,
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
    print(f"passing         : {passing}/{len(rows)}")
    print(
        f"graded score    : {numerator}/{denominator}"
        + (f"  ({100 * numerator / denominator:.1f}%)" if denominator else "")
    )
    print(f"with the rule on: {numerator_with_rule}/{denominator}")
    reasons: dict[str, int] = {}
    for s in rows:
        reasons[str(s["termination"])] = reasons.get(str(s["termination"]), 0) + 1
    print(f"termination     : {reasons}")
    durations = [s["elapsed"] for s in rows if s["elapsed"]]
    if durations:
        print(f"time            : {sum(durations) / 3600:.2f} hours in total")

    # Was the threshold cutting progress or success: what happened after the cut
    # point.
    print()
    print("after the cut point:")
    stalled = [
        s
        for s in rows
        if not s.get("kesim_sonrasi_yeni_uc") and not s.get("kesim_sonrasi_durum_degisikligi")
    ]
    extra_steps = sum(s.get("kesim_sonrasi_adim", 0) for s in rows)
    new_endpoints = sum(s.get("kesim_sonrasi_yeni_uc", 0) for s in rows)
    state = sum(s.get("kesim_sonrasi_durum_degisikligi", 0) for s in rows)
    print(f"  episodes where nothing happened: {len(stalled)}/{len(rows)}")
    print(f"  extra steps in total          : {extra_steps}")
    print(f"  new endpoints in total        : {new_endpoints}")
    print(f"  steps that changed state      : {state}")

    # The seam: if the set ran under more than one commit or boot, it has to be
    # visible.
    commits = {s["code_commit"][:7] for s in rows if s["code_commit"]}
    boots = {s["boot_id"][:8] for s in rows if s["boot_id"]}
    print()
    print(f"code_commit : {sorted(commits)}")
    print(f"boot_id     : {sorted(boots)}")
    if len(commits) > 1 or len(boots) > 1:
        print("  the set ran under more than one commit or boot; to be flagged in the report")
    print(f"\nwritten: {OUTPUT}")


if __name__ == "__main__":
    main()
