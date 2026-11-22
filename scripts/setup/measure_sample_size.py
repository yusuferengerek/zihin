"""How many action tasks bring the memorisation gate into range at the rate we have.

**The question.** The derived threshold (K-146) asks for a pass rate of 0.75-0.85
and the action stratum measures 0.280. Raising the rate is one way to close that
gap; enlarging the sample is another, and this prices it. The binding requirement
is the memorisation gate: it reads half the sample, and telling "half the gain was
kept" from "none of it was" needs that half's interval narrower than half the
effect.

**Everything is held fixed except the sample.** The pass rate stays at the
rate `results/pass-threshold.json` measured on the action stratum, the ceiling
rule stays, the cost of a solved episode is resampled
from the record, and the estimator is imported from `scripts/analyze_pilot.py`.
Only the number of tasks moves, so the curve is the curve of sample size and
nothing else.

**Anchors come from real tasks, not from a distribution.** Up to the tasks the
evaluation stratum already has, the anchors are those tasks'. Beyond that they
come from the action-type tasks of the other splits, in the order a real expansion
would take them, because "grow the sample" means taking those tasks and no others.

**Nothing here is a copy of another measurement's number.** The pass rate is
read from `results/pass-threshold.json`, the current sample is the pool's
`test_normal` share, and the largest size is the pool. All three were literals
once - 0.280, 105 and 623 - and when the touched list grew by four tasks the
script refused to run rather than notice (K-167).

**A price is a distribution, not a point.** The headline is the smallest size at
which the *median* of the replicates falls under the bound. Shifting the bootstrap
seed by one moved that headline from 500 to 623, 400 and unreachable, so every
replicate's own answer is recorded beside it, with the seed it ran on (K-168).

**What it does not decide.** Whether to take them. Enlarging the sample means
changing the definition of the held-out set, and the splits it would draw from are
named here so the cost is visible.

Usage:

    uv run python scripts/setup/measure_sample_size.py
    uv run python scripts/setup/measure_sample_size.py --replicates 5
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

from appworld.task import load_task_ids  # noqa: E402

from zihin.touched import TouchedListError, load_touched  # noqa: E402

OUTPUT = REPOSITORY / "results/sample-size.json"
TASKS = REPOSITORY / "data/tasks"

MULTIPLIER, FLOOR, CAP = 2, 20, 150
NOISE_CV = 0.075
# Where the action stratum's measured pass rate is read from.
THRESHOLD = REPOSITORY / "results/pass-threshold.json"
# The memorisation gate reads half the sample and needs that half's interval
# narrower than half the effect (Y-2, as read in K-146).
GATE_BOUND = 0.5
# The sizes between the current sample and the whole pool. The ends are not here:
# they are the sample and the pool themselves (`sizes_for`).
GRID = (130, 160, 200, 250, 300, 400, 500)
EFFECTS = (0.10, 0.20, 0.30, 0.50)
# The order a real expansion would take tasks in: the evaluation split first, then
# the splits that are not the accumulation pool, then the pool.
EXPANSION_ORDER = ("test_normal", "test_challenge", "dev", "train")


def analysis():
    path = REPOSITORY / "scripts/analyze_pilot.py"
    spec = importlib.util.spec_from_file_location("analyze_pilot", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_pilot"] = module
    spec.loader.exec_module(module)
    return module


def shape():
    path = REPOSITORY / "scripts/analyze_passes.py"
    spec = importlib.util.spec_from_file_location("analyze_passes", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_passes"] = module
    spec.loader.exec_module(module)
    return module.task_shape


def action_pool() -> list[tuple[str, str, int]]:
    """Every action-type task not touched by setup, in expansion order."""
    task_shape = shape()
    try:
        listed = load_touched()
    except TouchedListError as error:
        sys.exit(str(error))
    print(f"touched list: {listed.basis}")
    pool = []
    for split in EXPANSION_ORDER:
        skip = set(listed.tasks(split))
        for task in load_task_ids(split):
            if task in skip:
                continue
            metadata = TASKS / task / "ground_truth" / "metadata.json"
            if not metadata.exists():
                continue
            if task_shape(task)["kind"] == "answer":
                continue
            pool.append((split, task, int(json.loads(metadata.read_text())["num_api_calls"])))
    return pool


def measured_pass_rate(path: pathlib.Path = THRESHOLD) -> float:
    """The action stratum's pass rate, as `derive_pass_threshold.py` recorded it."""
    if not path.exists():
        sys.exit(
            f"{path.name} is absent; the pass rate this measurement holds fixed is read from it"
        )
    return float(json.loads(path.read_text(encoding="utf-8"))["observed"]["rate"])


def sizes_for(pool: list[tuple[str, str, int]]) -> tuple[int, ...]:
    """The current sample, the grid points above it, and the whole pool."""
    current = sum(1 for split, _, _ in pool if split == EXPANSION_ORDER[0])
    inner = tuple(size for size in GRID if current < size < len(pool))
    return (current, *inner, len(pool))


def passing_costs() -> list[int]:
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


def replicate(module, sample, costs, effect, rng, seed, iterations, pass_rate):
    """One simulated experiment; returns the effect and the gate's own width."""
    episode_of = module.Episode
    solved = {task for _, task, _ in sample if rng.random() < pass_rate}
    episodes = []
    for _, task, anchor in sample:
        ceiling = ceiling_of(anchor)
        latent = rng.choice(costs)
        passed = task in solved

        def cost(reduction: float, ceiling: int = ceiling, latent: int = latent) -> int:
            return max(1, min(ceiling, round(latent * (1 - reduction) * rng.gauss(1.0, NOISE_CV))))

        episodes.append(
            episode_of(
                task,
                module.BASELINE,
                cost(0.0) if passed else ceiling,
                ceiling,
                passed,
                0,
                not passed,
            )
        )
        episodes.append(
            episode_of(
                task,
                "skills_failures",
                cost(effect) if passed else ceiling,
                ceiling,
                passed,
                0,
                not passed,
            )
        )

    paired = module.paired(episodes, "skills_failures", module.BASELINE, 1.0)
    values = [difference for _, difference in paired]
    mean = statistics.fmean(values)
    half = len(paired) // 2
    low, high = module.bootstrap_ci([d for _, d in paired[:half]], seed, iterations)
    return abs(mean), high - low


def first_size_under(sizes: list[int], ratios: list[float], bound: float) -> int | None:
    """The smallest size from which every larger size stays under the bound."""
    for position, size in enumerate(sizes):
        if all(ratio <= bound for ratio in ratios[position:]):
            return size
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=7)
    options = parser.parse_args()

    module = analysis()
    seed, iterations = module.load_config()
    pool = action_pool()
    costs = passing_costs()
    pass_rate = measured_pass_rate()
    sizes = sizes_for(pool)
    if not sizes[0] or len(costs) < 10:
        sys.exit(
            f"the pool holds {sizes[0]} evaluation tasks and the record {len(costs)} "
            "passing episodes; this measurement declines rather than simulating from "
            "nothing."
        )
    rng = random.Random(seed)

    by_split: dict[str, int] = {}
    anchors_by_split: dict[str, list[int]] = {}
    for split, _, anchor in pool:
        by_split[split] = by_split.get(split, 0) + 1
        anchors_by_split.setdefault(split, []).append(anchor)
    # Enlarging the sample does not only add precision: the splits it would draw
    # from have a different anchor distribution, so the ceiling distribution moves
    # and the population the estimand is about moves with it.
    profile = {
        split: {
            "tasks": len(values),
            "anchor_median": statistics.median(values),
            "anchor_mean": round(statistics.fmean(values), 1),
            "anchor_max": max(values),
            "share_at_or_above_75": round(sum(1 for v in values if v >= 75) / len(values), 4),
        }
        for split, values in anchors_by_split.items()
    }
    print(f"action-task pool: {len(pool)}  {by_split}")
    print(f"  {'split':<16} {'n':>5} {'median':>7} {'mean':>7} {'max':>6} {'>=75':>7}")
    for split, values in profile.items():
        print(
            f"  {split:<16} {values['tasks']:>5} {values['anchor_median']:>7.1f} "
            f"{values['anchor_mean']:>7.1f} {values['anchor_max']:>6} "
            f"{values['share_at_or_above_75']:>7.1%}"
        )
    print(
        f"pass rate held at {pass_rate}, gate needs the subgroup interval < "
        f"{GATE_BOUND} x the effect"
    )
    print()
    print(f"  {'n':>5} {'splits used':<34} " + "".join(f"{e:>9.2f}" for e in EFFECTS))
    rows = []
    # effect -> replicate -> the ratio at each size, in order
    trajectories = {effect: [[] for _ in range(options.replicates)] for effect in EFFECTS}
    for size in sizes:
        sample = pool[:size]
        used = {}
        for split, _, _ in sample:
            used[split] = used.get(split, 0) + 1
        cells = []
        for effect in EFFECTS:
            ratios = []
            for index in range(options.replicates):
                mean, width = replicate(
                    module, sample, costs, effect, rng, seed + index, iterations, pass_rate
                )
                ratio = width / mean if mean else float("inf")
                ratios.append(ratio)
                trajectories[effect][index].append(ratio)
            cells.append(round(statistics.median(ratios), 3))
        label = ", ".join(f"{k} {v}" for k, v in used.items())
        rows.append(
            {
                "tasks": size,
                "splits": used,
                "subgroup_width_over_effect": dict(
                    zip([str(e) for e in EFFECTS], cells, strict=True)
                ),
                "by_replicate": {
                    str(effect): [
                        round(trajectories[effect][r][-1], 3) for r in range(options.replicates)
                    ]
                    for effect in EFFECTS
                },
            }
        )
        print(f"  {size:>5} {label:<34} " + "".join(f"{c:>9.3f}" for c in cells), flush=True)

    print()
    print(f"  smallest n whose subgroup interval falls under {GATE_BOUND} x the effect")
    needed = {}
    for effect in EFFECTS:
        first = None
        for position, row in enumerate(rows):
            if all(
                later["subgroup_width_over_effect"][str(effect)] <= GATE_BOUND
                for later in rows[position:]
            ):
                first = row["tasks"]
                break
        needed[str(effect)] = first
        splits = next((r["splits"] for r in rows if r["tasks"] == first), None)
        print(
            f"    effect {effect:.2f}: "
            + (f"{first} tasks   {splits}" if first else "not reached within the pool")
        )

    print()
    print("  the same question asked of each replicate on its own")
    distribution = {}
    for effect in EFFECTS:
        answers = [
            {
                "replicate": index,
                "bootstrap_seed": seed + index,
                "tasks_needed": first_size_under(
                    list(sizes), trajectories[effect][index], GATE_BOUND
                ),
            }
            for index in range(options.replicates)
        ]
        reached = [a["tasks_needed"] for a in answers if a["tasks_needed"] is not None]
        distribution[str(effect)] = {
            "replicates": answers,
            "range": [min(reached), max(reached)] if reached else None,
            "unreachable": len(answers) - len(reached),
            "unreachable_seeds": [
                a["bootstrap_seed"] for a in answers if a["tasks_needed"] is None
            ],
            "reached_at_the_current_sample": sum(1 for n in reached if n == sizes[0]),
        }
        print(
            f"    effect {effect:.2f}: "
            + ", ".join(str(a["tasks_needed"] or "-") for a in answers)
            + f"   range {distribution[str(effect)]['range']}, "
            f"unreachable {distribution[str(effect)]['unreachable']}/{options.replicates}"
        )

    report = {
        "what": "how many action tasks bring the memorisation gate into range at the measured rate",
        "pass_rate": pass_rate,
        "pass_rate_from": "results/pass-threshold.json observed.rate",
        "gate_bound": GATE_BOUND,
        "gate": "Y-2 reads half the sample; that half's interval must be under half the effect",
        "pool": len(pool),
        "pool_by_split": by_split,
        "anchor_profile_by_split": profile,
        "what_changes_besides_precision": (
            "The added tasks come from test_challenge, whose action-task anchors are "
            "more dispersed with a far longer tail than test_normal's. Growing the "
            "sample therefore changes the population the estimand is about, not only "
            "the width of the interval around it."
        ),
        "expansion_order": list(EXPANSION_ORDER),
        "current_sample": sizes[0],
        "sizes": list(sizes),
        "bootstrap_seed": seed,
        "bootstrap_iterations": iterations,
        "replicates": options.replicates,
        "noise_cv": NOISE_CV,
        "limitation": "S-66: the noise coefficient came from two cells, so every width "
        "is a lower bound and every required size is optimistic",
        "curve": rows,
        "tasks_needed": needed,
        "tasks_needed_is": (
            "the smallest size at which the median over replicates stays under the bound"
        ),
        "tasks_needed_by_replicate": distribution,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
