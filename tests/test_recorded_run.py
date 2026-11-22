"""Was the single-task run from stage 1 really written into the schema?

A direct check of the acceptance criterion. Not synthetic data: it reads a real
episode run with `scripts/record_run.py`.

The database is not tracked and is not produced in CI, so the test carries the
`appworld` marker and is skipped when the file is absent. The date it was run
sits in the stage report.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zihin.records import open_database, read_episode_timeline

pytestmark = pytest.mark.appworld

DATABASE = Path("results/zihin.sqlite")


@pytest.fixture(scope="module")
def connection():
    if not DATABASE.exists():
        pytest.skip(
            f"{DATABASE} is absent: restore it with scripts/restore_records.py, "
            "or take a run with scripts/record_run.py"
        )
    with open_database(DATABASE) as db:
        yield db


def test_run_manifest_records_the_verified_context_window(connection):
    """K-37 first condition: no run is written before the effective window is verified."""
    manifest = connection.execute("SELECT * FROM run_manifests").fetchone()
    assert manifest is not None, "the manifest was not written"
    assert manifest["context_verified"] == 1
    assert manifest["num_ctx_effective"] == manifest["num_ctx_requested"]
    assert manifest["appworld_commit"]
    assert manifest["instruction_file_digest"]


def test_episode_carries_load_state_and_sequence(connection):
    episode = connection.execute("SELECT * FROM episodes ORDER BY episode_id").fetchone()
    assert episode["model_load_state"] in {"cold", "warm", "unknown"}
    assert episode["sequence_in_run"] >= 1
    assert episode["total_model_calls"] >= 1


def test_whole_episode_reads_back_in_order(connection):
    """One episode, several steps, several actions per step, one observation per step."""
    episode = connection.execute("SELECT * FROM episodes ORDER BY episode_id").fetchone()
    rows = read_episode_timeline(connection, episode["episode_id"])
    assert rows, "the timeline is empty"

    steps = [s["step_index"] for s in rows]
    assert steps == sorted(steps), "the steps do not come in order"
    assert len(set(steps)) >= 2, "several steps were expected"

    step_count = connection.execute(
        "SELECT COUNT(*) AS n FROM steps WHERE episode_id = ?", (episode["episode_id"],)
    ).fetchone()["n"]
    observation_count = connection.execute(
        "SELECT COUNT(*) AS n FROM observations o "
        "JOIN steps s ON s.step_id = o.step_id WHERE s.episode_id = ?",
        (episode["episode_id"],),
    ).fetchone()["n"]
    assert observation_count == step_count, "every step must have one observation"


def test_at_least_one_step_produced_multiple_actions(connection):
    row = connection.execute(
        "SELECT step_id, COUNT(*) AS n FROM actions GROUP BY step_id ORDER BY n DESC LIMIT 1"
    ).fetchone()
    assert row is not None, "no action was written"
    assert row["n"] >= 2, "several actions per step were expected"


def test_actions_carry_full_raw_parameters(connection):
    """K-15. An empty dict is valid too, but the column must be filled."""
    missing = connection.execute(
        "SELECT COUNT(*) AS n FROM actions WHERE raw_parameters IS NULL"
    ).fetchone()["n"]
    assert missing == 0
