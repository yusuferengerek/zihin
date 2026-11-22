"""The pass-rate threshold, derived from the preregistration instead of chosen.

**The logic.** The interval table answered "how wide". "How wide is acceptable"
needs a reference, and the reference is already written down: every declaration
that tells two results apart carries an implicit width requirement. The
memorisation gate says the unseen gain must stay above half the seen gain, so
telling "half" from "none" needs an interval narrower than half the gain. Each
declaration is read that way and the threshold is the largest of them.

**Every requirement reduces to one measured quantity.** Write `w` for the width
of the primary estimate's interval and `d` for the primary effect. A declaration
about a *derived* quantity — a subgroup, a difference of two differences, a
single arm — needs the width of that quantity, and its ratio to `w` is a
structural fact of the sample, not of the effect size. Those ratios are measured
here. What is left is a requirement on `w/|d|`, and that is measured here too, on
the action stratum. It is not read from `results/interval-width.json`: that sweep
was written before the stratification (K-144) and runs on the whole evaluation
sample, both strata together, so its widths are about a different sample.

**Three parameters are declared, not measured, and they are named.** The
preregistration does not say how large the volume effect is relative to the
mechanism effect, nor how much of the combined effect a single arm carries, nor
how far apart two axis points must be to call a shape falling. Nothing in the
record supplies them. They are swept over a conservative and a lenient value and
both rows are reported; the derivation's dependence on them is part of the
answer, not a hidden step.

**Three outcomes were written before the run.** All distinctions become readable
at one rate, and the threshold is that rate. Or some become readable at no rate,
and those are claims the design cannot carry — a finding, not a defect. Or the
derived threshold lands above 0.367, and then 32B does not qualify either and the
experiment is underpowered as designed.

**S-66 rides on every row.** The noise coefficient behind the widths was measured
on two repeated cells, so every width is a lower bound and every derived
threshold is on the optimistic side.

Usage:

    uv run python scripts/setup/derive_pass_threshold.py
    uv run python scripts/setup/derive_pass_threshold.py --replicates 8
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import random
import sqlite3
import statistics
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from appworld.task import load_task_ids  # noqa: E402

from zihin.touched import TouchedListError, load_touched  # noqa: E402

OUTPUT = REPOSITORY / "results/pass-threshold.json"
TYPES = REPOSITORY / "results/task-types.json"
TASKS = REPOSITORY / "data/tasks"

MULTIPLIER, FLOOR, CAP = 2, 20, 150
NOISE_CV = 0.075

RATES = (0.10, 0.15, 0.20, 0.25, 0.30, 0.37, 0.45, 0.55, 0.65, 0.75, 0.85)
EFFECTS = (0.10, 0.20, 0.30, 0.50)

# Declared, not measured. Named so the derivation's dependence on them is visible.
SHAPES = {
    "conservative": {
        # The irrelevant arm's gain as a share of the mechanism's.
        "volume_share": 0.25,
        # A single mechanism arm's gain as a share of the combined arm's. K-84's
        # mirror finding argues the two arms target the same failure, so the
        # combined gain may be no larger than either — that is the lenient side.
        "single_share": 0.50,
        # How far two axis points' effects must differ before a shape is a shape.
        "axis_gap": 0.50,
    },
    "lenient": {"volume_share": 0.50, "single_share": 1.00, "axis_gap": 1.00},
}


def measured_pass_rate() -> dict | None:
    """The 32B run's pass rate, split by stratum.

    The headline 11/30 mixes the two strata, and the answer stratum is the one
    where a do-nothing agent collects a free test (K-144). The primary sample is
    the action stratum, so that is the rate the threshold is compared against.
    """
    scan_path = REPOSITORY / "results/b32c-taramasi.json"
    kinds_path = TYPES
    if not scan_path.exists() or not kinds_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(
        "analyze_passes", REPOSITORY / "scripts/analyze_passes.py"
    )
    passes = importlib.util.module_from_spec(spec)
    sys.modules["analyze_passes"] = passes
    spec.loader.exec_module(passes)

    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    episodes = scan.get("episodes_with_steps") or []
    if not episodes:
        return None
    action = [e for e in episodes if passes.task_shape(e["task"])["kind"] != "answer"]
    answer = [e for e in episodes if passes.task_shape(e["task"])["kind"] == "answer"]
    if not action:
        return None
    return {
        "scan": "results/b32c-taramasi.json",
        "attempted": len(action),
        "passed": sum(1 for e in action if e.get("passed")),
        "rate": sum(1 for e in action if e.get("passed")) / len(action),
        "answer_attempted": len(answer),
        "answer_passed": sum(1 for e in answer if e.get("passed")),
        "all_attempted": len(episodes),
        "all_passed": sum(1 for e in episodes if e.get("passed")),
        "all_rate": sum(1 for e in episodes if e.get("passed")) / len(episodes),
    }


def analysis():
    path = REPOSITORY / "scripts/analyze_pilot.py"
    spec = importlib.util.spec_from_file_location("analyze_pilot", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_pilot"] = module
    spec.loader.exec_module(module)
    return module


def action_stratum() -> list[tuple[str, int]]:
    """The primary sample after K-144: the action-type tasks and their anchors."""
    kinds = json.loads(TYPES.read_text(encoding="utf-8"))["per_task"]
    try:
        listed = load_touched()
    except TouchedListError as error:
        sys.exit(str(error))
    print(f"touched list: {listed.basis}")
    touched = set(listed.tasks("test_normal"))
    sample = []
    for task in load_task_ids("test_normal"):
        if task in touched or kinds.get(task, {}).get("kind") == "answer":
            continue
        metadata = TASKS / task / "ground_truth" / "metadata.json"
        if not metadata.exists() or task not in kinds:
            continue
        sample.append((task, int(json.loads(metadata.read_text())["num_api_calls"])))
    return sample


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


def one_run(module, sample, costs, rate, effect, volume_share, rng, seed, iterations):
    """One simulated design; returns the primary width, the effect, and two ratios."""
    episode_of = module.Episode
    solved = {task for task, _ in sample if rng.random() < rate}

    episodes = []
    for task, anchor in sample:
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
        episodes.append(
            episode_of(
                task,
                module.IRRELEVANT,
                cost(effect * volume_share) if passed else ceiling,
                ceiling,
                passed,
                0,
                not passed,
            )
        )

    primary = module.paired(episodes, "skills_failures", module.BASELINE, 1.0)
    values = [difference for _, difference in primary]
    mean = statistics.fmean(values)
    low, high = module.bootstrap_ci(values, seed, iterations)
    width = high - low

    # A subgroup: the memorisation gate splits the sample in two.
    half = len(primary) // 2
    subgroup = [difference for _, difference in primary[:half]]
    sub_low, sub_high = module.bootstrap_ci(subgroup, seed, iterations)

    # A difference of two paired differences: the subtractive control.
    volume = dict(module.paired(episodes, module.IRRELEVANT, module.BASELINE, 1.0))
    difference_of_differences = [value - volume[task] for task, value in primary if task in volume]
    dod_low, dod_high = module.bootstrap_ci(difference_of_differences, seed, iterations)

    return {
        "mean": mean,
        "width": width,
        "sub_width": sub_high - sub_low,
        "dod_width": dod_high - dod_low,
    }


def requirements(shape: dict, rho_sub: float, rho_dod: float) -> list[dict]:
    """Every declaration that tells two results apart, as a bound on w/|d|."""
    volume, single, gap = shape["volume_share"], shape["single_share"], shape["axis_gap"]
    return [
        {
            "id": "Y-1",
            "declaration": "the paired difference is distinguishable from zero",
            "distinction": "an effect against no effect",
            "bound": 2.0,
            "why": "an interval that excludes zero has half-width below the effect, "
            "so the width is below twice it",
        },
        {
            "id": "Y-2",
            "declaration": "unseen gain over seen gain, threshold one half",
            "distinction": "half the gain against none of it",
            "bound": 0.5 / rho_sub,
            "why": "the gate reads a subgroup, whose interval is wider by the measured ratio",
        },
        {
            "id": "Y-6.1",
            "declaration": "the irrelevant arm is distinguishable from baseline",
            "distinction": "a volume effect against none",
            "bound": 2.0 * volume,
            "why": "the volume effect is a declared share of the mechanism effect",
        },
        {
            "id": "Y-6.2",
            "declaration": "the irrelevant arm does not improve as much as the mechanism arm",
            "distinction": "content against volume",
            "bound": 2.0 * (1.0 - volume) / rho_dod,
            "why": "the content-minus-volume effect is (1 - share) of the mechanism effect, "
            "and the subtractive control's interval is wider by the measured ratio",
        },
        {
            "id": "Y-4/Y-5",
            "declaration": "a single mechanism arm shows an effect",
            "distinction": "one mechanism working against not working",
            "bound": 2.0 * single,
            "why": "a single arm carries a declared share of the combined effect",
        },
        {
            "id": "A.11",
            "declaration": "the axis is flat rather than falling",
            "distinction": "one shape against another",
            "bound": 2.0 * gap / math.sqrt(2),
            "why": "the two points differ by a declared share of the effect, and their "
            "difference comes from independent runs, so its interval widens by root two",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # Nine: the committed artefact was produced with nine, and the earlier default
    # of eight did not reproduce it - the command behind the number was never
    # written down (S-75).
    parser.add_argument("--replicates", type=int, default=9)
    options = parser.parse_args()

    module = analysis()
    seed, iterations = module.load_config()
    sample = action_stratum()
    costs = passing_costs()
    if len(sample) < 80 or len(costs) < 10:
        sys.exit(
            f"the action stratum has {len(sample)} tasks and there are {len(costs)} "
            "passing costs. This derivation declines rather than deriving a "
            "threshold from a sample it cannot calibrate."
        )
    rng = random.Random(seed)

    print(f"primary sample : {len(sample)} action-type tasks (K-144)")
    print(f"passing cost   : n={len(costs)}, median {statistics.median(costs)}")
    print(f"bootstrap      : seed {seed}, {iterations} iterations, {options.replicates} replicates")
    print()

    # --- the measured part: w/|d| by rate and effect, and the two structural ratios
    measured: dict[tuple[float, float], dict] = {}
    rho_subs, rho_dods = [], []
    print("measured widths")
    print(
        f"  {'rate':>5} {'effect':>7} {'|d|':>7} {'w':>7} {'w/|d|':>7} "
        f"{'w_sub/w':>8} {'w_dod/w':>8}"
    )
    for rate in RATES:
        for effect in EFFECTS:
            runs = [
                one_run(
                    module,
                    sample,
                    costs,
                    rate,
                    effect,
                    SHAPES["conservative"]["volume_share"],
                    rng,
                    seed + index,
                    iterations,
                )
                for index in range(options.replicates)
            ]
            mean = statistics.median([abs(r["mean"]) for r in runs])
            width = statistics.median([r["width"] for r in runs])
            rho_sub = statistics.median([r["sub_width"] / r["width"] for r in runs])
            rho_dod = statistics.median([r["dod_width"] / r["width"] for r in runs])
            rho_subs.append(rho_sub)
            rho_dods.append(rho_dod)
            measured[(rate, effect)] = {
                "effect_abs": mean,
                "width": width,
                "ratio": width / mean if mean else float("inf"),
                "rho_sub": rho_sub,
                "rho_dod": rho_dod,
            }
            print(
                f"  {rate:>5.2f} {effect:>7.2f} {mean:>7.2f} {width:>7.2f} "
                f"{width / mean if mean else float('inf'):>7.2f} "
                f"{rho_sub:>8.2f} {rho_dod:>8.2f}",
                flush=True,
            )

    rho_sub = statistics.median(rho_subs)
    rho_dod = statistics.median(rho_dods)
    print()
    print(
        f"structural ratios, median over the grid: subgroup {rho_sub:.2f}x, "
        f"subtractive {rho_dod:.2f}x the primary width"
    )

    report = {
        "what": "the pass-rate threshold derived from the preregistration's own distinctions",
        "primary_sample": len(sample),
        "stratum": "action-type tasks only (K-144)",
        "bootstrap_seed": seed,
        "bootstrap_iterations": iterations,
        "replicates": options.replicates,
        "noise_cv": NOISE_CV,
        "limitation": "S-66: the noise coefficient was measured on two cells, so every "
        "width here is a lower bound and every derived threshold is optimistic",
        "structural_ratios": {"subgroup": rho_sub, "subtractive": rho_dod},
        "measured": [
            {
                "pass_rate": rate,
                "effect": effect,
                **{k: (None if v == float("inf") else round(v, 4)) for k, v in value.items()},
            }
            for (rate, effect), value in measured.items()
        ],
        "shapes": SHAPES,
        "derivation": {},
    }

    for label, shape in SHAPES.items():
        needed = requirements(shape, rho_sub, rho_dod)
        print()
        print(f"=== requirements, {label} shape parameters ===")
        print(f"  {'id':<9} {'needs w/|d| <':>14}  distinction")
        for item in needed:
            print(f"  {item['id']:<9} {item['bound']:>14.2f}  {item['distinction']}")

        print()
        print(f"  smallest pass rate at which each becomes readable, {label}")
        header = "  " + "id".ljust(9) + "".join(f"{e:>9.2f}" for e in EFFECTS)
        print(header + "   (effect size)")
        rows = []
        for item in needed:
            cells = []
            for effect in EFFECTS:
                first = None
                for position, rate in enumerate(RATES):
                    if all(
                        measured[(higher, effect)]["ratio"] <= item["bound"]
                        for higher in RATES[position:]
                    ):
                        first = rate
                        break
                cells.append(first)
            readable = dict(zip([str(e) for e in EFFECTS], cells, strict=True))
            rows.append({**item, "readable_at": readable})
            print(
                "  "
                + item["id"].ljust(9)
                + "".join((f"{c:>9.2f}" if c is not None else f"{'never':>9}") for c in cells)
            )

        threshold = {}
        for effect in EFFECTS:
            cells = [row["readable_at"][str(effect)] for row in rows]
            threshold[str(effect)] = None if any(c is None for c in cells) else max(cells)
        print(
            "  "
            + "THRESHOLD".ljust(9)
            + "".join(
                (f"{threshold[str(e)]:>9.2f}" if threshold[str(e)] is not None else f"{'-':>9}")
                for e in EFFECTS
            )
        )
        report["derivation"][label] = {"requirements": rows, "threshold": threshold}

    # --- the verdict: the derived threshold against the rate that was measured
    observed = measured_pass_rate()
    report["observed"] = observed
    if observed:
        print()
        print("the rate that was measured, on the primary stratum")
        print(
            f"  {observed['scan']}: {observed['passed']}/{observed['attempted']} "
            f"= {observed['rate']:.3f} on action-type tasks"
        )
        print(
            f"  (the whole set, both strata, was {observed['all_passed']}/"
            f"{observed['all_attempted']} = {observed['all_rate']:.3f}; the answer "
            f"stratum passes {observed['answer_passed']}/{observed['answer_attempted']})"
        )
        print()
        print("  verdict, per expected effect size")
        for effect in EFFECTS:
            verdicts = []
            for label in SHAPES:
                threshold = report["derivation"][label]["threshold"][str(effect)]
                if threshold is None:
                    verdicts.append(f"{label}: no rate carries every distinction")
                elif observed["rate"] >= threshold:
                    verdicts.append(
                        f"{label}: {threshold:.2f} <= {observed['rate']:.3f}, qualifies"
                    )
                else:
                    verdicts.append(
                        f"{label}: {threshold:.2f} > {observed['rate']:.3f}, does NOT qualify"
                    )
            print(f"    effect {effect:.2f}  " + "   ".join(verdicts))

    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
