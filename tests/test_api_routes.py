"""Endpoint resolution, and a health check against a pinned log.

This handle is S-32's sentry. The fault was this: the stopping rule read `app`
and `api` keys off the actions, `api_calls.jsonl` rows carry no such keys,
`.get()` returned None in silence, and the endpoint criterion never worked. The
rule's unit tests used the same invented shape, so every one of them passed.

The tests here close that gap from two sides:

  1. **The shape is pinned.** Every row of the log under `tests/data/` has exactly
     the three keys an `api_calls.jsonl` row has: `method`, `url` and `data`. A
     reader that looks for `app` and `api` keys fails against it.
  2. **A health criterion.** If a many-call log's distinct endpoint count drops to
     one, resolution has collapsed. The broken rule produced exactly that: one
     endpoint per episode, `None.None`.

**Where the sample comes from.** It is synthetic, written by
`scripts/build_api_calls_fixture.py`: 22 calls over ten routes, two of the
templates reached through several ids. It carries no task text, no model output
and no trajectory, and every call's `data` is empty. A copy of a recorded run used
to stand here; every recorded run is an AppWorld experiment output, which is why
it left (S-80).

**What a synthetic log cannot do.** It cannot notice a change in the production
shape: it has the shape the generator gives it. That check is the corpus
measurement: if `experiments/outputs` holds at least one log, every call in it is
checked for the same three keys and for resolution, otherwise the test is skipped.
A live run's own health check lives in `record_run.py --saglik-denetimi` and runs
by itself in the band sweep's preflight.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zihin.api_routes import endpoint_identity, route_table, route_template, split_endpoint

SAMPLE = Path(__file__).parent / "data" / "api_calls-synthetic.jsonl"
# Synthetic: written by scripts/build_api_calls_fixture.py, 22 calls over ten routes.
REQUIRED_KEYS = {"method", "url", "data"}


def _rows() -> list[dict]:
    with SAMPLE.open(encoding="utf-8") as handle:
        return [json.loads(s) for s in handle if s.strip()]


# --- route table ---


def test_route_table_covers_every_app():
    table = route_table()
    assert set(table) == {
        "admin",
        "amazon",
        "api_docs",
        "file_system",
        "gmail",
        "phone",
        "simple_note",
        "splitwise",
        "spotify",
        "supervisor",
        "todoist",
        "venmo",
    }


def test_route_table_size_is_pinned():
    """The pinned AppWorld commit carries 338 distinct path templates.

    If the count drifts the test should fail: if the table empties in silence or
    framework routes leak in, the rule breaks in silence again.
    """
    assert sum(len(v) for v in route_table().values()) == 338


def test_framework_routes_are_excluded():
    table = route_table()
    paths = {path for records in table.values() for _, path, _ in records}
    assert "/openapi.json" not in paths
    assert "/docs" not in paths


# --- resolution ---


@pytest.mark.parametrize(
    ("app", "path", "expected"),
    [
        ("simple_note", "notes/3084", "notes/{note_id}"),
        ("simple_note", "notes", "notes"),
        ("venmo", "friends/susan.burton@gmail.com", "friends/{user_email}"),
        ("venmo", "transactions/42/comments", "transactions/{transaction_id}/comments"),
        ("spotify", "library/playlists", "library/playlists"),
        ("spotify", "music_player/song_queue/3", "music_player/song_queue/{position}"),
    ],
)
def test_known_urls_resolve_to_their_template(app, path, expected):
    assert route_template(app, path) == expected


def test_two_templates_can_match_the_same_path_and_the_method_separates_them():
    """S-36. `phone` carries two pairs of ambiguous templates.

        GET, DELETE  /messages/text/{text_message_id}
        POST         /messages/text/{phone_number}

    The regexes match the same string, so the path alone does not resolve. Given
    the method the separation is exact, because each pair's methods are disjoint.

    The mutation this test kills: dropping the method from resolution. Measured —
    26 recorded calls landed on the wrong template and the shield waved them
    through as unknown endpoints, while two of them were real writes returning
    200.
    """
    assert route_template("phone", "messages/text/9999", "POST") == "messages/text/{phone_number}"
    assert route_template("phone", "messages/text/9999", "GET") == "messages/text/{text_message_id}"
    assert route_template("phone", "messages/voice/9999", "POST") == "messages/voice/{phone_number}"


def test_a_method_the_endpoint_does_not_accept_resolves_to_none():
    """When the path matches but no route accepts this method, the answer is None.

    That is a 405, not "an endpoint we failed to find". Mutation: falling back to
    the path match when the method does not match — then the shield judges a call
    the server would refuse by looking at the wrong endpoint.
    """
    assert route_template("venmo", "transactions", "PUT") is None
    assert route_template("venmo", "transactions", "GET") == "transactions"


def test_unknown_app_and_path_return_none():
    assert route_template("no_such_app", "x") is None
    assert route_template("venmo", "no_such_endpoint/1") is None


def test_identity_falls_back_to_the_concrete_path():
    """An unresolvable path is an endpoint on its own; two different paths are
    two different identities."""
    assert endpoint_identity("venmo", "no_such_endpoint/1") == "venmo.no_such_endpoint/1"
    assert endpoint_identity("venmo", "no_such_endpoint/2") == "venmo.no_such_endpoint/2"


# --- against a real log ---


def test_log_lines_have_exactly_the_three_documented_keys():
    """The core of S-32: there are no `app` and `api` keys."""
    rows = _rows()
    assert rows, "the sample log is empty"
    for row in rows:
        assert set(row) == REQUIRED_KEYS, row


def test_every_recorded_url_resolves():
    unresolved = []
    for row in _rows():
        app, path = split_endpoint(row["url"])
        if route_template(app, path) is None:
            unresolved.append(row["url"])
    assert not unresolved, f"unresolved URL: {unresolved[:5]}"


def test_a_many_call_episode_touches_more_than_one_endpoint():
    """The health criterion. The broken rule produced 1 here.

    If a many-call log has collapsed to a single endpoint, resolution has broken.
    The threshold is not two: the sample's count is ten and a regression would
    take it to one.
    """
    rows = _rows()
    assert len(rows) >= 20, "not enough calls for the health criterion"
    endpoints = {endpoint_identity(*split_endpoint(s["url"])) for s in rows}
    assert len(endpoints) > 1, "a single endpoint in a many-call episode: resolution has collapsed"
    assert len(endpoints) == 10


def test_identity_collapses_ids_but_not_operations():
    """In the same log ids merge and different operations stay apart."""
    rows = _rows()
    concrete = {split_endpoint(s["url"]) for s in rows}
    templated = {endpoint_identity(*split_endpoint(s["url"])) for s in rows}
    assert len(templated) < len(concrete), "the identity abstraction merged nothing"


# --- the whole corpus, when present locally ---

CORPUS = Path(__file__).resolve().parents[1] / "experiments" / "outputs"
NO_CORPUS = (
    "experiments/outputs holds no api_calls.jsonl log: the recorded AppWorld runs are "
    "untracked and are not in this checkout"
)


def _corpus_logs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.glob("*/tasks/*/logs/api_calls.jsonl") if "legacy_" not in str(p)]


def _check_corpus(root: Path) -> int:
    """Checks every call in every log under `root`; returns how many calls it checked.

    Zero logs is a skip, decided when the check runs rather than when the module is
    collected: an empty corpus checks nothing, and nothing checked is not a pass.
    """
    logs = _corpus_logs(root)
    if not logs:
        pytest.skip(NO_CORPUS)
    total = 0
    unresolved: list[str] = []
    key_sets = set()
    for path in logs:
        with path.open(encoding="utf-8") as handle:
            for row in handle:
                if not row.strip():
                    continue
                record = json.loads(row)
                key_sets.add(frozenset(record))
                total += 1
                app, endpoint = split_endpoint(record["url"])
                if route_template(app, endpoint) is None:
                    unresolved.append(record["url"])
    assert total > 0, f"{len(logs)} logs hold no call"
    assert key_sets == {frozenset(REQUIRED_KEYS)}
    assert not unresolved, f"{len(unresolved)}/{total} did not resolve: {unresolved[:5]}"
    return total


def test_the_whole_local_corpus_resolves():
    """Coverage against every recorded run. When measured it was 7138/7138."""
    _check_corpus(CORPUS)


def test_a_corpus_without_logs_skips_instead_of_passing(tmp_path):
    with pytest.raises(pytest.skip.Exception, match="no api_calls.jsonl"):
        _check_corpus(tmp_path / "absent")
    with pytest.raises(pytest.skip.Exception, match="no api_calls.jsonl"):
        _check_corpus(tmp_path)
    # A legacy log is not part of the corpus, so a corpus of legacy logs is empty.
    legacy = tmp_path / "legacy_run" / "tasks" / "t_1" / "logs" / "api_calls.jsonl"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(pytest.skip.Exception, match="no api_calls.jsonl"):
        _check_corpus(tmp_path)
    # The complement: one real-shaped log is checked, call by call.
    log = tmp_path / "run" / "tasks" / "t_1" / "logs" / "api_calls.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    assert _check_corpus(tmp_path) == len(_rows()) == 22
