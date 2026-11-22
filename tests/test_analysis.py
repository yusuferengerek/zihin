"""Tests for the pre-registered analysis, against data whose answer is known.

The point of a synthetic dataset here is not coverage but arithmetic: every number
below can be computed by hand, so a test failing means the analysis changed, not
that the data moved. A.3's censoring rule and A.4's subtraction are the two places
where an off-by-one would silently change a headline number, so both are pinned to
exact values rather than to inequalities.
"""

import importlib.util
import pathlib
import sys

import pytest

# The production module is loaded, not reimplemented: a measurement that
# reimplements what it measures produces two right answers (setup protocol §6).
SPEC = importlib.util.spec_from_file_location(
    "analyze_pilot", pathlib.Path(__file__).resolve().parents[1] / "scripts/analyze_pilot.py"
)
analysis = importlib.util.module_from_spec(SPEC)
# Registered before execution: `@dataclass` looks its own module up in
# `sys.modules`, and a module loaded by path is not there unless it is put there.
# Without this the class body raises, and the failure points at dataclasses
# rather than at the loading.
sys.modules[SPEC.name] = analysis
SPEC.loader.exec_module(analysis)


def test_a_censored_episode_contributes_the_ceiling_not_its_step_count():
    censored = analysis.Episode("t", "skills", 7, 20, False, 0, False)
    assert analysis.restricted(censored, 1.0) == 20.0
    passed = analysis.Episode("t", "skills", 7, 20, True, 0, False)
    assert analysis.restricted(passed, 1.0) == 7.0


def test_censoring_follows_the_verdict_not_the_termination_reason():
    """K-53: an episode the agent reported as finished can still be censored."""
    finished_but_failed = analysis.Episode("t", "skills", 9, 20, False, 0, hit_ceiling=False)
    assert finished_but_failed.censored
    hit_ceiling_but_passed = analysis.Episode("t", "skills", 20, 20, True, 0, hit_ceiling=True)
    assert not hit_ceiling_but_passed.censored


def test_the_restricted_mean_difference_is_the_hand_computed_value():
    episodes = analysis.synthetic()
    differences = [d for _, d in analysis.paired(episodes, "skills", analysis.BASELINE, 1.0)]
    # Five easy tasks: 12 − 20 = −8. Five hard tasks: both censored at 20, so 0.
    assert sorted(differences) == [-8.0] * 5 + [0.0] * 5
    assert sum(differences) / len(differences) == -4.0


def test_the_subtractive_control_removes_the_volume_arm():
    episodes = analysis.synthetic()
    effect = [d for _, d in analysis.subtractive_effect(episodes, "skills", 1.0)]
    # Easy: (12−20) − (16−20) = −4. Hard: 0 − 0 = 0.
    assert sorted(effect) == [-4.0] * 5 + [0.0] * 5
    assert sum(effect) / len(effect) == -2.0


def test_the_sensitivity_multiplier_moves_the_censored_cells_only():
    episodes = analysis.synthetic()
    at_one = [d for _, d in analysis.paired(episodes, "skills", analysis.BASELINE, 1.0)]
    at_two = [d for _, d in analysis.paired(episodes, "skills", analysis.BASELINE, 2.0)]
    # The censored pairs move together, so their difference stays zero either way.
    assert sorted(at_one) == sorted(at_two)


def test_the_uncensored_subset_drops_a_task_if_either_arm_is_censored():
    episodes = analysis.synthetic()
    uncensored = analysis.uncensored_differences(episodes, "skills", analysis.BASELINE, 1.0)
    assert uncensored == [-8.0] * 5


def test_the_bootstrap_is_reproducible_and_brackets_the_mean():
    values = [d for _, d in analysis.paired(analysis.synthetic(), "skills", analysis.BASELINE, 1.0)]
    first = analysis.bootstrap_ci(values, seed=7, iterations=400)
    assert first == analysis.bootstrap_ci(values, seed=7, iterations=400)
    assert first[0] <= -4.0 <= first[1]


def test_the_seed_moves_the_interval_when_the_data_has_spread():
    """On the synthetic set the endpoints coincide across seeds, and that is the
    data's property rather than the code's: two distinct values put every
    resampled mean on a coarse grid. The claim being tested is that the seed
    reaches the interval at all, so it needs data with spread."""
    spread = [float(v) for v in range(1, 21)]
    assert analysis.bootstrap_ci(spread, seed=7, iterations=400) != analysis.bootstrap_ci(
        spread, seed=8, iterations=400
    )


def test_the_two_rates_are_computed_separately():
    """A.3 forbids conflating them, so they are asserted to differ where they do."""
    measured = analysis.rates(analysis.synthetic(), analysis.BASELINE)
    assert measured["ceiling_hit_rate"] == 0.5
    assert measured["censoring_rate"] == 0.5
    # Same value here by construction; the test that matters is that a passing
    # episode which hit the ceiling moves one and not the other.
    episodes = [
        analysis.Episode("a", analysis.BASELINE, 20, 20, True, 1, hit_ceiling=True),
        analysis.Episode("b", analysis.BASELINE, 5, 20, False, 1, hit_ceiling=False),
    ]
    split = analysis.rates(episodes, analysis.BASELINE)
    assert split["ceiling_hit_rate"] == 0.5
    assert split["censoring_rate"] == 0.5
    only_ceiling = [analysis.Episode("a", analysis.BASELINE, 20, 20, True, 1, hit_ceiling=True)]
    assert analysis.rates(only_ceiling, analysis.BASELINE)["ceiling_hit_rate"] == 1.0
    assert analysis.rates(only_ceiling, analysis.BASELINE)["censoring_rate"] == 0.0


def test_gate_one_fires_when_the_difference_is_not_negative():
    flat = [
        analysis.Episode("t", analysis.BASELINE, 10, 20, True, 1, False),
        analysis.Episode("t", "skills", 10, 20, True, 1, False),
    ]
    verdicts = analysis.gates(flat, "skills", 1.0, coverage=1.0)
    assert verdicts[0]["verdict"] == "hypothesis not supported"


def test_gate_three_fires_below_the_coverage_threshold():
    verdicts = analysis.gates(analysis.synthetic(), "skills", 1.0, coverage=0.2)
    assert verdicts[2]["verdict"].startswith("the symbolic retriever")
    held = analysis.gates(analysis.synthetic(), "skills", 1.0, coverage=0.3)
    assert held[2]["verdict"] == "not triggered"


def test_the_signed_rank_needs_a_sample_and_reports_nan_below_it():
    assert analysis.signed_rank([1.0, -1.0])[1] != analysis.signed_rank([1.0, -1.0])[1]


def test_the_signed_rank_finds_a_one_sided_shift():
    statistic, p = analysis.signed_rank([-3.0, -4.0, -2.0, -5.0, -1.0, -6.0, -7.0])
    assert statistic == 0.0
    assert p < 0.05


@pytest.mark.parametrize("missing", ["bootstrap_seed", "bootstrap_iterations"])
def test_the_config_has_no_silent_default(missing, tmp_path, monkeypatch):
    """S-30's rule: a parameter that affects a reported number cannot default."""
    lines = [
        line for line in ["bootstrap_seed: 1", "bootstrap_iterations: 10"] if missing not in line
    ]
    config = tmp_path / "analysis.yaml"
    config.write_text("\n".join(lines), encoding="utf-8")
    monkeypatch.setattr(analysis, "CONFIG", config)
    with pytest.raises(SystemExit):
        analysis.load_config()
