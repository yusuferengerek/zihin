"""The prerequisite check asks for the ledger table, read-only (K-171).

K-162 moved the ledger into the record, but the real record was never opened by
code that knew the table: its last write came an hour before the schema change.
Branch A reads the table, so a record without it cannot evaluate half of the
stopping rule. The check has to find that, and it must not repair the file while
looking, or it would report a table it had just created.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

from zihin.records import open_database, schema_statement, table_matches_schema

REPOSITORY = Path(__file__).resolve().parents[1]


def _preflight():
    path = REPOSITORY / "scripts/setup/check_prerequisites.py"
    spec = importlib.util.spec_from_file_location("check_prerequisites_ledger", path)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["check_prerequisites.py"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    module.results.clear()
    return module


def _state(preflight, path: Path) -> str:
    preflight.run_ledger_table(path)
    return {name: state for state, name, _, _ in preflight.results}["run ledger"]


def _record(tmp_path: Path) -> Path:
    path = tmp_path / "record.sqlite"
    open_database(path).close()
    return path


def test_a_record_made_by_the_schema_has_the_ledger(tmp_path) -> None:
    assert _state(_preflight(), _record(tmp_path)) == "ok"


def test_a_record_without_the_ledger_is_named(tmp_path) -> None:
    path = _record(tmp_path)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE run_ledger")
    assert _state(_preflight(), path) == "MISSING"


def test_a_ledger_without_its_constraints_is_named(tmp_path) -> None:
    path = _record(tmp_path)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE run_ledger")
        connection.execute("CREATE TABLE run_ledger (prefix TEXT, block INTEGER)")
    assert _state(_preflight(), path) == "MISSING"


def test_the_check_does_not_create_what_it_looks_for(tmp_path) -> None:
    path = _record(tmp_path)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE run_ledger")
    _state(_preflight(), path)
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        assert table_matches_schema(connection, "run_ledger") is None


def test_the_schema_is_read_by_one_reader() -> None:
    statement = schema_statement("run_ledger")
    assert statement is not None and "UNIQUE (prefix, block)" in statement
    assert schema_statement("no_such_table") is None
