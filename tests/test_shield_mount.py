"""The shield's mount point: does the predicate actually see live calls?

`test_shield.py` covers the predicate branch by branch. This handle covers the
wiring, which is a separate failure surface and has already produced its own
class of bug in this project: a function was corrected and its caller kept
taking the old path, so the correction never reached the measurement.

So the tests here do not re-verify decisions. They verify that

  * the wrapper consults the shield at all, and **before** the call runs,
  * resolution happens with the method (S-36 reaches the mount too),
  * shadow mode changes nothing about what the wrapper did before,
  * violations drain at the step boundary rather than accumulating over the
    episode,
  * enforce mode refuses to be constructed while its response shape is
    undecided.

The fake Requester is the one from `test_api_capture.py`, deliberately: the two
handles have to see the same wrapper, and a second fake would let the two drift.
"""

from __future__ import annotations

import pytest
from tests.test_api_capture import FakeError, FakeRequester

from zihin.api_capture import capturing
from zihin.shield import ShieldMode
from zihin.shield_mount import ShieldMount

# A hand-written write set, not the derived one. The derived file is the
# shield's input under measurement; a test that read it would fail whenever the
# derivation changed, and it would be testing the derivation, not the mount.
WRITE_SET = {
    ("spotify", "songs", "GET"): (),
    ("spotify", "player/pause", "POST"): ("spotify",),
    ("spotify", "downloads", "POST"): ("file_system",),
    ("phone", "messages/text/{phone_number}", "POST"): ("phone",),
    ("phone", "messages/text/{text_message_id}", "GET"): (),
}


def mount(*allowed: str) -> ShieldMount:
    return ShieldMount(allowed_apps=frozenset(allowed), write_set=WRITE_SET)


# --- the wrapper consults the shield ---


def test_the_wrapper_asks_the_shield_on_every_call():
    """The mount is dead code unless the wrapper calls it.

    Mutation this kills: dropping the `capture.shield.check(...)` line. Every
    other test in this handle would still pass, because they could all be
    satisfied by calling `check` directly.
    """
    shield = mount("spotify")
    with capturing(FakeRequester, shield=shield):
        FakeRequester()._get("/spotify/songs")
        FakeRequester()._post("/spotify/player/pause")
    assert sum(shield.predicate_counts.values()) == 2


def test_the_shield_sees_the_call_even_when_it_fails():
    """A denied write that would have failed anyway is still a decision.

    Mutation: moving the check inside the `try` after `real(...)`. Then a call
    that raises is never judged, and enforce mode would let exactly the calls
    the server rejects go unrecorded.
    """
    shield = mount("spotify")
    with capturing(FakeRequester, shield=shield), pytest.raises(FakeError):
        FakeRequester()._get("/spotify/yok")
    assert sum(shield.predicate_counts.values()) == 1


def test_shadow_mode_changes_nothing_the_wrapper_did():
    """Shadow means shadow: the same calls, the same captures, the same bodies.

    Mutation: making the mount swallow, alter or short-circuit a call. Shadow
    mode is what the block rate gets measured in, and a shadow that perturbed
    the run would measure a different run.
    """
    shield = mount()  # allows nothing: every write is a violation
    with capturing(FakeRequester, shield=shield) as with_shield:
        FakeRequester()._post("/spotify/player/pause", {"x": 1})
    with capturing(FakeRequester) as without:
        FakeRequester()._post("/spotify/player/pause", {"x": 1})

    assert shield.violations, "the write should have been a violation"
    assert len(with_shield.calls) == len(without.calls) == 1
    assert with_shield.calls[0] == without.calls[0]


def test_no_shield_leaves_the_wrapper_exactly_as_it_was():
    with capturing(FakeRequester) as capture:
        FakeRequester()._get("/spotify/songs")
    assert capture.shield is None
    assert len(capture.calls) == 1


# --- resolution ---


def test_resolution_passes_the_method_through():
    """S-36 reaches the mount as well.

    `phone` carries two templates that match the same string and differ only by
    method. If the mount resolved without the method, the POST would land on
    the GET template, find an empty write set there and be recorded as a read.

    Mutation: dropping the method argument in `check`.
    """
    shield = mount()
    shield.check("post", "/phone/messages/text/5551234", None)
    assert shield.predicate_counts["write_outside_allowed_apps"] == 1

    shield.check("get", "/phone/messages/text/5551234", None)
    assert shield.predicate_counts["read"] == 1


def test_an_unresolvable_path_is_passed_through_as_itself():
    """The fail-open branch. It is named so a rise in it is visible."""
    shield = mount()
    shield.check("get", "/spotify/no_such_endpoint", None)
    assert shield.predicate_counts["unknown_endpoint"] == 1
    assert not shield.violations


def test_a_cross_app_write_is_caught_through_the_mount():
    """The nine `download_*` endpoints are the reason the shield exists.

    Allowed to touch spotify, not allowed to touch file_system: the call is
    addressed to spotify and writes to file_system.
    """
    shield = mount("spotify")
    shield.check("post", "/spotify/downloads", None)
    assert shield.predicate_counts["cross_app_write_outside_allowed_apps"] == 1
    assert shield.violations[0].reason == "cross_app_write_outside_allowed_apps"


# --- the recorded row ---


def test_the_violation_row_holds_the_concrete_path_not_the_template():
    """The row has to line up with the `actions` row for the same call.

    `actions.api` is what `split_endpoint` produced; if the violation held the
    template instead, joining the two tables on (app, api) would silently match
    nothing.
    """
    shield = mount()
    shield.check("post", "/phone/messages/text/5551234", {"message": "hi"})
    row = shield.violations[0]
    assert (row.app, row.api) == ("phone", "messages/text/5551234")
    assert row.http_method == "POST"
    assert row.raw_parameters == {"message": "hi"}
    assert row.mode == "shadow"


def test_a_call_with_no_body_records_an_empty_dict_not_none():
    """`shield_violations.raw_parameters` is NOT NULL."""
    shield = mount()
    shield.check("post", "/spotify/player/pause", None)
    assert shield.violations[0].raw_parameters == {}


# --- draining ---


def test_violations_drain_at_the_step_boundary():
    """A violation belongs to the step whose code produced it.

    Mutation: returning the list without clearing it. Then every step after the
    first would re-record every earlier violation, and `shield_violations`
    would grow quadratically while looking plausible.
    """
    shield = mount()
    shield.check("post", "/spotify/player/pause", None)
    first = shield.drain()
    assert len(first) == 1

    shield.check("post", "/spotify/downloads", None)
    second = shield.drain()
    assert len(second) == 1
    assert second[0].api == "downloads"
    assert shield.drain() == []


def test_draining_does_not_reset_the_counts():
    """The counts are per episode; the violations are per step.

    They are drained by different consumers and a shared reset would make the
    predicate distribution report only the last step.
    """
    shield = mount()
    shield.check("post", "/spotify/player/pause", None)
    shield.drain()
    shield.check("get", "/spotify/songs", None)
    assert sum(shield.predicate_counts.values()) == 2


# --- enforce ---


def test_enforce_mode_refuses_to_be_constructed():
    """Enforce is not mounted, and the refusal is loud on purpose.

    Blocking means the call never reaches the server, so something has to stand
    in for the response the agent expected. An exception, a 403 body and an
    empty result produce three different trajectories, so the substitute is a
    condition variable and is not decided yet.

    A mount that silently behaved like shadow while claiming to enforce would
    produce a run whose manifest said `enforce` and whose behaviour was
    `shadow`. Failing at construction makes that impossible.
    """
    with pytest.raises(NotImplementedError, match="shadow"):
        ShieldMount(allowed_apps=frozenset(), write_set=WRITE_SET, mode=ShieldMode.ENFORCE)
