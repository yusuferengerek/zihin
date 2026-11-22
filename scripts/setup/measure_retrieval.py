"""Measures what the retriever finds, and above all its coverage.

**Coverage is a falsification gate, not a diagnostic.** Below 25% the finding is
not "we could not test the mechanism" but "the symbolic retriever finds no
relevant experience in this environment" (`05-experiment-design.tr.md`). So it is
measured before anything is run with cards, and on the splits the pilot will
use rather than on the twenty tasks the library was mined from.

**The mined tasks are reported separately.** A retriever measured only on the
tasks its own library came from would report the accuracy of a memory, not of a
retriever.

Every threshold is swept. None is chosen here.

Usage:

    uv run python scripts/setup/measure_retrieval.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import warnings

warnings.filterwarnings("ignore")

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.records import open_library  # noqa: E402
from zihin.retriever import retrieve, task_apps  # noqa: E402

OUTPUT = "results/retrieval-coverage.json"
SPLITS = ("train", "dev", "test_normal")
SAVING_THRESHOLDS = (0, 8, 10, 20, 30)
CONDITION_CAPS: tuple[int | None, ...] = (None, 10, 5, 2, 1)


def mined_tasks(connection: sqlite3.Connection, library_id: str) -> set[str]:
    tasks: set[str] = set()
    for row in connection.execute(
        "SELECT supporting_tasks FROM skills WHERE library_id = ?", (library_id,)
    ):
        tasks |= set(json.loads(row["supporting_tasks"]))
    return tasks


def main() -> None:
    # This measurement is about the library, so it opens the library's own
    # series. It used to open ACTIVE_SERIES, which stopped carrying a library
    # when series 3 opened and would have refused on the mining step (K-143).
    connection, library_id, index_id = open_library()
    seen = mined_tasks(connection, library_id)

    print(f"library {library_id}, index {index_id}")
    print(f"tasks the library was mined from: {len(seen)}")
    print()

    report: dict[str, dict] = {}
    for split in SPLITS:
        task_ids = list(load_task_ids(split))
        rows = []
        for task_id in task_ids:
            try:
                instruction = task_instruction(task_id)
            except FileNotFoundError:
                continue
            rows.append((task_id, instruction))

        # The sweep. Each cell is the coverage at one setting; the point is the
        # shape of the surface, not any single number on it.
        grid: dict[str, dict] = {}
        for saving in SAVING_THRESHOLDS:
            for cap in CONDITION_CAPS:
                for unverified in (True, False):
                    covered = skill_covered = failure_covered = 0
                    skills = failures = 0
                    for task_id, instruction in rows:
                        found = retrieve(
                            connection,
                            instruction,
                            library_id=library_id,
                            index_id=index_id,
                            min_expected_saving=saving,
                            max_discriminating_conditions=cap,
                            include_unverified_cards=unverified,
                            task_id=task_id,
                        )
                        covered += found.covered
                        # Per mechanism as well as overall. The pilot runs
                        # "skills only" and "failures only" as separate
                        # conditions, and each needs its own coverage: a task
                        # that gets a failure card but no skill is covered for
                        # one condition and uncovered for the other.
                        skill_covered += bool(found.skills)
                        failure_covered += bool(found.failures)
                        skills += len(found.skills)
                        failures += len(found.failures)
                    key = f"saving{saving}-cap{cap}-unverified{int(unverified)}"
                    grid[key] = {
                        "tasks": len(rows),
                        "covered": covered,
                        "coverage": round(covered / len(rows), 4) if rows else 0.0,
                        "skill_coverage": round(skill_covered / len(rows), 4) if rows else 0.0,
                        "failure_coverage": round(failure_covered / len(rows), 4) if rows else 0.0,
                        "skill_cards": skills,
                        "failure_cards": failures,
                    }

        # The headline configuration: no filtering at all, which is the ceiling.
        ceiling = grid["saving0-capNone-unverified1"]
        unseen = [(t, i) for t, i in rows if t not in seen]
        unseen_covered = sum(
            retrieve(
                connection,
                instruction,
                library_id=library_id,
                index_id=index_id,
                min_expected_saving=0,
                max_discriminating_conditions=None,
                include_unverified_cards=True,
                task_id=task_id,
            ).covered
            for task_id, instruction in unseen
        )
        app_counts = collections.Counter(len(task_apps(i)) for _, i in rows)

        report[split] = {
            "tasks": len(rows),
            "ceiling": ceiling,
            "unseen_tasks": len(unseen),
            "unseen_covered": unseen_covered,
            "unseen_coverage": round(unseen_covered / len(unseen), 4) if unseen else None,
            "apps_named_per_task": dict(sorted(app_counts.items())),
            "grid": grid,
        }

        print(f"--- {split}: {len(rows)} tasks ---")
        print(
            f"   tavan kapsama (filtresiz) : {ceiling['covered']}/{ceiling['tasks']} = "
            f"{ceiling['coverage']:.1%}"
        )
        print(
            f"   on unmined tasks: {unseen_covered}/{len(unseen)} = "
            f"{unseen_covered / len(unseen):.1%}"
            if unseen
            else "   no unmined tasks"
        )
        print(
            f"   skills-only coverage      : {ceiling['skill_coverage']:.1%}"
            f"   failures-only coverage: {ceiling['failure_coverage']:.1%}"
        )
        print(
            f"   total cards               : {ceiling['skill_cards']} beceri, "
            f"{ceiling['failure_cards']} hata"
        )
        print(f"   apps named per task: {dict(sorted(app_counts.items()))}")
        print()

    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {"library_id": library_id, "index_id": index_id, "splits": report},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"written: {OUTPUT}")
    print()
    print("--- falsification gate: is coverage below 25% ---")
    print("    (per mechanism, because the pilot runs them as separate conditions)")
    for split, data in report.items():
        for name, key in (
            ("herhangi", "coverage"),
            ("beceri", "skill_coverage"),
            ("hata", "failure_coverage"),
        ):
            ratio = data["ceiling"][key]
            status = (
                "BELOW — finding: the retriever finds no relevant experience"
                if ratio < 0.25
                else "above"
            )
            print(f"   {split:<14} {name:<9} {ratio:>6.1%}  {status}")


if __name__ == "__main__":
    main()
