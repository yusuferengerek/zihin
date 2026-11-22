"""The shield's first-stage predicate.

Filters an action before it executes. Open in all five conditions
(`03-architecture.tr.md`), so it is not a condition variable: what changes between
conditions is the cards, not the shield.

**The predicate is pure and separate from the mount point.** Input: the call,
the task's allowed app set, and the write set. Output: a decision. It performs
no I/O, records nothing and blocks nothing. The mount point calls it and acts on
the answer.

The separation is not tidiness. The mount point moves: today the shield sits
where `ApiCapture` wraps `Requester`, and when the sandbox arrives both move to
the loopback recording proxy (K-65). A predicate that carried mounting details
would have to be rewritten at that point, and a rewritten predicate is a
different measuring instrument.

**Two sets, not one.** A call can write into an app other than the one it was
addressed to: nine `download_*` endpoints are GETs on one app that write into
`file_system` through a separate access token (K-41). So the predicate looks up
a *mapping* — endpoint to the apps it writes into — never the API's own app
label. Deriving the target from the calling app would wave all nine through, and
those nine are the reason the shield exists.

**The deny reason comes from a closed vocabulary.** It feeds the error taxonomy
and the three-gate blame attribution; free text would make both unparseable.

**Shadow mode is part of the design, not an addition.** The predicate always
returns the same decision; `ShieldMode` says whether the mount point acts on it.
The mechanism pilot's fourth measurement is the false-positive rate in shadow
mode, and a mode bolted on afterwards would change the shield itself — what was
measured would not be what gets used.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ShieldMode(StrEnum):
    """Whether the mount point acts on the decision.

    The values match the `mode` CHECK on `shield_violations`.
    """

    ENFORCE = "enforce"
    SHADOW = "shadow"


class Predicate(StrEnum):
    """Which branch decided. Recorded on every decision, allow or deny.

    Allowing branches are named too: the mechanism pilot needs to know why a
    call passed, not only that it did.
    """

    READ = "read"
    WRITE_WITHIN_ALLOWED_APPS = "write_within_allowed_apps"
    WRITE_OUTSIDE_ALLOWED_APPS = "write_outside_allowed_apps"
    CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS = "cross_app_write_outside_allowed_apps"
    UNKNOWN_ENDPOINT = "unknown_endpoint"


class DenyReason(StrEnum):
    """Closed vocabulary. No free text reaches the record."""

    WRITE_OUTSIDE_ALLOWED_APPS = "write_outside_allowed_apps"
    CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS = "cross_app_write_outside_allowed_apps"


@dataclass(frozen=True)
class Call:
    """A call as the predicate sees it.

    `endpoint` is the route template, not the concrete path: the write set is
    keyed by template because that is what the static derivation produces.
    Resolving a URL to its template is the mount point's job.
    """

    app: str
    endpoint: str
    method: str


@dataclass(frozen=True)
class Decision:
    allowed: bool
    predicate: Predicate
    reason: DenyReason | None
    writes_to: tuple[str, ...]
    outside: tuple[str, ...]


# Endpoint key -> the apps that endpoint writes into.
WriteSet = dict[tuple[str, str, str], tuple[str, ...]]


def key(call: Call) -> tuple[str, str, str]:
    """The write set's key. One named API per (app, template, method)."""
    return (call.app, call.endpoint, call.method.upper())


def evaluate(call: Call, allowed_apps: frozenset[str], write_set: WriteSet) -> Decision:
    """Decide whether the call may execute.

    A call is denied when it writes into an app the task is not allowed to
    touch. Reads are never denied: they change no state, so they cannot make a
    change irreversible or move the verifier's verdict.

    An endpoint absent from the write set is allowed and recorded as
    `UNKNOWN_ENDPOINT`. The write set is derived from the complete route table,
    so an absent endpoint is one that does not exist and would 404 anyway. It is
    named rather than folded into `READ` so that shadow-mode statistics show it
    separately — a rising count there means the write set has drifted from the
    route table.
    """
    writes_to = write_set.get(key(call))
    if writes_to is None:
        return Decision(True, Predicate.UNKNOWN_ENDPOINT, None, (), ())
    if not writes_to:
        return Decision(True, Predicate.READ, None, (), ())

    outside = tuple(sorted(set(writes_to) - allowed_apps))
    if not outside:
        return Decision(True, Predicate.WRITE_WITHIN_ALLOWED_APPS, None, tuple(writes_to), ())

    # Which vocabulary entry applies depends on whether the offending app is the
    # one the call was addressed to. The distinction is what the taxonomy needs:
    # a cross-app write is a different failure from calling a forbidden app.
    crosses = bool(set(outside) - {call.app})
    reason = (
        DenyReason.CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS
        if crosses
        else DenyReason.WRITE_OUTSIDE_ALLOWED_APPS
    )
    predicate = (
        Predicate.CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS
        if crosses
        else Predicate.WRITE_OUTSIDE_ALLOWED_APPS
    )
    return Decision(False, predicate, reason, tuple(writes_to), outside)


def load_write_set(path: str) -> WriteSet:
    """Reads the write set produced by `scripts/setup/derive_write_set.py`.

    Only the static half exists today. K-41 fixes the write set as
    `static ∪ empirical`; until the empirical half is collected the shield runs
    on the static half alone (S-35 records what that leaves open).
    """
    import json
    import pathlib

    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    write_set: WriteSet = {}
    for record in raw["endpoints"].values():
        endpoint = record["path"].lstrip("/")
        for method in record["methods"]:
            write_set[(record["app"], endpoint, method)] = tuple(record["writes_to"])
    return write_set
