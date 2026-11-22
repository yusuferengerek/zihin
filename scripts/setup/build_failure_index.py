"""Builds the failure index and writes it into `failure_patterns`.

The mirror of `build_skill_library.py`, and it mines the opposite half of the
record: skills come from passing episodes, failure cards from failing actions.

**Failing actions from every episode, not only failing ones.** A passing episode
can contain a failed call the agent recovered from, and that failure is as real
as any other. Restricting to failing episodes would throw away the cases where
the agent already knew how to recover — which are the ones a card can teach.

Usage:

    uv run python scripts/setup/build_failure_index.py --min-support 1
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sqlite3
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

from zihin.failure_index import (  # noqa: E402
    ObservedAction,
    action_from_row,
    mine_failure_patterns,
)
from zihin.records import (  # noqa: E402
    ACTIVE_SERIES,
    insert_failure_pattern,
    open_database,
    replace_index,
)


def parse_options(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compiles the failure index.")
    parser.add_argument("--min-support", type=int, required=True)
    # The corpus rule, required for the same reason as in the compiler (K-159).
    parser.add_argument("--model-tag", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--index-id", default=None)
    parser.add_argument("--database", default=ACTIVE_SERIES)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def code_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "bilinmiyor"


def observed_episodes(
    connection: sqlite3.Connection, *, model_tag: str, split: str
) -> dict[int, list[ObservedAction]]:
    """Every action of one model on one split, passing or not.

    The same rule as the skill compiler's `passing_sequences`, for the same
    reason: the index is mined in the same block from the same corpus (section
    18.4), and an index mined across models and across the evaluation split
    would carry the other model's failures and the evaluation tasks' call
    shapes (K-159).
    """
    rows = connection.execute(
        """SELECT a.app, a.api, a.http_method, a.result_status, a.error_class,
                  a.raw_parameters, s.episode_id, e.task_id
           FROM actions a
           JOIN steps s USING(step_id)
           JOIN episodes e ON e.episode_id = s.episode_id
           WHERE e.model_ref = ? AND e.split = ?
           ORDER BY s.episode_id, s.step_index, a.action_index""",
        (model_tag, split),
    ).fetchall()
    episodes: dict[int, list[ObservedAction]] = collections.defaultdict(list)
    for row in rows:
        episode = episodes[row["episode_id"]]
        episode.append(action_from_row(row, len(episode)))
    return dict(episodes)


def every_observed_episode(connection: sqlite3.Connection) -> dict[int, list[ObservedAction]]:
    """The whole file, unfiltered - for the setup-phase substrate measurements only.

    Named, so that the one place the unfiltered read still exists is visible.
    `measure_failure_index_build.py` and `measure_accumulation.py` reported the
    failure substrate as "every recorded episode" (142 episodes, 36 tasks), and
    that number is a recorded artefact; the production builder never calls this.
    """
    rows = connection.execute(
        """SELECT a.app, a.api, a.http_method, a.result_status, a.error_class,
                  a.raw_parameters, s.episode_id, e.task_id
           FROM actions a
           JOIN steps s USING(step_id)
           JOIN episodes e ON e.episode_id = s.episode_id
           ORDER BY s.episode_id, s.step_index, a.action_index"""
    ).fetchall()
    episodes: dict[int, list[ObservedAction]] = collections.defaultdict(list)
    for row in rows:
        episode = episodes[row["episode_id"]]
        episode.append(action_from_row(row, len(episode)))
    return dict(episodes)


def main(argv: list[str]) -> None:
    options = parse_options(argv)
    connection = open_database(options.database)
    connection.row_factory = sqlite3.Row

    episodes = observed_episodes(connection, model_tag=options.model_tag, split=options.split)
    patterns, tally = mine_failure_patterns(episodes, min_support=options.min_support)

    commit = code_commit()
    index_id = options.index_id or f"v0-sup{options.min_support}-{commit[:7]}"

    print(f"epizot {len(episodes)}, eylem {sum(len(v) for v in episodes.values())}")
    print()
    print("--- elimination breakdown ---")
    for key, value in tally.items():
        print(f"   {key:<28} {value}")
    print()
    print(f"--- indeks: {len(patterns)} cards ---")
    for pattern in patterns:
        condition = pattern.condition
        print(
            f"  destek {pattern.support:>2}  {len(pattern.failures):>4} hata  "
            f"[{pattern.label}]  {pattern.method} {pattern.app}.{pattern.api}"
        )
        print(f"        argument shape : {list(pattern.shape)}")
        if condition is None:
            print("        condition      : NONE, no contrasting success found")
            print("        NO KNOWN SUCCESS: a discrimination claim would be vacuous (K-85)")
            continue
        yon = "VAR" if condition.present else "YOK"
        guven = "its own app" if pattern.own_app_condition else "UNRELATED APP"
        print(f"        condition      : prior successful {condition.call} {yon}")
        print(
            f"        discriminator  : {pattern.discriminator}"
            f"   contrasting successes: {pattern.contrast_successes}"
        )
        print(f"        separating     : {pattern.discriminating_count} conditions, chose {guven}")

    if options.dry_run:
        print("\n--dry-run: nothing was written to the database")
        return

    rows = []
    for pattern in patterns:
        condition = pattern.condition
        payload = json.dumps(
            [
                index_id,
                pattern.app,
                pattern.api,
                pattern.method,
                list(pattern.shape),
                pattern.status,
            ],
            ensure_ascii=False,
        )
        rows.append(
            {
                "pattern_id": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
                "index_id": index_id,
                "app": pattern.app,
                "api": pattern.api,
                "http_method": pattern.method,
                "argument_shape": list(pattern.shape),
                "status_code": pattern.status,
                "failure_label": pattern.label,
                "condition": None if condition is None else condition.as_dict(),
                "discriminator": pattern.discriminator or None,
                "support": pattern.support,
                "supporting_tasks": sorted(pattern.tasks),
                "failure_count": len(pattern.failures),
                "contrast_successes": pattern.contrast_successes,
                "no_known_success": int(pattern.no_known_success),
                "discriminating_count": (
                    None if condition is None else pattern.discriminating_count
                ),
                "own_app_condition": (
                    None if condition is None else int(pattern.own_app_condition)
                ),
                "min_support": options.min_support,
                "compiler_commit": commit,
            }
        )

    with connection:
        removed = replace_index(connection, index_id)
        if removed:
            print(f"\n{removed} earlier rows deleted, the index is being regenerated")
        for row in rows:
            insert_failure_pattern(connection, **row)
    print(f"\nwritten: {options.database}, {len(rows)} rows  (index {index_id})")


if __name__ == "__main__":
    main(sys.argv[1:])
