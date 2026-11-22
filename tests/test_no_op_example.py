"""The observation preregistration A.5 cites, and what its eleven siblings say (S-77).

A.5's example of inaction being rewarded comes from one carded episode of
`0de03ea_1`. The graded score's free tests - `no_op_pass` - are what that episode
lost, so the count of them has to be read, not inferred.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from zihin import verification

REPOSITORY = Path(__file__).resolve().parents[1]


def test_the_graded_detail_counts_the_free_tests_it_could_have_passed(tmp_path, monkeypatch):
    evaluations = tmp_path / "exp" / "evaluations"
    evaluations.mkdir(parents=True)
    entry = {
        "passes": [{"label": "no_op_fail"}, {"label": "no_op_pass"}],
        "failures": [{"label": "no_op_fail"}, {"label": "no_op_pass"}],
    }
    (evaluations / "on_only_t_1.json").write_text(
        json.dumps({"individual": {"t_1": entry}}), encoding="utf-8"
    )
    monkeypatch.setattr(
        verification, "path_store", SimpleNamespace(experiment_outputs=str(tmp_path))
    )
    detail = verification.graded_detail("exp", "t_1")
    assert detail == {
        "meaningful_passed": 1,
        "meaningful_total": 2,
        "trivial_passed": 1,
        "trivial_total": 2,
    }


def test_the_artefact_says_what_its_rows_say():
    report = json.loads((REPOSITORY / "results/no-op-example.json").read_text(encoding="utf-8"))
    carded = [e for e in report["episodes"] if e["condition"] == "skills_failures"]
    assert report["carded_episodes"] == len(carded)
    assert report["carded_episodes_that_lost_a_free_test"] == [
        e["run"] for e in carded if e["trivial_lost"]
    ]
    assert report["cited_by_a5"] in {e["run"] for e in carded}
