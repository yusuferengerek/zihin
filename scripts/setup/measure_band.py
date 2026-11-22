"""Is there a measurable band: a success scan stratified by reference length.

**Why.** The censorship measurement came out at 100% on all three models, 7B
included. The mechanism mines skills only from successful episodes; if success is
zero there is no corpus to mine. This scan says whether the experiment is
feasible at all.

**What it measures.** Four numbers:

1. The success rate by reference-length band.
2. How many tasks are in the shortest band (the whole split, not the sample).
3. Partial completion: how many of the tests labelled `no_op_fail` were passed.
   AppWorld's official criterion is binary, but `TestTracker` labels every test,
   and the tests that pass even when the agent does nothing (`no_op_pass`) can be
   separated out.
4. The model calls spent in the passing episodes. If there is a band, this is
   what gives the step-ceiling multiplier.

**The ceiling is per task.** The anchor is `metadata.num_api_calls` (K-44), the
ceiling is `ZIHIN_MULTIPLIER × anchor` and at least `ZIHIN_FLOOR_CEILING`. A fixed
ceiling does not measure the band: on a task whose anchor is 195, 20 model calls
measure the ceiling rather than the task.

**The split is test_normal.** The band question is about the evaluation sample and
the evaluation is drawn from there (K-42). test_normal's reference lengths are
shorter than train's, so measuring on train would make feasibility look worse than
it is.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/measure_band.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld.task import load_task_ids  # noqa: E402

from zihin.declared import declared_model  # noqa: E402
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

SPLIT = os.environ.get("ZIHIN_SPLIT", "test_normal")
PER_BAND = int(os.environ.get("ZIHIN_PER_BAND", "6"))
MULTIPLIER = float(os.environ.get("ZIHIN_MULTIPLIER", "2"))
FLOOR_CEILING = int(os.environ.get("ZIHIN_FLOOR_CEILING", "20"))
CEILING_CAP = int(os.environ.get("ZIHIN_CEILING_LIMIT", "150"))
DATABASE = ACTIVE_SERIES

# The run prefix comes from the command line, not from the environment: the run
# id does not affect the measurement but it goes into the manifest's primary key,
# so running the same scan a second time needs a separate prefix.
# Parsed, not scanned. The previous form looked for two flag spellings in
# `sys.argv` and dropped everything else in silence: `--stop-threshold 15` was
# accepted by the shell, ignored by this script, and the run used the
# configuration's 40 while the protocol declared 15. An argument that is not
# understood is now an error, because a silently dropped condition is worse than
# a rejected one (S-58, K-136).
_PARSER = argparse.ArgumentParser(description="Band scan over the split.")
_PARSER.add_argument("prefix", nargs="?", default="band", help="run id prefix")
_PARSER.add_argument("--allow-dirty-tree", action="store_true")
_PARSER.add_argument(
    "--stop-threshold",
    type=int,
    default=None,
    help="the stopping rule's threshold, forwarded to every episode. 0 = rule off.",
)
_PARSER.add_argument(
    "--max-output-tokens",
    type=int,
    default=None,
    help="the output budget, forwarded to every episode.",
)
_OPTIONS = _PARSER.parse_args()
PREFIX = _OPTIONS.prefix
ALLOW_DIRTY = _OPTIONS.allow_dirty_tree

# The model comes from the conditions declared for THIS prefix. The prefix is
# already on the command line, so nothing else has to be told which model runs.
_DECLARED_MODEL = declared_model(PREFIX)
if os.environ.get("ZIHIN_MODEL") and os.environ["ZIHIN_MODEL"] != _DECLARED_MODEL:
    sys.exit(
        f"ZIHIN_MODEL is {os.environ['ZIHIN_MODEL']!r} but {PREFIX} declares "
        f"{_DECLARED_MODEL!r}. One run, one model name."
    )
MODEL = _DECLARED_MODEL
OUTPUT = f"results/{PREFIX}-taramasi.json" if PREFIX != "bant" else "results/bant-taramasi.json"

BANDS = ((1, 10), (11, 20), (21, 40), (41, 89), (90, 10**9))


def band_name(alt: int, ust: int) -> str:
    return f"{alt}-{ust}" if ust < 10**9 else f"{alt}+"


def anchor(task: str) -> int:
    path = os.path.join("data", "tasks", task, "ground_truth", "metadata.json")
    with open(path, encoding="utf-8") as handle:
        return int(json.load(handle)["num_api_calls"])


def ceiling(task_anchor: int) -> int:
    return min(max(int(MULTIPLIER * task_anchor), FLOOR_CEILING), CEILING_CAP)


def sample() -> tuple[list[tuple[str, int, int, str]], dict[str, int]]:
    """Evenly spaced selection per band.

    Not random: so that the same tasks are selected within the same split, they
    are sorted by task name and taken at even intervals. No seed is needed and it
    is reproducible.
    """
    every_row = sorted((g, anchor(g)) for g in load_task_ids(SPLIT))
    band_size: dict[str, int] = {}
    selection: list[tuple[str, int, int, str]] = []
    for alt, ust in BANDS:
        name = band_name(alt, ust)
        icindekiler = [(g, c) for g, c in every_row if alt <= c <= ust]
        band_size[name] = len(icindekiler)
        if not icindekiler:
            continue
        count = min(PER_BAND, len(icindekiler))
        step = len(icindekiler) / count
        for i in range(count):
            g, c = icindekiler[int(i * step)]
            selection.append((g, c, ceiling(c), name))
    return selection, band_size


def run_episode(
    task: str, step_ceiling: int, prefix: str | None = None, health_check: bool = False
) -> int:
    environment = dict(os.environ)
    environment["ZIHIN_TASK_ID"] = task
    environment["ZIHIN_MODEL"] = MODEL
    environment["ZIHIN_SPLIT"] = SPLIT
    environment["ZIHIN_MAX_STEPS"] = str(step_ceiling)
    environment["ZIHIN_EXPERIMENT"] = f"{prefix or PREFIX}-{task}"
    command = [sys.executable, "scripts/record_run.py"]
    # Forwarded, not assumed. These are the conditions the protocol declares;
    # they reach the manifest only if they reach the episode.
    if _OPTIONS.stop_threshold is not None:
        command += ["--stop-threshold", str(_OPTIONS.stop_threshold)]
    if _OPTIONS.max_output_tokens is not None:
        command += ["--max-output-tokens", str(_OPTIONS.max_output_tokens)]
    if ALLOW_DIRTY:
        command.append("--allow-dirty-tree")
    if health_check:
        command.append("--health-check")
    result = subprocess.run(command, env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  run failed ({result.returncode}): {result.stderr.strip().splitlines()[-1:]}")
    return result.returncode


# The preflight task. One of the forty-five `test_normal` tasks touched during
# setup, so it is already out of the evaluation sample. The ceiling is three: the
# preflight does not have to solve the task, it has to show that the recorder
# writes from beginning to end.
PREFLIGHT_TASK = "024c982_1"
PREFLIGHT_CEILING = 3


def check_schema() -> None:
    """Are the manifest constraints really in force in the file the run uses
    (S-29)."""
    missing = missing_manifest_constraints(open_database(DATABASE))
    if missing:
        sys.exit(
            f"{DATABASE} does not carry the manifest constraints: {missing}. "
            "The scan was not started."
        )
    print(f"schema check: {DATABASE} carries all the constraints")


def run_identity(task: str) -> str:
    """The run id `main` writes for a task, so the guard looks where the rows go."""
    return f"{PREFIX}-{task}-{task}-{MODEL.split(':')[1].split('-')[0]}"


def remaining(connection, selection):
    """Drops from the selection those already written completely.

    **Why the scan needed this.** Until now the loop ran every task
    unconditionally: the runner had a condition guard and a preflight but no
    skipping, so an interrupted scan restarted from the first task and either
    collided with the manifest's primary key or spent the episodes again. That
    was tolerable while a scan ran to completion in one sitting on a local
    machine. It stops being tolerable on a rented or session-limited runtime,
    where the plan for surviving a cut-off *is* this mechanism.

    The source is the database, not the file system: the experiment output
    directory survives an interrupted episode and a task that left a trace there
    would look completed. Completeness is what `completed_runs` checks — an
    episode row without a step or without a verdict does not count.

    Order is preserved and skipping only removes.
    """
    identity = {task: run_identity(task) for task, _, _, _ in selection}
    already = completed_runs(connection, identity.values())
    return [item for item in selection if identity[item[0]] not in already]


def guard_written_condition(connection, selection) -> None:
    """Refuses the scan if rows already under this prefix ran under another condition.

    The scan has no resume path — every task runs — but the guard is not about
    resuming. It is about a database that already holds rows under this prefix: if
    their condition differs from the one about to run, the set becomes a mixture of
    two measurements, and the manifest records that without preventing it (S-31).

    The structural count of guards against runners (K-115) found this missing here
    and `preflight` missing in `measure_rule_off.py`. The two gaps did not overlap,
    which is exactly what a prose scan of the declarations could not see: from a
    distance each runner looked protected, because each carried one of the two.
    """
    identity = {task: run_identity(task) for task, _, _, _ in selection}
    already = completed_runs(connection, identity.values())
    if not already:
        return
    model_config = load_model_config("config/models.yaml")
    limits = load_recording_limits("config/recording.yaml")
    expected = {
        run_id: {
            "model_tag": MODEL,
            "serving_mode": "local",
            "temperature": model_config.temperature,
            "base_seed": model_config.base_seed,
            "max_output_tokens": limits.max_output_tokens,
            "library_id": None,
            "working_tree": working_tree(),
            "condition": "baseline",
            "split": SPLIT,
        }
        for run_id in identity.values()
        if run_id in already
    }
    check = resume_check(connection, expected)
    for row in check.uyar:
        print(f"  warning: {row}")
    if not check.passed:
        for row in check.reddet:
            print(f"  REJECTED: {row}")
        sys.exit(
            f"{len(already)} episodes are already written under this prefix and their "
            "condition is not the one about to run. Use a new prefix."
        )
    print(f"resume guard: {len(already)} episodes already written, condition matches")


def preflight() -> None:
    """Verifies the recorder with a single episode before starting thirty.

    S-28: while a field was being added to the manifest it was written at the
    wrong call site, all thirty episodes of that scan failed while the agent was
    being constructed, and the scan produced no data at all. The smoke test
    existed that day too and was not run. A guard that depends on being remembered
    is not a guard; that is why this is not a tool run by hand but the scan's own
    preflight.

    The presence of the manifest row is not enough, the episode row is looked for
    as well: if the runner writes the manifest and then fails during the episode,
    the scan is wasted all the same.

    `--health-check` closes a second failure class: if the endpoint set the
    stopping rule sees collapses, the episode is written but the rule silently
    falls back to the state criterion alone (S-32). The preflight task touches
    more than one endpoint at this ceiling, so the criterion is meaningful here.
    """
    check_schema()
    print(f"preflight: {PREFLIGHT_TASK}  ceiling={PREFLIGHT_CEILING}")
    code = run_episode(
        PREFLIGHT_TASK, PREFLIGHT_CEILING, prefix=f"{PREFIX}-onkontrol", health_check=True
    )
    if code != 0:
        sys.exit(f"The preflight failed (exit {code}). The scan was not started.")

    row = (
        open_database(DATABASE)
        .execute(
            "SELECT m.serving_mode, m.max_output_tokens, m.no_progress_limit, m.boot_id, "
            "m.wall_clock_utc, m.journal_mode, m.synchronous_setting, "
            "e.total_model_calls, e.termination_reason "
            "FROM run_manifests m JOIN episodes e USING(run_id) WHERE m.run_id LIKE ?",
            (f"{PREFIX}-onkontrol-%",),
        )
        .fetchone()
    )
    if row is None:
        sys.exit(
            "The preflight ran but there is no manifest or episode row. The scan was not started."
        )
    if not row["total_model_calls"]:
        sys.exit("The preflight episode wrote no model call at all. The scan was not started.")
    print("  " + "  ".join(f"{name}={row[name]}" for name in row.keys()))
    print()


def verdict_detail(task: str) -> dict[str, int]:
    """How many of the tests labelled `no_op_fail` were passed.

    The official criterion is binary. This number carries partial progress and
    leaves out the trivial tests: a test labelled `no_op_pass` passes even when
    the agent does nothing, so it is not evidence of progress.
    """
    path = os.path.join(
        "experiments", "outputs", f"{PREFIX}-{task}", "evaluations", f"on_only_{task}.json"
    )
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        entry = (json.load(handle).get("individual") or {}).get(task) or {}
    passing = entry.get("passes") or []
    failing = entry.get("failures") or []
    meaningful_passed = sum(1 for t in passing if t.get("label") == "no_op_fail")
    meaningful_total = sum(1 for t in passing + failing if t.get("label") == "no_op_fail")
    return {
        "meaningful_passed": meaningful_passed,
        "meaningful_total": meaningful_total,
        "trivial_passed": sum(1 for t in passing if t.get("label") == "no_op_pass"),
    }


def main() -> None:
    if not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not set.")

    selection, band_size = sample()
    print(f"split={SPLIT}  model={MODEL}  tasks={len(selection)}  multiplier={MULTIPLIER}")
    print(f"band sizes (whole split): {band_size}")
    print(f"database={DATABASE}  prefix={PREFIX}")
    print()

    connection = open_database(DATABASE)
    guard_written_condition(connection, selection)

    # Skipping comes after the condition guard on purpose: what is already
    # written has to match the condition about to run before it is treated as
    # done. Skipping first would carry an episode from another condition into
    # this set silently (S-31).
    todo = remaining(connection, selection)
    skipped = len(selection) - len(todo)
    if skipped:
        print(f"resume: {skipped} of {len(selection)} episodes already written, skipping them")
    if not todo:
        print("every episode in this set is already written. Nothing to run.")
        return

    preflight()

    for index, (task, task_anchor, step_ceiling, name) in enumerate(todo, 1):
        print(
            f"[{index}/{len(todo)}] {task}  band={name}  anchor={task_anchor}"
            f"  ceiling={step_ceiling}"
        )
        run_episode(task, step_ceiling)

    connection = open_database(DATABASE)
    rows = []
    for task, task_anchor, step_ceiling, name in selection:
        record = connection.execute(
            "SELECT e.total_model_calls, e.termination_reason, e.duration_seconds, v.passed "
            "FROM episodes e JOIN verifier_results v USING(episode_id) "
            "WHERE e.run_id = ?",
            (f"{PREFIX}-{task}-{task}-{MODEL.split(':')[1].split('-')[0]}",),
        ).fetchone()
        row = {
            "task": task,
            "band": name,
            "anchor": task_anchor,
            "ceiling": step_ceiling,
            "ceiling_at_cap": step_ceiling == CEILING_CAP,
            "step": record[0] if record else None,
            "termination": record[1] if record else None,
            "elapsed": record[2] if record else None,
            "passed": record[3] if record else None,
        }
        row.update(verdict_detail(task))
        rows.append(row)

    summary = {
        # Which series a number came from stands next to it. The old file is not
        # an archive but a live reference: the two diagnostics still standing are
        # fed from there, and three weeks later a number with no series attached
        # looks like the whole to whoever queries a single file.
        "database": DATABASE,
        "prefix": PREFIX,
        "split": SPLIT,
        "model": MODEL,
        "multiplier": MULTIPLIER,
        "floor_ceiling": FLOOR_CEILING,
        "ceiling_cap": CEILING_CAP,
        "band_size": band_size,
        "episodes_with_steps": rows,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print()
    print(
        f"{'band':>8} {'n':>3} {'passing':>7} {'meaningful test':>16} {'steps in passing ep.':>21}"
    )
    for alt, ust in BANDS:
        name = band_name(alt, ust)
        grup = [s for s in rows if s["band"] == name]
        if not grup:
            continue
        passing = [s for s in grup if s["passed"] == 1]
        numerator = sum(s.get("meaningful_passed", 0) for s in grup)
        denominator = sum(s.get("meaningful_total", 0) for s in grup)
        steps = ",".join(str(s["step"]) for s in passing) or "-"
        ratio = f"{numerator}/{denominator}"
        print(f"{name:>8} {len(grup):>3} {len(passing):>6} {ratio:>14} {steps:>20}")

    # The distribution of termination reasons. This is the indicator that shows
    # the corrected stopping rule behaves as expected: the `no_progress` share was
    # 53% in the old scan and had polluted it (S-27).
    print()
    print("sonlanma sebebi:")
    reasons: dict[str, int] = {}
    for s in rows:
        reasons[str(s["termination"])] = reasons.get(str(s["termination"]), 0) + 1
    for reason, count in sorted(reasons.items(), key=lambda p: -p[1]):
        print(f"  {reason:<20} {count:>3}/{len(rows)}  ({100 * count / len(rows):.0f}%)")

    # The distribution of episode durations. The main-run estimate is redone with
    # this: the old forty-hour number rested on durations under the old stopping
    # rule.
    durations = sorted(s["elapsed"] for s in rows if s["elapsed"] is not None)
    if durations:
        n = len(durations)
        ortanca = durations[n // 2] if n % 2 else (durations[n // 2 - 1] + durations[n // 2]) / 2
        print()
        print("episode duration (seconds):")
        print(
            f"  n={n}  shortest={durations[0]:.0f}  median={ortanca:.0f}  "
            f"mean={sum(durations) / n:.0f}  longest={durations[-1]:.0f}"
        )
        print(f"  total={sum(durations) / 3600:.2f} hours")

    # The graded score, the declared diagnostic metric (setup protocol, section
    # 5).
    numerator = sum(s.get("meaningful_passed", 0) for s in rows)
    denominator = sum(s.get("meaningful_total", 0) for s in rows)
    passing_total = sum(1 for s in rows if s["passed"] == 1)
    print()
    print(f"pass rate      : {passing_total}/{len(rows)}")
    print(
        f"graded score   : {numerator}/{denominator}"
        + (f"  ({100 * numerator / denominator:.1f}%)" if denominator else "")
    )
    print(f"\nwritten: {OUTPUT}")


if __name__ == "__main__":
    main()
