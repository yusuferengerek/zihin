"""Turning the verifier's verdict into a record.

The censoring definition rests on this field (K-53), so the behaviour really
being pinned is the `passed` field's three states. If an unreadable verdict were
written as `0`, a measurement fault would disappear inside the censoring count.

The tests put a fake function in place of `evaluate_dataset`; they need neither
AppWorld data nor a run episode.
"""

from __future__ import annotations

import pytest

from zihin import verification


def _fake_result(result: dict):
    def fake(**_kwargs):
        return result

    return fake


def test_success_becomes_one(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        verification,
        "evaluate_dataset",
        _fake_result({"individual": {"g_1": {"success": True, "passes": [1, 2], "failures": []}}}),
    )
    verdict = verification.verdict("experiment", "g_1")
    assert verdict["passed"] == 1
    assert verdict["num_passed_tests"] == 2
    assert verdict["num_failed_tests"] == 0


def test_failure_becomes_zero(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        verification,
        "evaluate_dataset",
        _fake_result(
            {"individual": {"g_1": {"success": False, "passes": [1], "failures": [1, 2]}}}
        ),
    )
    verdict = verification.verdict("experiment", "g_1")
    assert verdict["passed"] == 0
    assert verdict["num_passed_tests"] == 1
    assert verdict["num_failed_tests"] == 2


def test_missing_verdict_stays_none(monkeypatch: pytest.MonkeyPatch):
    """When the verdict cannot be read, `passed` is None, not 0. K-53 separates the two."""
    monkeypatch.setattr(verification, "evaluate_dataset", _fake_result({"individual": {}}))
    verdict = verification.verdict("experiment", "g_1")
    assert verdict["passed"] is None
    assert verdict["num_passed_tests"] is None
    assert verdict["num_failed_tests"] is None


def test_empty_result_stays_none(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(verification, "evaluate_dataset", _fake_result({}))
    assert verification.verdict("experiment", "g_1")["passed"] is None


def test_detail_path_is_none_when_report_is_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        verification,
        "evaluate_dataset",
        _fake_result({"individual": {"g_1": {"success": False, "passes": [], "failures": [1]}}}),
    )
    assert verification.verdict("olmayan-experiment", "g_1")["detail_path"] is None
