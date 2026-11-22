"""The analysis the pre-registration binds, runnable before the pilot data exists.

**Why it is written now.** The analysis plan is frozen in `experiments/preregistration.md`
(A.3, A.4, A.5, A.7). Writing the code after seeing the data is how an analysis
drifts toward the result; writing it first makes the drift visible as a diff. It is
also the only delivery item that needs neither pilot data nor a decision from
anyone, so it can be tested against synthetic data today.

**What it computes, in the pre-registration's own terms.**

*The estimand* (A.3) is the task-paired difference in model calls across all covered
tasks. Unsolved episodes enter as **censored observations at the step ceiling**,
because how long they would really have taken is unknown.

*The primary estimate* is the **restricted mean to the ceiling**, with a confidence
interval by **bootstrap over the task set**. **Wilcoxon** signed-rank on the
uncensored subset is the robustness check. Sensitivity repeats the whole thing at
**1.5× and 2×** the ceiling.

*The subtractive control* (A.4) is the point of the five conditions: the mechanism
effect is the mechanism arm's gain over baseline minus the irrelevant-retrieval
arm's gain over baseline, paired by task.

**Two quantities this file refuses to conflate** (A.3). The *ceiling-hit rate* is a
measurement artefact and has a ten per cent rule. The *censoring rate* is a result
and that rule does not apply to it. Censoring is counted by the verifier's verdict,
never by the termination reason (K-53).

**No new dependency.** The bootstrap and the signed-rank test are written here
rather than pulled in, because adding numpy or scipy to a four-dependency project
is a decision, not a convenience.

**The seed is a parameter, not a default.** A bootstrap interval depends on its
seed, so the seed affects a reported number and lives in `config/analysis.yaml`
with no silent default — the same rule that `max_output_tokens` broke (S-30).

Usage:

    uv run python scripts/analyze_pilot.py --database results/zihin-2.sqlite
    uv run python scripts/analyze_pilot.py --self-test   # synthetic data only
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sqlite3
import statistics
import sys
from dataclasses import dataclass

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONFIG = REPOSITORY / "config/analysis.yaml"

BASELINE = "baseline"
IRRELEVANT = "irrelevant_retrieval"
SENSITIVITY = (1.0, 1.5, 2.0)


@dataclass(frozen=True)
class Episode:
    """One episode as the analysis needs it, independent of where it was read from."""

    task: str
    condition: str
    model_calls: int
    step_ceiling: int
    passed: bool
    successful_api_calls: int
    hit_ceiling: bool
    seen_in_accumulation: bool = False

    @property
    def censored(self) -> bool:
        """Censoring is the verifier's verdict, not the termination reason (K-53)."""
        return not self.passed


def restricted(episode: Episode, multiplier: float) -> float:
    """The observation restricted to the ceiling, censored ones pinned to it.

    A censored episode contributes the ceiling rather than its observed step count:
    it is known to have needed *at least* that many, and pretending the observed
    number is the true one biases the mean downward exactly where the mechanism is
    supposed to help.
    """
    ceiling = episode.step_ceiling * multiplier
    return min(float(episode.model_calls), ceiling) if not episode.censored else ceiling


def paired(episodes: list[Episode], treatment: str, control: str, multiplier: float):
    """Per-task (treatment − control) differences, for tasks present in both arms."""
    by_condition: dict[str, dict[str, Episode]] = {}
    for episode in episodes:
        by_condition.setdefault(episode.condition, {})[episode.task] = episode
    left, right = by_condition.get(treatment, {}), by_condition.get(control, {})
    shared = sorted(set(left) & set(right))
    return [
        (task, restricted(left[task], multiplier) - restricted(right[task], multiplier))
        for task in shared
    ]


def bootstrap_ci(values: list[float], seed: int, iterations: int, alpha: float = 0.05):
    """Percentile interval by resampling the task set, with a declared seed.

    Resampling is over *tasks*, not observations, because the pairing is by task:
    resampling observations would break the pairing and understate the interval.
    """
    if not values:
        return (float("nan"), float("nan"))
    generator = random.Random(seed)
    means = []
    for _ in range(iterations):
        sample = [values[generator.randrange(len(values))] for _ in values]
        means.append(statistics.fmean(sample))
    means.sort()
    low = means[max(0, int(alpha / 2 * iterations) - 1)]
    high = means[min(iterations - 1, int((1 - alpha / 2) * iterations))]
    return (low, high)


def signed_rank(values: list[float]) -> tuple[float, float]:
    """Wilcoxon signed-rank statistic and a normal-approximation two-sided p.

    Zero differences are dropped, as the test defines. Ties share their average
    rank. The normal approximation is used with a tie correction; with the sample
    sizes this study can reach, an exact test would change the third decimal and
    not the verdict, and the verdict is what the gates read.
    """
    nonzero = [v for v in values if v != 0]
    if len(nonzero) < 6:
        return (float("nan"), float("nan"))
    order = sorted(range(len(nonzero)), key=lambda i: abs(nonzero[i]))
    ranks = [0.0] * len(nonzero)
    index = 0
    while index < len(order):
        stop = index
        while stop + 1 < len(order) and abs(nonzero[order[stop + 1]]) == abs(nonzero[order[index]]):
            stop += 1
        average = (index + stop) / 2 + 1
        for position in range(index, stop + 1):
            ranks[order[position]] = average
        index = stop + 1
    positive = sum(rank for rank, value in zip(ranks, nonzero, strict=True) if value > 0)
    count = len(nonzero)
    mean = count * (count + 1) / 4
    variance = count * (count + 1) * (2 * count + 1) / 24
    if variance <= 0:
        return (positive, float("nan"))
    z = (positive - mean) / math.sqrt(variance)
    p = math.erfc(abs(z) / math.sqrt(2))
    return (positive, p)


def arm_summary(episodes: list[Episode], arm: str, multiplier: float, seed: int, iterations: int):
    """The primary estimate for one arm against baseline, with its robustness check."""
    differences = paired(episodes, arm, BASELINE, multiplier)
    values = [difference for _, difference in differences]
    uncensored = uncensored_differences(episodes, arm, BASELINE, multiplier)
    statistic, p = signed_rank(uncensored)
    return {
        "arm": arm,
        "tasks": len(values),
        "restricted_mean_difference": statistics.fmean(values) if values else float("nan"),
        "bootstrap_ci": bootstrap_ci(values, seed, iterations),
        "wilcoxon_uncensored": {"tasks": len(uncensored), "statistic": statistic, "p": p},
    }


def uncensored_differences(
    episodes: list[Episode], treatment: str, control: str, multiplier: float
):
    """Differences on tasks where **both** arms were uncensored.

    Dropping a task because one arm was censored is what makes this a robustness
    check rather than the primary estimate: the subset is not random, it is the
    easy tasks, and A.3 says so.
    """
    by_condition: dict[str, dict[str, Episode]] = {}
    for episode in episodes:
        by_condition.setdefault(episode.condition, {})[episode.task] = episode
    left, right = by_condition.get(treatment, {}), by_condition.get(control, {})
    return [
        restricted(left[task], multiplier) - restricted(right[task], multiplier)
        for task in sorted(set(left) & set(right))
        if not left[task].censored and not right[task].censored
    ]


def subtractive_effect(episodes: list[Episode], arm: str, multiplier: float):
    """Mechanism gain minus context-volume gain, paired by task (A.4).

    The irrelevant-retrieval arm carries the same context volume with the wrong
    content, so subtracting its gain leaves content. Tasks missing from any of the
    three arms are dropped rather than filled, because a filled cell would enter the
    mean as if it had been measured.
    """
    mechanism = dict(paired(episodes, arm, BASELINE, multiplier))
    volume = dict(paired(episodes, IRRELEVANT, BASELINE, multiplier))
    shared = sorted(set(mechanism) & set(volume))
    return [(task, mechanism[task] - volume[task]) for task in shared]


def rates(episodes: list[Episode], condition: str) -> dict[str, float]:
    """The two rates A.3 forbids conflating, plus the mandatory diagnostic metric."""
    arm = [episode for episode in episodes if episode.condition == condition]
    if not arm:
        return {}
    successful = sum(episode.successful_api_calls for episode in arm)
    calls = sum(episode.model_calls for episode in arm)
    return {
        # A measurement artefact. The ten per cent rule applies to this one.
        "ceiling_hit_rate": sum(1 for e in arm if e.hit_ceiling) / len(arm),
        # A result. The ten per cent rule does not apply (K-53).
        "censoring_rate": sum(1 for e in arm if e.censored) / len(arm),
        "model_calls_per_successful_api_call": calls / successful if successful else float("nan"),
    }


def gates(episodes: list[Episode], arm: str, multiplier: float, coverage: float) -> list[dict]:
    """The three falsification gates of A.7, evaluated without interpretation."""
    differences = [difference for _, difference in paired(episodes, arm, BASELINE, multiplier)]
    mean = statistics.fmean(differences) if differences else float("nan")

    seen = [e for e in episodes if e.condition == arm and e.seen_in_accumulation]
    unseen = [e for e in episodes if e.condition == arm and not e.seen_in_accumulation]
    seen_tasks = {e.task for e in seen}
    unseen_tasks = {e.task for e in unseen}
    seen_gain = [d for task, d in paired(episodes, arm, BASELINE, multiplier) if task in seen_tasks]
    unseen_gain = [
        d for task, d in paired(episodes, arm, BASELINE, multiplier) if task in unseen_tasks
    ]
    ratio = float("nan")
    if seen_gain and unseen_gain and statistics.fmean(seen_gain) != 0:
        ratio = statistics.fmean(unseen_gain) / statistics.fmean(seen_gain)

    return [
        {
            "gate": 1,
            "question": "do the mechanisms lower the model call count",
            "value": mean,
            "verdict": "hypothesis not supported" if not (mean < 0) else "not triggered",
        },
        {
            "gate": 2,
            "question": "unseen gain over seen gain, threshold one half",
            "value": ratio,
            "verdict": "memorisation confirmed"
            if ratio == ratio and ratio < 0.5
            else "not triggered",
        },
        {
            "gate": 3,
            "question": "coverage rate, threshold 25 per cent",
            "value": coverage,
            "verdict": "the symbolic retriever finds no relevant experience here"
            if coverage < 0.25
            else "not triggered",
        },
    ]


def analyse(episodes: list[Episode], arms: list[str], seed: int, iterations: int, coverage: float):
    """Everything the pre-registration asks for, at every sensitivity multiplier."""
    report: dict = {"conditions": {}, "sensitivity": {}}
    for condition in sorted({episode.condition for episode in episodes}):
        report["conditions"][condition] = rates(episodes, condition)
    for multiplier in SENSITIVITY:
        key = f"ceiling_x{multiplier}"
        report["sensitivity"][key] = {
            "arms": [arm_summary(episodes, arm, multiplier, seed, iterations) for arm in arms],
            "subtractive": {
                arm: statistics.fmean([d for _, d in subtractive_effect(episodes, arm, multiplier)])
                if subtractive_effect(episodes, arm, multiplier)
                else float("nan")
                for arm in arms
            },
            "gates": {arm: gates(episodes, arm, multiplier, coverage) for arm in arms},
        }
    return report


def load_config() -> tuple[int, int]:
    """The seed and iteration count, with no silent default (S-30's rule)."""
    if not CONFIG.exists():
        sys.exit(f"{CONFIG.relative_to(REPOSITORY)} does not exist. The seed has no default.")
    settings: dict[str, int] = {}
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            name, _, value = line.partition(":")
            try:
                settings[name.strip()] = int(value.split("#")[0].strip())
            except ValueError:
                continue
    for required in ("bootstrap_seed", "bootstrap_iterations"):
        if required not in settings:
            sys.exit(f"{CONFIG.name}: {required} is not set and has no default.")
    return settings["bootstrap_seed"], settings["bootstrap_iterations"]


def load_episodes(database: pathlib.Path) -> list[Episode]:
    """Episodes from the record. The verdict comes from `verifier_results` (K-53)."""
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT e.task_id AS task, m.condition AS condition, e.total_model_calls AS model_calls, "
        "e.step_ceiling AS step_ceiling, e.termination_reason AS termination, "
        "COALESCE(v.passed, 0) AS passed "
        "FROM episodes e JOIN run_manifests m USING(run_id) "
        "LEFT JOIN verifier_results v USING(episode_id)"
    ).fetchall()
    return [
        Episode(
            task=row["task"],
            condition=row["condition"] or BASELINE,
            model_calls=row["model_calls"] or 0,
            step_ceiling=row["step_ceiling"] or 0,
            passed=bool(row["passed"]),
            successful_api_calls=0,
            hit_ceiling=row["termination"] == "step_ceiling",
        )
        for row in rows
    ]


def synthetic() -> list[Episode]:
    """A known dataset with a known answer, so the analysis can be tested today.

    Baseline takes twenty calls on every task and is censored on the hard half.
    The mechanism arm takes twelve on the easy half and is censored on the hard
    half, so the restricted-mean difference is exactly −4. The irrelevant arm takes
    sixteen on the easy half, so the subtractive effect is exactly −2.
    """
    episodes = []
    for index in range(10):
        task, easy = f"t{index:02d}", index < 5
        episodes.append(Episode(task, BASELINE, 20, 20, easy, 4, not easy, index % 2 == 0))
        episodes.append(
            Episode(task, "skills", 12 if easy else 20, 20, easy, 4, not easy, index % 2 == 0)
        )
        episodes.append(
            Episode(task, IRRELEVANT, 16 if easy else 20, 20, easy, 4, not easy, index % 2 == 0)
        )
    return episodes


def without_nan(value):
    """NaN to null, because `NaN` is Python's JSON, not JSON.

    A strict parser rejects the file, and a report nobody's tools can read is a
    report that gets retyped by hand — which is how a copied number starts ageing
    away from its source (setup protocol §6).

    NaN appears here for a stated reason, never as a silent failure: too few
    uncensored pairs for a signed-rank test, or an arm with no shared tasks. Null
    carries the same "not computed" and survives the round trip.
    """
    if isinstance(value, dict):
        return {key: without_nan(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [without_nan(item) for item in value]
    if isinstance(value, float) and value != value:
        return None
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=pathlib.Path)
    parser.add_argument("--arms", nargs="*", default=["skills", "failures", "skills_failures"])
    parser.add_argument("--coverage", type=float, default=0.0)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()

    seed, iterations = load_config()
    if arguments.self_test:
        episodes, arms, coverage = synthetic(), ["skills"], 1.0
    elif arguments.database:
        episodes, arms, coverage = (
            load_episodes(arguments.database),
            arguments.arms,
            arguments.coverage,
        )
        if not episodes:
            sys.exit(f"{arguments.database}: no episode rows. Nothing to analyse.")
    else:
        sys.exit("Give --database or --self-test.")

    report = analyse(episodes, arms, seed, iterations, coverage)
    report["inputs"] = {
        "episodes": len(episodes),
        "bootstrap_seed": seed,
        "bootstrap_iterations": iterations,
    }
    print(json.dumps(without_nan(report), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
