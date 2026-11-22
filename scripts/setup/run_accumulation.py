"""The accumulation run: a corpus from the evaluated model's own episodes.

**What it does.** Sweeps the `train` split with the model the protocol declares
for its prefix, and every thirty episodes re-mines the skill library **and** the
failure index with the real builders. The stopping criterion is read off the
ledger it writes, not off memory.

**Two branches, whichever fires first** (protocol section 18.3):

- **A, yield.** Two consecutive blocks that add zero new skills stop the run. It
  reads skills, not patterns: the filtering chain that takes 105 patterns down to
  4 skills does not track the pattern count.
- **B, a cap.** 270 episodes. If A has not fired the run stops anyway and the
  result is "the library had not saturated at 270 episodes" — a result, not a
  failure.

**The index is re-mined in the same block.** `S-65` happened once: the corpus
grew, the index did not, and the record fell five cards behind. Re-mining one
without the other is what produced that gap, so here they move together.

**One seed on the first sweep.** Support is counted by distinct task, so a second
seed on a task that already passed adds nothing. Later sweeps re-run only the
failures, at the next seed index.

**The model is not named here.** The prefix names its conditions section and the
model is resolved from it (K-138).

Usage:

    uv run python scripts/setup/run_accumulation.py bir1
    uv run python scripts/setup/run_accumulation.py bir1 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from appworld.task import load_task_ids  # noqa: E402

from zihin.declared import Undeclared, declared_field, declared_model  # noqa: E402
from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    LIBRARY_SERIES,
    completed_runs,
    insert_ledger_row,
    ledger_rows,
    load_model_config,
    load_recording_limits,
    missing_manifest_constraints,
    open_database,
    resume_check,
    working_tree,
)

LEDGER = REPOSITORY / "results/accumulation-ledger.json"
SPLIT = "train"
BLOCK = 30
CAP = 270
# Branch A: this many consecutive zero-yield blocks stop the run.
QUIET_BLOCKS = 2
MULTIPLIER, FLOOR_CEILING, CEILING_CAP = 2, 20, 150
# The preflight task, already outside the evaluation sample.
PREFLIGHT_TASK = "024c982_1"
PREFLIGHT_CEILING = 3
# The split the preflight task really belongs to. It is one of the `test_normal`
# tasks touched during setup, deliberately outside the swept sample - and the
# record was saying otherwise: `run_episode` wrote `ZIHIN_SPLIT=train` for it
# too, so seven health-check rows and one older row claim a split their task is
# not in. The corpus filter reads that column (K-159), so a health check that
# ever passed would have entered the corpus as a `train` episode. Measured on
# the record: eight such rows, all failing, so none reached the compiler
# (K-163). A test pins the constant against `load_task_ids`.
PREFLIGHT_SPLIT = "test_normal"
# How many seeds exist at all. One source: the derivation's own limit in
# `config/models.yaml`, which is what `seed_for` refuses to exceed. Section 18.3
# declares that failed tasks are re-run "with the next seed" and names no
# number; section 18.2 declares one seed for this run. The runner does not
# choose between them - it refuses to ask for a seed that cannot be derived
# (K-162).
SEED_COUNT = load_model_config("config/models.yaml").seed_count

PARSER = argparse.ArgumentParser(description="The accumulation run over the train split.")
PARSER.add_argument("prefix", help="run id prefix; it names the conditions section")
PARSER.add_argument("--allow-dirty-tree", action="store_true")
PARSER.add_argument("--dry-run", action="store_true", help="plan only; runs no episode")
OPTIONS = PARSER.parse_args()
PREFIX = OPTIONS.prefix
MODEL = declared_model(PREFIX)
SHORT = MODEL.split(":")[1].split("-")[0]
# The preflight's run ids are a family of their own, the way `measure_band.py`
# gives its preflight one. Without it the health check wrote under the id a swept
# task would use: `measure_band.py` had already solved this and this runner,
# written from it, dropped that argument (K-155).
PREFLIGHT_PREFIX = f"{PREFIX}-onkontrol"


def anchor(task: str) -> int:
    path = REPOSITORY / "data/tasks" / task / "ground_truth" / "metadata.json"
    return int(json.loads(path.read_text(encoding="utf-8"))["num_api_calls"])


def ceiling(value: int) -> int:
    return max(FLOOR_CEILING, min(CEILING_CAP, MULTIPLIER * value))


def run_identity(task: str, seed_index: int) -> str:
    """The run id for a task at a seed. The seed is in the id from the second
    sweep on, so a re-run is a new row rather than a collision."""
    suffix = "" if seed_index == 0 else f"-s{seed_index}"
    return f"{PREFIX}{suffix}-{task}-{task}-{SHORT}"


def run_episode(
    task: str,
    seed_index: int,
    step_ceiling: int,
    health_check: bool = False,
    prefix: str | None = None,
    split: str | None = None,
) -> int:
    suffix = "" if seed_index == 0 else f"-s{seed_index}"
    environment = dict(os.environ)
    environment["ZIHIN_TASK_ID"] = task
    environment["ZIHIN_MODEL"] = MODEL
    environment["ZIHIN_SPLIT"] = split or SPLIT
    environment["ZIHIN_MAX_STEPS"] = str(step_ceiling)
    environment["ZIHIN_SEED_INDEX"] = str(seed_index)
    environment["ZIHIN_EXPERIMENT"] = f"{prefix or PREFIX}{suffix}-{task}"
    command = [sys.executable, "scripts/record_run.py"]
    if OPTIONS.allow_dirty_tree:
        command.append("--allow-dirty-tree")
    if health_check:
        command.append("--health-check")
    result = subprocess.run(
        command, cwd=REPOSITORY, env=environment, capture_output=True, text=True
    )
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-1:] or ["(no stderr)"]
        print(f"  episode failed ({result.returncode}): {tail[0][:140]}")
    return result.returncode


def build(script: str, *arguments: str) -> int:
    """Runs one of the real builders. A failed build stops the run: mining half
    the pair is what S-65 is.

    **The database is passed, not defaulted.** Both builders default to
    `ACTIVE_SERIES` on their own, so the parent and the child were each deciding
    independently which file to open. They agree today; two independent decisions
    that agree are still two decisions (K-138).
    """
    result = subprocess.run(
        [sys.executable, f"scripts/setup/{script}", "--database", str(ACTIVE_SERIES), *arguments],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        tail = result.stderr.strip().splitlines()[-3:]
        sys.exit(f"{script} failed ({result.returncode}):\n  " + "\n  ".join(tail))
    return result.returncode


_SWEPT: list[str] = []


def swept_tasks() -> list[str]:
    """The tasks of the accumulation split, read once."""
    if not _SWEPT:
        _SWEPT.extend(sorted(load_task_ids(SPLIT)))
    return _SWEPT


def blocks_closed(ledger: dict) -> int:
    """How many block boundaries the ledger has mined - blocks, not rows.

    A catch-up row covers every boundary that went by unmined (K-156), so one
    row can stand for two blocks. Counting rows numbered the block after the
    catch-up as 2 and told the next restart that two boundaries were due when
    one was (K-160).
    """
    return sum(int(row.get("blocks_covered", 1)) for row in ledger["blocks"])


def library_state() -> dict:
    connection = open_database(ACTIVE_SERIES)
    connection.row_factory = None
    skills = connection.execute(
        "SELECT library_id, COUNT(*) FROM skills GROUP BY library_id ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()
    index = connection.execute(
        "SELECT index_id, COUNT(*) FROM failure_patterns GROUP BY index_id "
        "ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()
    effects = (
        [
            row[0]
            for row in connection.execute(
                "SELECT effect_suffix FROM skills WHERE library_id = ?", (skills[0],)
            )
        ]
        if skills
        else []
    )
    # The separator is in the pattern. Without it `b32%` matches `b32c-...` as
    # well, and both live in this file: 27 episodes under `b32` and 31 under
    # `b32c`, so that pattern returns 58. `bir1` has no such sibling today and
    # the numbers below are the ones the stopping decision reads, so the
    # boundary goes in before the pattern is right by luck (K-155).
    # The whole preflight family is excluded, not one id: it takes a new number
    # every start. It spends an episode and writes a row, but it is a health
    # check at a ceiling of three, not one of the sweep's episodes; counted in,
    # it would add one to the run's total on every start and the stopping rule
    # reads that total.
    # And only tasks of the swept split. The first preflight, before K-155,
    # wrote under the run's own id - `bir1-024c982_1-...`, a `test_normal` task
    # at a ceiling of three - and that row is neither a sweep episode nor under
    # the preflight family. Counted, it put the boundary one episode early and
    # left sweep 0 at 89 of 90 (K-160). The record is append-only, so the row
    # stays and the count learns what a sweep episode is.
    tasks = swept_tasks()
    marks = ", ".join("?" for _ in tasks)
    episodes = connection.execute(
        "SELECT COUNT(*) FROM episodes WHERE run_id LIKE ? AND run_id NOT LIKE ? "
        f"AND task_id IN ({marks})",
        (PREFIX + "-%", PREFLIGHT_PREFIX + "%", *tasks),
    ).fetchone()[0]
    passed = connection.execute(
        "SELECT COUNT(DISTINCT e.task_id) FROM episodes e "
        "JOIN verifier_results v ON v.episode_id = e.episode_id "
        "WHERE v.passed = 1 AND e.run_id LIKE ? AND e.run_id NOT LIKE ? "
        f"AND e.task_id IN ({marks})",
        (PREFIX + "-%", PREFLIGHT_PREFIX + "%", *tasks),
    ).fetchone()[0]
    connection.close()
    return {
        "library_id": skills[0] if skills else None,
        "skills": skills[1] if skills else 0,
        "effect_suffixes": sorted(effects),
        "index_id": index[0] if index else None,
        "cards": index[1] if index else 0,
        "episodes_this_run": episodes,
        "distinct_tasks_passed": passed,
    }


def load_ledger() -> dict:
    """The run's ledger, read from the record.

    **It used to be read from a JSON under `results/`, and that was the defect.**
    On Colab the checkout is re-cloned every session while the record is
    symlinked to Drive, so the file went and the episodes stayed. Across seven
    mining events the runner read "0 blocks closed" every time, every block
    counted its skills as new, and branch A - two consecutive quiet blocks - was
    never once evaluated (K-162). The record is the only durable store the run
    has, so the ledger lives there.
    """
    connection = open_database(ACTIVE_SERIES)
    try:
        blocks = ledger_rows(connection, PREFIX)
    finally:
        connection.close()
    stopped = next((row["stopped"] for row in reversed(blocks) if row["stopped"]), None)
    return {
        "what": "the accumulation run, block by block, and the stopping decision",
        "prefix": PREFIX,
        "model": MODEL,
        "split": SPLIT,
        "block_size": BLOCK,
        "episode_cap": CAP,
        "quiet_blocks_to_stop": QUIET_BLOCKS,
        "declared_in": "experiments/setup-protocol.tr.md section 18",
        "source": f"{ACTIVE_SERIES} table run_ledger",
        "blocks": blocks,
        "stopped": stopped,
    }


def save(ledger: dict) -> None:
    """Writes the JSON projection. It is generated, not the source (K-162)."""
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def quiet_blocks(ledger: dict) -> int:
    """How many blocks in a row added no new skill, counting back from the last."""
    quiet = 0
    for entry in reversed(ledger["blocks"]):
        if entry["new_skills"] == 0:
            quiet += 1
        else:
            break
    return quiet


def branch_a_fired(ledger: dict) -> bool:
    """Branch A, asked of the ledger rather than computed while mining.

    A question about the ledger belongs to the ledger. Kept inside the mining
    step it could only ever be asked of blocks this session had closed, and on
    Colab that was never more than one - the ledger was reloaded empty every
    session, so the count restarted and the criterion was never met (K-162).
    """
    return quiet_blocks(ledger) >= QUIET_BLOCKS


def close_block(ledger: dict, number: int, episodes_run: int, covers: int = 1) -> bool:
    """Re-mines both, appends a ledger row, and says whether branch A fired.

    `covers`: how many block boundaries this one mining stands for. It is 1 in
    the ordinary case and more only when a restart found boundaries that had gone
    by unmined. Branch A counts consecutive rows, so a row covering two blocks is
    one observation, not two - the corpus of the block in between was never mined
    and nothing can be said about what it would have yielded.
    """
    print(f"\n--- block {number}: re-mining the library and the index together")
    # The thresholds come from the run's declared conditions. They used not to be
    # passed at all, and both builders require them: the run reached sixty
    # episodes and then died at this line on argparse's exit code 2 (K-156).
    # The corpus rule goes with the thresholds: the evaluated model on the
    # accumulation split, and nothing else the file holds (K-159).
    # The depth cap is a budget, not a declared threshold. It is passed only
    # when section 18.2 declares `library_max_length`; otherwise the compiler's
    # own default applies and the guard still names itself if it binds (K-160).
    cap: list[str] = []
    try:
        cap = ["--max-length", declared_field("library_max_length", PREFIX)]
    except Undeclared:
        pass
    build(
        "build_skill_library.py",
        "--max-gap",
        declared_field("library_max_gap", PREFIX),
        "--min-support",
        declared_field("library_min_support", PREFIX),
        "--model-tag",
        MODEL,
        "--split",
        SPLIT,
        *cap,
    )
    build(
        "build_failure_index.py",
        "--min-support",
        declared_field("index_min_support", PREFIX),
        "--model-tag",
        MODEL,
        "--split",
        SPLIT,
    )
    # The builders write into the active series. K-143's open gap is that
    # LIBRARY_SERIES does not follow on its own, so from this block on a carded
    # run would read the old library unless that line moves. The preflight asks
    # too; this says it where it happens.
    if LIBRARY_SERIES != ACTIVE_SERIES:
        print(
            f"    NOTE: the library is now in {ACTIVE_SERIES} but "
            f"zihin.records.LIBRARY_SERIES still names {LIBRARY_SERIES}. "
            "Move that line before any carded run (K-143)."
        )
    state = library_state()
    previous = ledger["blocks"][-1] if ledger["blocks"] else None
    before = set(previous["effect_suffixes"]) if previous else set()
    new = sorted(set(state["effect_suffixes"]) - before)
    row = {
        "prefix": PREFIX,
        "block": number,
        "blocks_covered": covers,
        "episodes_run_total": episodes_run,
        **state,
        "new_skills": len(new),
        "new_effect_suffixes": new,
    }
    # Into the record first, and in the same store as the episodes it counts.
    # `episodes_this_run` is a count, not a column of this table: it is derived
    # from the episodes and would be a second copy of them.
    written_row = {key: value for key, value in row.items() if key != "episodes_this_run"}
    connection = open_database(ACTIVE_SERIES)
    try:
        with connection:
            insert_ledger_row(connection, **written_row)
    finally:
        connection.close()
    ledger["blocks"].append(row)
    save(ledger)
    print(
        f"    episodes {episodes_run}  distinct passed {state['distinct_tasks_passed']}  "
        f"skills {state['skills']} (+{len(new)})  cards {state['cards']}"
    )

    quiet = quiet_blocks(ledger)
    if quiet >= QUIET_BLOCKS:
        print(f"    branch A: {quiet} consecutive blocks added no new skill. Stopping.")
        return True
    return False


def guard_written_condition(connection, identities: list[str]) -> None:
    """Refuses if rows already under this prefix ran under another condition.

    Skipping what is already written comes *after* this on purpose. Skipping
    first would carry an episode from another condition into the corpus in
    silence, and the manifest would record the mixture without preventing it
    (S-31). This run mines from those very episodes, so a mixed corpus would
    become a mixed library.
    """
    already = completed_runs(connection, identities)
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
            "no_progress_limit": limits.no_progress_limit,
            "working_tree": working_tree(),
            "split": SPLIT,
        }
        for run_id in identities
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


def boundaries_due(ledger: dict, spent: int) -> int:
    """How many block boundaries have gone by without being mined.

    Asked of the ledger and the record, never of this session's counters. The
    ledger only advances when a block closes, so a run that dies mid-block leaves
    episodes written and no row for them; a restart that trusted its own counters
    started from zero and put the next boundary a whole block late (K-156).
    """
    return max(0, spent // BLOCK - blocks_closed(ledger))


def catch_up(ledger: dict, spent: int) -> tuple[int, bool]:
    """Mines what the restart found unmined. Returns (episodes since the last
    boundary, whether branch A fired).

    One mining for however many boundaries went by, recorded as covering that
    many. Mining twice over one corpus would produce the same library the second
    time and count as a quiet block - an observation of something nobody ran.
    """
    due = boundaries_due(ledger, spent)
    if not due:
        return spent - blocks_closed(ledger) * BLOCK, False
    closed = spent // BLOCK
    print(
        f"resume: {spent} episode(s) written, {blocks_closed(ledger)} block(s) closed in "
        f"the ledger, so {due} boundary(ies) are due before any new episode"
    )
    fired = close_block(ledger, closed, spent, covers=due)
    return spent - closed * BLOCK, fired


def preflight_prefix() -> str:
    """A new run id family for each start, numbered from the record.

    **The preflight is a health check, not a measurement**, and that decides
    this. Its ceiling is three: it cannot solve the task and is not meant to. Its
    task is from `test_normal` while the run sweeps `train`, so it is outside the
    sample by construction. It is excluded from the run's episode counts. What it
    proves is that *this session* can write an episode from beginning to end -
    the recorder, the database, the Drive-backed file, the disk.

    So it has to run on every start, and every start must therefore write a new
    identity. The alternative - writing and then deleting the row - was rejected:
    episodes are append-only and only derived projections are deletable
    (`03-architecture.tr.md`), and a health check that erased its own evidence
    would leave the one thing it proves unrecorded. A record that says the check
    ran three times is telling the truth; three starts happened.

    The number comes from the record rather than from a clock: two starts on one
    Colab VM share a boot id and a wall clock is not in the record's vocabulary,
    while "how many are already there" is a question the record answers (K-157).
    """
    connection = open_database(ACTIVE_SERIES)
    try:
        seen = connection.execute(
            "SELECT COUNT(DISTINCT run_id) FROM episodes WHERE run_id LIKE ?",
            (PREFLIGHT_PREFIX + "%",),
        ).fetchone()[0]
    finally:
        connection.close()
    return f"{PREFLIGHT_PREFIX}{seen + 1}"


def preflight() -> None:
    prefix = preflight_prefix()
    print(f"preflight: {PREFLIGHT_TASK}  ceiling={PREFLIGHT_CEILING}  id={prefix}")
    code = run_episode(
        PREFLIGHT_TASK,
        0,
        PREFLIGHT_CEILING,
        health_check=True,
        prefix=prefix,
        split=PREFLIGHT_SPLIT,
    )
    if code != 0:
        sys.exit(f"the preflight failed (exit {code}). The accumulation run was not started.")


def written(connection, task: str, seed_index: int) -> bool:
    return (
        connection.execute(
            "SELECT COUNT(*) FROM episodes e JOIN verifier_results v "
            "ON v.episode_id = e.episode_id WHERE e.run_id = ?",
            (run_identity(task, seed_index),),
        ).fetchone()[0]
        > 0
    )


def main() -> None:
    if not OPTIONS.dry_run and not os.environ.get("MODEL_SERVER_URL"):
        sys.exit("MODEL_SERVER_URL is not set.")

    tasks = sorted(load_task_ids(SPLIT))
    print(f"prefix={PREFIX}  model={MODEL}  split={SPLIT}  tasks={len(tasks)}")
    print(f"block={BLOCK}  cap={CAP}  branch A after {QUIET_BLOCKS} quiet blocks")
    print(f"database={ACTIVE_SERIES}")

    missing = missing_manifest_constraints(open_database(ACTIVE_SERIES))
    if missing:
        sys.exit(
            f"{ACTIVE_SERIES} does not carry the manifest constraints: {missing}. "
            "The accumulation run was not started."
        )
    print(f"schema check: {ACTIVE_SERIES} carries all the constraints")

    identities = [run_identity(task, seed) for task in tasks for seed in range(SEED_COUNT)]
    guard_written_condition(open_database(ACTIVE_SERIES), identities)

    ledger = load_ledger()
    if ledger.get("stopped"):
        print(f"this run already stopped: {ledger['stopped']}. Nothing to do.")
        return

    if OPTIONS.dry_run:
        print("\ndry run: the plan, no episode is spent")
        print(f"  sweep 0: {len(tasks)} tasks at seed 0")
        print(f"  then failures only, at seed 1, 2, ... up to {CAP} episodes")
        print(f"  a block boundary every {BLOCK} episodes re-mines both builders")
        print(f"  ledger: {LEDGER}")
        return

    preflight()

    connection = open_database(ACTIVE_SERIES)
    # Both counts come from the record, not from this session. The ledger only
    # advances when a block closes, so a run that died mid-block resumed with
    # `spent = 0` while sixty episodes were already written: the cap would have
    # been overrun by sixty and the first block boundary would have landed thirty
    # episodes late. "Is block 1 mined" is answered by the ledger; "how many
    # episodes exist" is answered by the database (K-156).
    spent = library_state()["episodes_this_run"]
    seed_index = 0
    stop = None
    since_block, fired = catch_up(ledger, spent)
    if fired:
        print("branch A fired on the catch-up mining. Stopping.")
        return
    connection = open_database(ACTIVE_SERIES)

    while spent < CAP and stop is None:
        if seed_index == 0:
            todo = [t for t in tasks if not written(connection, t, 0)]
        else:
            passed = {
                row[0]
                for row in connection.execute(
                    "SELECT DISTINCT e.task_id FROM episodes e "
                    "JOIN verifier_results v ON v.episode_id = e.episode_id "
                    "WHERE v.passed = 1 AND e.run_id LIKE ? AND e.run_id NOT LIKE ?",
                    (PREFIX + "-%", PREFLIGHT_PREFIX + "%"),
                )
            }
            todo = [t for t in tasks if t not in passed and not written(connection, t, seed_index)]
        if not todo:
            if seed_index == 0:
                print("sweep 0 is already written; moving to the failures")
            elif seed_index >= SEED_COUNT - 1:
                stop = "no task is left to re-run"
                break
            seed_index += 1
            continue

        print(f"\n=== sweep {seed_index}: {len(todo)} task(s)")
        for index, task in enumerate(todo, 1):
            if spent >= CAP:
                stop = f"branch B: the cap of {CAP} episodes was reached"
                break
            step_ceiling = ceiling(anchor(task))
            print(f"[{index}/{len(todo)}] {task}  seed={seed_index}  ceiling={step_ceiling}")
            run_episode(task, seed_index, step_ceiling)
            spent += 1
            since_block += 1
            if since_block >= BLOCK:
                since_block = 0
                connection.close()
                if close_block(ledger, blocks_closed(ledger) + 1, spent):
                    stop = "branch A: two consecutive blocks added no new skill"
                    break
                connection = open_database(ACTIVE_SERIES)
        if stop is None:
            seed_index += 1
            if seed_index >= SEED_COUNT:
                # The seed derivation allows `seed_count` seeds and refuses the
                # next one (`seed_for`, models.yaml). The runner asked for a
                # fourth and the schema stopped it - correctly, but after the
                # sweep had already been chosen. What happens when they run out
                # is now written down rather than discovered: the run stops and
                # says so. Whether section 18.3 means more seeds than this is a
                # question for the declaration, not for the runner (K-162).
                stop = (
                    f"the seed derivation allows {SEED_COUNT} seed(s) "
                    f"(0 to {SEED_COUNT - 1}) and all of them are spent"
                )

    if since_block and stop is None:
        connection.close()
        close_block(ledger, blocks_closed(ledger) + 1, spent)
        connection = open_database(ACTIVE_SERIES)
    if stop is None and spent >= CAP:
        stop = f"branch B: the cap of {CAP} episodes was reached"
    ledger["stopped"] = stop or "every sweep is exhausted"
    ledger["episodes_spent"] = spent
    # The branch that stopped the run goes onto the last block row, in the
    # record: a stop kept only in the projection would be lost with it.
    if ledger["blocks"]:
        with open_database(ACTIVE_SERIES) as durable:
            durable.execute(
                "UPDATE run_ledger SET stopped = ? WHERE prefix = ? AND block = ?",
                (ledger["stopped"], PREFIX, ledger["blocks"][-1]["block"]),
            )
    save(ledger)
    connection.close()

    print()
    print(f"stopped: {ledger['stopped']}")
    print(f"episodes spent: {spent}")
    print(f"ledger: {LEDGER}")


if __name__ == "__main__":
    main()
