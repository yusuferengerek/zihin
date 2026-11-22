"""The experiment's driver: phase 1, one slice per session (K-185).

**What it does.** Takes the next N tasks of the declared order as a slice, writes
the slice into the record before any episode, and runs every task's three seeds
of phase 1's three conditions (`baseline`, `skills_failures`,
`irrelevant_retrieval`). On a task the carded arm cannot reach only the baseline
runs (K1). A slice left open by a session that died is finished before a new one
opens, whatever N says.

**When it stops before running anything.**

- A measurement-defining path changed since the experiment's first episode. The
  slices on either side of that change cannot be pooled and the change needs a
  dated addendum; the driver does not warn and go on. `--accept-path-change` goes
  on, and every episode it lets through carries the flag in `experiment_episodes`.
- The library the runner opens is not the one the analysis sets were derived
  from, or the slots it builds today are not the ones they were derived from.
- The preflight fails. It runs under `dnyk`, the experiment's control prefix, on
  a task setup already touched, so it touches nothing new (K-178).

**What it prints at the end.** Tasks finished, episodes written, and the mean
duration over every condition - nothing by condition and nothing confirmatory
(K-186).

**It carries no `--allow-dirty-tree`.** The runner refuses a dirty tree for the
experiment (K-180, K-182); this driver has no way to ask for one.

Usage:

    uv run python scripts/run_experiment.py dny --tasks 10
    uv run python scripts/run_experiment.py dny --tasks 10 --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.declared import (  # noqa: E402
    EXPERIMENT_CONTROL_PREFIX,
    EXPERIMENT_PREFIX,
    Undeclared,
    declared_model,
)
from zihin.experiment import (  # noqa: E402
    descriptive,
    episodes_of,
    experiment_name,
    load_order,
    load_sets,
    run_identity,
)
from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    boot_id,
    changed_files,
    completed_runs,
    insert_experiment_slice,
    load_model_config,
    load_recording_limits,
    missing_manifest_constraints,
    open_database,
    open_library,
    resume_check,
    table_matches_schema,
)
from zihin.slots import compose  # noqa: E402
from zihin.touched import (  # noqa: E402
    RECORD_SERIES,
    experiment_problems,
    load_touched,
    split_membership,
)

SPLIT = "test_normal"
# The band sweep's own formula, the one every declared run has used (§18.2).
MULTIPLIER, FLOOR_CEILING, CEILING_CAP = 2, 20, 150
# The preflight task: a `test_normal` task setup already touched, so a `dnyk`
# episode on it changes nothing in the touched list.
PREFLIGHT_TASK = "024c982_1"
PREFLIGHT_CEILING = 3
EXPERIMENT_TABLES = ("experiment_slices", "experiment_episodes")


def parse(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefix", help="the experiment's prefix; it names its conditions section")
    parser.add_argument("--tasks", type=int, required=True, help="how many tasks a new slice takes")
    parser.add_argument(
        "--accept-path-change",
        action="store_true",
        help=(
            "Goes on although a measurement-defining path changed since the experiment's "
            "first episode. Written into every episode it lets through."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="plan only; writes nothing")
    options = parser.parse_args(argv)
    if options.prefix != EXPERIMENT_PREFIX:
        parser.error(f"this driver runs the experiment, whose prefix is {EXPERIMENT_PREFIX!r}")
    if options.tasks < 1:
        parser.error("--tasks takes a positive number")
    return options


def anchor(task: str) -> int:
    path = REPOSITORY / "data/tasks" / task / "ground_truth" / "metadata.json"
    return int(json.loads(path.read_text(encoding="utf-8"))["num_api_calls"])


def ceiling(value: int) -> int:
    return max(FLOOR_CEILING, min(CEILING_CAP, MULTIPLIER * value))


def current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY, capture_output=True, text=True, check=True
    ).stdout.strip()


def session_id() -> str:
    """One driver invocation. The UTC start and the machine's boot id together."""
    started = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{started}-{boot_id()[:8]}"


# --- the stop rule ------------------------------------------------------------


def first_experiment_commit(connection, prefix: str) -> str | None:
    """The commit the experiment's first episode ran on, or None before it."""
    row = connection.execute(
        "SELECT m.code_commit FROM episodes e JOIN run_manifests m USING (run_id) "
        "WHERE e.run_id LIKE ? ORDER BY e.episode_id LIMIT 1",
        (prefix + "-%",),
    ).fetchone()
    return None if row is None else row[0]


def path_change(connection, prefix: str, commit: str, accept: bool) -> bool:
    """Whether this session runs past a path change. Exits when it may not.

    Compared with the experiment's first episode, not the last one: two small
    changes each below notice would otherwise add up to a different measurement.
    A git that cannot be read reports its failure as a changed path, so it stops
    too - a comparison that did not happen is not an agreement.
    """
    first = first_experiment_commit(connection, prefix)
    if first is None or first == commit:
        return False
    changed, defining = changed_files(first, commit)
    if not defining:
        print(
            f"since the first episode ({first[:7]}): {len(changed)} file(s) changed, none of them "
            "measurement-defining"
        )
        return False
    print(
        f"since the experiment's first episode ({first[:7]} -> {commit[:7]}) measurement-defining "
        "paths changed:"
    )
    for path in defining:
        print(f"  {path}")
    if not accept:
        sys.exit(
            "STOPPED: the slices before and after this change cannot be pooled, and the change "
            "needs a dated addendum. To go on anyway pass --accept-path-change; every episode "
            "it lets through carries the flag."
        )
    print("going on: --accept-path-change was given, and every episode of this session says so")
    return True


# --- slices -------------------------------------------------------------------


def slices(connection) -> dict[int, list[str]]:
    rows = connection.execute(
        "SELECT slice, task_id FROM experiment_slices ORDER BY slice, position"
    ).fetchall()
    found: dict[int, list[str]] = {}
    for number, task in rows:
        found.setdefault(number, []).append(task)
    return found


def unfinished(tasks, written: set[str], covered: dict[str, bool], seeds: int, short: str):
    return [
        task
        for task in tasks
        if not all(
            run_identity(EXPERIMENT_PREFIX, c, s, task, short) in written
            for c, s in episodes_of(task, covered[task], seeds)
        )
    ]


def plan_slice(
    opened: dict[int, list[str]],
    order: list[str],
    size: int,
    written: set[str],
    covered: dict[str, bool],
    seeds: int,
    short: str,
) -> tuple[int, list[str], bool]:
    """(slice number, its tasks, whether it is new). An open slice is finished first."""
    if opened:
        last = max(opened)
        if unfinished(opened[last], written, covered, seeds, short):
            return last, opened[last], False
    taken = {task for tasks in opened.values() for task in tasks}
    remaining = [task for task in order if task not in taken]
    return (max(opened) + 1 if opened else 1), remaining[:size], True


# --- episodes -----------------------------------------------------------------


def run_episode(
    model: str,
    task: str,
    condition: str,
    seed_index: int,
    step_ceiling: int,
    *,
    slice_number: int | None,
    session: str | None,
    accepted: bool,
    name: str,
    health_check: bool = False,
) -> int:
    environment = dict(os.environ)
    environment.update(
        {
            "ZIHIN_TASK_ID": task,
            "ZIHIN_MODEL": model,
            "ZIHIN_SPLIT": SPLIT,
            "ZIHIN_MAX_STEPS": str(step_ceiling),
            "ZIHIN_SEED_INDEX": str(seed_index),
            "ZIHIN_EXPERIMENT": name,
        }
    )
    command = [sys.executable, "scripts/record_run.py"]
    if slice_number is not None:
        command += ["--condition", condition, "--slice", str(slice_number), "--session", session]
    if accepted:
        command.append("--path-change-accepted")
    if health_check:
        command.append("--health-check")
    result = subprocess.run(
        command, cwd=REPOSITORY, env=environment, capture_output=True, text=True
    )
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-1:] or result.stdout.strip().splitlines()[-1:]
        print(f"  episode failed ({result.returncode}): {(tail or ['(no output)'])[0][:160]}")
    return result.returncode


def boundary() -> set[str]:
    """The committed touched list's `test_normal` tasks, and the boundary checked.

    **The list is read without comparing it to the record, and that is deliberate.**
    Every session's preflight writes a new `dnyk-onkontrol<n>` family on a task
    the list already holds, and the list keeps each family as provenance. The
    membership does not move, but the full comparison would: the second session
    would find the list behind the record and stop. The comparison stays where the
    list is regenerated - locally, with `build_touched_tasks.py` - and what the
    run path needs from the record is checked here directly: that no experiment
    episode crossed the boundary (K-178).
    """
    listed = load_touched(series=())
    present = [REPOSITORY / name for name in RECORD_SERIES if (REPOSITORY / name).exists()]
    crossings = experiment_problems(present, split_membership(), listed.document)
    if crossings:
        sys.exit("the experiment boundary is crossed: " + "; ".join(crossings[:5]))
    return set(listed.tasks(SPLIT))


def preflight(model: str, touched: set[str]) -> None:
    """A health check under the control prefix, numbered from the record (K-178)."""
    family = f"{EXPERIMENT_CONTROL_PREFIX}-onkontrol"
    if PREFLIGHT_TASK not in touched:
        sys.exit(
            f"the preflight task {PREFLIGHT_TASK} is not one setup touched; "
            "it would touch a new one"
        )
    with open_database(ACTIVE_SERIES) as connection:
        seen = connection.execute(
            "SELECT COUNT(DISTINCT run_id) FROM episodes WHERE run_id LIKE ?", (family + "%",)
        ).fetchone()[0]
    name = f"{family}{seen + 1}-{PREFLIGHT_TASK}"
    print(f"preflight: {PREFLIGHT_TASK}  ceiling={PREFLIGHT_CEILING}  id={name}")
    code = run_episode(
        model,
        PREFLIGHT_TASK,
        "baseline",
        0,
        PREFLIGHT_CEILING,
        slice_number=None,
        session=None,
        accepted=False,
        name=name,
        health_check=True,
    )
    if code != 0:
        sys.exit(f"the preflight failed (exit {code}); no experiment episode was started")


def guard_written_condition(connection, expected: dict[str, dict]) -> None:
    """Refuses if an episode already written under a run id ran another condition."""
    already = completed_runs(connection, expected)
    if not already:
        return
    check = resume_check(connection, {r: expected[r] for r in already})
    for line in check.uyar:
        print(f"  warning: {line}")
    if not check.passed:
        for line in check.reddet:
            print(f"  REFUSED: {line}")
        sys.exit("episodes already written here ran under another condition; nothing was run")
    print(f"resume: {len(already)} episode(s) of this slice already written, condition matches")


def slots_today(sets: dict, tasks: list[str]) -> dict[str, bool]:
    """Whether the carded arm reaches each task, built again with the runner's selection.

    The analysis sets were derived from these slots; if the library or the
    selection moved since, the sets describe slots no episode will see.
    """
    connection, library_id, index_id = open_library()
    try:
        if (library_id, index_id) != (sets["library_id"], sets["index_id"]):
            sys.exit(
                f"the runner opens {library_id} / {index_id}; the analysis sets were derived "
                f"from {sets['library_id']} / {sets['index_id']}"
            )
        covered = {}
        for task in tasks:
            today = {}
            for condition in ("skills_failures", "irrelevant_retrieval"):
                slot = compose(
                    connection,
                    task_instruction(task),
                    condition,
                    library_id=library_id,
                    index_id=index_id,
                    task_id=task,
                )
                today[condition] = (len(slot.cards.skills), len(slot.cards.failures))
            declared = {
                c: (sets["per_task"][task][c]["skills"], sets["per_task"][task][c]["failures"])
                for c in today
            }
            if today != declared:
                sys.exit(f"{task}: the slots today are {today}; the analysis sets say {declared}")
            covered[task] = sets["per_task"][task]["skills_failures"]["covered"]
        return covered
    finally:
        connection.close()


def main() -> None:
    options = parse()
    prefix = options.prefix
    if not options.dry_run and not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not set.")
    try:
        model = declared_model(prefix)
    except Undeclared as error:
        sys.exit(str(error))
    short = model.split(":")[1].split("-")[0]
    model_config = load_model_config(REPOSITORY / "config/models.yaml")
    limits = load_recording_limits(REPOSITORY / "config/recording.yaml")
    seeds = model_config.seed_count
    order = load_order()["order"]
    sets = load_sets()
    commit = current_commit()
    print(f"prefix={prefix}  model={model}  commit={commit[:7]}  database={ACTIVE_SERIES}")

    with open_database(ACTIVE_SERIES) as connection:
        missing = missing_manifest_constraints(connection)
        if missing:
            sys.exit(f"{ACTIVE_SERIES} does not carry the manifest constraints: {missing}")
        for table in EXPERIMENT_TABLES:
            if table_matches_schema(connection, table) is not True:
                sys.exit(f"{table} in {ACTIVE_SERIES} is not the schema's table")
        accepted = path_change(connection, prefix, commit, options.accept_path_change)
        written = completed_runs(
            connection,
            [
                run_identity(prefix, c, s, t, short)
                for t in order
                for c, s in episodes_of(t, True, seeds)
            ],
        )
        opened = slices(connection)

    covered_all = {t: sets["per_task"][t]["skills_failures"]["covered"] for t in order}
    number, tasks, new = plan_slice(
        opened, order, options.tasks, written, covered_all, seeds, short
    )
    if not tasks:
        print("every task of the order is in a slice and finished")
    else:
        what = "opens" if new else "is open; its remaining tasks are finished first, --tasks unused"
        print(f"slice {number} {what}: {len(tasks)} task(s)")
    if options.dry_run:
        todo = [
            (t, c, s)
            for t in tasks
            for c, s in episodes_of(t, covered_all[t], seeds)
            if run_identity(prefix, c, s, t, short) not in written
        ]
        print(f"dry run: {len(todo)} episode(s) would run; nothing was written")
        return
    if not tasks:
        _print_summary(prefix, short, sets)
        return

    touched = boundary()
    covered = slots_today(sets, tasks)
    session = session_id()
    print(f"session {session}")
    preflight(model, touched)

    with open_database(ACTIVE_SERIES) as connection:
        if new:
            with connection:
                for task in tasks:
                    insert_experiment_slice(
                        connection,
                        slice=number,
                        position=order.index(task) + 1,
                        task_id=task,
                        session_id=session,
                        opened_commit=commit,
                    )
        expected = {
            run_identity(prefix, c, s, t, short): {
                "model_tag": model,
                "serving_mode": "local",
                "temperature": model_config.temperature,
                "base_seed": model_config.base_seed,
                "max_output_tokens": limits.max_output_tokens,
                "no_progress_limit": limits.no_progress_limit,
                "split": SPLIT,
                "condition": c,
                "step_ceiling": ceiling(anchor(t)),
            }
            for t in tasks
            for c, s in episodes_of(t, covered[t], seeds)
        }
        guard_written_condition(connection, expected)
        written = completed_runs(connection, expected)

    for index, task in enumerate(tasks, 1):
        step_ceiling = ceiling(anchor(task))
        for condition, seed in episodes_of(task, covered[task], seeds):
            if run_identity(prefix, condition, seed, task, short) in written:
                continue
            print(
                f"[{index}/{len(tasks)}] {task}  {condition}  seed={seed}  ceiling={step_ceiling}"
            )
            code = run_episode(
                model,
                task,
                condition,
                seed,
                step_ceiling,
                slice_number=number,
                session=session,
                accepted=accepted,
                name=experiment_name(prefix, condition, seed, task),
            )
            if code != 0:
                sys.exit(
                    f"stopped at the first failed episode (exit {code}); running the same command "
                    "again resumes from here"
                )
    _print_summary(prefix, short, sets)


def _print_summary(prefix: str, short: str, sets: dict) -> None:
    with open_database(ACTIVE_SERIES) as connection:
        summary = descriptive(connection, sets, prefix, short)
    print()
    print(f"tasks finished : {summary['tasks_finished']} of {summary['tasks']}")
    print(f"episodes       : {summary['episodes']} of {summary['episodes_planned']}")
    mean = summary["mean_duration_seconds"]
    print(f"mean duration  : {'-' if mean is None else f'{mean} s'}, every condition together")


if __name__ == "__main__":
    main()
