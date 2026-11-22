"""Turns the verifier's verdict into an episode record.

`solve_tasks` does not run evaluation; the verdict is fetched by a separate
call. The CLI's `appworld evaluate` command calls the same function.

The verdict is the sole basis of the censoring definition (K-53), so it is
taken while the episode is being written. It cannot be deferred: evaluation
reads the final database state in the task output directory, and that
directory is overwritten when the same task is run with another model.

**What is extracted.** The `success` field is the verdict itself, with the
passed and failed test counts alongside it. The two components in S-04 —
whether the expected change was completed and whether an unexpected change is
present — cannot be extracted separately, so they stay `None`.
"""

from __future__ import annotations

import json
import os
from typing import Any

from appworld.common.path_store import path_store
from appworld.evaluator import evaluate_dataset


def verdict(experiment_name: str, task_id: str) -> dict[str, Any]:
    """An episode's verifier verdict, shaped as `insert_verifier_result` fields.

    `passed` carries three states: 1 passed, 0 failed, `None` verdict
    unreadable. The third must not be confused with "failed" — the censoring
    definition treats a non-pass as censored, but an unreadable verdict is a
    measurement fault and must be reported as one.
    """
    result = evaluate_dataset(
        experiment_name=experiment_name,
        dataset_name=None,
        task_id=task_id,
        suppress_errors=True,
        include_details=True,
        aggregate_only=False,
        save_reports=True,
        print_report=False,
    )
    entry = (result.get("individual") or {}).get(task_id) or {}
    success = entry.get("success")
    report = os.path.join(
        path_store.experiment_outputs, experiment_name, "tasks", task_id, "evaluation", "report.md"
    )
    return {
        "passed": None if success is None else int(bool(success)),
        "expected_changes_complete": None,
        "unexpected_changes_present": None,
        "num_passed_tests": len(entry["passes"]) if "passes" in entry else None,
        "num_failed_tests": len(entry["failures"]) if "failures" in entry else None,
        "detail_path": report if os.path.exists(report) else None,
    }


def graded_detail(experiment_name: str, task_id: str) -> dict[str, int]:
    """Components of the graded score, corrected against the no-op baseline.

    AppWorld's official metric is binary. A graded score can be built from
    `TestTracker`'s labels: a test labelled `no_op_fail` is one that an agent
    doing nothing would fail, and a test labelled `no_op_pass` is one that
    passes even when the agent does nothing. Counting the latter overstates
    progress.

    Reads the evaluation file, does not re-run evaluation; so it can be called
    once `verdict` has run.
    """
    path = os.path.join(
        path_store.experiment_outputs,
        experiment_name,
        "evaluations",
        f"on_only_{task_id}.json",
    )
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        entry = (json.load(handle).get("individual") or {}).get(task_id) or {}
    passes = entry.get("passes") or []
    failures = entry.get("failures") or []
    return {
        "meaningful_passed": sum(1 for t in passes if t.get("label") == "no_op_fail"),
        "meaningful_total": sum(1 for t in passes + failures if t.get("label") == "no_op_fail"),
        "trivial_passed": sum(1 for t in passes if t.get("label") == "no_op_pass"),
        "trivial_total": sum(1 for t in passes + failures if t.get("label") == "no_op_pass"),
    }
