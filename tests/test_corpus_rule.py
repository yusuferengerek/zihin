"""The corpus rule: the evaluated model on the accumulation split, nothing else.

Both readers - the skill compiler's `passing_sequences` and the failure index's
`observed_episodes` - read every episode in the file once. On Colab that file
carried three runs, and the guard bound on a length-12 pattern supported by two
`b32c` episodes and one `bir1`: the same model, but on `test_normal`, which is
the evaluation split. A skill mined from those encodes an evaluation task's call
sequence (K-159). The rule is model tag AND split, and it is a rule rather than
a prefix so that a second train run joins and a sibling on the evaluation split
stays out.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

from zihin.records import (
    insert_action,
    insert_episode,
    insert_run_manifest,
    insert_step,
    insert_verifier_result,
    open_database,
)

REPOSITORY = Path(__file__).resolve().parents[1]
MODEL_32B = "qwen2.5-coder:32b-instruct-q4_K_M"
MODEL_14B = "qwen2.5-coder:14b-instruct-q4_K_M"


def _module(name: str):
    path = REPOSITORY / "scripts/setup" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _manifest(run_id: str, model: str) -> dict:
    return {
        "run_id": run_id,
        "created_at": "uptime:1.0",
        "model_tag": model,
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


def _episode(db, prefix: str, task: str, model: str, split: str, passed: int = 1) -> int:
    run_id = f"{prefix}-{task}-{task}-x"
    insert_run_manifest(db, **_manifest(run_id, model))
    episode_id = insert_episode(
        db,
        run_id=run_id,
        task_id=task,
        split=split,
        condition="baseline",
        model_ref=model,
        seed=1,
        sequence_in_run=1,
        model_load_state="cold",
        step_ceiling=20,
        started_at="uptime:1.0",
    )
    step_id = insert_step(db, episode_id=episode_id, step_index=1, instruction_digest="0" * 64)
    insert_action(
        db,
        step_id=step_id,
        action_index=1,
        app="spotify",
        api="/auth/token",
        http_method="POST",
        raw_parameters="{}",
        result_status="ok",
    )
    insert_verifier_result(db, episode_id=episode_id, passed=passed)
    return episode_id


@pytest.fixture
def record(tmp_path):
    """The file as Colab had it: three runs, then a sibling on the wrong split."""
    db = open_database(tmp_path / "record.sqlite")
    db.row_factory = __import__("sqlite3").Row
    with db:
        ids = {
            "b14": _episode(db, "b14", "t1", MODEL_14B, "test_normal"),
            "b32c": _episode(db, "b32c", "t2", MODEL_32B, "test_normal"),
            "bir1": _episode(db, "bir1", "t3", MODEL_32B, "train"),
            "bir1_failed": _episode(db, "bir1", "t4", MODEL_32B, "train", passed=0),
        }
    yield db, ids
    db.close()


def test_the_compiler_reads_only_the_declared_model_on_the_declared_split(record):
    db, ids = record
    mine_skills = _module("mine_skills")
    got = {
        s.episode_id for s in mine_skills.passing_sequences(db, model_tag=MODEL_32B, split="train")
    }
    assert got == {ids["bir1"]}, got


def test_a_sibling_of_the_same_model_on_the_evaluation_split_stays_out(record):
    """The leak, by construction: same model, `test_normal`, a pass."""
    db, ids = record
    with db:
        sibling = _episode(db, "bir1", "t5", MODEL_32B, "test_normal")
    mine_skills = _module("mine_skills")
    got = {
        s.episode_id for s in mine_skills.passing_sequences(db, model_tag=MODEL_32B, split="train")
    }
    assert sibling not in got
    assert got == {ids["bir1"]}


def test_a_second_train_run_of_the_same_model_joins(record):
    """Why it is a rule and not a prefix."""
    db, ids = record
    with db:
        second = _episode(db, "bir2", "t6", MODEL_32B, "train")
    mine_skills = _module("mine_skills")
    got = {
        s.episode_id for s in mine_skills.passing_sequences(db, model_tag=MODEL_32B, split="train")
    }
    assert got == {ids["bir1"], second}


def test_the_failure_index_reads_the_same_corpus_passes_and_failures(record):
    """Same rule, without the pass requirement: failures are what it indexes."""
    db, ids = record
    with db:
        sibling = _episode(db, "bir1", "t5", MODEL_32B, "test_normal", passed=0)
    index = _module("build_failure_index")
    got = set(index.observed_episodes(db, model_tag=MODEL_32B, split="train"))
    assert got == {ids["bir1"], ids["bir1_failed"]}, got
    assert sibling not in got and ids["b14"] not in got and ids["b32c"] not in got


def test_the_rule_cannot_be_left_off():
    """No default: a caller that does not say which corpus gets no corpus."""
    mine_skills = _module("mine_skills")
    index = _module("build_failure_index")
    with pytest.raises(TypeError):
        mine_skills.passing_sequences(None)
    with pytest.raises(TypeError):
        index.observed_episodes(None)


def test_the_unfiltered_read_exists_only_under_its_own_name():
    """The setup-phase substrate measurements keep the whole-file read, named.

    Nothing in the production builders may call it: the name is the fence.
    """
    for script in ("build_skill_library.py", "build_failure_index.py"):
        source = (REPOSITORY / "scripts/setup" / script).read_text(encoding="utf-8")
        tree = ast.parse(source)
        main = next(
            n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "main"
        )
        calls = {
            n.func.id
            for n in ast.walk(main)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        assert "every_observed_episode" not in calls, f"{script} reads the whole file"


def test_the_runner_hands_both_builders_the_model_and_the_split():
    """The declared rule reaches the two builders from the runner's own MODEL and SPLIT."""
    source = (REPOSITORY / "scripts/setup/run_accumulation.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    seen = {}
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "build"
        ):
            continue
        script = node.args[0].value
        values = [ast.unparse(a) for a in node.args[1:]]
        seen[script] = values
    for script in ("build_skill_library.py", "build_failure_index.py"):
        values = seen[script]
        assert "'--model-tag'" in values and values[values.index("'--model-tag'") + 1] == "MODEL", (
            script
        )
        assert "'--split'" in values and values[values.index("'--split'") + 1] == "SPLIT", script
