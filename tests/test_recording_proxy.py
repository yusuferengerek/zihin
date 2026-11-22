"""The proxy's route policy: what it passes and what it cuts.

**Two arms, and without the second the first proves nothing.** The first arm
presents measured real traffic to the policy; all of it must pass, otherwise the
world cannot be built. The second arm tampers with the same calls in the escape
direction; all of it must be cut. With only the first arm green, an "allow
everything" policy would pass too.

**The bodies were measured, not guessed.** The proxy was run in observation mode
and the eleven management bodies the environment server sends were read off it;
four guessed fields turned out wrong (the seed's key is `seed`, the relative path
starts with `./`, the target is `:memory:task_output-<task>`, and
`DELETE /date_time` carries a UUID generated at run time). The constants here
come from that measurement.

The tests need AppWorld's app modules (`get_all_apps`), so they carry the
`appworld` marker.
"""

from __future__ import annotations

import json

import pytest

from zihin.recording_proxy import (
    PROXY_VERSION,
    RouteClass,
    RoutePolicy,
    policy_for_episode,
    task_datetime,
)

pytestmark = pytest.mark.appworld

TASK = "0de03ea_1"
DENEY = "proxy-test"
SEED = 100

# The eleven bodies the environment server really sends. Eight at setup, one per
# step, two at teardown.
REAL_TRAFFIC: list[tuple[str, str, dict]] = [
    (
        "POST",
        "/dbs",
        {
            "create": False,
            "from_db_home_path": f"./data/tasks/{TASK}/dbs",
            "to_db_home_path": f":memory:task_output-{TASK}",
        },
    ),
    ("GET", "/dbs", {}),
    ("POST", "/date_time", {"date_and_time": "2023-05-18T12:00:00"}),
    ("GET", "/date_time", {}),
    ("POST", "/seed", {"seed": SEED}),
    ("POST", "/show_api_response_schemas", {"show_api_response_schemas": True}),
    ("GET", "/show_api_response_schemas", {}),
    (
        "POST",
        "/dbs/save",
        {
            "app_names": [
                "api_docs",
                "supervisor",
                "amazon",
                "phone",
                "file_system",
                "spotify",
                "venmo",
                "gmail",
                "splitwise",
                "simple_note",
                "todoist",
                "admin",
            ],
            "delete_if_exists": True,
            "format": "changes",
            "from_db_home_path": f":memory:task_output-{TASK}",
            "save_model_hashes": True,
            "skip_mandatory_apps": False,
            "to_db_home_path": f"./experiments/outputs/{DENEY}/tasks/{TASK}/dbs",
            "vaccum": False,
        },
    ),
    ("DELETE", "/dbs/cache", {"task_id": TASK}),
    ("DELETE", "/date_time", {"time_freezer_id": "8e48f74a-9baf-49c7-b248-407d9ed328a1"}),
]


@pytest.fixture(scope="module")
def policy() -> RoutePolicy:
    return policy_for_episode(experiment_name=DENEY, task_id=TASK, random_seed=SEED)


def _sunar(policy: RoutePolicy, method: str, path: str, body: dict | None):
    payload = json.dumps(body).encode("utf-8") if body else b""
    return policy.permits(method, path, payload)


# --- first arm: real traffic must pass ---


@pytest.mark.parametrize(("method", "path", "body"), REAL_TRAFFIC)
def test_the_environment_servers_own_traffic_passes(policy, method, path, body):
    """If this arm fails the world cannot be built: cutting the management routes
    entirely was measured to be impossible."""
    allowed, reason = _sunar(policy, method, path, body)
    assert allowed, f"{method} {path} kesildi: {reason}"


def test_the_measured_traffic_covers_every_whitelisted_route(policy):
    """The whitelist must carry no route never seen in real traffic.

    An extra entry would be a permission whose reason was never measured.
    """
    seen = {(m, p) for m, p, _ in REAL_TRAFFIC}
    assert set(policy.expected_management) == seen


# --- second arm: tampered traffic must be cut ---


TAMPERINGS: list[tuple[str, str, str, dict]] = [
    # §6.4's escape route: making the host-side server write wherever it likes.
    (
        "write into the record directory",
        "POST",
        "/dbs/save",
        {
            "app_names": None,
            "delete_if_exists": True,
            "format": "full",
            "from_db_home_path": f":memory:task_output-{TASK}",
            "save_model_hashes": True,
            "skip_mandatory_apps": False,
            "to_db_home_path": "./results",
            "vaccum": False,
        },
    ),
    (
        "escape outside the repository",
        "POST",
        "/dbs/save",
        {
            "app_names": None,
            "delete_if_exists": True,
            "format": "full",
            "from_db_home_path": f":memory:task_output-{TASK}",
            "save_model_hashes": True,
            "skip_mandatory_apps": False,
            "to_db_home_path": "../../../etc",
            "vaccum": False,
        },
    ),
    ("change the seed", "POST", "/seed", {"seed": 7}),
    ("change the world clock", "POST", "/date_time", {"date_and_time": "2024-01-01T00:00:00"}),
    ("change the active task", "POST", f"/activate/task/{TASK}", {}),
    ("activate a different task", "POST", "/activate/task/0a9d82a_1", {}),
    ("read the task list", "GET", "/tasks", {}),
    ("read the supervisor list", "GET", "/supervisors", {}),
    ("change the theme", "POST", "/themes/spotify/dark", {}),
    (
        "load another task database",
        "POST",
        "/dbs",
        {
            "create": False,
            "from_db_home_path": "./data/tasks/0a9d82a_1/dbs",
            "to_db_home_path": ":memory:task_output-0a9d82a_1",
        },
    ),
    ("adding an unknown field", "POST", "/seed", {"seed": SEED, "extra": 1}),
    (
        "skip the required apps",
        "POST",
        "/dbs/save",
        {
            "app_names": None,
            "delete_if_exists": True,
            "format": "full",
            "from_db_home_path": f":memory:task_output-{TASK}",
            "save_model_hashes": True,
            "skip_mandatory_apps": True,
            "to_db_home_path": f"./experiments/outputs/{DENEY}/tasks/{TASK}/dbs",
            "vaccum": False,
        },
    ),
]


@pytest.mark.parametrize(("name", "method", "path", "body"), TAMPERINGS)
def test_tampering_is_refused(policy, name, method, path, body):
    allowed, _ = _sunar(policy, method, path, body)
    assert not allowed, f"{name} passed; that is a hole"


def test_the_refusal_reason_names_the_field(policy):
    """The reason must carry the field name, so nobody has to hunt for which
    criterion held."""
    allowed, reason = _sunar(
        policy,
        "POST",
        "/dbs/save",
        {
            "app_names": None,
            "delete_if_exists": True,
            "format": "full",
            "from_db_home_path": f":memory:task_output-{TASK}",
            "save_model_hashes": True,
            "skip_mandatory_apps": False,
            "to_db_home_path": "./results",
            "vaccum": False,
        },
    )
    assert not allowed
    assert "to_db_home_path" in reason


def test_a_non_json_management_body_is_refused(policy):
    allowed, reason = policy.permits("POST", "/seed", b"tohum=7")
    assert not allowed
    assert "JSON" in reason


# --- app routes ---


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/supervisor/account_passwords"),
        ("POST", "/spotify/songs/9/like"),
        ("GET", "/api_docs/apis"),
        ("DELETE", "/venmo/transactions/12"),
    ],
)
def test_app_routes_pass_untouched(policy, method, path):
    """Deciding on these is the shield's job; the policy only says they exist.
    The two layers are separate."""
    allowed, _ = _sunar(policy, method, path, None)
    assert allowed
    assert policy.classify(method, path) == RouteClass.APP


def test_an_unknown_app_name_is_not_an_app_route(policy):
    """A first segment that is not an app name counts as management, so the
    whitelist is consulted. Otherwise `/dbs` would pass as if it were an app."""
    assert policy.classify("POST", "/dbs/save") == RouteClass.MANAGEMENT
    assert policy.classify("GET", "/no_such_app/x") == RouteClass.MANAGEMENT


# --- policy digest ---


def test_the_digest_changes_when_the_policy_changes(policy):
    """The digest is computed, not incremented by hand: a hand-incremented number
    is a number the hand forgets (the shield's `config_digest` rationale)."""
    other = policy_for_episode(experiment_name=DENEY, task_id=TASK, random_seed=SEED + 1)
    assert policy.digest() != other.digest()
    identical = policy_for_episode(experiment_name=DENEY, task_id=TASK, random_seed=SEED)
    assert policy.digest() == identical.digest()


def test_the_proxy_version_is_recorded():
    assert PROXY_VERSION


def test_the_task_datetime_comes_from_the_task_data():
    """The world's clock is part of the measurement, and taking the criterion from
    the container would empty the filter of meaning."""
    assert task_datetime(TASK) == "2023-05-18T12:00:00"
