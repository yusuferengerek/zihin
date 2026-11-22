"""The standing check on series 3: what the merge left is still there (S-74).

The series was overwritten once by a file that lacked four prefixes, and nothing
asked. The record is append-only, so every prefix the merge left must stay with
at least as many episodes; a record without the ledger table cannot evaluate
branch A (K-171).
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

from zihin.records import insert_episode, insert_run_manifest, open_database

REPOSITORY = Path(__file__).resolve().parents[1]
FLOOR = {"bir1": 2, "b3l": 1}


def _module():
    path = REPOSITORY / "scripts/verify_series_merge.py"
    spec = importlib.util.spec_from_file_location("verify_series_merge", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_series_merge"] = module
    spec.loader.exec_module(module)
    return module


def _manifest(run_id: str) -> dict:
    return {
        "run_id": run_id,
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
        "no_progress_limit": 40,
        "max_output_tokens": 4000,
        "max_prompt_characters": 50000,
        "model_server_env": {"OLLAMA_CONTEXT_LENGTH": "32768"},
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": "deadbeef",
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux / 3.11",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }


def _record(path: Path, runs: list[str]) -> Path:
    db = open_database(path)
    with db:
        for index, run_id in enumerate(runs):
            insert_run_manifest(db, **_manifest(run_id))
            insert_episode(
                db,
                run_id=run_id,
                task_id=f"t{index}_1",
                split="train",
                condition="baseline",
                model_ref="m",
                seed=1,
                sequence_in_run=1,
                model_load_state="cold",
                step_ceiling=20,
                started_at="uptime:1.0",
            )
    db.close()
    return path


def test_the_series_the_merge_left_passes(tmp_path) -> None:
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "bir1-b", "b3l-a"])
    _, problems = module.standing_problems(path, FLOOR, [])
    assert problems == []


def test_a_series_that_grew_passes(tmp_path) -> None:
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "bir1-b", "bir1-c", "b3l-a", "new-a"])
    _, problems = module.standing_problems(path, FLOOR, [])
    assert problems == []


def test_a_series_missing_a_prefix_is_not_the_series(tmp_path) -> None:
    """The S-74 case: the file at the path was replaced by one without b3l."""
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "bir1-b"])
    _, problems = module.standing_problems(path, FLOOR, [])
    assert any(line.startswith("b3l: 0 episode(s)") for line in problems)


def test_a_series_that_shrank_is_not_the_series(tmp_path) -> None:
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "b3l-a"])
    _, problems = module.standing_problems(path, FLOOR, [])
    assert any(line.startswith("bir1: 1 episode(s)") for line in problems)


def test_a_scan_artefact_whose_prefix_is_absent_is_named(tmp_path) -> None:
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "bir1-b", "b3l-a"])
    _, problems = module.standing_problems(path, FLOOR, [("b7l-taramasi.json", "b7l")])
    assert any("b7l-taramasi.json" in line for line in problems)


def test_a_series_without_the_ledger_table_is_named(tmp_path) -> None:
    module = _module()
    path = _record(tmp_path / "r.sqlite", ["bir1-a", "bir1-b", "b3l-a"])
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE run_ledger")
    _, problems = module.standing_problems(path, FLOOR, [])
    assert any("run_ledger" in line for line in problems)


def _step_e() -> str:
    text = (REPOSITORY / "scripts/colab_bootstrap.sh").read_text(encoding="utf-8")
    start = text.index('step "E. Record database from Drive"')
    return text[start : text.index('step "E2.', start)]


def test_the_bootstrap_checks_the_series_on_drive_before_linking_it() -> None:
    """The copy on Drive is verified before anything can write to it (K-173)."""
    block = _step_e()
    check = block.index("verify_series_merge.py --check --database")
    assert "|| fail" in block[check : block.index("\n", block.index("|| fail", check)) + 1]
    assert check < block.index("ln -sfn")


def test_the_bootstrap_does_not_start_a_new_series() -> None:
    """A missing series stops the session; it is not created empty on Drive."""
    block = _step_e()
    assert 'touch "$DRIVE_ROOT/results/$SERIES_NAME"' not in block
    assert '[ -f "$DRIVE_ROOT/results/$SERIES_NAME" ] || fail' in block
