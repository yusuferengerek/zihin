"""Is the API capture's recording order right?

What is really under test here is not a behaviour but an order. `Requester._get`
and its siblings call `raise_if_failure` before returning and raise on a failed
response. If the recording is taken after the exception, failed calls are never
recorded and the measurement looks green.

This happened exactly once: in the first probe all seven of seven calls were
reported as 200 while two of them had failed. The order is pinned by a test for
that reason; if someone refactors and breaks it later, it fails here.

The tests use a fake Requester class, so they need no AppWorld installation and
they run in CI.
"""

from __future__ import annotations

import pytest

from zihin.api_capture import ApiCapture, CapturedCall, capturing, install, uninstall


class FakeResponse:
    def __init__(self, status_code: int, body):
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self):
        return self._body


class FakeError(Exception):
    """Imitates the exception AppWorld raises on a failed response."""


class FakeTracker:
    """The relevant surface of AppWorld's `request_tracker` object."""

    def __init__(self):
        self.requests: list[dict] = []

    def add_request(self, method: str, url: str) -> None:
        self.requests.append({"method": method, "url": url})


class FakeRequester:
    """Imitates the two relevant behaviours of the real one.

    First: the `raise` happens before the return. Second: the framework's own
    internal calls are not written to the tracker.
    """

    def __init__(self):
        self.request_tracker = FakeTracker()

    def _get(self, url, data=None, track=True, **kwargs):
        if track:
            self.request_tracker.add_request("get", url)
        if url.endswith("/yok"):
            raise FakeError('Response status code is 404:\n{"message":"Not found"}')
        return FakeResponse(200, {"url": url})

    def _post(self, url, data=None, track=True, **kwargs):
        if track:
            self.request_tracker.add_request("post", url)
        if data and data.get("password") == "wrong":
            raise FakeError('Response status code is 401:\n{"message":"Invalid credentials"}')
        return FakeResponse(200, {"token": "abc"})


def test_successful_call_is_captured_with_body():
    with capturing(FakeRequester) as capture:
        FakeRequester()._get("/spotify/songs")
    assert len(capture.calls) == 1
    call = capture.calls[0]
    assert call.method == "get"
    assert call.url == "/spotify/songs"
    assert call.status_code == 200
    assert call.response == {"url": "/spotify/songs"}
    assert call.error_class is None
    assert call.succeeded


def test_failing_call_is_captured_before_the_exception_propagates():
    """The rule itself. If the recording is not taken before the raise, this test fails."""
    with capturing(FakeRequester) as capture:
        with pytest.raises(FakeError):
            FakeRequester()._get("/spotify/yok")
    assert len(capture.calls) == 1, "the failed call was never recorded"
    call = capture.calls[0]
    assert call.error_class == "FakeError"
    assert call.status_code == 404
    assert not call.succeeded


def test_status_code_is_recovered_from_the_exception_text():
    """The exception does not carry the response object; the status code is
    parsed out of its text."""
    with capturing(FakeRequester) as capture:
        with pytest.raises(FakeError):
            FakeRequester()._post("/spotify/auth/token", {"password": "wrong"})
    assert capture.calls[0].status_code == 401


def test_capture_keeps_order_across_success_and_failure():
    with capturing(FakeRequester) as capture:
        istemci = FakeRequester()
        istemci._get("/a")
        with pytest.raises(FakeError):
            istemci._get("/yok")
        istemci._get("/b")
    assert [c.url for c in capture.calls] == ["/a", "/yok", "/b"]
    assert [c.succeeded for c in capture.calls] == [True, False, True]


def test_drain_empties_the_buffer():
    """This is how the step boundary is drawn: the calls accumulated between two executes."""
    with capturing(FakeRequester) as capture:
        istemci = FakeRequester()
        istemci._get("/a")
        birinci = capture.drain()
        istemci._get("/b")
        second = capture.drain()
    assert [c.url for c in birinci] == ["/a"]
    assert [c.url for c in second] == ["/b"]
    assert capture.drain() == []


def test_uninstall_restores_the_original_methods():
    ozgun_get = FakeRequester._get
    capture = ApiCapture()
    ozgun = install(capture, FakeRequester)
    assert FakeRequester._get is not ozgun_get
    uninstall(ozgun, FakeRequester)
    assert FakeRequester._get is ozgun_get


def test_wrapper_does_not_swallow_the_exception():
    """If the wrapper takes the recording and swallows the exception, the
    agent's error path breaks."""
    with capturing(FakeRequester) as capture:
        with pytest.raises(FakeError):
            FakeRequester()._get("/yok")
    assert capture.calls[0].error_class == "FakeError"


def test_framework_internal_calls_are_not_captured():
    """The framework's own internal calls are not the agent's actions.

    AppWorld does not write calls such as `/supervisor/active_task` to its own
    tracker. If the capture recorded them, every step would gain a ghost action;
    in a real run 2 actions per step were counted instead of 1, and the difference
    was only visible because two sources were being compared.
    """
    with capturing(FakeRequester) as capture:
        istemci = FakeRequester()
        istemci._get("/supervisor/active_task", track=False)
        istemci._get("/spotify/songs")
    assert [c.url for c in capture.calls] == ["/spotify/songs"]


def test_untracked_failing_call_is_also_skipped():
    with capturing(FakeRequester) as capture:
        istemci = FakeRequester()
        with pytest.raises(FakeError):
            istemci._get("/yok", track=False)
    assert capture.calls == []


def test_capture_matches_the_frameworks_own_count():
    """The captured call count must match the framework's own count exactly."""
    with capturing(FakeRequester) as capture:
        istemci = FakeRequester()
        istemci._get("/a")
        istemci._get("/internal", track=False)
        with pytest.raises(FakeError):
            istemci._get("/yok")
    assert len(capture.calls) == len(istemci.request_tracker.requests)


def test_captured_call_marks_non_200_as_unsuccessful():
    call = CapturedCall(
        method="get", url="/x", data=None, status_code=500, response={}, error_class=None
    )
    assert not call.succeeded
