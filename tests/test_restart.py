"""Three starts in a row, and no write collides in any of them.

**Why a whole run and not another unit test.** Three restarts produced three
different resume failures, one per round, and each was found by running:

| Round | What collided | Fixed by |
|---|---|---|
| 1 | `run_manifests.run_id` | the manifest compares (K-155) |
| 2 | the block boundary was counted per session | the count comes from the record (K-156) |
| 3 | `episodes.run_id, task_id, condition, seed` | the episode compares, and the
      health check takes a new id (K-157) |

Each fix was pinned by a test of its own and the next failure was still found in
Colab, because no test ever started the runner twice. This one starts it three
times.

**What is stood in for and what is not.** The model server is replaced: the
stand-in performs exactly the writes `record_run.py` performs - manifest,
episode, steps, verdict, in one transaction, through the real `zihin.records`
helpers - because those writes are the thing under test. The builders at the
block boundary are the real scripts, as subprocesses. The only injected failure
is a single `SystemExit` from `build`, which is what `build` itself raises when
a builder fails, reproducing the second start's crash.
"""

from __future__ import annotations

import ast
import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

from zihin.records import (
    AlreadyRecorded,
    insert_episode,
    insert_run_manifest,
    insert_step,
    insert_verifier_result,
    open_database,
)

REPOSITORY = Path(__file__).resolve().parents[1]
RUNNER = REPOSITORY / "scripts/setup/run_accumulation.py"

MANIFEST = {
    "created_at": "uptime:1.0",
    "model_tag": "qwen2.5-coder:32b-instruct-q4_K_M",
    "num_ctx_requested": 32768,
    "num_ctx_effective": 32768,
    "context_verified": 1,
    "kv_cache_type": "q8_0",
    "flash_attention": 1,
    "temperature": 0.2,
    "base_seed": 123,
    "keep_alive": "30m0s",
    "no_progress_limit": 40,
    "max_output_tokens": 4000,
    "max_prompt_characters": 50000,
    "model_server_env": {"OLLAMA_CONTEXT_LENGTH": "32768"},
    "appworld_version": "0.2.0.dev0",
    "appworld_commit": "a072b7a",
    "code_commit": "deadbeef",
    "instruction_file_digest": "0" * 64,
    "os_environment": "Linux / 3.11",
    "shield_mode": "shadow",
    "shield_config_digest": "a" * 64,
}


class Died(RuntimeError):
    """The session was reclaimed. Not a failure of the run, a failure of the runtime."""


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_accumulation_restart", RUNNER)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["run_accumulation.py", "bir1"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    return module


class Session:
    """One start of the runner, with the model stood in for and the writes real."""

    def __init__(self, runner, database: Path, die_after: int | None = None):
        self.runner = runner
        self.database = database
        self.die_after = die_after
        self.written: list[str] = []
        self.collisions: list[str] = []

    def run_episode(
        self, task, seed_index, step_ceiling, health_check=False, prefix=None, split=None
    ):
        suffix = "" if seed_index == 0 else f"-s{seed_index}"
        family = prefix or self.runner.PREFIX
        run_id = f"{family}{suffix}-{task}-{task}-{self.runner.SHORT}"
        connection = open_database(self.database)
        try:
            with connection:
                insert_run_manifest(connection, run_id=run_id, **MANIFEST)
                episode_id = insert_episode(
                    connection,
                    run_id=run_id,
                    task_id=task,
                    split=split or "train",
                    condition="baseline",
                    model_ref=MANIFEST["model_tag"],
                    seed=1,
                    sequence_in_run=1,
                    model_load_state="cold",
                    step_ceiling=step_ceiling,
                    started_at="uptime:1.0",
                )
                insert_step(
                    connection, episode_id=episode_id, step_index=1, instruction_digest="0" * 64
                )
                insert_verifier_result(connection, episode_id=episode_id, passed=1)
        except sqlite3.IntegrityError as error:
            self.collisions.append(f"{run_id}: {error}")
            raise
        finally:
            connection.close()
        self.written.append(run_id)
        # The health check is not counted here for the same reason the run's own
        # counts exclude it: it is not one of the sweep's episodes.
        if health_check:
            return 0
        spent = sum(1 for name in self.written if "onkontrol" not in name)
        if self.die_after is not None and spent >= self.die_after:
            raise Died(f"the session ended after {spent} sweep episode(s)")
        return 0


@pytest.fixture
def three_starts(tmp_path, monkeypatch):
    runner = _load_runner()
    database = tmp_path / "record.sqlite"
    open_database(database).close()
    monkeypatch.setattr(runner, "ACTIVE_SERIES", str(database))
    monkeypatch.setattr(runner, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setenv("MODEL_SERVER_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(runner.OPTIONS, "dry_run", False, raising=False)
    return runner, database


def _episodes(database: Path, pattern: str) -> int:
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return connection.execute(
            "SELECT COUNT(*) FROM episodes WHERE run_id LIKE ?", (pattern,)
        ).fetchone()[0]
    finally:
        connection.close()


def test_three_starts_in_a_row_collide_on_nothing(three_starts, monkeypatch, capsys):
    runner, database = three_starts
    sessions = []

    # ---- start 1: dies mid-block, before any boundary
    first = Session(runner, database, die_after=20)
    sessions.append(first)
    monkeypatch.setattr(runner, "run_episode", first.run_episode)
    with pytest.raises(Died):
        runner.main()
    assert not first.collisions, first.collisions
    assert _episodes(database, "bir1-%") == 20 + 1, "twenty episodes and one health check"

    # ---- start 2: resumes, and the block boundary fails the way it did in Colab
    second = Session(runner, database)
    sessions.append(second)
    monkeypatch.setattr(runner, "run_episode", second.run_episode)
    real_build = runner.build
    calls = {"n": 0}

    def build_once_broken(script, *arguments):
        calls["n"] += 1
        if calls["n"] == 1:
            raise SystemExit(f"{script} failed (2): the second start's crash")
        return real_build(script, *arguments)

    monkeypatch.setattr(runner, "build", build_once_broken)
    with pytest.raises(SystemExit):
        runner.main()
    assert not second.collisions, second.collisions
    assert calls["n"] == 1, "the boundary was not reached"

    # ---- start 3: everything real, and it finishes
    monkeypatch.setattr(runner, "build", real_build)
    third = Session(runner, database)
    sessions.append(third)
    monkeypatch.setattr(runner, "run_episode", third.run_episode)
    runner.main()
    assert not third.collisions, third.collisions

    # ---- what the three starts left behind
    collisions = [line for session in sessions for line in session.collisions]
    assert collisions == [], collisions

    ledger = runner.load_ledger()
    assert ledger["blocks"], "no block was ever closed"

    # The stand-in writes no API calls, so the miner finds no skill in any block
    # and branch A fires after two quiet ones. That is the declared rule working,
    # not an artefact of the test: the run stops where it says it stops.
    assert "branch A" in (ledger["stopped"] or ""), ledger["stopped"]
    assert [row["block"] for row in ledger["blocks"]] == [1, 2]
    assert [row["blocks_covered"] for row in ledger["blocks"]] == [1, 1]

    sweep = _episodes(database, "bir1-%") - _episodes(database, "bir1-onkontrol%")
    assert sweep == 60, f"two blocks of thirty were run, the record has {sweep}"
    assert _episodes(database, "bir1-onkontrol%") == 3, "one health check per start"

    # And every episode identity is distinct: a collision would have raised, but
    # a silent duplicate under a different identity would not have.
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT run_id) FROM episodes"
        ).fetchone()
    finally:
        connection.close()
    assert rows[0] == rows[1], f"{rows[0]} episodes under {rows[1]} distinct run ids"


def test_the_health_check_takes_a_new_identity_every_start(three_starts, monkeypatch):
    """Its ceiling is three and its task is outside the swept split: it is a
    health check, so it runs every start and each run is its own episode."""
    runner, database = three_starts
    seen = []
    for _ in range(3):
        prefix = runner.preflight_prefix()
        seen.append(prefix)
        session = Session(runner, database)
        session.run_episode(
            runner.PREFLIGHT_TASK, 0, runner.PREFLIGHT_CEILING, health_check=True, prefix=prefix
        )
    assert len(set(seen)) == 3, seen
    assert seen == ["bir1-onkontrol1", "bir1-onkontrol2", "bir1-onkontrol3"]
    assert _episodes(database, "bir1-onkontrol%") == 3


def test_the_health_check_is_not_counted_among_the_runs_episodes(three_starts, monkeypatch):
    runner, database = three_starts
    session = Session(runner, database)
    session.run_episode(
        runner.PREFLIGHT_TASK,
        0,
        runner.PREFLIGHT_CEILING,
        health_check=True,
        prefix=runner.preflight_prefix(),
    )
    # A task of the swept split: the count is over sweep episodes, and a
    # synthetic id would not be one (K-160).
    session.run_episode(runner.swept_tasks()[0], 0, 20)
    assert _episodes(database, "bir1-%") == 2
    assert runner.library_state()["episodes_this_run"] == 1


def test_an_episode_re_attempted_under_another_condition_is_refused(three_starts):
    """The other half of the rule: identical conditions continue, different ones stop."""
    runner, database = three_starts
    session = Session(runner, database)
    session.run_episode("t000_1", 0, 20)
    connection = open_database(database)
    try:
        with pytest.raises(Exception) as error:
            with connection:
                insert_episode(
                    connection,
                    run_id=f"bir1-t000_1-t000_1-{runner.SHORT}",
                    task_id="t000_1",
                    split="test_normal",
                    condition="baseline",
                    model_ref=MANIFEST["model_tag"],
                    seed=1,
                    sequence_in_run=1,
                    model_load_state="cold",
                    step_ceiling=20,
                    started_at="uptime:1.0",
                )
        assert "split" in str(error.value)
    finally:
        connection.close()


def test_an_episode_re_attempted_under_the_same_condition_is_not_written_twice(three_starts):
    """The backstop the numbering sits in front of.

    With the health check numbered, the three starts above re-attempt no episode
    identity at all - which is the point of the numbering. This asks the write
    itself what it does when an identity does come back.
    """
    runner, database = three_starts
    session = Session(runner, database)
    session.run_episode("t000_1", 0, 20)
    before = _episodes(database, "bir1-%")
    with pytest.raises(AlreadyRecorded) as already:
        session.run_episode("t000_1", 0, 20)
    assert already.value.episode_id
    assert _episodes(database, "bir1-%") == before, "a second row was written"


def test_the_recorder_treats_an_already_recorded_episode_as_a_finished_one():
    """And the caller honours it: `record_run.py` exits 0 rather than crashing.

    Read from the file rather than run, because running it needs a model server.
    What is pinned is the shape the fix depends on - the episode write inside a
    `try` whose handler names `AlreadyRecorded` and leaves with status zero.
    """
    source = (REPOSITORY / "scripts/record_run.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    handlers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        and any(
            isinstance(handler.type, ast.Name) and handler.type.id == "AlreadyRecorded"
            for handler in node.handlers
        )
    ]
    assert handlers, "record_run.py does not handle AlreadyRecorded"
    guarded = handlers[0]
    calls = [
        node.func.id
        for node in ast.walk(guarded)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "insert_episode" in calls, "the episode write is not inside the guarded block"
    handler = next(
        h
        for h in guarded.handlers
        if isinstance(h.type, ast.Name) and h.type.id == "AlreadyRecorded"
    )
    exits = [
        node
        for node in ast.walk(handler)
        if isinstance(node, ast.Raise)
        and isinstance(node.exc, ast.Call)
        and getattr(node.exc.func, "id", "") == "SystemExit"
    ]
    assert exits, "the handler does not leave with a status"
    assert exits[0].exc.args[0].value == 0, "an already recorded episode is not a failure"


def test_a_row_under_the_runs_id_for_a_task_outside_the_split_is_not_a_sweep_episode(
    three_starts,
):
    """The first preflight, before K-155, wrote under the run's own id: task
    `024c982_1` from `test_normal`, ceiling 3. It is neither under the preflight
    family nor a sweep episode, and counting it put the boundary one episode
    early - sweep 0 closed at 89 of 90 (K-160)."""
    runner, database = three_starts
    session = Session(runner, database)
    session.run_episode(runner.swept_tasks()[0], 0, 20)
    session.run_episode("024c982_1", 0, 3)  # under bir1-..., not the preflight family
    assert "024c982_1" not in runner.swept_tasks()
    assert _episodes(database, "bir1-%") == 2
    assert runner.library_state()["episodes_this_run"] == 1


def test_blocks_are_counted_by_coverage_not_by_ledger_rows(three_starts):
    """One catch-up row can stand for two blocks. Counting rows numbered the
    next block 2 and told the next restart two boundaries were due (K-160)."""
    runner, _ = three_starts
    ledger = runner.load_ledger()
    ledger["blocks"] = [{"block": 2, "blocks_covered": 2, "episodes_run_total": 60}]
    assert runner.blocks_closed(ledger) == 2
    assert runner.boundaries_due(ledger, 90) == 1
    assert runner.boundaries_due(ledger, 89) == 0
    ledger["blocks"].append({"block": 3, "episodes_run_total": 90})  # no field: one block
    assert runner.blocks_closed(ledger) == 3
    assert runner.boundaries_due(ledger, 120) == 1


def test_the_loop_numbers_the_next_block_after_the_blocks_closed():
    """Read off the file: both call sites number the block from coverage."""
    source = RUNNER.read_text(encoding="utf-8")
    assert 'len(ledger["blocks"]) + 1' not in source
    assert source.count("close_block(ledger, blocks_closed(ledger) + 1, spent)") == 2


def test_the_depth_cap_is_passed_only_when_declared(three_starts, monkeypatch):
    """A budget, not a declared threshold: absent from section 18.2 the compiler
    keeps its own default, present it is passed through (K-160)."""
    runner, database = three_starts
    seen = []
    monkeypatch.setattr(runner, "build", lambda script, *a: seen.append((script, a)) or 0)
    ledger = runner.load_ledger()
    ledger["blocks"] = []
    runner.close_block(ledger, 1, 30)
    library = next(a for s, a in seen if s == "build_skill_library.py")
    declared = runner.declared_field
    try:
        expected = declared("library_max_length", runner.PREFIX)
    except runner.Undeclared:
        expected = None
    if expected is None:
        assert "--max-length" not in library
    else:
        assert library[library.index("--max-length") + 1] == expected
