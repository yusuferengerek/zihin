"""The block boundary: the path that only ever ran for the first time in Colab.

**Why this file exists.** `--dry-run` spends no episode, so it never reaches a
block boundary; the mining call was first executed on a real runtime, sixty
episodes in, and it died on argparse's exit code 2 because the runner passed
neither `--max-gap` nor `--min-support`. Every test here runs the **real**
builders as subprocesses against a temporary record. Nothing is mocked: a mock
of a script that rejects its arguments would have passed.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import pytest

from zihin.records import (
    insert_episode,
    insert_run_manifest,
    insert_step,
    insert_verifier_result,
    open_database,
)

REPOSITORY = Path(__file__).resolve().parents[1]
RUNNER = REPOSITORY / "scripts/setup/run_accumulation.py"


@pytest.fixture(scope="module")
def runner():
    """`run_accumulation.py` as a module, with a declared prefix on the line."""
    spec = importlib.util.spec_from_file_location("run_accumulation", RUNNER)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["run_accumulation.py", "bir1"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    return module


# ---------------------------------------------------------------------------
# 1. Every script the runner invokes, and every argument it must be given
# ---------------------------------------------------------------------------


def _parser_of(relative: str) -> argparse.ArgumentParser | None:
    """The script's own parser, built by the script, not described by this test."""
    path = REPOSITORY / relative
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        builds = any(
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "ArgumentParser"
            for inner in ast.walk(node)
        )
        if not builds:
            continue
        namespace: dict = {
            "argparse": argparse,
            "ACTIVE_SERIES": "results/x.sqlite",
            "__doc__": "",
        }
        function = ast.Module(body=[node], type_ignores=[])
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(function, str(path), "exec"), namespace)  # noqa: S102
        # The parser is a local of that function, so it is caught on its way into
        # `parse_args` rather than looked for afterwards.
        caught: list[argparse.ArgumentParser] = []
        original = argparse.ArgumentParser.parse_args

        def intercept(self, args=None, namespace=None, _into=caught):
            _into.append(self)
            raise SystemExit(0)

        argparse.ArgumentParser.parse_args = intercept
        # Some of these take the argument vector and some read `sys.argv`; the
        # signature says which, rather than one call shape being assumed.
        wants_argv = bool(node.args.args)
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                namespace[node.name]([]) if wants_argv else namespace[node.name]()
        except SystemExit:
            pass
        except Exception:  # noqa: BLE001 - a parser that cannot be built is reported below
            pass
        finally:
            argparse.ArgumentParser.parse_args = original
        if caught:
            return caught[0]
    return None


def _required(parser: argparse.ArgumentParser) -> set[str]:
    return {
        action.option_strings[0] if action.option_strings else action.dest
        for action in parser._actions
        if action.dest != "help" and (action.required or not action.option_strings)
    }


def _flags(nodes) -> set[str]:
    return {
        node.value
        for node in nodes
        if isinstance(node, ast.Constant) and str(node.value).startswith("--")
    }


def _invocations() -> list[tuple[str, set[str]]]:
    """(script, the flags the runner passes) for every script it invokes.

    Both shapes are read, because the question is "does the runner call anything
    else", not "does it call anything else through `build`". A new call site that
    used a third shape would show up as a script this sweep does not list, and the
    floor test below is what makes that visible.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # build("x.py", "--flag", value, ...)
        if isinstance(node.func, ast.Name) and node.func.id == "build" and node.args:
            script = node.args[0]
            if isinstance(script, ast.Constant):
                found.append(("scripts/setup/" + script.value, _flags(node.args[1:])))
            continue
    # [sys.executable, "scripts/x.py", ...] - as a literal anywhere, because the
    # list is usually built into a variable first and only then handed to
    # `subprocess.run`, so reading the call's arguments finds a Name and nothing
    # else.
    for node in ast.walk(tree):
        if not isinstance(node, ast.List):
            continue
        named = [
            element.value
            for element in node.elts
            if isinstance(element, ast.Constant) and str(element.value).endswith(".py")
        ]
        for script in named:
            found.append((script, _flags(node.elts)))
    return found


def _appended_flags() -> set[str]:
    """Flags the runner adds to a command after building the list.

    `record_run.py`'s optional flags are appended conditionally, which no reading
    of the list literal can see.
    """
    source = RUNNER.read_text(encoding="utf-8")
    return set(re.findall(r'command\.append\("(--[\w-]+)"\)', source)) | set(
        re.findall(r'command \+= \["(--[\w-]+)"', source)
    )


# Every script the runner is known to invoke. A new one appears here when it is
# added, and until it does the floor below fails - which is the point: "does it
# call anything else" is a question that must be answered by the file, not
# remembered.
INVOKED = {
    "scripts/setup/build_skill_library.py",
    "scripts/setup/build_failure_index.py",
    "scripts/record_run.py",
}


def test_the_runner_invokes_exactly_the_scripts_this_file_knows_about():
    """A floor and a ledger at once.

    If the sweep stops finding call sites it checks nothing, and if the runner
    grows a new one the sweep must be told - otherwise a required argument goes
    unpassed again and it is found by running, at the price of a session.
    """
    scripts = {script for script, _ in _invocations()}
    assert scripts == INVOKED, f"found {sorted(scripts)}, expected {sorted(INVOKED)}"


@pytest.mark.parametrize("script,passed", _invocations(), ids=lambda v: str(v)[:40])
def test_every_invoked_script_gets_its_required_arguments(script, passed):
    """The failure, generalised: a required argument the caller does not pass.

    `build()` adds `--database` to every call, so that one is added here rather
    than being read off the call site.
    """
    parser = _parser_of(script)
    assert parser is not None, f"no parser found in {script}; this test stopped reading it"
    required = _required(parser)
    given = passed | {"--database"} | _appended_flags()
    missing = required - given
    assert not missing, f"{script} requires {sorted(missing)} and the runner passes {sorted(given)}"


def test_the_thresholds_are_read_and_not_written_into_the_runner():
    """A literal here would be the second copy the declaration exists to prevent."""
    source = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id != "build":
            continue
        for previous, argument in zip(node.args, node.args[1:], strict=False):
            if not (isinstance(previous, ast.Constant) and isinstance(previous.value, str)):
                continue
            if previous.value not in ("--max-gap", "--min-support"):
                continue
            assert isinstance(argument, ast.Call), (
                f"{previous.value} is passed a literal; it has a declared source"
            )
            assert argument.func.id == "declared_field"


# ---------------------------------------------------------------------------
# 2. The boundary itself, with the real builders
# ---------------------------------------------------------------------------


def _manifest(run_id: str) -> dict:
    return {
        "run_id": run_id,
        "created_at": "uptime:1.0",
        "model_tag": "qwen2.5-coder:32b-instruct-q4_K_M",
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


def _corpus(path: Path, episodes: int, prefix: str = "bir1") -> None:
    """A record with `episodes` complete episodes under `prefix`.

    Small and repetitive on purpose: the point is not what the miner finds, it is
    that the miner runs with the arguments it was given.
    """
    with open_database(path) as db:
        with db:
            for number in range(episodes):
                task = f"t{number:03d}_1"
                run_id = f"{prefix}-{task}-{task}-32b"
                insert_run_manifest(db, **_manifest(run_id))
                episode_id = insert_episode(
                    db,
                    run_id=run_id,
                    task_id=task,
                    split="train",
                    condition="baseline",
                    model_ref="qwen2.5-coder:32b-instruct-q4_K_M",
                    seed=1,
                    sequence_in_run=1,
                    model_load_state="cold",
                    step_ceiling=20,
                    started_at="uptime:1.0",
                )
                for step in range(3):
                    insert_step(
                        db,
                        episode_id=episode_id,
                        step_index=step + 1,
                        instruction_digest="0" * 64,
                    )
                insert_verifier_result(db, episode_id=episode_id, passed=1)


@pytest.fixture
def record(tmp_path, runner, monkeypatch):
    """A temporary record and ledger the runner is pointed at."""

    def build(episodes: int, blocks: list | None = None):
        path = tmp_path / "record.sqlite"
        _corpus(path, episodes)
        ledger_path = tmp_path / "ledger.json"
        monkeypatch.setattr(runner, "ACTIVE_SERIES", str(path))
        monkeypatch.setattr(runner, "LEDGER", ledger_path)
        # The run's episode count is over the swept split's tasks (K-160), and
        # this corpus is synthetic: tell the runner these are the swept tasks.
        monkeypatch.setattr(runner, "swept_tasks", lambda: [f"t{n:03d}_1" for n in range(episodes)])
        ledger = runner.load_ledger()
        ledger["blocks"] = blocks or []
        return ledger, path, ledger_path

    return build


def test_the_block_boundary_runs_the_real_builders(record, runner):
    """The call that failed in Colab, run here with the real scripts.

    `build()` exits the process when a builder fails, so reaching the assertions
    at all is the assertion: argparse's exit code 2 would have stopped this test
    exactly where it stopped the run.
    """
    ledger, _, ledger_path = record(30)
    fired = runner.close_block(ledger, 1, 30)
    assert fired is False
    assert ledger["blocks"], "no ledger row was written"
    row = ledger["blocks"][-1]
    assert row["block"] == 1
    assert row["blocks_covered"] == 1
    assert row["episodes_run_total"] == 30
    assert json.loads(ledger_path.read_text(encoding="utf-8"))["blocks"], "the ledger was not saved"


def test_the_builders_receive_the_declared_thresholds(record, runner, monkeypatch):
    """Not that they run - that they run with the numbers the protocol declares."""
    seen = []
    real = runner.subprocess.run

    def watch(command, **kwargs):
        seen.append(command)
        return real(command, **kwargs)

    monkeypatch.setattr(runner.subprocess, "run", watch)
    ledger, path, _ = record(30)
    runner.close_block(ledger, 1, 30)

    library = next(c for c in seen if "build_skill_library.py" in c[1])
    index = next(c for c in seen if "build_failure_index.py" in c[1])
    assert library[library.index("--max-gap") + 1] == "2"
    assert library[library.index("--min-support") + 1] == "3"
    assert index[index.index("--min-support") + 1] == "1"
    assert library[library.index("--database") + 1] == str(path)
    assert index[index.index("--database") + 1] == str(path)


# ---------------------------------------------------------------------------
# 3. The restart
# ---------------------------------------------------------------------------


def test_a_restart_finds_the_boundaries_that_went_by_unmined(record, runner):
    """Sixty episodes written, no ledger row: two boundaries are due."""
    ledger, _, _ = record(0)
    assert runner.boundaries_due(ledger, 60) == 2
    assert runner.boundaries_due(ledger, 30) == 1
    assert runner.boundaries_due(ledger, 29) == 0
    ledger["blocks"] = [{"block": 1}]
    assert runner.boundaries_due(ledger, 60) == 1
    assert runner.boundaries_due(ledger, 30) == 0


def test_a_restart_mines_block_one_rather_than_deferring_it(record, runner):
    """The measured failure: sixty episodes and block 1 never mined.

    Before, `spent` came from the ledger and the ledger was empty, so the runner
    started from zero and the next boundary landed thirty episodes late. Now the
    count comes from the record and the mining happens before any new episode.
    """
    ledger, _, _ = record(60)
    since_block, fired = runner.catch_up(ledger, 60)
    assert fired is False
    assert since_block == 0
    assert len(ledger["blocks"]) == 1, "the catch-up did not mine"
    row = ledger["blocks"][-1]
    assert row["episodes_run_total"] == 60
    assert row["block"] == 2


def test_a_catch_up_over_two_boundaries_is_one_observation(record, runner):
    """Branch A counts consecutive quiet blocks, and it must not count an
    observation of a corpus nobody mined."""
    ledger, _, _ = record(60)
    runner.catch_up(ledger, 60)
    assert ledger["blocks"][-1]["blocks_covered"] == 2


def test_nothing_is_mined_when_no_boundary_is_due(record, runner, monkeypatch):
    """The ordinary case still costs no mining."""
    calls = []
    monkeypatch.setattr(runner, "close_block", lambda *a, **k: calls.append(a) or False)
    ledger, _, _ = record(20)
    since_block, fired = runner.catch_up(ledger, 20)
    assert calls == []
    assert (since_block, fired) == (20, False)


def test_the_record_knows_the_count_when_the_ledger_does_not(record, runner):
    """Sixty episodes written, no ledger row, and the count is still sixty.

    This is the number the cap is read against. Taken from the ledger it was
    zero, because the ledger only advances when a block closes and the run died
    before block 1 closed - so a restart would have spent sixty episodes over
    the cap.
    """
    ledger, _, _ = record(60)
    assert ledger["blocks"] == []
    assert runner.library_state()["episodes_this_run"] == 60


def test_the_episode_count_comes_from_the_record_not_the_ledger():
    """And pinned where it is read, because the value is passed in everywhere else.

    `catch_up` and `boundaries_due` take the count as an argument, so a test that
    calls them cannot see where `main` got it. This reads the assignment.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    main = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    assignments = [
        node
        for node in ast.walk(main)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "spent" for t in node.targets)
    ]
    assert assignments, "main no longer assigns `spent`; this test stopped reading it"
    source = ast.unparse(assignments[0].value)
    assert "library_state" in source, (
        f"`spent` is assigned from {source!r}; it must come from the record, because "
        "the ledger only advances when a block closes"
    )
    assert "ledger" not in source, f"`spent` is read from the ledger: {source!r}"
