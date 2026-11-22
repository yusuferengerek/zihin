"""At what pass rate does the primary estimate's interval stay narrow enough to read?

**The question, narrowly.** The primary estimand is the task-paired difference in
model calls, restricted to the ceiling, with unsolved episodes censored *at* the
ceiling. It uses every task, so it needs no paired subset — that requirement
belongs to Wilcoxon, which is the robustness check. What the pass rate governs is
not how many tasks enter, but how many of them carry a **non-zero** difference: a
task both arms fail contributes ceiling - ceiling = 0.

**Why simulate rather than reason.** The interval's width is driven by the spread
of the per-task differences, and that spread has two very different sources here,
both measured from the record:

- a task both arms solve differs by a few model calls (passing episodes cost 6-23
  calls, median 12);
- a task one arm solves and the other does not differs by the **ceiling minus
  those calls**, which is 20 to 150.

So one censoring flip moves the mean further than ten savings do, and no closed
form gives the width. Two grids are reported for that reason: one where the arms
solve the same tasks and the mechanism only spends fewer calls, one where the
mechanism converts failures.

**Which sample.** The action stratum (K-144): the primary sample, taken from
`derive_pass_threshold.py`'s `action_stratum` rather than written a second time.
The sweep was first run on the whole evaluation sample, both strata together, and
that table - `results/interval-width.json` - described a sample the primary
estimate is no longer read on. It is kept and marked superseded; this one is
`results/interval-width-action.json` (K-174).

**Calibrated, not invented.** Anchors come from the evaluation sample's own task
data; ceilings are the protocol's `max(20, min(150, 2 x anchor))`; the cost of a
solved episode is resampled from the passing episodes in the record; the
within-cell noise is the measured coefficient of variation.

**The analysis is imported, not re-implemented.** `bootstrap_ci`, `paired` and
`restricted` come from `scripts/analyze_pilot.py`, and the seed and iteration
count from `config/analysis.yaml`. A second copy of the estimator would make this
sweep an answer about an analysis nobody runs.

Usage:

    uv run python scripts/setup/measure_interval_width.py
    uv run python scripts/setup/measure_interval_width.py --replicates 5
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import random
import sqlite3
import statistics
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))


OUTPUT = REPOSITORY / "results/interval-width-action.json"
SUPERSEDED = "results/interval-width.json"
TASKS = REPOSITORY / "data/tasks"

# The protocol's ceiling rule (measure_band.py): twice the anchor, floored and capped.
MULTIPLIER, FLOOR, CAP = 2, 20, 150
# Measured on the repeated passing cells in the record. Those cells are few and the
# report says how few; it is still a measurement rather than a guess.
NOISE_CV = 0.075

PASS_RATES = (0.10, 0.20, 0.37, 0.50, 0.70)
SAVINGS = (0.10, 0.20, 0.30, 0.50)
FLIPS = (2, 5, 10, 20)


def analysis():
    path = REPOSITORY / "scripts/analyze_pilot.py"
    spec = importlib.util.spec_from_file_location("analyze_pilot", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_pilot"] = module
    spec.loader.exec_module(module)
    return module


def primary_stratum() -> list[tuple[str, int]]:
    """The action stratum and its anchors, from the threshold derivation's definition."""
    path = REPOSITORY / "scripts/setup/derive_pass_threshold.py"
    spec = importlib.util.spec_from_file_location("derive_pass_threshold", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["derive_pass_threshold"] = module
    spec.loader.exec_module(module)
    return module.action_stratum()


def passing_costs() -> list[int]:
    """What a solved episode costs, from every passing episode in the record."""
    costs = []
    for name in ("results/zihin-2.sqlite", "results/zihin-3.sqlite"):
        path = REPOSITORY / name
        if not path.exists():
            continue
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        costs += [
            row[0]
            for row in connection.execute(
                "SELECT e.total_model_calls FROM episodes e "
                "JOIN verifier_results v ON v.episode_id = e.episode_id "
                "WHERE v.passed = 1 AND e.total_model_calls IS NOT NULL"
            )
        ]
        connection.close()
    return costs


def ceiling_of(anchor: int) -> int:
    return max(FLOOR, min(CAP, MULTIPLIER * anchor))


def replicate(module, sample, costs, rate, saving, flips, rng, seed, iterations):
    """One simulated experiment, analysed by the real estimator."""
    episode_of = module.Episode
    solved = {task for task, _ in sample if rng.random() < rate}
    remaining = [task for task, _ in sample if task not in solved]
    rng.shuffle(remaining)
    converted = set(remaining[:flips])

    episodes = []
    for task, anchor in sample:
        ceiling = ceiling_of(anchor)
        latent = rng.choice(costs)
        base_calls = max(1, min(ceiling, round(latent * rng.gauss(1.0, NOISE_CV))))
        base_passed = task in solved
        episodes.append(
            episode_of(
                task,
                module.BASELINE,
                base_calls if base_passed else ceiling,
                ceiling,
                base_passed,
                0,
                not base_passed,
            )
        )
        arm_passed = base_passed or task in converted
        if arm_passed:
            target = base_calls if base_passed else max(1, min(ceiling, round(latent)))
            arm_calls = max(
                1, min(ceiling, round(target * (1 - saving) * rng.gauss(1.0, NOISE_CV)))
            )
        else:
            arm_calls = ceiling
        episodes.append(
            episode_of(task, "skills", arm_calls, ceiling, arm_passed, 0, not arm_passed)
        )

    differences = [d for _, d in module.paired(episodes, "skills", module.BASELINE, 1.0)]
    low, high = module.bootstrap_ci(differences, seed, iterations)
    return statistics.fmean(differences), low, high


def sweep(module, sample, costs, axis, values, replicates, seed, iterations, rng):
    rows = []
    for rate in PASS_RATES:
        for value in values:
            means, widths, excludes, readable = [], [], 0, 0
            for index in range(replicates):
                saving = value if axis == "saving" else 0.0
                flips = value if axis == "flips" else 0
                mean, low, high = replicate(
                    module, sample, costs, rate, saving, flips, rng, seed + index, iterations
                )
                means.append(mean)
                widths.append(high - low)
                if high < 0 or low > 0:
                    excludes += 1
                if mean != 0 and (high - low) < abs(mean):
                    readable += 1
            middle_mean = statistics.median(means)
            middle_width = statistics.median(widths)
            row = {
                "pass_rate": rate,
                axis: value,
                "true_mean": round(middle_mean, 2),
                "ci_width": round(middle_width, 2),
                "width_over_effect": (
                    round(middle_width / abs(middle_mean), 2) if middle_mean else None
                ),
                "excludes_zero": round(excludes / replicates, 2),
                "factor_of_two_readable": round(readable / replicates, 2),
            }
            rows.append(row)
            print(
                f"  {rate:>5.2f} {value:>7} {row['true_mean']:>9.2f} {row['ci_width']:>9.2f} "
                f"{str(row['width_over_effect']):>7} {row['excludes_zero']:>8.2f} "
                f"{row['factor_of_two_readable']:>9.2f}",
                flush=True,
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=12)
    options = parser.parse_args()

    module = analysis()
    seed, iterations = module.load_config()
    sample = primary_stratum()
    costs = passing_costs()
    if len(sample) < 100 or len(costs) < 10:
        sys.exit(
            f"the sample has {len(sample)} tasks and {len(costs)} passing costs. "
            "This sweep declines rather than reporting widths off a corpus it "
            "cannot calibrate against."
        )
    ceilings = [ceiling_of(a) for _, a in sample]
    rng = random.Random(seed)

    print(
        f"evaluation sample : {len(sample)} tasks, ceilings {min(ceilings)}-{max(ceilings)} "
        f"(median {statistics.median(ceilings):.0f})"
    )
    print(
        f"passing cost      : n={len(costs)}, median {statistics.median(costs)}, "
        f"mean {statistics.fmean(costs):.1f}"
    )
    print(
        f"bootstrap         : seed {seed}, {iterations} iterations, "
        f"{options.replicates} replicates per cell"
    )
    print()

    header = (
        f"  {'rate':>5} {'effect':>7} {'true d':>9} {'CI width':>9} "
        f"{'w/|d|':>7} {'excl 0':>8} {'2x read':>9}"
    )
    print("A. the arms solve the same tasks; the mechanism spends fewer calls")
    print(header)
    saving_rows = sweep(
        module, sample, costs, "saving", SAVINGS, options.replicates, seed, iterations, rng
    )
    print()
    print("B. the mechanism converts failures (extra tasks solved, out of the sample)")
    print(header)
    flip_rows = sweep(
        module, sample, costs, "flips", FLIPS, options.replicates, seed, iterations, rng
    )

    report = {
        "what": "the width of the primary estimate's bootstrap interval, by pass rate and effect",
        "sample": "the action stratum (K-144), the primary sample",
        "evaluation_tasks": len(sample),
        "supersedes": SUPERSEDED,
        "ceiling_rule": {"multiplier": MULTIPLIER, "floor": FLOOR, "cap": CAP},
        "passing_cost_observations": len(costs),
        "passing_cost_median": statistics.median(costs),
        "noise_cv": NOISE_CV,
        "bootstrap_seed": seed,
        "bootstrap_iterations": iterations,
        "replicates": options.replicates,
        "grid_saving": saving_rows,
        "grid_flips": flip_rows,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
