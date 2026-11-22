"""Compiles the skill library and writes it into `skills`.

`mine_skills.py` sweeps the thresholds and reports the sensitivity; this script
writes one library at one configuration. They are separate because the sweep is
a measurement and the library is an artefact, and a measurement that also wrote
would tempt whoever ran it to keep the configuration that produced the nicest
number.

**No value filter is applied.** The expected saving is computed and stored as a
column; the threshold's number belongs to the setup phase and has not been
chosen (K-50). Filtering here would bake an unchosen number into the record,
and the sensitivity grid in `experiments/preregistration.md` is what the choice
should be made from.

**The library replaces itself.** `skills` is a derived projection
(`03-architecture.tr.md`) and carries no append-only trigger; each build deletes
its own `library_id` first. What makes a rebuild auditable is the provenance on
every row: gap, support, thresholds, compiler commit, write-set digest.

Usage:

    uv run python scripts/setup/build_skill_library.py --max-gap 2 --min-support 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

from zihin.compiler import (  # noqa: E402
    classify_arguments,
    effect_elements,
    effect_suffix,
    merge_by_effect_suffix,
    mine_patterns,
    occurrences_of,
    pattern_postcondition,
    scaffold_control_elements,
    session_endpoint_keys,
)
from zihin.records import ACTIVE_SERIES, insert_skill, open_database, replace_library  # noqa: E402
from zihin.shield import load_write_set  # noqa: E402
from zihin.shield_mount import config_digest  # noqa: E402

sys.path.insert(0, "scripts/setup")
from mine_skills import passing_sequences  # noqa: E402

WRITE_SET_PATH = "inputs/write-set-static.json"


def parse_options(argv: list[str]) -> argparse.Namespace:
    """Every parameter is explicit; none of them has a silent default.

    They define the library, so a value that slipped in unnoticed would define
    it too (K-50).
    """
    parser = argparse.ArgumentParser(description="Compiles the skill library.")
    parser.add_argument("--max-gap", type=int, required=True)
    parser.add_argument("--min-support", type=int, required=True)
    # The corpus rule. Required, like the thresholds: a default here would be a
    # second place the model name lives (K-138), and a library built from
    # whatever the file holds is what section 18.1 was violated by (K-159).
    parser.add_argument("--model-tag", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--constant-threshold", type=int, default=3)
    # The two search guards. No default here: None means the compiler's own
    # value applies, so the number lives in one place (K-138). They are raised
    # when the guard's report says it is a budget that bound, not a rule.
    parser.add_argument("--max-length", type=int, default=None)
    parser.add_argument("--max-patterns", type=int, default=None)
    parser.add_argument("--library-id", default=None)
    parser.add_argument("--database", default=ACTIVE_SERIES)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compiles and prints; does not touch the database.",
    )
    return parser.parse_args(argv)


def code_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


def median_steps(skill, sequences, max_gap: int) -> int | None:
    """How many steps the body occupied, as a median over its occurrences.

    One step is one model call, so this — not the call count — is what the skill
    would actually save. The two differ: measured, one of the four skills makes
    three calls in two steps.
    """
    by_id = {s.episode_id: s for s in sequences}
    episodes = {e for member in skill.members for e in member.ends}
    counts: list[int] = []
    for episode_id in sorted(episodes):
        sequence = by_id.get(episode_id)
        if sequence is None:
            continue
        for positions in occurrences_of(skill.body, sequence, max_gap):
            counts.append(len({sequence.step_ids[i] for i in positions}))
    if not counts:
        return None
    counts.sort()
    return counts[len(counts) // 2]


def corpus_summary(connection: sqlite3.Connection, sequences) -> str:
    """What the miner was mining, in one line, by prefix.

    `passing_sequences` is now filtered by model tag and split, and the prefix
    breakdown here is how that is seen to hold: a report on the declared corpus
    names one family of run ids.
    """
    heads: dict[str, int] = {}
    for sequence in sequences:
        row = connection.execute(
            "SELECT run_id FROM episodes WHERE episode_id = ?", (sequence.episode_id,)
        ).fetchone()
        head = (row[0] if row else "?").split("-")[0]
        heads[head] = heads.get(head, 0) + 1
    calls = sum(len(s.calls) for s in sequences)
    longest = max((len(s.calls) for s in sequences), default=0)
    alphabet = len({element for s in sequences for element in s.elements})
    tasks = len({s.task_id for s in sequences})
    return (
        f"{len(sequences)} passing episode(s), {tasks} distinct task(s), {calls} call(s), "
        f"alphabet {alphabet}, longest episode {longest} call(s), by prefix "
        f"{dict(sorted(heads.items()))}"
    )


def main(argv: list[str]) -> None:
    options = parse_options(argv)
    connection = open_database(options.database)
    connection.row_factory = sqlite3.Row

    sequences = passing_sequences(connection, model_tag=options.model_tag, split=options.split)
    write_set = load_write_set(WRITE_SET_PATH)
    session_keys = session_endpoint_keys(WRITE_SET_PATH)
    effects = effect_elements(sequences, write_set, session_keys)
    excluded = scaffold_control_elements(sequences)

    guards = {
        name: value
        for name, value in (
            ("max_length", options.max_length),
            ("max_patterns", options.max_patterns),
        )
        if value is not None
    }
    result = mine_patterns(
        sequences,
        min_support=options.min_support,
        max_gap=options.max_gap,
        min_length=2,
        excluded_elements=excluded,
        **guards,
    )
    if result.guarded:
        # A truncated search must never become a library that looks complete.
        # The refusal carries the guard's own sentence and the corpus it bound
        # on: which guard, the value it saw, its limit, and what it was mining.
        # "The search hit a guard" alone sent one round back to Colab with no
        # way to choose between raising a budget and stopping (K-158).
        raise SystemExit(
            "the search hit a guard and the result is incomplete. No library is "
            "produced from an incomplete search.\n  "
            + result.guard_report()
            + "\n  corpus: "
            + corpus_summary(connection, sequences)
        )

    with_effect = [p for p in result.patterns if effect_suffix(p.elements, effects)]
    skills = merge_by_effect_suffix(with_effect, effects)

    digest = config_digest(WRITE_SET_PATH)
    commit = code_commit()
    library_id = options.library_id or (
        f"v0-gap{options.max_gap}-sup{options.min_support}-{commit[:7]}"
    )

    rows = []
    for skill in skills:
        episodes = {e for member in skill.members for e in member.ends}
        classes = classify_arguments(
            skill.body,
            sequences,
            episodes,
            options.max_gap,
            constant_threshold=options.constant_threshold,
        )
        indices = effect_suffix(skill.body, effects)
        postcondition = pattern_postcondition(
            skill.body, sequences, episodes, options.max_gap, indices
        )
        steps = median_steps(skill, sequences, options.max_gap)
        # The identity is the effect suffix (K-75), so that is what the id
        # digests — not the body, which is only the widest-supported member and
        # can change when a new episode arrives without the skill changing.
        payload = json.dumps([library_id, list(skill.effect_suffix)], ensure_ascii=False)
        rows.append(
            {
                "skill_id": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
                "library_id": library_id,
                "effect_suffix": list(skill.effect_suffix),
                "body": list(skill.body),
                "body_length": len(skill.body),
                "support": skill.support,
                "supporting_tasks": sorted(skill.tasks),
                "supporting_episodes": sorted(episodes),
                "merged_from": len(skill.members),
                "bound_arguments": {str(k): sorted(v) for k, v in classes.bound.items()},
                "free_parameters": sorted(classes.free),
                "constants": {k: list(v) for k, v in classes.constants.items()},
                "postcondition": postcondition,
                # The primary metric is the model call, and one step is one
                # model call (K-82). The call-based figure is kept beside it as
                # a diagnostic, because the gap between the two is what showed
                # the specification was counting the wrong unit.
                "expected_saving": (None if steps is None else (steps - 1) * skill.support),
                "expected_saving_calls": (len(skill.body) - 1) * skill.support,
                "observed_steps": steps,
                "max_gap": options.max_gap,
                "min_support": options.min_support,
                "constant_threshold": options.constant_threshold,
                "compiler_commit": commit,
                "write_set_digest": digest,
            }
        )

    print(f"library: {library_id}")
    print(f"skills: {len(rows)}   (no value filter applied, stored as a column)")
    for row in rows:
        print(
            f"  support {row['support']:>2}  saving {row['expected_saving']:>3} model calls"
            f"  (call-based {row['expected_saving_calls']:>3})"
            f"  {' + '.join(row['effect_suffix'])}"
        )

    if options.dry_run:
        print("\n--dry-run: nothing was written to the database")
        return

    with connection:
        removed = replace_library(connection, library_id)
        if removed:
            print(f"\n{removed} earlier rows deleted, the library is being regenerated")
        for row in rows:
            insert_skill(connection, **row)
    print(f"\nwritten: {options.database}, {len(rows)} rows")


if __name__ == "__main__":
    main(sys.argv[1:])
