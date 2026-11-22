"""The threshold calibration tool itself.

The tool picks the threshold, so it decides the measuring instrument's setting.
If it goes wrong in silence, the wrong threshold is chosen and there is no way
left to notice. Three things are checked:

  1. No prefix leakage. The pattern `sinir3` must not catch `sinir3-kapali-...`
     rows; a run id has the shape `prefix-task-model`.
  2. A cut episode does not enter the calibration set, because its real stall
     length is unknown.
  3. The cut step and the longest-stall computation are done with the production
     rule itself.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from zihin.records import insert_episode, insert_run_manifest, insert_step, open_database

BETIK = Path(__file__).resolve().parents[1] / "scripts" / "setup" / "calibrate_stopping_rule.py"


@pytest.fixture(scope="module")
def alet():
    spec = importlib.util.spec_from_file_location("kalibrasyon", BETIK)
    modul = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["calibrate_stopping_rule.py", "sinir3"]
    try:
        spec.loader.exec_module(modul)
    finally:
        sys.argv = previous
    return modul


def _manifest(**degisiklik):
    fields = {
        "created_at": "uptime:1.0",
        "model_tag": "m",
        "num_ctx_requested": 32768,
        "num_ctx_effective": 32768,
        "context_verified": 1,
        "kv_cache_type": "q8_0",
        "flash_attention": 1,
        "temperature": 0.2,
        "base_seed": 123,
        "keep_alive": "30m0s",
        "no_progress_limit": 15,
        "max_output_tokens": 4000,
        "max_prompt_characters": 50000,
        "model_server_env": {"X": "1"},
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": "deadbeef",
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux / 3.11",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }
    fields.update(degisiklik)
    return fields


def _write_episode(db, run_id, task, *, termination, step_count=3, threshold=15):
    from zihin.records import insert_action, insert_verifier_result

    insert_run_manifest(db, **_manifest(run_id=run_id, no_progress_limit=threshold))
    episode_id = insert_episode(
        db,
        run_id=run_id,
        task_id=task,
        split="test_normal",
        condition="baseline",
        model_ref="m",
        seed=1,
        sequence_in_run=1,
        model_load_state="unknown",
        started_at="uptime:1.0",
        termination_reason=termination,
        total_model_calls=step_count,
        step_ceiling=20,
    )
    for index in range(1, step_count + 1):
        step_id = insert_step(
            db, episode_id=episode_id, step_index=index, instruction_digest="0" * 64
        )
        insert_action(
            db,
            step_id=step_id,
            action_index=1,
            app="venmo",
            api="auth/token",
            http_method="POST",
            raw_parameters={},
            normalized_parameters=None,
            result_status="200",
            error_class=None,
            latency_seconds=None,
        )
    insert_verifier_result(db, episode_id=episode_id, passed=1)
    return episode_id


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        yield connection


def test_prefixes_do_not_bleed(db, alet):
    with db:
        _write_episode(db, "sinir3-kapali-g1-model", "g1", termination="agent_finished")
    assert alet.episodes_with_steps(db, "sinir3") == []
    assert [e["task"] for e in alet.episodes_with_steps(db, "sinir3-kapali")] == ["g1"]


def test_cut_episodes_are_excluded_from_the_merge_when_a_complete_one_exists(db, alet):
    with db:
        _write_episode(db, "sinir3-g1-model", "g1", termination="no_progress")
        _write_episode(db, "sinir3-kapali-g1-model", "g1", termination="step_ceiling", threshold=0)
    birlesik = alet.merge(
        [alet.episodes_with_steps(db, "sinir3"), alet.episodes_with_steps(db, "sinir3-kapali")]
    )
    assert len(birlesik) == 1
    assert birlesik[0]["prefix"] == "sinir3-kapali"
    assert birlesik[0]["kosu_esigi"] == 0


def test_a_complete_episode_is_not_replaced_by_a_cut_one(db, alet):
    """Even with the order reversed, the complete trajectory wins."""
    with db:
        _write_episode(db, "sinir3-g1-model", "g1", termination="agent_finished")
        _write_episode(db, "sinir3-kapali-g1-model", "g1", termination="no_progress", threshold=0)
    birlesik = alet.merge(
        [alet.episodes_with_steps(db, "sinir3"), alet.episodes_with_steps(db, "sinir3-kapali")]
    )
    assert birlesik[0]["prefix"] == "sinir3"


def test_stall_length_uses_the_production_rule(alet):
    """Five steps hitting the same endpoint: the first is progress, four are stalled."""
    steps = [{"state_delta": {}, "progress_identities": {"venmo.auth/token|{}"}} for _ in range(5)]
    assert alet.longest_stall(steps) == 4


def test_state_change_resets_the_stall(alet):
    steps = [
        {"state_delta": {}, "progress_identities": {"venmo.auth/token|{}"}},
        {"state_delta": {}, "progress_identities": {"venmo.auth/token|{}"}},
        {"state_delta": {"venmo.Transaction": 1}, "progress_identities": {"venmo.auth/token|{}"}},
        {"state_delta": {}, "progress_identities": {"venmo.auth/token|{}"}},
    ]
    assert alet.longest_stall(steps) == 1


def test_cut_step_is_where_the_rule_would_fire(alet):
    """Threshold 3: step one is progress, two-three-four are stalled, the cut is 4."""
    steps = [{"state_delta": {}, "progress_identities": {"venmo.auth/token|{}"}} for _ in range(10)]
    assert alet.cut_step(steps, 3) == 4
    assert alet.cut_step(steps, 15) is None


def test_a_genuinely_exploring_episode_is_never_cut(alet):
    steps = [
        {"state_delta": {}, "progress_identities": {f"venmo.endpoint{i}|{{}}"}} for i in range(20)
    ]
    assert alet.cut_step(steps, 3) is None
    assert alet.longest_stall(steps) == 0
