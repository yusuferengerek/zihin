"""Runs compiler v0 over the recorded passing episodes and reports what it finds.

**Thresholds are swept, not chosen.** Their numbers belong to the setup phase
(K-50) and this corpus has 20 tasks; picking one number and reporting it would
hide how much the answer depends on it. The pre-registration says that if
nothing clears the thresholds the honest move is to report the sensitivity
rather than lower them until a number appears.

**What counts as an effect is the compiler's own question** (K-78). The shield's
write set is one input, but the compiler adds the session endpoints the shield
exempts and removes the scaffold's control channel. `zihin.compiler` owns that
policy; this script only reports it.

Usage:

    uv run python scripts/setup/mine_skills.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import warnings

warnings.filterwarnings("ignore")

from zihin.compiler import (  # noqa: E402
    EpisodeSequence,
    call_from_action,
    classify_arguments,
    effect_elements,
    effect_suffix,
    merge_by_effect_suffix,
    mine_patterns,
    pattern_postcondition,
    scaffold_control_elements,
    session_endpoint_keys,
)
from zihin.shield import load_write_set  # noqa: E402

SERIES = "results/zihin-2.sqlite"
WRITE_SET_PATH = "inputs/write-set-static.json"
OUTPUT = "results/mined-skills.json"

SUPPORT_VALUES = (2, 3, 4, 5, 6, 8, 10)
GAP_VALUES = (0, 2, 5)
CONSTANT_THRESHOLD = 3
LEAD = "gap2-sup3"

# The corpus the thresholds were calibrated on, as a rule rather than a prefix:
# the DeepSeek bootstrap run (`sinir3`) on `test_normal`. Measured off the file
# (K-159). The setup-phase measurements that read `zihin-2.sqlite` pass this.
CALIBRATION_MODEL_TAG = "openrouter/deepseek/deepseek-v4-flash-0731"
CALIBRATION_SPLIT = "test_normal"


def passing_sequences(
    connection: sqlite3.Connection, *, model_tag: str, split: str
) -> list[EpisodeSequence]:
    """Passing episodes of one model on one split: skills are mined from successes.

    **Both conditions are required, and they are a rule, not a prefix.** This
    read every passing episode in the file once, and on Colab the file carried
    three runs: the declared corpus is "the evaluated model's own episodes"
    (section 18.1), and `b14` is another model. `b32c` is the same model but ran
    on `test_normal`, which is also the evaluation split: a skill mined from its
    passes encodes an evaluation task's call sequence, and measuring on that set
    afterwards would be training on the test set. Measured: the length-12
    patterns the guard bound on were `GET spotify.songs/{song_id}` repeated,
    supported by two `b32c` episodes and one `bir1` (K-159).

    Written as model tag and split so that a second train run under the same
    model joins the corpus, and a run of the same model on the evaluation split
    stays out - a prefix would have said neither.
    """
    episodes = connection.execute(
        """SELECT e.episode_id, e.task_id FROM episodes e
           JOIN verifier_results v ON v.episode_id = e.episode_id
           WHERE v.passed = 1 AND e.model_ref = ? AND e.split = ?
           ORDER BY e.episode_id""",
        (model_tag, split),
    ).fetchall()

    sequences = []
    for row in episodes:
        actions = connection.execute(
            """SELECT s.step_id, s.step_index, a.app, a.api, a.http_method, a.raw_parameters
               FROM actions a JOIN steps s USING(step_id)
               WHERE s.episode_id = ?
               ORDER BY s.step_index, a.action_index""",
            (row["episode_id"],),
        ).fetchall()
        per_step = collections.Counter(a["step_id"] for a in actions)

        calls, step_ids, counts = [], [], []
        for action in actions:
            calls.append(
                call_from_action(
                    action["app"], action["api"], action["http_method"], action["raw_parameters"]
                )
            )
            step_ids.append(action["step_id"])
            counts.append(per_step[action["step_id"]])

        deltas: dict[int, dict[str, int]] = {}
        observations: list[tuple[int, str]] = []
        for step in connection.execute(
            """SELECT s.step_id, s.state_change, o.truncated_text
               FROM steps s LEFT JOIN observations o USING(step_id)
               WHERE s.episode_id = ? ORDER BY s.step_index""",
            (row["episode_id"],),
        ).fetchall():
            # A missing `state_change` means "not measured" and stays absent;
            # `{}` means "measured, nothing changed" and is stored as such.
            if step["state_change"] is not None:
                deltas[step["step_id"]] = json.loads(step["state_change"])
            observations.append((step["step_id"], step["truncated_text"] or ""))

        sequences.append(
            EpisodeSequence(
                episode_id=row["episode_id"],
                task_id=row["task_id"],
                calls=tuple(calls),
                step_ids=tuple(step_ids),
                step_call_counts=tuple(counts),
                step_deltas=deltas,
                observations=tuple(observations),
            )
        )
    return sequences


def main() -> None:
    connection = sqlite3.connect(f"file:{SERIES}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    sequences = passing_sequences(
        connection, model_tag=CALIBRATION_MODEL_TAG, split=CALIBRATION_SPLIT
    )
    write_set = load_write_set(WRITE_SET_PATH)
    session_keys = session_endpoint_keys(WRITE_SET_PATH)
    effects = effect_elements(sequences, write_set, session_keys)
    excluded = scaffold_control_elements(sequences)

    tasks = {s.task_id for s in sequences}
    alphabet = {e for s in sequences for e in s.elements}
    print(f"passing episodes: {len(sequences)}  distinct tasks: {len(tasks)}")
    print(f"total calls: {sum(len(s.calls) for s in sequences)}")
    print(f"alphabet: {len(alphabet)} symbols, of which counted as effects: {len(effects)}")
    print(f"excluded from skill bodies (scaffold control channel): {sorted(excluded)}")
    print()

    grid: dict[str, dict] = {}
    print(f"{'gap':>7} {'support':>7} {'closed':>8} {'raw':>10} {'SKILLS':>10} {'prefixes':>12}")
    for max_gap in GAP_VALUES:
        for min_support in SUPPORT_VALUES:
            result = mine_patterns(
                sequences,
                min_support=min_support,
                max_gap=max_gap,
                min_length=2,
                excluded_elements=excluded,
            )
            raw_skills, prefixes = [], []
            for pattern in result.patterns:
                target = raw_skills if effect_suffix(pattern.elements, effects) else prefixes
                target.append(pattern)
            merged = merge_by_effect_suffix(raw_skills, effects)

            key = f"gap{max_gap}-sup{min_support}"
            grid[key] = {
                "closed_patterns": len(result.patterns),
                "patterns_with_an_effect": len(raw_skills),
                "skills_after_merge": len(merged),
                "discovery_prefixes": len(prefixes),
                "guard_bound": result.guarded,
                "guard": result.guard_report() if result.guarded else None,
                "skill_records": (
                    _describe(merged, sequences, effects, max_gap) if key == LEAD else []
                ),
                "top_prefixes": [
                    {"elements": list(p.elements), "support": p.support} for p in prefixes[:5]
                ],
            }
            flag = f"  ! {result.guard_report()}" if result.guarded else ""
            print(
                f"{max_gap:>7} {min_support:>7} {len(result.patterns):>8} {len(raw_skills):>10} "
                f"{len(merged):>10} {len(prefixes):>12}{flag}"
            )

    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {
                "episodes": len(sequences),
                "tasks": len(tasks),
                "calls": sum(len(s.calls) for s in sequences),
                "alphabet": len(alphabet),
                "effect_elements": sorted(effects),
                "constant_threshold": CONSTANT_THRESHOLD,
                "lead_configuration": LEAD,
                "grid": grid,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nwritten: {OUTPUT}")
    _report_lead(grid[LEAD])


def _describe(skills, sequences, effects, max_gap) -> list[dict]:
    """The full record for the configuration the report leads with."""
    records = []
    for skill in skills:
        episodes = {e for member in skill.members for e in member.ends}
        classes = classify_arguments(
            skill.body,
            sequences,
            episodes,
            max_gap,
            constant_threshold=CONSTANT_THRESHOLD,
        )
        indices = effect_suffix(skill.body, effects)
        postcondition = pattern_postcondition(skill.body, sequences, episodes, max_gap, indices)
        records.append(
            {
                "elements": list(skill.body),
                "effect_sequence": list(skill.effect_suffix),
                "merged_from": len(skill.members),
                "support": skill.support,
                "tasks": sorted(skill.tasks),
                "episodes": sorted(episodes),
                "effect_suffix": list(indices),
                "postcondition": postcondition,
                "bound_arguments": {str(k): sorted(v) for k, v in classes.bound.items()},
                "free_parameters": sorted(classes.free),
                "constants": {k: list(v) for k, v in classes.constants.items()},
                "arguments_inspected": classes.inspected,
            }
        )
    return records


def _report_lead(cell: dict) -> None:
    records = cell["skill_records"]
    print(f"\n--- {LEAD}: {len(records)} skills after the merge ---")
    bound_total = sum(len(v) for r in records for v in r["bound_arguments"].values())
    free_total = sum(len(r["free_parameters"]) for r in records)
    measured = [r for r in records if r["postcondition"] is not None]
    non_empty = [r for r in measured if r["postcondition"]]
    print(f"  bound arguments: {bound_total}   free parameters: {free_total}")
    print(
        f"  with a measurable postcondition: {len(measured)}/{len(records)}, "
        f"of which non-empty: {len(non_empty)}"
    )
    for record in records[:10]:
        print()
        print(
            f"  support {record['support']:>2}  merged from {record['merged_from']} patterns  "
            f"etki={record['effect_sequence']}"
        )
        for index, element in enumerate(record["elements"]):
            mark = "*" if index in record["effect_suffix"] else " "
            print(f"      {mark} {element}")
        print(f"        postcondition : {record['postcondition']}")
        print(f"        bound         : {record['bound_arguments']}")
        print(f"        serbest   : {record['free_parameters']}")
        print(f"        sabit     : {list(record['constants'])}")

    print(f"\n--- {LEAD}: discovery prefixes ---")
    for prefix in cell["top_prefixes"]:
        print(f"  destek {prefix['support']:>2}  {' | '.join(prefix['elements'])}")


if __name__ == "__main__":
    main()
