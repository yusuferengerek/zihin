"""The experiment's tables and the runner's rules for a `dny` run (K-180, K-182).

**The runner refuses on its own.** `check_declared_conditions` refuses a declared
command that carries `--allow-dirty-tree`; a runner called directly never meets
that check. So `record_run.py` asks the parsed options, where argparse has already
turned every abbreviation into the one option it reaches.

**Every experiment episode says where it belongs.** A slice, a session, whether its
slot matched the carded arm's volume, and whether a path change was accepted - in
the episode's own transaction, checked against the slice that opened its task.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import sqlite3
from pathlib import Path

import pytest

from zihin.declared import experiment_run_problems
from zihin.records import (
    RecordError,
    insert_experiment_episode,
    insert_experiment_slice,
    open_database,
    table_matches_schema,
)

REPOSITORY = Path(__file__).resolve().parents[1]
RUNNER = REPOSITORY / "scripts/record_run.py"
RUN_ID = "dny-baseline-s0-a_1-a_1-32b"


def _parse(argv: list[str]) -> argparse.Namespace:
    """The runner's own parser, built from its source, fed `argv`."""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    node = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "parse_options"
    )
    namespace: dict = {"argparse": argparse, "__doc__": ""}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(RUNNER), "exec"), namespace)  # noqa: S102
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("sys.argv", ["record_run.py", *argv])
        with contextlib.redirect_stderr(io.StringIO()):
            return namespace["parse_options"]()


def _problems(argv: list[str], run_id: str = RUN_ID, split: str = "test_normal") -> list[str]:
    options = _parse(argv)
    return experiment_run_problems(
        run_id,
        allow_dirty_tree=options.allow_dirty_tree,
        named_condition=options.condition,
        split=split,
        slice_number=options.slice,
        session_id=options.session,
        path_change_accepted=options.path_change_accepted,
    )


CLEAN = ["--condition", "baseline", "--slice", "1", "--session", "s1"]


def test_a_clean_experiment_run_passes() -> None:
    assert _problems(CLEAN) == []


@pytest.mark.parametrize("token", ["--allow-dirty-tree", "--allow-dirty", "--allow", "--al"])
def test_the_runner_refuses_the_flag_by_its_parsed_option(token) -> None:
    problems = _problems([*CLEAN, token])
    assert any("--allow-dirty-tree" in p for p in problems), problems


def test_the_flag_is_not_asked_of_a_run_outside_the_experiment() -> None:
    assert _problems(["--allow-dirty-tree"], run_id="bir1-a_1-a_1-32b") == []


def test_an_experiment_run_names_its_condition() -> None:
    problems = _problems(["--cards", "--slice", "1", "--session", "s1"])
    assert any("--condition" in p for p in problems)


def test_an_experiment_run_carries_a_slice_and_a_session() -> None:
    problems = _problems(["--condition", "baseline"])
    assert any("slice" in p for p in problems) and any("session" in p for p in problems)


def test_an_experiment_run_is_on_the_evaluation_split() -> None:
    assert any("split" in p for p in _problems(CLEAN, split="train"))


def test_the_experiment_options_are_refused_outside_the_experiment() -> None:
    problems = _problems(CLEAN, run_id="bir1-a_1-a_1-32b")
    assert len(problems) == 2


def test_the_runner_asks_before_it_opens_the_record() -> None:
    """Every keyword is the parsed option of the same name, read off the call itself:
    the manifest's call passes `allow_dirty_tree` too, so the text alone could not
    tell which call a match came from."""
    source = RUNNER.read_text(encoding="utf-8")
    asked = source.index("refused = experiment_run_problems(")
    assert source.index("if refused:") > asked
    assert asked < source.index("connection = open_database(DATABASE)")
    call = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", None) == "experiment_run_problems"
    )
    passed = {k.arg: ast.unparse(k.value) for k in call.keywords}
    assert passed["allow_dirty_tree"] == "options.allow_dirty_tree"
    assert passed["named_condition"] == "options.condition"
    assert passed["slice_number"] == "options.slice"
    assert passed["session_id"] == "options.session"


def test_the_runner_writes_the_row_inside_the_episodes_transaction() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    block = source[
        source.index("        with connection:") : source.index("except AlreadyRecorded")
    ]
    assert "insert_experiment_episode(" in block
    assert block.index("insert_episode(") < block.index("insert_experiment_episode(")


# --- the tables ---------------------------------------------------------------


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        # The episode the row points at is not what is under test here, and
        # building a whole manifest for it would test the manifest's contract.
        connection.execute("PRAGMA foreign_keys = OFF")
        insert_experiment_slice(
            connection, slice=1, position=1, task_id="a_1", session_id="s1", opened_commit="c"
        )
        yield connection


def _row(**overrides):
    row = {
        "task_id": "a_1",
        "episode_id": 1,
        "slice": 1,
        "session_id": "s1",
        "volume_matched": None,
        "path_change_accepted": 0,
    }
    row.update(overrides)
    return row


def test_an_episode_row_is_written_for_a_task_its_slice_holds(db) -> None:
    insert_experiment_episode(db, **_row())
    assert db.execute("SELECT COUNT(*) FROM experiment_episodes").fetchone()[0] == 1


@pytest.mark.parametrize("overrides", [{"slice": 2}, {"task_id": "b_1"}])
def test_an_episode_outside_its_slice_is_refused(db, overrides) -> None:
    with pytest.raises(RecordError, match="belongs to the slice that opened its task"):
        insert_experiment_episode(db, **_row(**overrides))


@pytest.mark.parametrize(
    "overrides",
    [{"volume_matched": 2}, {"path_change_accepted": None}, {"path_change_accepted": 3}],
)
def test_the_schema_refuses_a_value_it_does_not_define(db, overrides) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        insert_experiment_episode(db, **_row(**overrides))


def test_a_task_belongs_to_one_slice(db) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        insert_experiment_slice(
            db, slice=2, position=2, task_id="a_1", session_id="s2", opened_commit="c"
        )


def test_an_existing_series_gets_the_tables_as_the_schema_writes_them(tmp_path) -> None:
    path = tmp_path / "old.sqlite"
    with open_database(path) as connection:
        connection.execute("DROP TABLE experiment_episodes")
        connection.execute("DROP TABLE experiment_slices")
    with open_database(path) as connection:
        assert table_matches_schema(connection, "experiment_episodes") is True
        assert table_matches_schema(connection, "experiment_slices") is True
