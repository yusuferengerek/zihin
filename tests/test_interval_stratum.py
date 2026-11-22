"""The interval sweep describes the primary sample (K-174).

It was first run on both strata together, before the stratification (K-144), and
went on describing a sample the primary estimate is no longer read on. The sweep
now takes the action stratum from the threshold derivation's own definition, and
the artefacts that describe the primary sample have to agree on its size.
"""

from __future__ import annotations

import json
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


def _read(name: str) -> dict:
    return json.loads((REPOSITORY / name).read_text(encoding="utf-8"))


def test_the_sweep_has_no_sample_definition_of_its_own() -> None:
    source = (REPOSITORY / "scripts/setup/measure_interval_width.py").read_text(encoding="utf-8")
    assert "action_stratum()" in source
    assert "load_task_ids(" not in source


def test_the_primary_sample_has_one_size_everywhere() -> None:
    sweep = _read("results/interval-width-action.json")["evaluation_tasks"]
    threshold = _read("results/pass-threshold.json")["primary_sample"]
    stratum = _read("results/task-types.json")["kinds"]["answer+world"]
    assert sweep == threshold == stratum


def test_the_pooled_sweep_is_kept_and_says_it_is_superseded() -> None:
    pooled = _read("results/interval-width.json")
    assert pooled["status"] == "superseded"
    assert pooled["superseded_by"] == "results/interval-width-action.json"
    assert (
        pooled["evaluation_tasks"] > _read("results/interval-width-action.json")["evaluation_tasks"]
    )
