"""What may be read before the full set, and whether the slices pool (K-186)."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[1]


def _analysis():
    path = REPOSITORY / "scripts/analyze_experiment.py"
    spec = importlib.util.spec_from_file_location("analyze_experiment", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _defining(changes: dict[str, list[str]]):
    return lambda first, commit: changes.get(commit, [])


# --- comparability --------------------------------------------------------------


def test_one_commit_pools() -> None:
    rows = [(1, 1, "a"), (2, 1, "a"), (3, 2, "a")]
    pooling = _analysis().comparability(rows, _defining({}))
    assert pooling["poolable"] and pooling["breaks"] == []


def test_a_change_outside_the_list_pools() -> None:
    rows = [(1, 1, "a"), (2, 2, "b")]
    assert _analysis().comparability(rows, _defining({"b": []}))["poolable"]


def test_a_defining_change_between_slices_is_a_break() -> None:
    rows = [(1, 1, "a"), (2, 1, "a"), (3, 2, "b")]
    pooling = _analysis().comparability(rows, _defining({"b": ["src/zihin/slots.py"]}))
    assert not pooling["poolable"]
    assert pooling["breaks"] == [
        "slices 1 and 2 ran on code that differs on measurement-defining paths"
    ]
    assert pooling["groups"] == [[], ["src/zihin/slots.py"]]


def test_a_defining_change_inside_a_slice_is_a_break() -> None:
    rows = [(1, 1, "a"), (2, 1, "b")]
    pooling = _analysis().comparability(rows, _defining({"b": ["config/models.yaml"]}))
    assert pooling["breaks"] == ["slice 1 spans comparability groups [0, 1]"]


def test_every_commit_is_compared_with_the_first_not_the_previous() -> None:
    """Two changes each against the previous commit would each look small."""
    seen = []

    def defining(first, commit):
        seen.append((first, commit))
        return []

    _analysis().comparability([(1, 1, "a"), (2, 2, "b"), (3, 3, "c")], defining)
    assert seen == [("a", "b"), ("a", "c")]


# --- the partial-reading rule -----------------------------------------------------

PARTIAL = {
    "tasks_finished": 10,
    "tasks": 104,
    "episodes": 90,
    "episodes_planned": 930,
    "mean_duration_seconds": 101.2,
}
FULL = {**PARTIAL, "tasks_finished": 104, "episodes": 930}


def test_the_full_set_is_every_planned_episode() -> None:
    analysis = _analysis()
    assert not analysis.complete(PARTIAL)
    assert analysis.complete(FULL)


def test_a_partial_report_carries_no_outcome_and_nothing_by_condition() -> None:
    lines = _analysis().report(PARTIAL, {"groups": [[]], "breaks": [], "poolable": True})
    text = "\n".join(lines)
    for forbidden in ("pass", "call", "baseline", "skills", "irrelevant", "interval", "ci "):
        assert forbidden not in text.lower(), forbidden
    assert [line.split(":")[0].strip() for line in lines if not line.startswith("  ")] == [
        "tasks finished",
        "episodes",
        "mean duration",
        "comparability",
    ]


def test_the_confirmatory_reading_is_refused_before_the_full_set(monkeypatch, capsys) -> None:
    analysis = _analysis()
    monkeypatch.setattr(analysis, "declared_model", lambda prefix: "m:32b-x")
    monkeypatch.setattr(analysis, "load_sets", lambda: {})
    monkeypatch.setattr(analysis, "descriptive", lambda *a: PARTIAL)
    monkeypatch.setattr(analysis, "experiment_rows", lambda *a: [])
    monkeypatch.setattr(analysis.sqlite3, "connect", lambda *a, **k: _Closing())
    monkeypatch.setattr("sys.argv", ["analyze_experiment.py", "--confirmatory"])
    with pytest.raises(SystemExit) as stopped:
        analysis.main()
    assert "REFUSED" in str(stopped.value)
    assert not re.search(r"\bpass|model call", capsys.readouterr().out.lower())


class _Closing:
    def close(self) -> None:
        pass
