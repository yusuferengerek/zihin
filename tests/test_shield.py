"""The shield's first-stage predicate.

One test per predicate branch, and for each test the **mutation it kills** is
written down. Writing the mutation makes visible what the test protects: whatever
wrong implementation a test cannot catch is a wrong implementation that can be
made in silence.

The predicate is pure, so the tests need neither a database nor AppWorld.
"""

from __future__ import annotations

import pytest

from zihin.shield import (
    Call,
    DenyReason,
    Predicate,
    ShieldMode,
    evaluate,
    load_write_set,
)

# The apps the task is permitted to touch.
ALLOWED = frozenset({"venmo", "spotify"})

# A small write set, in the same shape as the real derivation: (app, template,
# method) -> the apps written into.
WRITE_SET = {
    # read
    ("venmo", "transactions", "GET"): (),
    ("spotify", "library/playlists", "GET"): (),
    # write into an allowed app
    ("venmo", "transactions", "POST"): ("venmo",),
    # write into a disallowed app
    ("gmail", "emails", "POST"): ("gmail",),
    # cross-boundary write: GET, the called app is permitted, the written one is not
    ("venmo", "transactions/{transaction_id}/receipt", "GET"): ("file_system", "venmo"),
    # cross-boundary write, target permitted
    ("venmo", "balance", "POST"): ("venmo", "spotify"),
}


def decision(app: str, endpoint: str, method: str, allowed=ALLOWED):
    return evaluate(Call(app, endpoint, method), allowed, WRITE_SET)


# --- branch 1: read ---


def test_read_is_allowed():
    """A read is never denied: it changes no state.

    Mutation: subjecting reads to the allowed-app set as well. Then the agent
    cannot read an app it was not permitted and exploration dies, while a read
    does nothing irreversible.
    """
    d = decision("venmo", "transactions", "GET")
    assert d.allowed
    assert d.predicate is Predicate.READ
    assert d.reason is None


def test_read_on_a_forbidden_app_is_still_allowed():
    """Reading is unconditionally free, and the rationale was measured (K-69).

    The shield's allowed-app set is inferred from the task text and the inference
    is 75.5% accurate. `phone` is missed in **30 of 147** tasks, and all thirty of
    those need only to *read* `phone` — an instruction saying "find the
    roommates" means reading contact records, not writing them. In the reference
    solutions, zero of those thirty write to `phone`.

    With a read gate we would break one task in five. A read gate cannot be built
    on an inference that is 75% accurate.

    Mutation: applying the `call.app in allowed_apps` check to reads as well.
    """
    d = evaluate(Call("spotify", "library/playlists", "GET"), frozenset({"venmo"}), WRITE_SET)
    assert d.allowed
    assert d.predicate is Predicate.READ


# --- branch 2: write into an allowed app ---


def test_write_within_allowed_apps_is_allowed():
    """Mutation: denying every write. The shield then blocks the task as well."""
    d = decision("venmo", "transactions", "POST")
    assert d.allowed
    assert d.predicate is Predicate.WRITE_WITHIN_ALLOWED_APPS
    assert d.writes_to == ("venmo",)
    assert d.outside == ()


def test_write_to_several_allowed_apps_is_allowed():
    """It passes when every written app is permitted.

    Mutation: computing `outside` as an intersection rather than a difference, or
    looking at a single app and ignoring the rest.
    """
    d = decision("venmo", "balance", "POST")
    assert d.allowed
    assert d.writes_to == ("venmo", "spotify")


# --- branch 3: write into a disallowed app ---


def test_write_outside_allowed_apps_is_denied():
    """Mutation: ignoring the write set and waving every call through."""
    d = decision("gmail", "emails", "POST")
    assert not d.allowed
    assert d.predicate is Predicate.WRITE_OUTSIDE_ALLOWED_APPS
    assert d.reason is DenyReason.WRITE_OUTSIDE_ALLOWED_APPS
    assert d.outside == ("gmail",)


# --- branch 4: cross-app write, the shield's reason to exist ---


def test_cross_app_write_is_denied_even_though_the_called_app_is_allowed():
    """The measured case: the nine `download_*` endpoints (K-41).

    The call is on `venmo` and `venmo` is permitted; it is a GET, so the method
    looks innocent too. But the endpoint writes into `file_system` and that one is
    not permitted.

    **The mutation this test kills is the shield's most likely wrong
    implementation:** taking the written app to be `call.app` instead of reading
    it from the mapping. Under that mutation all nine of the nine pass and the
    shield loses its reason to exist.
    """
    d = decision("venmo", "transactions/{transaction_id}/receipt", "GET")
    assert not d.allowed
    assert d.predicate is Predicate.CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS
    assert d.reason is DenyReason.CROSS_APP_WRITE_OUTSIDE_ALLOWED_APPS
    assert d.outside == ("file_system",)


def test_the_same_call_is_allowed_when_the_written_app_is_permitted():
    """The same call passes when `file_system` is permitted.

    It shows the predicate looks at the written app and does not decide by the
    method being GET or by the endpoint's name. Mutation: blacklisting the
    `download_*` prefix — then this test fails.
    """
    d = decision(
        "venmo",
        "transactions/{transaction_id}/receipt",
        "GET",
        allowed=frozenset({"venmo", "file_system"}),
    )
    assert d.allowed
    assert d.predicate is Predicate.WRITE_WITHIN_ALLOWED_APPS


# --- branch 5: unknown endpoint ---


def test_unknown_endpoint_is_allowed_and_named():
    """An endpoint absent from the write set passes but is marked separately.

    The write set is derived from the complete route table, so an endpoint absent
    from it would 404 anyway. It is named separately rather than folded into
    `READ`: a rise in this count in shadow mode shows the write set has drifted
    from the route table.

    Mutation: counting an unknown endpoint as `READ`. Then the drift becomes
    invisible.
    """
    d = decision("venmo", "no_such_endpoint", "GET")
    assert d.allowed
    assert d.predicate is Predicate.UNKNOWN_ENDPOINT


def test_method_is_part_of_the_key():
    """The same path under a different method is a different endpoint.

    `venmo.transactions` is a read under GET and a write under POST. Mutation:
    dropping the method from the key — then the two collapse into one endpoint and
    one takes the other's decision.
    """
    assert decision("venmo", "transactions", "GET").predicate is Predicate.READ
    assert (
        decision("venmo", "transactions", "POST").predicate is Predicate.WRITE_WITHIN_ALLOWED_APPS
    )


def test_method_case_does_not_matter():
    """Mutation: forgetting to upper-case the key.

    The capture carries the method in lower case (`get` inside
    `api_calls.jsonl`), the derivation in upper case. Without normalisation every
    call becomes an unknown endpoint and the shield does nothing, in silence.
    """
    assert (
        decision("venmo", "transactions", "post").predicate is Predicate.WRITE_WITHIN_ALLOWED_APPS
    )


# --- the reason comes from a closed vocabulary ---


def test_deny_reasons_are_a_closed_vocabulary():
    """No free-text reason.

    The reason feeds the error taxonomy and the three-gate blame attribution.
    Mutation: putting a formatted string in the `reason` field — then both
    consumers receive unparseable data.
    """
    for d in (
        decision("gmail", "emails", "POST"),
        decision("venmo", "transactions/{transaction_id}/receipt", "GET"),
    ):
        assert isinstance(d.reason, DenyReason)
    assert {r.value for r in DenyReason} == {
        "write_outside_allowed_apps",
        "cross_app_write_outside_allowed_apps",
    }


def test_allowing_branches_are_named_too():
    """The allowing branches are named too.

    The mechanism pilot has to know why a call passed, not merely that it did.
    Mutation: naming the predicate only for the denied ones.
    """
    for d in (
        decision("venmo", "transactions", "GET"),
        decision("venmo", "transactions", "POST"),
        decision("venmo", "no_such_endpoint", "GET"),
    ):
        assert d.allowed
        assert isinstance(d.predicate, Predicate)


# --- shadow mode is part of the design ---


def test_shadow_mode_values_match_the_schema():
    """The `shield_violations.mode` CHECK wants exactly these two values.

    Mutation: adding a third mode. The schema refuses it and the violation cannot
    be written.
    """
    assert {m.value for m in ShieldMode} == {"enforce", "shadow"}


def test_the_decision_does_not_depend_on_the_mode():
    """The predicate never sees the mode.

    Shadow mode is the mount point's decision; the predicate gives the same answer
    in both modes. Mutation: passing the mode into the predicate as a parameter —
    then what is measured in shadow mode stops being what gets used in enforce
    mode.
    """
    import inspect

    imza = inspect.signature(evaluate)
    assert "mode" not in imza.parameters
    assert list(imza.parameters) == ["call", "allowed_apps", "write_set"]


# --- against the real derivation ---


def test_the_real_write_set_loads_and_carries_the_download_group():
    """The derived file loads and the nine `download_*` endpoints are in it.

    Mutation: not stripping the leading slash from the path inside
    `load_write_set`, or not expanding the methods. Either shifts the key and the
    real shield finds nothing — while the tests would keep passing against the
    fake set.
    """
    path = "inputs/write-set-static.json"
    try:
        elements = load_write_set(path)
    except FileNotFoundError:
        pytest.skip(f"{path} is absent; `derive_write_set.py` was not run")

    d = evaluate(
        Call("venmo", "transactions/{transaction_id}/receipt", "GET"),
        frozenset({"venmo"}),
        elements,
    )
    assert not d.allowed, "a download_* endpoint must be denied against the real set too"
    assert d.outside == ("file_system",)

    read = evaluate(Call("venmo", "transactions", "GET"), frozenset({"venmo"}), elements)
    assert read.predicate is Predicate.READ
