"""The analysis sets come from the runner's own slots, by one rule (K-181, K-184)."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from zihin.experiment import SETS, analysis_sets, load_order, phase_one_episodes
from zihin.records import LIBRARY_SERIES

REPOSITORY = Path(__file__).resolve().parents[1]
MEASUREMENT = REPOSITORY / "scripts/setup/measure_experiment_sets.py"


def _document() -> dict:
    return json.loads((REPOSITORY / SETS).read_text(encoding="utf-8"))


def test_the_sets_follow_from_the_recorded_slots_by_the_rule() -> None:
    document = _document()
    sets = analysis_sets(document["per_task"])
    assert {name: entry["task_ids"] for name, entry in document["sets"].items()} == sets


def test_the_sets_cover_the_declared_order() -> None:
    assert set(_document()["per_task"]) == set(load_order()["order"])


def test_the_phase_one_episode_count_follows_from_the_slots() -> None:
    document = _document()
    phase = document["phase_one"]
    assert phase["episodes"] == phase_one_episodes(document["per_task"], phase["seeds"])


def test_an_uncovered_task_is_in_no_set_and_a_short_arm_leaves_only_its_contrasts() -> None:
    per_task = {
        "covered": {c: {"covered": True, "volume_matched": True} for c in _CONDITIONS},
        "short": {
            **{c: {"covered": True, "volume_matched": True} for c in _CONDITIONS},
            "irrelevant_retrieval": {"covered": True, "volume_matched": False},
        },
        "bare": {c: {"covered": False, "volume_matched": True} for c in _CONDITIONS},
    }
    sets = analysis_sets(per_task)
    assert sets["Y-1"] == ["covered", "short"]
    assert sets["Y-6.2"] == ["covered"]
    assert sets["Y-5"] == ["covered", "short"]


_CONDITIONS = ("skills_failures", "skills", "failures", "irrelevant_retrieval")


def test_the_measurement_builds_the_slots_the_runner_builds() -> None:
    source = MEASUREMENT.read_text(encoding="utf-8")
    assert "compose(" in source and "open_library()" in source
    assert "retrieve(" not in source


@pytest.mark.skipif(
    not (REPOSITORY / LIBRARY_SERIES).exists(),
    reason=f"{LIBRARY_SERIES} is absent: restore it with scripts/restore_records.py",
)
def test_the_committed_sets_are_what_the_slots_give_today() -> None:
    spec = importlib.util.spec_from_file_location("measure_experiment_sets", MEASUREMENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from zihin.experiment import render

    assert render(module.measure()) == (REPOSITORY / SETS).read_text(encoding="utf-8")


@pytest.mark.parametrize("language", ["tr", "en"])
def test_the_protocols_analysis_sets_are_the_measured_ones(language) -> None:
    """Section 19.7 states the counts; the file derived them. They must agree."""
    text = (REPOSITORY / f"experiments/setup-protocol.{language}.md").read_text(encoding="utf-8")
    section = text[text.index("### 19.7") :]
    stated = {
        name + (suffix or ""): int(count)
        for name, suffix, count in re.findall(
            r"^\| `(Y-[\d.]+)`(, [^|]+?)? \| [^|]+ \| \*\*(\d+)\*\* \|$", section, re.M
        )
    }
    measured = {name: entry["tasks"] for name, entry in _document()["sets"].items()}
    assert len(stated) == len(measured) == 5
    assert sorted(stated.values()) == sorted(measured.values())
    for name in ("Y-1", "Y-6.2", "Y-4", "Y-5"):
        assert stated[name] == measured[name], name
    episodes = re.search(r"\*\*(\d+)\*\*", section[section.index("930") - 10 :]).group(1)
    assert int(episodes) == _document()["phase_one"]["episodes"]
