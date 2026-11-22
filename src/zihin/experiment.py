"""The experiment's task order, and the file that keeps it (K-183).

**Fixed before the first episode, from a declared seed.** The experiment runs in
slices, the next N tasks of one order, and the order is not chosen as it goes:
a task picked after the previous slice was seen is a task picked by the result.
Each task's key is `sha256("<seed>:<task_id>")` and the order is the keys
ascending. The seed is `base_seed` in `config/models.yaml` (123), a value that
was declared long before this one, so the order carries no freedom of its own -
there is no second seed that could have been tried and discarded.

**Why a hash and not a shuffle.** A shuffle is only as reproducible as the random
number generator behind it, and that is an implementation detail of a Python
version. A hash of a declared string is the same everywhere.

**Why a file.** The order is also the protocol's declaration and the driver's
work list. The file carries the seed, the method, the order and its digest; the
protocol names the seed, the method and the digest; a test regenerates the order
from the sample and compares.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
ORDER = "results/experiment-order.json"
METHOD = 'sha256("<seed>:<task_id>"), ascending'


class OrderError(RuntimeError):
    """The committed order does not say what it claims."""


def order_key(seed: int, task_id: str) -> str:
    return hashlib.sha256(f"{seed}:{task_id}".encode()).hexdigest()


def task_order(tasks: Iterable[str], seed: int) -> list[str]:
    """The tasks in the experiment's order."""
    return sorted(set(tasks), key=lambda task: order_key(seed, task))


def order_digest(order: Sequence[str]) -> str:
    """One line per task, in order; the digest the protocol declares."""
    return hashlib.sha256("\n".join(order).encode()).hexdigest()


def order_document(tasks: Iterable[str], seed: int) -> dict:
    order = task_order(tasks, seed)
    return {
        "what": "the order the experiment runs its tasks in; slices take it from the front",
        "decision": "K-183",
        "sample": "the action stratum of the evaluation sample (K-144)",
        "seed": seed,
        "seed_source": "config/models.yaml:base_seed",
        "method": METHOD,
        "tasks": len(order),
        "digest": order_digest(order),
        "order": order,
    }


def render(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def load_order(root: Path = REPOSITORY) -> dict:
    """The committed order, checked against itself.

    Its digest must be its order's, and its order must be what the declared key
    gives for its own tasks. Whether the tasks are the sample is a second question,
    answered by regenerating (`scripts/setup/build_experiment_order.py --check`).
    """
    path = root / ORDER
    if not path.exists():
        raise OrderError(f"{ORDER} is absent; the experiment has no declared order")
    document = json.loads(path.read_text(encoding="utf-8"))
    order = document.get("order") or []
    if document.get("digest") != order_digest(order):
        raise OrderError(f"{ORDER}: its digest is not its order's")
    if order != task_order(order, document["seed"]):
        raise OrderError(f"{ORDER}: its order is not what {METHOD} gives for its tasks")
    if document.get("tasks") != len(order):
        raise OrderError(f"{ORDER}: it says {document.get('tasks')} tasks and lists {len(order)}")
    return document


# --- the analysis sets (K-184) --------------------------------------------------

SETS = "results/experiment-sets.json"

# Each confirmatory contrast and the two conditions it compares. `Y-6.2` is read
# in phase 1 against `skills_failures` (K2 of the phase design); K-31's own
# wording - `skills` against the control - is its second reading, in phase 2.
ANALYSES = {
    "Y-1": ("skills_failures", "baseline"),
    "Y-6.2": ("skills_failures", "irrelevant_retrieval"),
    "Y-4": ("failures", "baseline"),
    "Y-5": ("skills", "baseline"),
    "Y-6.2, second reading": ("skills", "irrelevant_retrieval"),
}
PHASE_ONE = ("baseline", "skills_failures", "irrelevant_retrieval")
PHASE_TWO = ("skills", "failures")


def analysis_sets(per_task: dict[str, dict[str, dict]]) -> dict[str, list[str]]:
    """The tasks each contrast is read on, from the slots the runner builds.

    A task is in a contrast's set when the carded arm reaches it with a card (A.3's
    covered task; no card-carrying condition runs elsewhere) and neither of the two
    conditions ran short of the carded arm's volume (A.4's correction, K-181).
    """
    sets = {}
    for name, pair in ANALYSES.items():
        sets[name] = sorted(
            task
            for task, slots in per_task.items()
            if slots["skills_failures"]["covered"]
            and all(slots[c]["volume_matched"] is not False for c in pair if c != "baseline")
        )
    return sets


def phase_one_episodes(per_task: dict[str, dict[str, dict]], seeds: int) -> int:
    """Three seeds of the three conditions on a covered task, of the baseline elsewhere."""
    return sum(
        seeds * (len(PHASE_ONE) if slots["skills_failures"]["covered"] else 1)
        for slots in per_task.values()
    )


# --- what the driver and the analysis read (K-185) ------------------------------


def run_identity(prefix: str, condition: str, seed_index: int, task: str, short: str) -> str:
    """The run id `record_run.py` will write for this episode.

    One manifest per episode: the name carries the condition and the seed, so two
    conditions never share a manifest and a resumed seed never shares one with a
    seed another session wrote.
    """
    return f"{experiment_name(prefix, condition, seed_index, task)}-{task}-{short}"


def experiment_name(prefix: str, condition: str, seed_index: int, task: str) -> str:
    """The experiment directory AppWorld writes the episode's outputs under."""
    return f"{prefix}-{condition}-s{seed_index}-{task}"


def episodes_of(task: str, covered: bool, seeds: int) -> list[tuple[str, int]]:
    """(condition, seed index) for every phase-1 episode of a task, in run order.

    Seed-major: a session cut short leaves whole seeds behind rather than one
    condition's seeds. On a task the carded arm cannot reach only the baseline
    runs (K1): every card-carrying slot is empty there.
    """
    conditions = PHASE_ONE if covered else ("baseline",)
    return [(condition, seed) for seed in range(seeds) for condition in conditions]


def load_sets(root: Path = REPOSITORY) -> dict:
    path = root / SETS
    if not path.exists():
        raise OrderError(f"{SETS} is absent; the analysis sets have not been derived")
    return json.loads(path.read_text(encoding="utf-8"))


def descriptive(connection, sets: dict, prefix: str, short: str) -> dict:
    """Tasks finished, episodes written, the mean duration over every condition.

    Nothing else, and never by condition: an episode's duration follows its model
    calls, so a duration per condition is the primary metric under another name,
    and it may not be read before the full set (the partial-reading rule, K-186).
    """
    seeds = sets["phase_one"]["seeds"]
    written = {
        row[0]: row[1]
        for row in connection.execute(
            "SELECT e.run_id, e.duration_seconds FROM episodes e "
            "WHERE e.run_id LIKE ? "
            "AND EXISTS (SELECT 1 FROM verifier_results v WHERE v.episode_id = e.episode_id)",
            (prefix + "-%",),
        )
    }
    finished = 0
    for task, slots in sets["per_task"].items():
        wanted = episodes_of(task, slots["skills_failures"]["covered"], seeds)
        if all(run_identity(prefix, c, s, task, short) in written for c, s in wanted):
            finished += 1
    durations = [d for d in written.values() if d is not None]
    return {
        "tasks_finished": finished,
        "tasks": len(sets["per_task"]),
        "episodes": len(written),
        "episodes_planned": sets["phase_one"]["episodes"],
        "mean_duration_seconds": round(sum(durations) / len(durations), 1) if durations else None,
    }
