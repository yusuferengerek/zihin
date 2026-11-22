"""Checks the rules the record schema carries.

The tests here run on synthetic data and need no AppWorld installation, so they
run in CI as well. Writing a real run into the schema is checked in a separate
test (`test_recorded_run.py`), and that one needs downloaded data.
"""

from __future__ import annotations

import sqlite3

import pytest

from zihin.records import (
    RecordError,
    RecordingLimits,
    insert_action,
    insert_episode,
    insert_observation,
    insert_run_manifest,
    insert_shield_violation,
    insert_step,
    insert_verifier_result,
    load_recording_limits,
    open_database,
    read_episode_timeline,
)

LIMITS = RecordingLimits(
    observation_max_bytes=64,
    run_disk_quota_bytes=1024,
    on_quota_exceeded="stop",
    no_progress_limit=4,
    max_output_tokens=4000,
    max_prompt_characters=50000,
)


@pytest.fixture
def connection(tmp_path):
    with open_database(tmp_path / "record.sqlite") as db:
        yield db


def _manifest(db: sqlite3.Connection, run_id: str = "run-1") -> str:
    return insert_run_manifest(
        db,
        run_id=run_id,
        created_at="uptime:1.0",
        model_tag="qwen2.5-coder:1.5b-instruct-q4_K_M",
        num_ctx_requested=32768,
        num_ctx_effective=32768,
        context_verified=1,
        kv_cache_type="q8_0",
        flash_attention=1,
        temperature=0.2,
        base_seed=123,
        keep_alive="30m",
        no_progress_limit=4,
        max_output_tokens=400,
        max_prompt_characters=50000,
        model_server_env={"loaded_models": ["qwen2.5-coder:1.5b-instruct-q4_K_M"]},
        appworld_version="0.2.0.dev0",
        appworld_commit="a072b7a",
        code_commit="deadbeef",
        instruction_file_digest="0" * 64,
        os_environment="Linux 6.6 / 3.11.15",
        shield_mode="shadow",
        shield_config_digest="a" * 64,
    )


def _episode(db: sqlite3.Connection, run_id: str = "run-1", **degisiklik) -> int:
    fields = {
        "run_id": run_id,
        "task_id": "82e2fac_1",
        "split": "train",
        "condition": "baseline",
        "model_ref": "qwen2.5-coder:1.5b-instruct-q4_K_M",
        "seed": 123,
        "sequence_in_run": 1,
        "model_load_state": "cold",
        "started_at": "uptime:1.0",
        "ended_at": "uptime:61.0",
        "termination_reason": "step_ceiling",
        "total_model_calls": 2,
        "input_tokens": 11916,
        "output_tokens": 480,
        "duration_seconds": 60.0,
    }
    fields.update(degisiklik)
    return insert_episode(db, **fields)


def _step(db: sqlite3.Connection, episode_id: int, index: int, **degisiklik) -> int:
    fields = {
        "episode_id": episode_id,
        "step_index": index,
        "instruction_digest": "a" * 64,
        "context_tokens": 5958,
        "generated_tokens": 240,
        "latency_seconds": 2.5,
        "generated_code": "print(apis.spotify.show_playlist_library())",
        "outcome_category": None,
    }
    fields.update(degisiklik)
    return insert_step(db, **fields)


def test_schema_creates_every_record_table(connection):
    tablolar = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert {
        "run_manifests",
        "episodes",
        "steps",
        "actions",
        "observations",
        "verifier_results",
        "shield_violations",
    } <= tablolar


def test_projection_tables_are_not_append_only(connection):
    """`skills` is a projection, not the record — and the distinction shows in the
    trigger.

    This test used to check the table's **absence**, because the library was not
    being produced yet. When the table arrived it was turned into a check of the
    real distinction: record tables are append-only (K-16), a projection can be
    deleted and regenerated (`03-architecture.tr.md`). A library that could not be
    deleted would turn into a second source of truth.

    Both are projections: `skills` and `failure_patterns`.
    """
    tablolar = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert {"skills", "failure_patterns"} <= tablolar

    tetikleyiciler = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'trigger'")
    }
    assert not [t for t in tetikleyiciler if t.startswith(("skills_", "failure_patterns_"))]
    assert "shield_violations_no_delete" in tetikleyiciler


@pytest.mark.parametrize(
    "table",
    [
        "run_manifests",
        "episodes",
        "steps",
        "actions",
        "observations",
        "verifier_results",
        "shield_violations",
    ],
)
def test_record_tables_reject_update_and_delete(connection, table):
    """Append-only is not a convention; it is enforced by a trigger (K-16)."""
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    insert_action(
        connection,
        step_id=step_id,
        action_index=1,
        app="spotify",
        api="library/playlists",
        http_method="GET",
        raw_parameters={"access_token": "x"},
    )
    insert_observation(connection, step_id=step_id, full_text="output", limits=LIMITS)
    insert_verifier_result(connection, episode_id=episode_id, passed=0)
    insert_shield_violation(
        connection,
        step_id=step_id,
        violation_index=1,
        app="spotify",
        api="songs",
        http_method="DELETE",
        raw_parameters={"song_id": 1},
        predicate="write_to_app_not_in_task",
        mode="enforce",
    )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(f"DELETE FROM {table}")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(f"UPDATE {table} SET rowid = rowid")


def test_foreign_keys_are_enforced(connection):
    with pytest.raises(sqlite3.IntegrityError):
        _episode(connection, run_id="no-such-run")


def test_four_levels_read_back_in_order(connection):
    """One episode, several steps, several actions per step, one observation per step."""
    _manifest(connection)
    episode_id = _episode(connection)

    for step_index in (1, 2):
        step_id = _step(connection, episode_id, step_index)
        for action_index in (1, 2, 3):
            insert_action(
                connection,
                step_id=step_id,
                action_index=action_index,
                app="spotify",
                api=f"songs/{action_index}",
                http_method="GET",
                raw_parameters={"i": action_index},
            )
        insert_observation(
            connection, step_id=step_id, full_text=f"step {step_index} output", limits=LIMITS
        )

    rows = read_episode_timeline(connection, episode_id)
    assert len(rows) == 6, "expected two steps and three actions per step"
    assert [(s["step_index"], s["action_index"]) for s in rows] == [
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (2, 2),
        (2, 3),
    ], "the ordering is broken"
    assert {s["api"] for s in rows} == {"songs/1", "songs/2", "songs/3"}


def test_step_without_action_still_appears_in_timeline(connection):
    """K-36's fourth and fifth categories produce no action at all.

    If those steps drop out of the timeline, a zero-action episode looks empty and
    cannot be told apart from an episode where the agent chose not to call.
    """
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1, outcome_category="execution_error_no_action")
    insert_observation(
        connection, step_id=step_id, full_text="Execution failed. NameError", limits=LIMITS
    )

    rows = read_episode_timeline(connection, episode_id)
    assert len(rows) == 1
    assert rows[0]["action_index"] is None
    assert rows[0]["outcome_category"] == "execution_error_no_action"


def test_unknown_step_outcome_is_rejected(connection):
    _manifest(connection)
    episode_id = _episode(connection)
    with pytest.raises(RecordError, match="unrecognised step category"):
        _step(connection, episode_id, 1, outcome_category="uydurma")


def test_observation_is_truncated_at_the_configured_limit(connection):
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    long_text = "x" * 500
    insert_observation(connection, step_id=step_id, full_text=long_text, limits=LIMITS)

    row = connection.execute("SELECT * FROM observations").fetchone()
    assert row["was_truncated"] == 1
    assert row["truncated_bytes"] == LIMITS.observation_max_bytes
    assert row["full_bytes"] == 500


def test_short_observation_is_not_marked_truncated(connection):
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    insert_observation(connection, step_id=step_id, full_text="short", limits=LIMITS)

    row = connection.execute("SELECT * FROM observations").fetchone()
    assert row["was_truncated"] == 0
    assert row["truncated_text"] == "short"


def test_one_observation_per_step(connection):
    """The observation is bound to the step and there is one per step (K-13)."""
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    insert_observation(connection, step_id=step_id, full_text="bir", limits=LIMITS)
    with pytest.raises(sqlite3.IntegrityError):
        insert_observation(connection, step_id=step_id, full_text="iki", limits=LIMITS)


def test_episode_sequence_is_unique_within_a_run(connection):
    """The sequence number must be unique within a run, otherwise drift cannot be checked."""
    _manifest(connection)
    _episode(connection, sequence_in_run=1)
    with pytest.raises(sqlite3.IntegrityError):
        _episode(connection, task_id="other", sequence_in_run=1)


def test_model_load_state_is_constrained(connection):
    _manifest(connection)
    with pytest.raises(sqlite3.IntegrityError):
        _episode(connection, model_load_state="lukewarm")


def test_shield_mode_is_constrained(connection):
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    with pytest.raises(sqlite3.IntegrityError):
        insert_shield_violation(
            connection,
            step_id=step_id,
            violation_index=1,
            app="spotify",
            api="songs",
            http_method="DELETE",
            raw_parameters={},
            predicate="p",
            mode="belki",
        )


def test_raw_parameters_are_stored_in_full(connection):
    """K-15: raw parameters in full, not as a digest."""
    _manifest(connection)
    episode_id = _episode(connection)
    step_id = _step(connection, episode_id, 1)
    parametreler = {"access_token": "gizli", "song_id": 42, "note": "a long text"}
    insert_action(
        connection,
        step_id=step_id,
        action_index=1,
        app="spotify",
        api="songs",
        http_method="POST",
        raw_parameters=parametreler,
    )
    row = connection.execute("SELECT raw_parameters FROM actions").fetchone()
    import json

    assert json.loads(row["raw_parameters"]) == parametreler


def test_recording_limits_load_from_config():
    limits = load_recording_limits("config/recording.yaml")
    assert limits.observation_max_bytes == 8192
    assert limits.on_quota_exceeded == "stop"


def test_recording_limits_reject_unknown_field(tmp_path):
    path = tmp_path / "bozuk.yaml"
    path.write_text(
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        "no_progress_limit: 4\nmax_output_tokens: 4000\nmax_prompt_characters: 50000\n"
        "fazla: 1\n",
        encoding="utf-8",
    )
    with pytest.raises(RecordError, match="unrecognised field"):
        load_recording_limits(path)


def test_recording_limits_carry_the_stopping_threshold():
    """The threshold is provisional, so its presence and type are checked, not its value."""
    assert load_recording_limits("config/recording.yaml").no_progress_limit >= 1


def test_zero_stopping_threshold_is_rejected(tmp_path):
    path = tmp_path / "bozuk.yaml"
    path.write_text(
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        "no_progress_limit: 0\nmax_output_tokens: 4000\nmax_prompt_characters: 50000\n",
        encoding="utf-8",
    )
    with pytest.raises(RecordError, match="no_progress_limit"):
        load_recording_limits(path)


def test_the_output_budget_has_no_silent_default(tmp_path):
    """Part of the measurement's definition: unspecified, the run fails.

    It used to be read from the environment with a silent default of 400. That
    default started a run on the wrong budget; at 400 the same model gives 6/30
    and at 4000 it gives 20/30 (S-26).
    """
    path = tmp_path / "missing.yaml"
    path.write_text(
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        "no_progress_limit: 4\n",
        encoding="utf-8",
    )
    with pytest.raises(RecordError, match="max_output_tokens"):
        load_recording_limits(path)


def test_a_nonpositive_output_budget_is_rejected(tmp_path):
    path = tmp_path / "bozuk.yaml"
    path.write_text(
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        "no_progress_limit: 4\nmax_output_tokens: 0\nmax_prompt_characters: 50000\n",
        encoding="utf-8",
    )
    with pytest.raises(RecordError, match="max_output_tokens"):
        load_recording_limits(path)


def _limits_yaml(ceiling: str) -> str:
    return (
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        f"no_progress_limit: 4\nmax_output_tokens: 4000\nmax_prompt_characters: {ceiling}\n"
    )


def test_the_prompt_ceiling_has_no_silent_default(tmp_path):
    """This is the number that decides the effective context (S-47), and
    unspecified, the run fails.

    A silent default would produce exactly S-47's fault: the value 50000 sat
    written in the code for three months, was recorded nowhere, and made the
    effective context 13K instead of 32K.
    """
    path = tmp_path / "missing.yaml"
    path.write_text(
        "observation_max_bytes: 10\nrun_disk_quota_bytes: 10\non_quota_exceeded: stop\n"
        "no_progress_limit: 4\nmax_output_tokens: 4000\n",
        encoding="utf-8",
    )
    with pytest.raises(RecordError, match="max_prompt_characters"):
        load_recording_limits(path)


def test_no_ceiling_is_written_as_minus_one(tmp_path):
    """Running without a ceiling is a valid choice; the agent's own spelling is `None`."""
    path = tmp_path / "tavansiz.yaml"
    path.write_text(_limits_yaml("-1"), encoding="utf-8")
    assert load_recording_limits(path).max_prompt_characters == -1


@pytest.mark.parametrize("ceiling", ["0", "-2", "fifty thousand"])
def test_a_meaningless_prompt_ceiling_is_rejected(tmp_path, ceiling):
    """A zero ceiling would mean no context at all and would break every episode in silence."""
    path = tmp_path / "bozuk.yaml"
    path.write_text(_limits_yaml(ceiling), encoding="utf-8")
    with pytest.raises(RecordError, match="max_prompt_characters"):
        load_recording_limits(path)
