"""Does the AppWorld database return to its initial state per episode?

This is the second half of stage 1's acceptance criterion. The experiment's whole
statistics rest on episodes being independent of one another; with leakage the
condition comparisons would lose their meaning.

The method: the first run creates a new note, the second run reopens the same
task and tries to read that note. Comparing two empty runs would not be enough —
two empty runs would come out equal even if the reset never worked at all. The
creation step is what makes the check meaningful.

This test needs an installed AppWorld and downloaded data, so it carries the
`appworld` marker and does not run in CI.

**Where the runs write.** AppWorld writes each run under
`<root>/experiments/outputs/<experiment name>/`, and its root is `APPWORLD_ROOT` or
the working directory. The test points the root at its own temporary directory, with
`data` linked back to the downloaded data, so nothing lands in the repository tree.
A run written there would join the local corpus that `test_api_routes` checks.
"""

from __future__ import annotations

import json
import pathlib

import pytest

pytestmark = pytest.mark.appworld

LOGIN = """
profile = apis.supervisor.show_profile()
password = [p for p in apis.supervisor.show_account_passwords()
            if p["account_name"] == "simple_note"][0]["password"]
token = apis.simple_note.login(username=profile["email"], password=password)["access_token"]
"""

YARAT = f"""
{LOGIN}
created = apis.simple_note.create_note(access_token=token, title="zihin probe",
                                       content="stage 1 reset check")
note_id = created["note_id"]
read_back = apis.simple_note.show_note(access_token=token, note_id=note_id)
print(json.dumps({{"note_id": note_id, "title": read_back.get("title")}}))
"""


def _read_back(note_id: int) -> str:
    return f"""
{LOGIN}
try:
    found = apis.simple_note.show_note(access_token=token, note_id={note_id})
    result = {{"found": True, "title": found.get("title")}}
except Exception as error:
    result = {{"found": False, "error": str(error)[:120]}}
print(json.dumps(result))
"""


def _run(task_id: str, experiment_name: str, code: str) -> dict:
    from appworld import AppWorld

    with AppWorld(task_id=task_id, experiment_name=experiment_name) as world:
        output = world.execute(code)
    for line in reversed(output.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    raise AssertionError(f"the sandbox output could not be parsed:\n{output[:800]}")


@pytest.fixture(scope="module")
def task_id() -> str:
    from appworld import load_task_ids

    return load_task_ids("train")[0]


@pytest.fixture
def private_root(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """AppWorld's root moved to this test's own directory; the data is linked, not copied."""
    from appworld.common.path_store import path_store

    data = pathlib.Path(path_store.data).resolve()
    (tmp_path / "data").symlink_to(data, target_is_directory=True)
    monkeypatch.setenv("APPWORLD_ROOT", str(tmp_path))
    return tmp_path


def test_episode_starts_from_a_clean_database(task_id: str, private_root: pathlib.Path) -> None:
    first = _run(task_id, "reset-check-1", YARAT)
    assert first["title"] == "zihin probe", (
        "run 1 could not create the note; the check is meaningless"
    )

    second = _run(task_id, "reset-check-2", _read_back(first["note_id"]))
    assert second["found"] is False, (
        f"the note run 1 created is still there in run 2: {second.get('title')!r}. "
        "The database is not reset between episodes."
    )
    written = sorted(p.name for p in (private_root / "experiments" / "outputs").iterdir())
    assert written == ["reset-check-1", "reset-check-2"], written
