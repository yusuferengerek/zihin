"""The experiment's driver: the stop rule, the slices, the plan and the summary (K-185).

**A measurement-defining change stops it.** Compared with the experiment's first
episode, not warned about: the slices on either side cannot be pooled. Only an
explicit flag goes on, and the runner writes the flag into every episode.

**A slice left open is finished first**, and a new slice takes the next tasks of
the declared order and nothing else.

**The summary is descriptive and pooled over conditions.**
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from zihin.experiment import descriptive, episodes_of, run_identity
from zihin.records import (
    insert_episode,
    insert_run_manifest,
    insert_verifier_result,
    open_database,
)

REPOSITORY = Path(__file__).resolve().parents[1]
MODEL = "qwen2.5-coder:32b-instruct-q4_K_M"


def _driver():
    path = REPOSITORY / "scripts/run_experiment.py"
    spec = importlib.util.spec_from_file_location("run_experiment", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest(run_id: str, commit: str) -> dict:
    return {
        "run_id": run_id,
        "created_at": "uptime:1.0",
        "model_tag": MODEL,
        "num_ctx_requested": 32768,
        "num_ctx_effective": 32768,
        "context_verified": 1,
        "kv_cache_type": "q8_0",
        "flash_attention": 1,
        "temperature": 0.2,
        "base_seed": 123,
        "keep_alive": "30m0s",
        "no_progress_limit": 40,
        "max_output_tokens": 4000,
        "max_prompt_characters": 50000,
        "model_server_env": {"OLLAMA_CONTEXT_LENGTH": "32768"},
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": commit,
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux / 3.11",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }


def _episode(db, run_id: str, task: str, commit: str = "first", seconds: float = 60.0) -> None:
    insert_run_manifest(db, **_manifest(run_id, commit))
    episode_id = insert_episode(
        db,
        run_id=run_id,
        task_id=task,
        split="test_normal",
        condition="baseline",
        model_ref=MODEL,
        seed=1,
        sequence_in_run=1,
        model_load_state="cold",
        step_ceiling=20,
        started_at="uptime:1.0",
        duration_seconds=seconds,
    )
    insert_verifier_result(
        db, episode_id=episode_id, passed=0, num_passed_tests=0, num_failed_tests=1
    )


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        _episode(connection, "bir1-a_1-a_1-32b", "a_1", commit="older")
        _episode(connection, "dny-baseline-s0-a_1-a_1-32b", "a_1", commit="first")
        _episode(connection, "dny-baseline-s1-a_1-a_1-32b", "a_1", commit="second")
        yield connection


# --- the stop rule ------------------------------------------------------------


def test_the_first_experiment_commit_is_the_first_dny_episodes(db) -> None:
    assert _driver().first_experiment_commit(db, "dny") == "first"


def test_no_experiment_episode_means_nothing_to_compare(tmp_path) -> None:
    with open_database(tmp_path / "empty.sqlite") as connection:
        assert _driver().path_change(connection, "dny", "anything", accept=False) is False


def _changed(defining):
    return lambda a, b: (["README.md", *defining], list(defining))


def test_a_measurement_defining_change_stops_the_driver(db, monkeypatch, capsys) -> None:
    driver = _driver()
    monkeypatch.setattr(driver, "changed_files", _changed(["src/zihin/slots.py"]))
    with pytest.raises(SystemExit) as stopped:
        driver.path_change(db, "dny", "later", accept=False)
    assert "STOPPED" in str(stopped.value)
    assert "src/zihin/slots.py" in capsys.readouterr().out


def test_the_flag_goes_on_and_says_so(db, monkeypatch) -> None:
    driver = _driver()
    monkeypatch.setattr(driver, "changed_files", _changed(["src/zihin/slots.py"]))
    assert driver.path_change(db, "dny", "later", accept=True) is True


def test_a_change_outside_the_list_is_not_a_stop(db, monkeypatch) -> None:
    driver = _driver()
    monkeypatch.setattr(driver, "changed_files", _changed([]))
    assert driver.path_change(db, "dny", "later", accept=False) is False


def test_the_first_commit_itself_is_not_a_change(db) -> None:
    assert _driver().path_change(db, "dny", "first", accept=False) is False


def test_the_driver_passes_the_flag_to_the_runner_only_as_the_runner_names_it() -> None:
    source = (REPOSITORY / "scripts/run_experiment.py").read_text(encoding="utf-8")
    assert 'command.append("--path-change-accepted")' in source
    assert "allow-dirty" not in source.replace("It carries no `--allow-dirty-tree`", "")


def test_the_driver_has_no_dirty_tree_option() -> None:
    with pytest.raises(SystemExit):
        _driver().parse(["dny", "--tasks", "1", "--allow-dirty-tree"])


@pytest.mark.parametrize("argv", [["bir1", "--tasks", "1"], ["dny", "--tasks", "0"], ["dny"]])
def test_the_driver_runs_the_experiment_and_takes_a_positive_slice(argv) -> None:
    with pytest.raises(SystemExit):
        _driver().parse(argv)


# --- slices -------------------------------------------------------------------

ORDER = ["t1", "t2", "t3", "t4", "t5"]
COVERED = {"t1": True, "t2": False, "t3": True, "t4": True, "t5": True}


def _written(*tasks: str) -> set[str]:
    return {
        run_identity("dny", c, s, t, "32b") for t in tasks for c, s in episodes_of(t, COVERED[t], 3)
    }


def test_the_first_slice_takes_the_front_of_the_order() -> None:
    assert _driver().plan_slice({}, ORDER, 2, set(), COVERED, 3, "32b") == (1, ["t1", "t2"], True)


def test_an_open_slice_is_finished_before_a_new_one(monkeypatch) -> None:
    written = _written("t1")
    plan = _driver().plan_slice({1: ["t1", "t2"]}, ORDER, 3, written, COVERED, 3, "32b")
    assert plan == (1, ["t1", "t2"], False)


def test_a_finished_slice_is_followed_by_the_next_tasks() -> None:
    written = _written("t1", "t2")
    plan = _driver().plan_slice({1: ["t1", "t2"]}, ORDER, 3, written, COVERED, 3, "32b")
    assert plan == (2, ["t3", "t4", "t5"], True)


def test_an_uncovered_task_runs_the_baseline_only() -> None:
    assert episodes_of("t2", False, 3) == [("baseline", 0), ("baseline", 1), ("baseline", 2)]
    assert len(episodes_of("t1", True, 3)) == 9
    assert episodes_of("t1", True, 3)[:3] == [
        ("baseline", 0),
        ("skills_failures", 0),
        ("irrelevant_retrieval", 0),
    ]


# --- the summary --------------------------------------------------------------


def test_the_summary_is_pooled_and_counts_finished_tasks(db) -> None:
    sets = {
        "phase_one": {"seeds": 2, "episodes": 2},
        "per_task": {"a_1": {"skills_failures": {"covered": False}}},
    }
    summary = descriptive(db, sets, "dny", "32b")
    assert summary == {
        "tasks_finished": 1,
        "tasks": 1,
        "episodes": 2,
        "episodes_planned": 2,
        "mean_duration_seconds": 60.0,
    }
