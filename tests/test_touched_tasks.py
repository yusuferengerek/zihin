"""The touched-task list: derived from the record, refused when it falls behind.

The list was hand-written once and fell four tasks behind the record, all four in
the evaluation sample. These tests build records with the real schema and show
that the loader refuses each way the list and the record can disagree - and that
the four measurement scripts cannot read the list any other way.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from zihin.records import insert_episode, insert_run_manifest, open_database
from zihin.touched import (
    RECORD_SERIES,
    TOUCHED,
    TouchedListError,
    derive,
    load_touched,
    render,
    structural_problems,
)

REPOSITORY = Path(__file__).resolve().parents[1]
MODEL = "qwen2.5-coder:32b-instruct-q4_K_M"
# A stand-in for AppWorld's split lists, so the synthetic records need no data.
SPLIT_OF = {
    "a_1": "test_normal",
    "b_1": "test_normal",
    "c_1": "train",
    "d_1": "train",
    "e_1": "test_normal",
    "f_1": "test_normal",
    "x_1": "test_challenge",
}
# The scripts that read the list themselves. `measure_interval_width.py` used to be
# one; it now takes its sample from `derive_pass_threshold.action_stratum`, which
# reads the list through the loader (K-174).
READERS = (
    "scripts/setup/measure_task_types.py",
    "scripts/setup/derive_pass_threshold.py",
    "scripts/setup/measure_sample_size.py",
)


def _manifest(run_id: str) -> dict:
    return {
        "run_id": run_id,
        "created_at": "uptime:1.0",
        "model_tag": MODEL,
        "num_ctx_requested": 32768,
        "num_ctx_effective": 32768,
        "context_verified": 1,
        "kv_cache_type": "q8_0",
        "flash_attention": 1,
        "temperature": 0.2,
        "base_seed": 123,
        "keep_alive": "30m0s",
        "no_progress_limit": 40,
        "max_output_tokens": 4000,
        "max_prompt_characters": 50000,
        "model_server_env": {"OLLAMA_CONTEXT_LENGTH": "32768"},
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": "deadbeef",
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux / 3.11",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }


def _episode(db, run: str, task: str, *, condition: str = "baseline", split: str | None = None):
    run_id = f"{run}-{task}-{task}-32b"
    insert_run_manifest(db, **_manifest(run_id))
    insert_episode(
        db,
        run_id=run_id,
        task_id=task,
        split=split or SPLIT_OF[task],
        condition=condition,
        model_ref=MODEL,
        seed=1,
        sequence_in_run=1,
        model_load_state="cold",
        step_ceiling=20,
        started_at="uptime:1.0",
    )


def _record(root: Path, episodes: dict[str, list[tuple]]) -> None:
    """One file per series; each series gets the episodes named for it."""
    (root / "results").mkdir(parents=True, exist_ok=True)
    for name in RECORD_SERIES:
        db = open_database(root / name)
        with db:
            for args in episodes.get(name, []):
                run, task, *rest = args
                _episode(db, run, task, **(rest[0] if rest else {}))
        db.close()


def _write_list(root: Path, document: dict) -> None:
    (root / TOUCHED).write_text(render(document), encoding="utf-8")


@pytest.fixture
def record(tmp_path):
    _record(
        tmp_path,
        {
            RECORD_SERIES[0]: [("bant", "a_1")],
            RECORD_SERIES[1]: [
                ("uckol-cards-0", "a_1", {"condition": "skills_failures"}),
                ("demo", "b_1"),
            ],
            # recorded as train, belongs to test_normal: the 024c982_1 case
            RECORD_SERIES[2]: [("bir1", "c_1"), ("bir1-onkontrol", "b_1", {"split": "train"})],
        },
    )
    return tmp_path


def _derived(root: Path) -> dict:
    return derive([root / name for name in RECORD_SERIES], SPLIT_OF)


def test_every_episode_counts_and_the_split_comes_from_appworld(record):
    document = _derived(record)
    assert document["test_normal"] == ["a_1", "b_1"]
    assert document["train"] == ["c_1"]
    assert document["test_challenge"] == []
    runs = {(e["run"], e["condition"]) for e in document["provenance"]["a_1"]}
    assert runs == {("bant", "baseline"), ("uckol-cards-0", "skills_failures")}
    assert document["recorded_split_disagrees"] == {
        "b_1": {"appworld": "test_normal", "recorded": {"train": 1}}
    }
    assert structural_problems(document) == []


def test_a_list_that_agrees_with_the_whole_record_loads(record):
    _write_list(record, _derived(record))
    touched = load_touched(record, split_of=SPLIT_OF)
    assert touched.basis == "checked against the full record"
    assert touched.tasks("test_normal") == ["a_1", "b_1"]


def test_a_list_behind_the_record_is_refused(record):
    document = _derived(record)
    document["test_normal"].remove("b_1")
    del document["provenance"]["b_1"]
    _write_list(record, document)
    with pytest.raises(TouchedListError, match=r"test_normal: the record touched \['b_1'\]"):
        load_touched(record, split_of=SPLIT_OF)


def test_a_list_ahead_of_the_record_is_refused(record):
    document = _derived(record)
    document["train"].append("d_1")
    document["provenance"]["d_1"] = [
        {
            "series": "zihin.sqlite",
            "run": "x",
            "condition": "baseline",
            "model": MODEL,
            "episodes": 1,
        }
    ]
    _write_list(record, document)
    with pytest.raises(TouchedListError, match=r"never ran it"):
        load_touched(record, split_of=SPLIT_OF)


def test_a_changed_provenance_is_refused_even_when_the_lists_agree(record):
    document = _derived(record)
    document["provenance"]["a_1"][0]["episodes"] += 1
    _write_list(record, document)
    with pytest.raises(TouchedListError, match="provenance or the sources differ"):
        load_touched(record, split_of=SPLIT_OF)


def test_one_challenge_episode_is_refused(record):
    document = _derived(record)
    _write_list(record, document)
    db = open_database(record / RECORD_SERIES[2])
    with db:
        _episode(db, "probe", "x_1")
    db.close()
    # The refusal is also reached through the comparison and, for a list that names
    # the task, through the structure check; this asserts that the reason given is
    # the split's, not a generic disagreement.
    with pytest.raises(TouchedListError, match="setup may not touch it"):
        load_touched(record, split_of=SPLIT_OF)


def test_a_partial_record_checks_containment_and_says_so(record):
    _write_list(record, _derived(record))
    (record / RECORD_SERIES[0]).unlink()
    touched = load_touched(record, split_of=SPLIT_OF)
    assert touched.basis.startswith("partial record")
    # a new touch in the part that is present is still caught
    db = open_database(record / RECORD_SERIES[2])
    with db:
        _episode(db, "fresh", "d_1")
    db.close()
    with pytest.raises(TouchedListError, match="omits tasks the present part"):
        load_touched(record, split_of=SPLIT_OF)


def test_no_record_checks_structure_only_and_says_so(tmp_path):
    (tmp_path / "results").mkdir()
    document = {"what": "x", "sources": [], "train": [], "dev": [], "test_normal": ["a_1"]}
    document["test_challenge"] = []
    document["provenance"] = {
        "a_1": [{"series": "s", "run": "r", "condition": "c", "model": "m", "episodes": 1}]
    }
    _write_list(tmp_path, document)
    assert load_touched(tmp_path).basis.startswith("no record here")


@pytest.mark.parametrize(
    "break_it",
    [
        lambda d: d["test_normal"].reverse(),
        lambda d: d["train"].append(d["test_normal"][0]),
        lambda d: d["test_challenge"].append("x_1"),
        lambda d: d["provenance"].pop("a_1"),
        lambda d: d["provenance"]["a_1"][0].update(episodes=0),
    ],
    ids=["unsorted", "two-splits", "challenge", "provenance-missing", "zero-episodes"],
)
def test_each_structural_defect_is_named(record, break_it):
    document = _derived(record)
    break_it(document)
    assert structural_problems(document)


def test_the_committed_list_is_well_formed():
    document = json.loads((REPOSITORY / TOUCHED).read_text(encoding="utf-8"))
    assert structural_problems(document) == []


@pytest.mark.appworld
def test_every_committed_task_is_in_the_split_it_is_listed_under():
    from zihin.touched import SPLITS, split_membership

    split_of = split_membership()
    document = json.loads((REPOSITORY / TOUCHED).read_text(encoding="utf-8"))
    misplaced = [
        (task, split, split_of.get(task))
        for split in SPLITS
        for task in document[split]
        if split_of.get(task) != split
    ]
    assert misplaced == []


@pytest.mark.parametrize("reader", READERS)
def test_every_reader_goes_through_the_loader(reader):
    """No reader opens the file itself; each calls `load_touched`."""
    source = (REPOSITORY / reader).read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "load_touched" in calls
    assert "touched-tasks.json" not in source


def test_nothing_but_the_loader_names_the_file() -> None:
    """No script can open the list by its path: the loader is the only way in.

    The generator names the file in its own description, and writes it through the
    loader module's constant.
    """
    naming = sorted(
        path.relative_to(REPOSITORY).as_posix()
        for tree in ("src", "scripts")
        for path in (REPOSITORY / tree).rglob("*.py")
        if "touched-tasks.json" in path.read_text(encoding="utf-8")
    )
    assert naming == ["scripts/setup/build_touched_tasks.py", "src/zihin/touched.py"]


# --- the experiment boundary (K-178) ---


def _add(root: Path, run: str, task: str) -> None:
    db = open_database(root / RECORD_SERIES[2])
    with db:
        _episode(db, run, task)
    db.close()


def test_the_experiment_does_not_change_the_list(record):
    before = _derived(record)
    _write_list(record, before)
    _add(record, "dny", "e_1")
    _add(record, "dny-s1", "e_1")
    assert render(_derived(record)) == render(before)
    assert load_touched(record, split_of=SPLIT_OF).basis == "checked against the full record"


def test_a_new_run_outside_the_experiment_changes_the_list(record):
    _write_list(record, _derived(record))
    _add(record, "fresh", "f_1")
    assert "f_1" in _derived(record)["test_normal"]
    with pytest.raises(TouchedListError, match=r"the record touched \['f_1'\]"):
        load_touched(record, split_of=SPLIT_OF)


def test_the_control_prefix_is_a_touch(record):
    """A preflight of the experiment is a touch like any other run."""
    _add(record, "dnyk", "f_1")
    assert "f_1" in _derived(record)["test_normal"]


def test_a_preflight_under_the_experiment_prefix_is_refused(record):
    _write_list(record, _derived(record))
    _add(record, "dny-onkontrol3", "e_1")
    with pytest.raises(TouchedListError, match="preflight under the experiment's prefix"):
        load_touched(record, split_of=SPLIT_OF)


@pytest.mark.parametrize(
    "task, why",
    [("a_1", "which setup touched"), ("c_1", "from train"), ("x_1", "from test_challenge")],
    ids=["touched", "train", "challenge"],
)
def test_an_experiment_episode_outside_the_sample_is_refused(record, task, why):
    _write_list(record, _derived(record))
    _add(record, "dny", task)
    with pytest.raises(TouchedListError, match=why):
        load_touched(record, split_of=SPLIT_OF)


def test_the_prefixes_are_the_ones_section_19_declares():
    from zihin.declared import EXPERIMENT_CONTROL_PREFIX, EXPERIMENT_PREFIX

    for name in ("experiments/setup-protocol.tr.md", "experiments/setup-protocol.en.md"):
        text = (REPOSITORY / name).read_text(encoding="utf-8")
        section = text[text.index("\n## 19. ") :]
        assert f"`{EXPERIMENT_PREFIX}`" in section, name
        assert f"`{EXPERIMENT_CONTROL_PREFIX}`" in section, name
