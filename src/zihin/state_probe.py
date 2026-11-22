"""Fingerprints the database state in the middle of an episode.

The empirical write set will be built on top of this (K-41). A static scan
showed that fifteen GET endpoints perform writes, but that is a lower bound:
the scan only sees direct calls in the handler body, not the ones delegated to
a helper function. The empirical set looks at behaviour, so it covers
delegation by construction.

**What it measures.** Row count per model per app. After `create_note` the
`Note` count goes up by one; after `delete_note` it goes down by one.

**What it does not measure, deliberately.** Row counts see inserts and
deletes, not updates. A `PATCH` that changes a field while leaving the row
count alone is invisible to this probe. There is a second layer for that: at
episode close, AppWorld's own `model_hashes.json` reports every change. If an
episode has a model that changed by hash but is not explained by any step's
counts, that episode's actions are marked "possible writer" and the evidence
is treated as weak.

Taking live hashes was possible but expensive: a single app holds more than
three thousand rows, and doing that per step for twelve apps would lengthen
episodes noticeably.
"""

from __future__ import annotations

from typing import Any

# Infrastructure apps whose counts are meaningless. `admin` and `supervisor`
# are used by the framework in every task; `api_docs` is read-only.
INFRASTRUCTURE_APPS = ("admin", "api_docs")


def snapshot(world: Any) -> dict[str, int]:
    """Row count per app and model."""
    collection = getattr(world, "models", None)
    if collection is None:
        return {}
    counts: dict[str, int] = {}
    for app in dir(collection):
        if app.startswith("_") or app in INFRASTRUCTURE_APPS:
            continue
        models = getattr(collection, app, None)
        if models is None:
            continue
        for model_name in dir(models):
            if model_name.startswith("_") or model_name == "SQLModel":
                continue
            model = getattr(models, model_name, None)
            counter = getattr(model, "count", None)
            if not callable(counter):
                continue
            try:
                counts[f"{app}.{model_name}"] = int(counter())
            except Exception:
                # A model that cannot be counted is not skipped silently, it is
                # marked as missing so it is never mistaken for "unchanged".
                counts[f"{app}.{model_name}"] = -1
    return counts


def diff(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    """Difference between two fingerprints. Only changed models are returned."""
    changed: dict[str, int] = {}
    for name in set(before) | set(after):
        previous = before.get(name)
        following = after.get(name)
        if previous is None or following is None or previous < 0 or following < 0:
            continue
        if previous != following:
            changed[name] = following - previous
    return changed
