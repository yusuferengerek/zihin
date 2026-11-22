"""The ledger survives what the episodes survive.

**Why this file exists, and why the old test could not have caught it.** The
three-start test pointed `LEDGER` at `tmp_path / "ledger.json"` and that path
lives for the whole test, so it modelled a ledger that survives a restart. The
real one did not: on Colab the record is symlinked to Drive and the ledger was a
JSON inside the checkout, which the notebook re-clones every session. The test
environment differed from the real one in exactly the property under test, which
is `K-117`, and the run paid for it - seven mining events, "0 blocks closed"
every time, and branch A never evaluated once (K-162).

So every case here wipes the checkout the way a new session does: the whole
`results/` directory goes, the record stays.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

from zihin.records import insert_ledger_row, ledger_rows, open_database

REPOSITORY = Path(__file__).resolve().parents[1]
RUNNER = REPOSITORY / "scripts/setup/run_accumulation.py"


def _runner():
    spec = importlib.util.spec_from_file_location("run_accumulation_ledger", RUNNER)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["run_accumulation.py", "bir1"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    return module


@pytest.fixture
def session(tmp_path, monkeypatch):
    """A checkout and a record, the way Colab has them: only the record endures."""
    runner = _runner()
    checkout = tmp_path / "checkout"
    (checkout / "results").mkdir(parents=True)
    drive = tmp_path / "drive"
    drive.mkdir()
    record = drive / "record.sqlite"
    open_database(record).close()
    monkeypatch.setattr(runner, "ACTIVE_SERIES", str(record))
    monkeypatch.setattr(runner, "LEDGER", checkout / "results/accumulation-ledger.json")
    monkeypatch.setattr(runner, "swept_tasks", lambda: [f"t{n:03d}_1" for n in range(90)])

    def new_session():
        """What the notebook does between runs: the checkout is cloned afresh."""
        for item in (checkout / "results").iterdir():
            item.unlink()

    return runner, record, checkout, new_session


def _row(block: int, **changes):
    row = {
        "prefix": "bir1",
        "block": block,
        "blocks_covered": 1,
        "episodes_run_total": block * 30,
        "library_id": f"v0-lib-{block}",
        "skills": 4,
        "effect_suffixes": ["a", "b", "c", "d"],
        "index_id": f"v0-idx-{block}",
        "cards": 15,
        "distinct_tasks_passed": 17,
        "new_skills": 0,
        "new_effect_suffixes": [],
    }
    row.update(changes)
    return row


def test_the_ledger_is_in_the_record_not_in_the_checkout(session):
    """The defect, stated as a property: a new session keeps the blocks."""
    runner, record, _, new_session = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1, new_skills=4, new_effect_suffixes=["a", "b", "c", "d"]))
    assert runner.blocks_closed(runner.load_ledger()) == 1

    new_session()
    ledger = runner.load_ledger()
    assert runner.blocks_closed(ledger) == 1, "the ledger did not survive the new session"
    assert ledger["blocks"][0]["new_skills"] == 4
    assert ledger["blocks"][0]["effect_suffixes"] == ["a", "b", "c", "d"]


def test_branch_a_can_fire_across_sessions(session):
    """Two quiet blocks written in two different sessions still stop the run.

    This is the thing that never happened: every session read an empty ledger,
    so every block counted its skills as new and the criterion was never met.
    """
    runner, record, _, new_session = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1, new_skills=0))
    new_session()
    with open_database(record) as db:
        insert_ledger_row(db, **_row(2, new_skills=0))
    new_session()

    ledger = runner.load_ledger()
    quiet = [row for row in ledger["blocks"] if row["new_skills"] == 0]
    assert len(quiet) >= runner.QUIET_BLOCKS
    assert runner.branch_a_fired(ledger) is True


def test_the_first_block_of_a_fresh_run_is_not_quiet(session):
    """And the criterion is not met by a single block, nor by an empty ledger."""
    runner, record, _, _ = session
    assert runner.branch_a_fired(runner.load_ledger()) is False
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1, new_skills=4))
    assert runner.branch_a_fired(runner.load_ledger()) is False


def test_re_closing_a_block_collides_rather_than_doubling(session):
    """A restart that re-closes a block it already closed is reported, not written.

    The ledger is append-only and `(prefix, block)` is its identity; a second row
    for one block would count as a second observation of a block that ran once.
    """
    runner, record, _, _ = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1))
    with pytest.raises(sqlite3.IntegrityError):
        with open_database(record) as db:
            insert_ledger_row(db, **_row(1))
    assert len(ledger_rows(open_database(record), "bir1")) == 1


def test_two_runs_keep_separate_ledgers(session):
    """`prefix` is in the identity: a second run does not read the first's blocks."""
    runner, record, _, _ = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1))
        insert_ledger_row(db, **_row(1, prefix="bir2"))
    assert len(ledger_rows(open_database(record), "bir1")) == 1
    assert runner.blocks_closed(runner.load_ledger()) == 1


def test_the_json_is_a_projection_and_is_rebuilt_from_the_record(session):
    """The file stays, so the artefact can still be published - but it is
    generated, and losing it loses nothing."""
    runner, record, checkout, new_session = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1))
    runner.save(runner.load_ledger())
    path = checkout / "results/accumulation-ledger.json"
    assert path.exists()
    before = json.loads(path.read_text(encoding="utf-8"))

    new_session()
    assert not path.exists()
    runner.save(runner.load_ledger())
    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["blocks"] == before["blocks"]
    assert after["source"].endswith("run_ledger")


def test_the_stop_is_written_into_the_record(session):
    """A stop kept only in the projection would be lost with it."""
    runner, record, _, new_session = session
    with open_database(record) as db:
        insert_ledger_row(db, **_row(1, stopped="branch A: two consecutive quiet blocks"))
    new_session()
    assert runner.load_ledger()["stopped"] == "branch A: two consecutive quiet blocks"


def test_the_table_migrates_into_an_existing_record(tmp_path):
    """The file on Drive was created before this table existed.

    `_add_missing_tables` reads the schema's own `CREATE TABLE`, so the
    constraints come with it - unlike a column migration (S-29).
    """
    record = tmp_path / "old.sqlite"
    open_database(record).close()
    with sqlite3.connect(record) as raw:
        raw.execute("DROP TABLE run_ledger")
    with sqlite3.connect(record) as raw:
        tables = {r[0] for r in raw.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "run_ledger" not in tables

    with open_database(record) as db:
        ddl = db.execute("SELECT sql FROM sqlite_master WHERE name = 'run_ledger'").fetchone()[0]
    assert "UNIQUE (prefix, block)" in ddl
    assert ddl.count("CHECK") >= 5


# ---------------------------------------------------------------------------
# The seed count
# ---------------------------------------------------------------------------
# The runner asked for `seed_index` 3 and `seed_for` refused: the derivation in
# `config/models.yaml` allows three seeds. The schema stopped it correctly, but
# only after the sweep had been chosen, and the reason it got that far was the
# ledger defect - branch A never fired, so the sweeps kept advancing (K-162).


def test_the_seed_count_comes_from_the_derivation():
    """One source: the limit `seed_for` itself refuses to exceed."""
    from zihin.records import load_model_config

    runner = _runner()
    assert runner.SEED_COUNT == load_model_config("config/models.yaml").seed_count


def test_no_identity_is_built_beyond_the_derivations_range():
    """The identity set used to span `range(4)` while the derivation allows three."""
    runner = _runner()
    from zihin.records import RecordError, load_model_config

    config = load_model_config("config/models.yaml")
    for seed in range(runner.SEED_COUNT):
        config.seed_for("t000_1", seed)  # every one of them derives
    with pytest.raises(RecordError):
        config.seed_for("t000_1", runner.SEED_COUNT)
    source = RUNNER.read_text(encoding="utf-8")
    assert "range(4)" not in source
    assert "for seed in range(SEED_COUNT)" in source


def test_running_out_of_seeds_stops_the_run_with_a_named_reason():
    """Written down rather than discovered: what happens when they run out."""
    source = RUNNER.read_text(encoding="utf-8")
    assert "seed_index >= SEED_COUNT" in source
    assert "all of them are spent" in source
    assert "seed_index >= 3" not in source, "the count is hard-coded again"


# ---------------------------------------------------------------------------
# The health check's split
# ---------------------------------------------------------------------------


def test_the_health_check_records_the_split_its_task_is_really_in():
    """The record must not claim a split the task is not in.

    Eight rows in the real record say `split='train'` for `024c982_1`, which is
    a `test_normal` task: `run_episode` wrote the run's split for the health
    check too. The corpus filter reads that column (K-159), so a health check
    that ever passed would have entered the corpus as a train episode. All eight
    failed, so none reached the compiler - but the record was saying something
    untrue (K-163).
    """
    from appworld.task import load_task_ids

    runner = _runner()
    assert runner.PREFLIGHT_TASK not in set(load_task_ids(runner.SPLIT))
    assert runner.PREFLIGHT_TASK in set(load_task_ids(runner.PREFLIGHT_SPLIT))


def test_the_preflight_is_run_with_its_own_split(monkeypatch):
    """And the runner passes it, rather than the sweep's."""
    runner = _runner()
    seen = {}

    def spy(task, seed_index, step_ceiling, health_check=False, prefix=None, split=None):
        seen.update(task=task, split=split, health_check=health_check)
        return 0

    monkeypatch.setattr(runner, "run_episode", spy)
    monkeypatch.setattr(runner, "preflight_prefix", lambda: "bir1-onkontrol1")
    runner.preflight()
    assert seen["task"] == runner.PREFLIGHT_TASK
    assert seen["split"] == runner.PREFLIGHT_SPLIT
    assert seen["health_check"] is True


def test_a_sweep_episode_still_carries_the_runs_split(monkeypatch):
    """The parameter defaults to the run's split; only the preflight overrides it."""
    runner = _runner()
    captured = {}

    def fake_run(command, **kwargs):
        captured.update(kwargs.get("env", {}))

        class Done:
            returncode = 0
            stderr = ""
            stdout = ""

        return Done()

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.run_episode("t000_1", 0, 20)
    assert captured["ZIHIN_SPLIT"] == runner.SPLIT
    runner.run_episode(runner.PREFLIGHT_TASK, 0, 3, split=runner.PREFLIGHT_SPLIT)
    assert captured["ZIHIN_SPLIT"] == runner.PREFLIGHT_SPLIT
