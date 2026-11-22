"""Pins the shape of the conditions tables the run's declaration is read from.

The guard these back has one failure mode and it is silent: a regex that stops
matching returns an empty table, every declared field agrees with nothing, and
the check reports agreement. That is the class K-103 recorded when thirty
rationales came out wrong, and the remedy is the same one — pin the shape.

The parsing lives in `zihin.declared`, so it is tested there rather than through
the script. The script had its own copy once and the copy fell behind (K-138).
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

from zihin.declared import Undeclared, conditions, declared_command, declared_model, run_prefix

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]

EXPECTED_FIELDS = {
    "model_tag",
    "serving_mode",
    "max_output_tokens",
    "no_progress_limit",
    "shield_mode",
    "temperature",
    "base_seed",
    "num_ctx_requested",
    "kv_cache_type",
    "flash_attention",
}


def _checker():
    path = REPOSITORY / "scripts/check_declared_conditions.py"
    spec = importlib.util.spec_from_file_location("check_declared_conditions", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_declared_conditions"] = module
    spec.loader.exec_module(module)
    return module


def test_every_declared_run_resolves_to_one_section() -> None:
    """Each prefix names exactly one declaration, and that declaration is complete."""
    for prefix, section in (
        ("b14", "15.2"),
        ("b32c", "16.2"),
        ("b15l", "17.2"),
        ("b3l", "17.3"),
        ("b7l", "17.4"),
    ):
        number, table = conditions(prefix)
        assert number == section, f"{prefix} resolved to {number}"
        missing = EXPECTED_FIELDS - set(table)
        assert not missing, f"{prefix} is missing {sorted(missing)}"
        assert table["model_tag"].startswith("qwen2.5-coder:")


def test_the_declared_values_are_the_ones_written_down() -> None:
    """The numbers themselves, so a silent edit of a declaration is visible."""
    _, b32c = conditions("b32c")
    assert b32c["max_output_tokens"] == "4000"
    assert b32c["no_progress_limit"] == "40"
    assert b32c["shield_mode"] == "shadow"
    _, b14 = conditions("b14")
    assert b14["max_output_tokens"] == "400"
    assert b14["no_progress_limit"] == "15"


def test_the_local_axis_shares_one_budget() -> None:
    """The point of the re-run: three sizes, one output budget."""
    for prefix in ("b15l", "b3l", "b7l"):
        _, table = conditions(prefix)
        assert table["max_output_tokens"] == "4000"
        assert table["no_progress_limit"] == "40"


def test_every_local_run_declares_its_own_command() -> None:
    for prefix in ("b15l", "b3l", "b7l"):
        command = declared_command(prefix)
        assert prefix in command
        assert "--max-output-tokens" in command
        assert command[command.index("--max-output-tokens") + 1] == "4000"


def test_the_model_is_resolved_from_the_declaration() -> None:
    assert declared_model("b15l").startswith("qwen2.5-coder:1.5b")
    assert declared_model("b7l").startswith("qwen2.5-coder:7b")
    assert declared_model("b32c").startswith("qwen2.5-coder:32b")


def test_an_undeclared_prefix_stops_rather_than_defaulting() -> None:
    """A run nobody declared must not silently borrow another run's conditions."""
    with pytest.raises(Undeclared) as stopped:
        conditions("bhicyok")
    assert "no conditions section" in str(stopped.value)


def test_an_unreadable_table_declines_instead_of_agreeing(monkeypatch, tmp_path) -> None:
    """The floor fires: no rows means no answer, not agreement."""
    import zihin.declared as declared

    empty = tmp_path / "protocol.md"
    empty.write_text("### 15.2 x (`b14`)\n\nno rows here\n\n### 15.3 y\n", encoding="utf-8")
    monkeypatch.setattr(declared, "PROTOCOL", empty)
    with pytest.raises(Undeclared) as stopped:
        conditions("b14")
    assert "floor" in str(stopped.value)


def test_the_prefix_comes_from_the_run_command() -> None:
    """The prefix is resolved from the notebook, and it is one the protocol declares.

    This used to assert the literal prefix of whichever run the notebook happened
    to start, so it broke every time the notebook moved to the next run and said
    nothing about whether the resolution worked. The invariant is that the prefix
    resolves and that the protocol declares a conditions section for it (K-153).
    """
    from zihin.declared import declared_prefixes

    prefix = run_prefix()
    assert prefix
    assert prefix in declared_prefixes()


def test_turkish_and_english_numbers_compare_equal() -> None:
    normalise = _checker().normalise
    assert normalise("0,2") == normalise("0.2")
    assert normalise("True") == normalise("1")
    assert normalise("400") == normalise("400.0")


# --- the experiment's command may not start on a dirty tree (K-180) ---


@pytest.mark.parametrize(
    "token", ["--allow-dirty-tree", "--allow-dirty", "--allow", "--al"], ids=str
)
def test_the_flag_and_every_abbreviation_argparse_accepts_are_refused(token) -> None:
    from zihin.declared import EXPERIMENT_PREFIX, experiment_command_problems

    command = ["uv", "run", "python", "scripts/record_run.py", token]
    assert experiment_command_problems(EXPERIMENT_PREFIX, command)


def test_the_flag_is_not_asked_of_a_run_outside_the_experiment() -> None:
    from zihin.declared import experiment_command_problems

    command = [
        "uv",
        "run",
        "python",
        "scripts/setup/run_accumulation.py",
        "bir1",
        "--allow-dirty-tree",
    ]
    assert experiment_command_problems("bir1", command) == []


def test_a_clean_experiment_command_passes() -> None:
    from zihin.declared import EXPERIMENT_PREFIX, experiment_command_problems

    command = [
        "uv",
        "run",
        "python",
        "scripts/record_run.py",
        "--cards",
        "--max-output-tokens",
        "4000",
    ]
    assert experiment_command_problems(EXPERIMENT_PREFIX, command) == []


def test_the_check_refuses_an_experiment_command_carrying_the_flag(monkeypatch, capsys) -> None:
    """End to end through the script's own entry point, with a dny section faked."""
    from zihin.declared import EXPERIMENT_PREFIX

    checker = _checker()
    table = {field: "x" for field in EXPECTED_FIELDS}
    monkeypatch.setattr(checker, "conditions", lambda prefix: ("19.9", table))
    monkeypatch.setattr(
        checker,
        "declared_command",
        lambda prefix: ["uv", "run", "python", "scripts/record_run.py", "--allow-dirty-tree"],
    )
    monkeypatch.setattr(sys, "argv", ["check_declared_conditions.py", EXPERIMENT_PREFIX])
    with pytest.raises(SystemExit) as stopped:
        checker.main()
    assert "REFUSED" in str(stopped.value)
    assert "--allow-dirty-tree" in capsys.readouterr().out


# --- the experiment's table: every row read, every row compared (K-187) ---


def _run_experiment_check(monkeypatch, capsys, *, table=None, body=None):
    from zihin.declared import EXPERIMENT_PREFIX

    checker = _checker()
    if table is not None:
        monkeypatch.setattr(checker, "conditions", lambda prefix: ("19.6", table))
    if body is not None:
        monkeypatch.setattr(checker, "section_for", lambda prefix: ("19.6", body))
    monkeypatch.setattr(sys, "argv", ["check_declared_conditions.py", EXPERIMENT_PREFIX])
    try:
        checker.main()
    except SystemExit as stopped:
        return stopped.code, capsys.readouterr().out
    return 0, capsys.readouterr().out


def _experiment_table() -> dict:
    from zihin.declared import EXPERIMENT_PREFIX, conditions

    return dict(conditions(EXPERIMENT_PREFIX)[1])


def test_the_experiments_table_resolves_every_row(monkeypatch, capsys) -> None:
    code, out = _run_experiment_check(monkeypatch, capsys)
    assert code == 0, out
    assert "??" not in out
    assert "declared conditions and the run agree" in out


def test_a_row_the_experiment_cannot_compare_fails_the_check(monkeypatch, capsys) -> None:
    table = {**_experiment_table(), "extra_field": "1"}
    code, out = _run_experiment_check(monkeypatch, capsys, table=table)
    assert code == 1
    assert "extra_field: declared and not compared with any source" in out


def test_a_row_the_parser_skips_fails_the_check(monkeypatch, capsys) -> None:
    from zihin.declared import EXPERIMENT_PREFIX, section_for

    _, body = section_for(EXPERIMENT_PREFIX)
    body = body.replace(
        "| `serving_mode` |", "| Step ceiling | 20 | a spaced key |\n| `serving_mode` |", 1
    )
    code, out = _run_experiment_check(monkeypatch, capsys, body=body)
    assert code == 1
    assert "Step ceiling: a row the parser does not read" in out


def test_a_row_that_disagrees_with_its_source_fails_the_check(monkeypatch, capsys) -> None:
    table = {**_experiment_table(), "task_order": "0" * 64}
    code, out = _run_experiment_check(monkeypatch, capsys, table=table)
    assert code == 1
    assert "task_order: the protocol declares" in out


def test_the_experiment_reads_the_library(monkeypatch) -> None:
    import importlib.util

    # The script parses its arguments when it is loaded.
    monkeypatch.setattr(sys, "argv", ["check_prerequisites.py"])
    path = REPOSITORY / "scripts/setup/check_prerequisites.py"
    spec = importlib.util.spec_from_file_location("check_prerequisites", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.reads_the_library("dny") == ("dny", True)
    assert module.reads_the_library("bir1") == ("bir1", False)
