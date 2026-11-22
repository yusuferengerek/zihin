"""The mining guards name themselves.

"The search hit a guard and the result is incomplete" was the whole message,
and it sent a round back to Colab with no way to tell a node budget from a
depth cap, or a near miss from an explosion. A failure names itself (K-125):
which guard, the value it saw, its limit, and the corpus it saw it on.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from zihin.compiler import EpisodeSequence, RecordedCall, mine_patterns
from zihin.records import open_database

REPOSITORY = Path(__file__).resolve().parents[1]
# The corpus rule the builder requires (K-159); these tests are about the
# guards, so any model and split will do as long as they are given.
RULE = ["--model-tag", "m", "--split", "train"]


def _sequence(episode_id: int, task: str, symbols: list[str]) -> EpisodeSequence:
    calls = tuple(
        RecordedCall(app="app", template=f"/{symbol}", method="GET", arguments={})
        for symbol in symbols
    )
    return EpisodeSequence(
        episode_id=episode_id,
        task_id=task,
        calls=calls,
        step_ids=tuple(range(len(calls))),
        step_call_counts=tuple(1 for _ in calls),
    )


def _shared_corpus(length: int, tasks: int = 4) -> list[EpisodeSequence]:
    """`tasks` distinct tasks that all make the same `length`-call sequence."""
    symbols = [f"s{i}" for i in range(length)]
    return [_sequence(i, f"t{i}", symbols) for i in range(tasks)]


def test_a_finished_search_says_so():
    result = mine_patterns(_shared_corpus(4), min_support=3, max_gap=2)
    assert not result.guarded
    assert result.guard is None
    assert "completed" in result.guard_report()


def test_the_depth_cap_names_itself():
    """Sixteen shared calls, a cap of twelve: the cap binds and says where."""
    result = mine_patterns(_shared_corpus(16), min_support=3, max_gap=2, max_length=12)
    assert result.guarded and result.hit_max_length and not result.hit_max_patterns
    assert result.guard == "max_length"
    assert result.observed == 12
    assert result.limit == 12
    assert result.frontier >= 1
    report = result.guard_report()
    assert "max_length" in report
    assert "12" in report
    assert "--max-length" in report, "the report does not say what to raise"


def test_the_node_budget_names_itself():
    """A budget of five on a corpus that grows past it: the budget binds and says
    the count it would have reached."""
    result = mine_patterns(_shared_corpus(8), min_support=3, max_gap=2, max_patterns=5)
    assert result.guarded and result.hit_max_patterns and not result.hit_max_length
    assert result.guard == "max_patterns"
    assert result.observed > 5
    assert result.limit == 5
    assert result.level >= 2
    report = result.guard_report()
    assert "max_patterns" in report
    assert str(result.observed) in report and "5" in report
    assert "--max-patterns" in report, "the report does not say what to raise"


def test_raising_the_binding_guard_completes_the_search():
    """The mechanical branch of the decision: a budget that bound is raised, and
    the search finishes with the guard silent."""
    corpus = _shared_corpus(8)
    bound = mine_patterns(corpus, min_support=3, max_gap=2, max_patterns=5)
    assert bound.guarded
    raised = mine_patterns(corpus, min_support=3, max_gap=2, max_patterns=5_000)
    assert not raised.guarded
    assert raised.guard_report().startswith("no guard bound")


def _builder():
    path = REPOSITORY / "scripts/setup/build_skill_library.py"
    spec = importlib.util.spec_from_file_location("build_skill_library_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_skill_library_probe"] = module
    spec.loader.exec_module(module)
    return module


def test_the_builder_refuses_with_the_guards_sentence_and_the_corpus(tmp_path, monkeypatch):
    """End to end through `build_skill_library.py`: the refusal carries the
    guard's report and what the miner was mining, not only "hit a guard"."""
    builder = _builder()
    database = tmp_path / "record.sqlite"
    open_database(database).close()

    bound = mine_patterns(_shared_corpus(16), min_support=3, max_gap=2, max_length=12)
    assert bound.guarded
    monkeypatch.setattr(builder, "mine_patterns", lambda *a, **k: bound)

    with pytest.raises(SystemExit) as refusal:
        builder.main(["--max-gap", "2", "--min-support", "3", "--database", str(database)] + RULE)
    message = str(refusal.value)
    assert "guard max_length bound" in message
    assert "limit is 12" in message
    assert "corpus:" in message
    assert "0 passing episode(s)" in message, "the corpus line is missing"


def test_the_builder_passes_the_raised_guards_through(tmp_path, monkeypatch):
    """`--max-length` and `--max-patterns` reach the compiler, and only when given:
    absent, the compiler's own defaults apply and no second copy lives here."""
    builder = _builder()
    database = tmp_path / "record.sqlite"
    open_database(database).close()
    seen = {}

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return mine_patterns(*args, **kwargs)

    monkeypatch.setattr(builder, "mine_patterns", spy)
    builder.main(
        [
            "--max-gap",
            "2",
            "--min-support",
            "3",
            "--database",
            str(database),
            "--max-length",
            "20",
            "--max-patterns",
            "999",
            "--dry-run",
        ]
        + RULE
    )
    assert seen["max_length"] == 20 and seen["max_patterns"] == 999

    seen.clear()
    builder.main(
        ["--max-gap", "2", "--min-support", "3", "--database", str(database), "--dry-run"] + RULE
    )
    assert "max_length" not in seen and "max_patterns" not in seen
