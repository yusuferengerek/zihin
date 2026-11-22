"""Pins the shape of the citation sweep over the skeleton and the pilot report.

The sweep's failure mode is silence: a regex that stops matching examines
nothing and reports that everything resolves. That is the class K-103 recorded,
and the remedy is the same one — pin the shape, and prove the floor fires.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]


def _module():
    path = REPOSITORY / "scripts/check_citations.py"
    spec = importlib.util.spec_from_file_location("check_citations", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_citations"] = module
    spec.loader.exec_module(module)
    return module


def test_both_documents_are_still_there() -> None:
    module = _module()
    for name in module.DOCUMENTS:
        assert (REPOSITORY / name).exists(), f"{name} is cited by the sweep but absent"


def test_the_file_pattern_reads_a_citation_with_a_key() -> None:
    module = _module()
    line = "| 2.8 | x | `results/card-demo.json` → `tasks[].entry`, 3 of 3 |"
    assert module.FILE.findall(line) == [("results/card-demo.json", "tasks[].entry")]


def test_the_file_pattern_reads_a_citation_without_a_key() -> None:
    module = _module()
    assert module.FILE.findall("see `results/sandbox-olcum.json` for it") == [
        ("results/sandbox-olcum.json", "")
    ]


def test_a_dotted_key_resolves_through_a_list() -> None:
    module = _module()
    blob = {"tasks": [{"entry": {"block_in_prompt": True}}]}
    value, missing = module.resolve(blob, "tasks[].entry.block_in_prompt")
    assert value is True and missing is None


def test_a_missing_key_is_named() -> None:
    module = _module()
    _, missing = module.resolve({"tasks": [{"entry": {}}]}, "tasks[].nope")
    assert missing == "nope"


def test_the_floor_is_below_what_the_documents_carry() -> None:
    """A floor above the real count would fail every run; below zero would never fire."""
    module = _module()
    assert 0 < module.FLOOR
    found = 0
    for name in module.DOCUMENTS:
        text = (REPOSITORY / name).read_text(encoding="utf-8")
        found += len(module.FILE.findall(text)) + len(module.OTHER_PATH.findall(text))
    assert found >= module.FLOOR, f"{found} citations found, floor is {module.FLOOR}"


# --- the derived-data manifest: three cases, and the archive's unchanged behaviour ---

CITED = "results/packed.json"


def _manifest_tree(root: pathlib.Path, listed: bytes) -> dict[str, str]:
    """A tree whose tracked manifest lists `CITED` with the sha256 of `listed`."""
    (root / "derived").mkdir(parents=True)
    entry = {"path": CITED, "sha256": hashlib.sha256(listed).hexdigest(), "bytes": len(listed)}
    (root / "derived" / "MANIFEST.json").write_text(json.dumps({"files": [entry]}))
    return _module().derived_manifest(root, {"derived/MANIFEST.json"})


def test_a_listed_file_that_is_absent_is_accepted(tmp_path) -> None:
    module = _module()
    manifest = _manifest_tree(tmp_path, b'{"a": {"b": 1}}')
    in_git = {"derived/MANIFEST.json"}
    assert module.file_problem(tmp_path, CITED, "a.b", in_git, manifest) == (
        None,
        "manifest-absent",
    )


def test_a_listed_file_that_matches_resolves_and_its_key_is_checked(tmp_path) -> None:
    module = _module()
    blob = b'{"a": {"b": 1}}'
    manifest = _manifest_tree(tmp_path, blob)
    (tmp_path / "results").mkdir()
    (tmp_path / CITED).write_bytes(blob)
    in_git = {"derived/MANIFEST.json"}
    assert module.file_problem(tmp_path, CITED, "a.b", in_git, manifest) == (None, "manifest")
    problem, how = module.file_problem(tmp_path, CITED, "a.c", in_git, manifest)
    assert how == "manifest" and "has no key 'a.c'" in problem


def test_a_listed_file_that_differs_fails_and_names_the_mismatch(tmp_path) -> None:
    module = _module()
    listed = b'{"a": {"b": 1}}'
    manifest = _manifest_tree(tmp_path, listed)
    (tmp_path / "results").mkdir()
    (tmp_path / CITED).write_bytes(b'{"a": {"b": 2}}')
    problem, how = module.file_problem(tmp_path, CITED, "a.b", {"derived/MANIFEST.json"}, manifest)
    assert how == "manifest"
    assert f"does not match {module.MANIFEST}" in problem
    assert hashlib.sha256(listed).hexdigest() in problem
    assert hashlib.sha256(b'{"a": {"b": 2}}').hexdigest() in problem


def test_without_a_tracked_manifest_nothing_changes(tmp_path) -> None:
    """The archive's case: a manifest on disk that git does not carry vouches for nothing."""
    module = _module()
    _manifest_tree(tmp_path, b"{}")
    assert module.derived_manifest(tmp_path, set()) == {}
    assert module.file_problem(tmp_path, CITED, "", {"x"}, {}) == (
        f"{CITED} does not exist",
        "missing",
    )
    (tmp_path / "results").mkdir()
    (tmp_path / CITED).write_bytes(b"{}")
    problem, how = module.file_problem(tmp_path, CITED, "", {"x"}, {})
    assert how == "untracked" and "git does not carry it" in problem
    assert module.file_problem(tmp_path, CITED, "", {CITED}, {}) == (None, "git")


def test_every_citation_in_the_documents_resolves(capsys) -> None:
    """The sweep itself, run as a test, so a stale citation fails the suite."""
    module = _module()
    if not module.tracked():
        pytest.skip(
            "`git ls-files` is empty here: the CI simulation copies the tracked "
            "files without `.git`. The sweep asks whether a cited artefact is in "
            "the repository and cannot answer that outside one."
        )
    with pytest.raises(SystemExit) as stopped:
        module.main()
        raise SystemExit(0)
    captured = capsys.readouterr().out
    assert stopped.value.code in (0, None), captured
