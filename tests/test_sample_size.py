"""The sample-size measurement derives its three inputs instead of copying them.

`PASS_RATE = 0.280`, `current_sample: 105` and a size grid ending at 623 were
literals copied from other measurements. When the touched list grew by four tasks
the pool fell to 622 and the script refused to run; had the numbers drifted the
other way it would have run on stale inputs without a word (K-167).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


def _module():
    path = REPOSITORY / "scripts/setup/measure_sample_size.py"
    spec = importlib.util.spec_from_file_location("measure_sample_size", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["measure_sample_size"] = module
    spec.loader.exec_module(module)
    return module


def _pool(test_normal: int, challenge: int, dev: int = 0) -> list[tuple[str, str, int]]:
    return (
        [("test_normal", f"n{i}_1", 10) for i in range(test_normal)]
        + [("test_challenge", f"c{i}_1", 10) for i in range(challenge)]
        + [("dev", f"d{i}_1", 10) for i in range(dev)]
    )


def test_the_sizes_run_from_the_current_sample_to_the_whole_pool():
    module = _module()
    sizes = module.sizes_for(_pool(104, 408, 45))
    assert sizes[0] == 104
    assert sizes[-1] == 557
    assert list(sizes) == sorted(set(sizes))


def test_a_grid_point_outside_the_pool_is_dropped_not_sampled_with_replacement():
    module = _module()
    assert module.sizes_for(_pool(104, 300)) == (104, 130, 160, 200, 250, 300, 400, 404)


def test_the_pass_rate_is_read_from_the_threshold_artefact(tmp_path):
    module = _module()
    artefact = tmp_path / "pass-threshold.json"
    artefact.write_text(json.dumps({"observed": {"rate": 0.31}}), encoding="utf-8")
    assert module.measured_pass_rate(artefact) == 0.31


def test_no_copied_number_is_left_in_the_module():
    module = _module()
    for name in ("PASS_RATE", "SIZES"):
        assert not hasattr(module, name), f"{name} is a copy of another measurement's number"


def test_a_replicate_counts_as_reached_only_if_it_stays_under_the_bound():
    """One replicate's answer: the first size from which every larger size is under.

    A size where the ratio dips under the bound and rises again is not an answer;
    the headline uses the same rule over the median (K-168).
    """
    module = _module()
    sizes = [104, 200, 300]
    assert module.first_size_under(sizes, [0.6, 0.4, 0.45], 0.5) == 200
    assert module.first_size_under(sizes, [0.4, 0.6, 0.4], 0.5) == 300
    assert module.first_size_under(sizes, [0.6, 0.4, 0.6], 0.5) is None
    assert module.first_size_under(sizes, [0.4, 0.4, 0.4], 0.5) == 104


def test_the_committed_price_carries_every_replicate():
    report = json.loads((REPOSITORY / "results/sample-size.json").read_text(encoding="utf-8"))
    distribution = report["tasks_needed_by_replicate"]
    for effect, cell in distribution.items():
        assert len(cell["replicates"]) == report["replicates"], effect
        reached = [r["tasks_needed"] for r in cell["replicates"] if r["tasks_needed"] is not None]
        assert cell["unreachable"] == report["replicates"] - len(reached)
        assert cell["range"] == ([min(reached), max(reached)] if reached else None)
