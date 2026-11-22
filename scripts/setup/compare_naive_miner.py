"""Does the compiler's complexity buy anything on this corpus?

**The naive miner, written to be naive.** Fixed-length contiguous n-grams over the
same call alphabet, support counted the same way (distinct tasks), and nothing
else: no closed-pattern filter, so a pattern and every sub-pattern of it survive
side by side; no gap, so an interruption ends a match; no argument classification,
so every argument is a free parameter; no effect-suffix requirement, so a card can
end on a read; and no merging, so two patterns with the same effect stay two cards.

Each of those five is a decision the real compiler makes. Removing them all at
once does not say which one earns its keep — it says whether *any* of them
changes the library on this corpus, which is the question that decides whether a
`naive_compiler` condition is worth an arm.

**The comparison is between libraries, not between miners.** The real library's
identity is the effect suffix (K-75), so the test is whether the naive miner's
cards carry those same effects — not whether the two produce the same number of
patterns, which they cannot.

**Decision criterion, written before the run.** If the two libraries differ
markedly, the naive-compiler condition enters the six and its cost is accepted.
If the naive miner produces the same skills, the condition is not written and the
finding is that on this corpus the compiler's complexity bought nothing.

**No model calls.** Both miners are pure functions of the record.

Usage:

    uv run python scripts/setup/compare_naive_miner.py
    uv run python scripts/setup/compare_naive_miner.py --lengths 2 3 4
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sqlite3
import sys
import warnings

warnings.filterwarnings("ignore")

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))
sys.path.insert(0, str(REPOSITORY / "scripts/setup"))

from mine_skills import CALIBRATION_MODEL_TAG, CALIBRATION_SPLIT, passing_sequences  # noqa: E402

from zihin.compiler import (  # noqa: E402
    effect_elements,
    effect_suffix,
    merge_by_effect_suffix,
    mine_patterns,
    scaffold_control_elements,
    session_endpoint_keys,
)
from zihin.records import CALIBRATION_SERIES  # noqa: E402
from zihin.shield import load_write_set  # noqa: E402

OUTPUT = REPOSITORY / "results/naive-miner.json"
WRITE_SET_PATH = "inputs/write-set-static.json"
# The real library's configuration, so the comparison is against the library that
# exists rather than against a differently-tuned one.
MIN_SUPPORT = 3
MAX_GAP = 2


def ngrams(sequences, length: int, excluded: frozenset[str]):
    """Every contiguous n-gram of exactly `length`, with the tasks it occurs in.

    Contiguous: no gap is allowed, which is the point. Excluded symbols are
    dropped from the stream rather than breaking it, so that the flag isolates
    "does the compiler's scaffold list matter" instead of also changing adjacency.
    """
    support: dict[tuple[str, ...], set[str]] = collections.defaultdict(set)
    for sequence in sequences:
        stream = [call.element for call in sequence.calls if call.element not in excluded]
        for index in range(len(stream) - length + 1):
            support[tuple(stream[index : index + length])].add(sequence.task_id)
    return support


def naive_library(sequences, lengths, min_support: int, excluded: frozenset[str]):
    """Every n-gram at every requested length that clears support. No closure."""
    cards = []
    for length in lengths:
        for elements, tasks in ngrams(sequences, length, excluded).items():
            if len(tasks) >= min_support:
                cards.append(
                    {
                        "body": list(elements),
                        "length": length,
                        "support": len(tasks),
                        "tasks": sorted(tasks),
                        # Every argument is free: the naive miner does not look at
                        # values, so it cannot say a parameter is bound or constant.
                        "free_parameters": "all",
                        "expected_saving_calls": (length - 1) * len(tasks),
                    }
                )
    return cards


def real_library(sequences):
    """The library the compiler builds, rebuilt here from the same corpus."""
    write_set = load_write_set(WRITE_SET_PATH)
    session_keys = session_endpoint_keys(WRITE_SET_PATH)
    effects = effect_elements(sequences, write_set, session_keys)
    excluded = scaffold_control_elements(sequences)
    result = mine_patterns(
        sequences,
        min_support=MIN_SUPPORT,
        max_gap=MAX_GAP,
        min_length=2,
        excluded_elements=excluded,
    )
    if result.guarded:
        sys.exit(
            "the compiler's search hit a guard; no comparison is made against a partial "
            "one.\n  " + result.guard_report()
        )
    with_effect = [p for p in result.patterns if effect_suffix(p.elements, effects)]
    skills = merge_by_effect_suffix(with_effect, effects)
    return skills, effects, excluded, len(result.patterns), len(with_effect)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=CALIBRATION_SERIES)
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3, 4, 5, 6])
    options = parser.parse_args()

    path = REPOSITORY / options.database
    if not path.exists():
        sys.exit(f"{options.database} does not exist; both miners read the same corpus.")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    sequences = passing_sequences(
        connection, model_tag=CALIBRATION_MODEL_TAG, split=CALIBRATION_SPLIT
    )
    if len(sequences) < MIN_SUPPORT:
        sys.exit(
            f"the corpus holds {len(sequences)} passing episodes and support is "
            f"{MIN_SUPPORT}. Neither miner has anything to find; this declines."
        )

    skills, effects, excluded, mined, with_effect = real_library(sequences)
    real_bodies = {tuple(skill.body) for skill in skills}
    real_effects = {tuple(skill.effect_suffix) for skill in skills}

    print(
        f"corpus: {len(sequences)} passing episodes, "
        f"{len({s.task_id for s in sequences})} distinct tasks"
    )
    print(
        f"alphabet: {len({c.element for s in sequences for c in s.calls})} symbols, "
        f"{len(excluded)} excluded as scaffold/control, {len(effects)} carry an effect"
    )
    print()
    print(
        f"compiler: {mined} closed patterns -> {with_effect} with an effect suffix "
        f"-> {len(skills)} skills after merging"
    )
    for skill in skills:
        print(f"   support {skill.support:>2}  {' + '.join(skill.effect_suffix)}")
    print()

    grids = {}
    for label, drop in (("with the scaffold list", excluded), ("without it", frozenset())):
        print(f"naive miner, {label}:")
        print(f"  {'n':>2} {'cards':>7} {'ends on an effect':>18} {'a real body':>12}")
        rows = []
        for length in options.lengths:
            cards = naive_library(sequences, [length], MIN_SUPPORT, drop)
            effectful = [c for c in cards if effect_suffix(tuple(c["body"]), effects)]
            matching = [c for c in cards if tuple(c["body"]) in real_bodies]
            rows.append(
                {
                    "n": length,
                    "cards": len(cards),
                    "cards_ending_on_an_effect": len(effectful),
                    "cards_that_are_a_real_body": len(matching),
                }
            )
            print(f"  {length:>2} {len(cards):>7} {len(effectful):>18} {len(matching):>12}")
        grids[label] = rows
        print()

    # The criterion's own question: does the naive miner reach the real effects?
    everything = naive_library(sequences, options.lengths, MIN_SUPPORT, excluded)
    reached = {
        tuple(effect_suffix_elements)
        for card in everything
        if (
            effect_suffix_elements := tuple(
                card["body"][i] for i in effect_suffix(tuple(card["body"]), effects)
            )
        )
    }
    covered = sorted(real_effects & reached)
    missed = sorted(real_effects - reached)
    extra_effects = sorted(reached - real_effects)

    print("the criterion")
    print(f"  the compiler's skills                : {len(real_effects)}")
    print(f"  of those, reachable by an n-gram     : {len(covered)}")
    print(f"  not reachable                        : {len(missed)}")
    print(f"  effects only the naive miner produces: {len(extra_effects)}")
    print(f"  naive cards in total, all lengths    : {len(everything)}")
    for effect in missed:
        print(f"    missed: {' + '.join(effect)}")

    report = {
        "what": "the compiler's library against a fixed-length n-gram miner, same corpus",
        "database": options.database,
        "min_support": MIN_SUPPORT,
        "max_gap_compiler": MAX_GAP,
        "lengths": options.lengths,
        "passing_episodes": len(sequences),
        "distinct_tasks": len({s.task_id for s in sequences}),
        "compiler": {
            "closed_patterns": mined,
            "with_effect_suffix": with_effect,
            "skills": len(skills),
            "effect_suffixes": [list(e) for e in sorted(real_effects)],
            "bodies": [list(b) for b in sorted(real_bodies)],
        },
        "naive": {
            "grids": grids,
            "cards_all_lengths": len(everything),
            "effects_reached": [list(e) for e in sorted(reached)],
        },
        "criterion": {
            "compiler_effects": len(real_effects),
            "reached_by_ngrams": [list(e) for e in covered],
            "missed_by_ngrams": [list(e) for e in missed],
            "only_naive": [list(e) for e in extra_effects],
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
