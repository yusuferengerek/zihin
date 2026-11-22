"""The tasks setup touched: derived from the record, and checked where it is read.

**Why this module exists.** The list was written once by hand and read by four
measurement scripts. It fell behind the record: four `test_normal` tasks - the
three `0a9d82a` variants and `0de03ea_1` - had forty-five episodes between them,
carded and uncarded, and were still in the evaluation sample. A list that is
written beside the record rather than read from it goes stale the day nobody
remembers to edit it.

**The rule.** A task is touched when the record holds an episode of it, in any
run, under any condition, before the experiment. Nothing else is asked: not
whether the run was a preflight, a demonstration or a scan. Which split a task
belongs to is AppWorld's answer, not the episode's `split` column - the column
says `train` for eight episodes of `024c982_1`, which is a `test_normal` task,
and those rows are named in the document rather than trusted.

**The experiment is not a touch.** The rule was written as "every run before
the experiment", and a rule that knows no boundary would count the experiment's
own episodes as touches the moment they are written, empty the evaluation sample
and refuse the list. The boundary is the prefix: a run whose id starts with
`dny` is the experiment, every other run is a touch (protocol section 19,
K-178). Two ways through that boundary are refused rather than trusted: a `dny`
run named as a preflight, and a `dny` episode of a task that is not in the
evaluation sample.

**Where the check lives.** Here, in the one loader every reader goes through.
When the record is present the loader derives the list again and refuses a
committed list that differs from it. When only part of the record is present it
refuses a list that is missing any task the present part touched. It refuses any
`test_challenge` task in either, because the challenge split is the only unseen
data this project has (preregistration A.10). With no record at all it can only
check the file's own structure, and says so.
"""

from __future__ import annotations

import collections
import json
import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from zihin.declared import EXPERIMENT_PREFIX, NON_MEASUREMENT_MARKERS
from zihin.records import ACTIVE_SERIES, CALIBRATION_SERIES

REPOSITORY = Path(__file__).resolve().parents[2]
TOUCHED = "results/touched-tasks.json"
# Every series of the record, oldest first. Series 1 was run under the old
# stopping rule and is read, not written; it still holds touched tasks.
RECORD_SERIES = ("results/zihin.sqlite", CALIBRATION_SERIES, ACTIVE_SERIES)
SPLITS = ("train", "dev", "test_normal", "test_challenge")
UNSEEN = "test_challenge"
WHAT = (
    "every task the record holds an episode of, by AppWorld split, with the runs, "
    "conditions and models that touched it"
)


class TouchedListError(RuntimeError):
    """The committed list and the record disagree, or the list is malformed."""


def split_membership() -> dict[str, str]:
    """Task id -> AppWorld split. Read from AppWorld, not from the episodes."""
    from appworld.task import load_task_ids

    return {task: split for split in SPLITS for task in load_task_ids(split)}


def run_family(run_id: str, task_id: str) -> str:
    """The part of a run id that names the run rather than the task.

    Run ids carry the task after the run's own name (`uckol-cards-0-0de03ea_1-...`,
    `bir1-onkontrol3-024c982_1-...`), so the family is everything before it.
    """
    marker = f"-{task_id}"
    return run_id.split(marker)[0] if marker in run_id else run_id


def is_experiment(run_id: str) -> bool:
    """Does this run belong to the experiment: its first segment is the prefix."""
    return run_id.split("-", 1)[0] == EXPERIMENT_PREFIX


def _episodes(path: Path) -> list[tuple]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return connection.execute(
            "SELECT run_id, task_id, condition, model_ref, split FROM episodes"
        ).fetchall()
    finally:
        connection.close()


def experiment_problems(
    series: Iterable[Path], split_of: dict[str, str], document: dict
) -> list[str]:
    """Every way the record's `dny` episodes break the boundary.

    An experiment episode that is a preflight, or that ran a task outside the
    evaluation sample - `test_normal` minus the touched tasks - would be invisible
    to the touched list, because the list does not count the experiment.
    """
    touched = set(document.get("test_normal") or [])
    problems = []
    for path in series:
        for run_id, task_id, *_ in _episodes(path):
            if not is_experiment(run_id):
                continue
            segments = run_family(run_id, task_id).split("-")[1:]
            if any(s.startswith(m) for s in segments for m in NON_MEASUREMENT_MARKERS):
                problems.append(
                    f"{path.name}: {run_id} is a preflight under the experiment's prefix; "
                    "a run that measures nothing belongs under the control prefix"
                )
            split = split_of.get(task_id)
            if split != "test_normal":
                problems.append(
                    f"{path.name}: {run_id} ran {task_id} from {split}; the experiment runs "
                    "the evaluation sample only"
                )
            elif task_id in touched:
                problems.append(
                    f"{path.name}: {run_id} ran {task_id}, which setup touched; it is not in "
                    "the evaluation sample"
                )
    return problems


def derive(series: Iterable[Path], split_of: dict[str, str]) -> dict:
    """The document the record implies. Every episode outside the experiment counts."""
    touched: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    disagreements: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    names = []
    for path in series:
        names.append(path.name)
        for run_id, task_id, condition, model, recorded in _episodes(path):
            if is_experiment(run_id):
                continue
            if task_id not in split_of:
                raise TouchedListError(
                    f"{path.name} holds an episode of {task_id!r}, which no AppWorld "
                    "split contains; the list cannot place it"
                )
            touched[task_id][(path.name, run_family(run_id, task_id), condition, model)] += 1
            if recorded != split_of[task_id]:
                disagreements[task_id][recorded] += 1

    document: dict = {"what": WHAT, "sources": names}
    for split in SPLITS:
        document[split] = sorted(task for task in touched if split_of[task] == split)
    document["provenance"] = {
        task: [
            {"series": s, "run": r, "condition": c, "model": m, "episodes": n}
            for (s, r, c, m), n in sorted(touched[task].items())
        ]
        for task in sorted(touched)
    }
    document["recorded_split_disagrees"] = {
        task: {"appworld": split_of[task], "recorded": dict(sorted(counts.items()))}
        for task, counts in sorted(disagreements.items())
    }
    return document


def render(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def structural_problems(document: dict) -> list[str]:
    """What is wrong with the file on its own, with no record to compare against."""
    problems = []
    for split in SPLITS:
        tasks = document.get(split)
        if not isinstance(tasks, list):
            problems.append(f"{split}: missing or not a list")
            continue
        if tasks != sorted(set(tasks)):
            problems.append(f"{split}: not sorted, or a task appears twice")
    listed = [task for split in SPLITS for task in document.get(split) or []]
    twice = sorted(task for task, n in collections.Counter(listed).items() if n > 1)
    if twice:
        problems.append(f"in more than one split: {twice}")
    if document.get(UNSEEN):
        problems.append(f"{UNSEEN} is touched: {document[UNSEEN]}")
    provenance = document.get("provenance")
    if not isinstance(provenance, dict):
        problems.append("provenance: missing")
        return problems
    if sorted(provenance) != sorted(set(listed)):
        missing = sorted(set(listed) - set(provenance))
        extra = sorted(set(provenance) - set(listed))
        problems.append(f"provenance does not match the lists: missing {missing}, extra {extra}")
    fields = {"series", "run", "condition", "model", "episodes"}
    for task, entries in provenance.items():
        if not entries:
            problems.append(f"{task}: listed as touched with no episode behind it")
        for entry in entries:
            if set(entry) != fields or not isinstance(entry["episodes"], int):
                problems.append(f"{task}: malformed provenance entry {entry}")
            elif entry["episodes"] < 1:
                problems.append(f"{task}: an entry with {entry['episodes']} episodes")
    return problems


@dataclass(frozen=True)
class Touched:
    document: dict
    basis: str

    def tasks(self, split: str) -> list[str]:
        return list(self.document.get(split) or [])


def _difference(committed: dict, derived: dict) -> str:
    lines = []
    for split in SPLITS:
        have, want = set(committed.get(split) or []), set(derived[split])
        if want - have:
            lines.append(f"{split}: the record touched {sorted(want - have)} and the list omits it")
        if have - want:
            lines.append(
                f"{split}: the list names {sorted(have - want)} and the record never ran it"
            )
    if not lines and committed != derived:
        lines.append("the task lists agree; the provenance or the sources differ")
    return "; ".join(lines)


def load_touched(
    root: Path = REPOSITORY,
    *,
    split_of: Callable[[], dict[str, str]] | dict[str, str] | None = None,
    series: Iterable[str] = RECORD_SERIES,
) -> Touched:
    """The committed list, checked against as much of the record as is here."""
    path = root / TOUCHED
    if not path.exists():
        raise TouchedListError(
            f"{TOUCHED} is absent and it defines which tasks are out of the evaluation; "
            "a measurement that cannot delimit its sample declines"
        )
    committed = json.loads(path.read_text(encoding="utf-8"))
    problems = structural_problems(committed)
    if problems:
        raise TouchedListError(f"{TOUCHED} is malformed: {'; '.join(problems)}")

    present = [root / name for name in series if (root / name).exists()]
    absent = [name for name in series if not (root / name).exists()]
    if not present:
        return Touched(committed, "no record here: the file's structure only was checked")

    membership = split_of() if callable(split_of) else split_of
    membership = membership if membership is not None else split_membership()
    derived = derive(present, membership)
    if derived[UNSEEN]:
        raise TouchedListError(
            f"the record holds episodes of {UNSEEN} tasks {derived[UNSEEN]}; that split is "
            "the only unseen data this project has and setup may not touch it"
        )
    crossings = experiment_problems(present, membership, committed)
    if crossings:
        raise TouchedListError(
            f"the experiment boundary is crossed: {'; '.join(crossings[:5])}"
            + (f" (and {len(crossings) - 5} more)" if len(crossings) > 5 else "")
        )
    if not absent:
        if render(committed) != render(derived):
            raise TouchedListError(
                f"{TOUCHED} disagrees with the record: {_difference(committed, derived)}. "
                "Regenerate it with scripts/setup/build_touched_tasks.py."
            )
        return Touched(committed, "checked against the full record")

    behind = {
        split: sorted(set(derived[split]) - set(committed.get(split) or [])) for split in SPLITS
    }
    behind = {split: tasks for split, tasks in behind.items() if tasks}
    if behind:
        raise TouchedListError(
            f"{TOUCHED} omits tasks the present part of the record touched: {behind}"
        )
    return Touched(
        committed,
        f"partial record ({', '.join(absent)} absent): only containment was checked",
    )
