"""Pins where the skill library is read from.

The library and the record are two questions with two answers, and the answers
agreed until series 3 opened. Everything that needed a card asked the connection
it was writing episodes to, which is the wrong question asked in a way that only
shows up once the two files differ (K-143).

What is pinned here: the two constants stay separate, the refusal names both, and
no caller goes back to asking the writing connection.
"""

from __future__ import annotations

import pathlib
import re
import sqlite3

import pytest

from zihin.records import (
    ACTIVE_SERIES,
    CALIBRATION_SERIES,
    LIBRARY_SERIES,
    RecordError,
    open_library,
)

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]


def test_the_two_series_are_separate_questions() -> None:
    """They may point at one file, but they may not be one constant."""
    assert ACTIVE_SERIES
    assert LIBRARY_SERIES


def test_the_library_is_where_the_constant_says_it_is() -> None:
    path = REPOSITORY / LIBRARY_SERIES
    if not path.exists():
        pytest.skip(f"{LIBRARY_SERIES} is absent: restore it with scripts/restore_records.py")
    connection, library_id, index_id = open_library(str(path))
    skills = connection.execute(
        "SELECT COUNT(*) FROM skills WHERE library_id = ?", (library_id,)
    ).fetchone()[0]
    patterns = connection.execute(
        "SELECT COUNT(*) FROM failure_patterns WHERE index_id = ?", (index_id,)
    ).fetchone()[0]
    connection.close()
    assert skills > 0 and patterns > 0


def test_an_empty_series_is_refused_and_the_refusal_names_both(tmp_path) -> None:
    """The message has to say where to look, not just that it did not find one."""
    empty = tmp_path / "empty.sqlite"
    connection = sqlite3.connect(empty)
    connection.execute("CREATE TABLE skills (library_id TEXT)")
    connection.execute("CREATE TABLE failure_patterns (index_id TEXT)")
    connection.commit()
    connection.close()

    with pytest.raises(RecordError) as refused:
        open_library(str(empty))
    message = str(refused.value)
    assert LIBRARY_SERIES in message
    assert ACTIVE_SERIES in message
    assert "empty.sqlite" in message


def test_a_missing_file_is_refused_by_name(tmp_path) -> None:
    with pytest.raises(RecordError) as refused:
        open_library(str(tmp_path / "nowhere.sqlite"))
    assert "LIBRARY_SERIES" in str(refused.value)


def test_no_caller_asks_the_writing_connection_for_the_library() -> None:
    """The shape of the bug, pinned so it cannot come back by copy-paste.

    A script that opens ACTIVE_SERIES and then calls latest_library_and_index on
    that same connection is asking "where are we writing" when it means "where
    was it mined".
    """
    pattern = re.compile(
        r"ACTIVE_SERIES.{0,400}?latest_library_and_index\(\s*connection", re.DOTALL
    )
    offenders = []
    for path in sorted((REPOSITORY / "scripts").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(path.relative_to(REPOSITORY).as_posix())
    assert not offenders, f"these read the library from the writing series: {offenders}"


def test_the_scripts_that_need_cards_go_through_open_library() -> None:
    """A floor: if none of them does, this test is reading the wrong tree."""
    users = [
        path
        for path in sorted((REPOSITORY / "scripts").rglob("*.py"))
        if "open_library" in path.read_text(encoding="utf-8")
    ]
    assert len(users) >= 6, f"only {len(users)} scripts call open_library()"


# ---------------------------------------------------------------------------
# The pointer after the accumulation, and the identity it must resolve
# ---------------------------------------------------------------------------


def test_the_library_pointer_followed_the_builders() -> None:
    """The accumulation re-mined the library into the active series (K-164).

    Until this line moved, a carded run would have resolved the four-skill
    library from series 2 while eleven skills sat in series 3, and the preflight
    said so at every block boundary.
    """
    assert LIBRARY_SERIES == ACTIVE_SERIES


def test_the_calibration_series_is_its_own_name() -> None:
    """One constant was doing two jobs: where the library lives, and the corpus
    the thresholds were calibrated on. Moving the first would have moved the
    second in silence."""
    assert CALIBRATION_SERIES != ACTIVE_SERIES
    assert CALIBRATION_SERIES.endswith("zihin-2.sqlite")


def test_the_setup_measurements_read_the_calibration_series_by_name() -> None:
    for relative in (
        "scripts/setup/compare_naive_miner.py",
        "scripts/setup/measure_failure_index_build.py",
    ):
        source = (REPOSITORY / relative).read_text(encoding="utf-8")
        assert "CALIBRATION_SERIES" in source, relative
        assert "LIBRARY_SERIES" not in source, f"{relative} still defaults to the library series"


def test_the_delivered_identity_is_declared() -> None:
    """The library is the experiment's input, so its identity is written down."""
    from zihin.declared import declared_field

    assert declared_field("delivered_library_id", "bir1") == "v0-gap2-sup3-0c3f4ac"
    assert declared_field("delivered_index_id", "bir1") == "v0-sup1-0c3f4ac"


class _Closable:
    """A stand-in connection: the guard closes what open_library hands it."""

    def close(self):
        return None


def _preflight():
    import importlib.util
    import sys

    path = REPOSITORY / "scripts/setup/check_prerequisites.py"
    spec = importlib.util.spec_from_file_location("check_prerequisites_probe", path)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["check_prerequisites.py"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    return module


def test_the_guard_refuses_a_library_that_is_not_the_declared_one(monkeypatch) -> None:
    """`latest_library_and_index` picks by row count, so a library mined later
    would take this one's place with nothing said (K-164)."""
    preflight = _preflight()
    monkeypatch.setattr(
        preflight,
        "note",
        lambda state, name, detail, remedy="": preflight.results.append(
            (state, name, detail, remedy)
        ),
    )
    preflight.results.clear()
    monkeypatch.setattr(
        "zihin.records.open_library",
        lambda path: (_Closable(), "v0-gap2-sup3-deadbee", "v0-sup1-deadbee"),
    )
    if not (REPOSITORY / LIBRARY_SERIES).exists():
        pytest.skip(f"{LIBRARY_SERIES} is absent: restore it with scripts/restore_records.py")
    preflight.delivered_library()
    states = {name: state for state, name, _, _ in preflight.results}
    assert states.get("delivered library") == "MISSING", preflight.results
    assert states.get("delivered index") == "MISSING", preflight.results


def test_the_guard_passes_on_the_declared_pair(monkeypatch) -> None:
    from zihin.declared import declared_field

    preflight = _preflight()
    preflight.results.clear()
    monkeypatch.setattr(
        "zihin.records.open_library",
        lambda path: (
            _Closable(),
            declared_field("delivered_library_id", "bir1"),
            declared_field("delivered_index_id", "bir1"),
        ),
    )
    if not (REPOSITORY / LIBRARY_SERIES).exists():
        pytest.skip(f"{LIBRARY_SERIES} is absent: restore it with scripts/restore_records.py")
    preflight.delivered_library()
    states = {name: state for state, name, _, _ in preflight.results}
    assert states.get("delivered library") == "ok", preflight.results
    assert states.get("delivered index") == "ok", preflight.results
