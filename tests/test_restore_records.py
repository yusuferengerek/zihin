"""scripts/restore_records.py: the record databases come back only as the manifest says.

The assets here are packed the way the record assets are: AppWorld's own `pack_bundle`
and constants, files under `<name>/`. They hold stand-in bytes, not databases, because
the script checks bytes and sha256 and never opens the file. The installed `appworld`
command opens them, as it does for a reader.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import types

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts" / "restore_records.py"
COMMITTED = REPOSITORY / "records" / "MANIFEST.json"


def _load():
    spec = importlib.util.spec_from_file_location("restore_records", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["restore_records"] = module
    spec.loader.exec_module(module)
    return module


restore_records = _load()
RestoreError = restore_records.RestoreError


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack(directory: pathlib.Path, name: str, files: dict[str, bytes], asset: str = "") -> None:
    """One asset, packed as the record assets are; `asset` renames the file."""
    import appworld.leaderboard as leaderboard
    from appworld.common.crypto import pack_bundle

    staging = pathlib.Path(tempfile.mkdtemp(dir=directory.parent))
    base = staging / "experiments" / "outputs"
    for path, data in files.items():
        target = base / name / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    pack_bundle(
        bundle_file_path=str(directory / (asset or f"{name}.bundle")),
        base_directory=str(base),
        include_directories=[name],
        password=leaderboard.PASSWORD,
        salt=leaderboard.SALT,
    )
    shutil.rmtree(staging)


def entry(name: str, data: bytes, path: str = "") -> dict:
    return {
        "asset": f"{name}.bundle",
        "name": name,
        "path": path or f"results/{name}.sqlite",
        "sha256": digest(data),
        "bytes": len(data),
        "episodes": 1,
    }


def write_manifest(path: pathlib.Path, entries: list[dict]) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"databases": entries}), encoding="utf-8")
    return path


def files_under(directory: pathlib.Path) -> list[str]:
    return sorted(p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file())


@pytest.fixture
def world(tmp_path):
    repository = tmp_path / "repository"
    (repository / "results").mkdir(parents=True)
    assets = tmp_path / "assets"
    assets.mkdir()
    a = b"stand-in for database a\n" * 200
    b = b"stand-in for database b\n" * 300
    pack(assets, "a", {"results/a.sqlite": a})
    pack(assets, "b", {"results/b.sqlite": b})
    manifest = write_manifest(tmp_path / "MANIFEST.json", [entry("a", a), entry("b", b)])
    return types.SimpleNamespace(
        root=tmp_path, repository=repository, assets=assets, manifest=manifest, a=a, b=b
    )


def test_every_asset_is_restored_under_results_and_matches_the_manifest(world):
    outcome = restore_records.restore(world.repository, world.assets, world.manifest)
    assert outcome.written == ["results/a.sqlite", "results/b.sqlite"]
    assert outcome.in_place == [] and outcome.missing == []
    assert (world.repository / "results/a.sqlite").read_bytes() == world.a
    assert (world.repository / "results/b.sqlite").read_bytes() == world.b
    assert files_under(world.repository) == ["results/a.sqlite", "results/b.sqlite"]
    assert files_under(world.assets) == ["a.bundle", "b.bundle"]


def test_a_second_run_writes_nothing_and_reports_the_files_in_place(world):
    restore_records.restore(world.repository, world.assets, world.manifest)
    outcome = restore_records.restore(world.repository, world.assets, world.manifest)
    assert outcome.written == []
    assert outcome.in_place == ["results/a.sqlite", "results/b.sqlite"]


def test_a_file_in_place_with_other_content_stops_the_run_before_any_write(world):
    (world.repository / "results/b.sqlite").write_bytes(b"someone's own file")
    with pytest.raises(RestoreError, match="different sha256; it is not overwritten"):
        restore_records.restore(world.repository, world.assets, world.manifest)
    assert (world.repository / "results/b.sqlite").read_bytes() == b"someone's own file"
    assert not (world.repository / "results/a.sqlite").exists()


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("../outside.sqlite", "escapes the repository"),
        ("/tmp/outside.sqlite", "escapes the repository"),
        ("results/../../outside.sqlite", "escapes the repository"),
        ("results/../src/a.sqlite", "escapes the repository"),
        ("src/a.sqlite", "is not a path under results/"),
        ("results", "is not a path under results/"),
    ],
)
def test_the_manifest_reader_refuses_a_path_outside_results(world, path, message):
    manifest = write_manifest(world.root / "bad.json", [entry("a", world.a, path)])
    with pytest.raises(RestoreError, match=message):
        restore_records.read_manifest(manifest)
    with pytest.raises(RestoreError, match=message):
        restore_records.restore(world.repository, world.assets, manifest)
    assert files_under(world.repository) == []
    assert not (world.root / "outside.sqlite").exists()


def test_a_results_directory_that_leads_outside_the_repository_is_refused(world):
    elsewhere = world.root / "elsewhere"
    elsewhere.mkdir()
    (world.repository / "results").rmdir()
    (world.repository / "results").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(RestoreError, match="outside the repository's results/"):
        restore_records.restore(world.repository, world.assets, world.manifest)
    assert files_under(elsewhere) == []


def test_a_restored_file_whose_sha256_differs_from_the_manifest_is_not_written(world):
    entries = [entry("a", world.a), {**entry("b", world.b), "sha256": "0" * 64}]
    manifest = write_manifest(world.root / "wrong.json", entries)
    with pytest.raises(RestoreError, match="sha256 does not match the manifest"):
        restore_records.restore(world.repository, world.assets, manifest)
    assert files_under(world.repository) == []


def test_a_restored_file_whose_size_differs_from_the_manifest_is_not_written(world):
    entries = [entry("a", world.a), {**entry("b", world.b), "bytes": len(world.b) + 1}]
    manifest = write_manifest(world.root / "wrong.json", entries)
    with pytest.raises(RestoreError, match="bytes restored, the manifest says"):
        restore_records.restore(world.repository, world.assets, manifest)
    assert files_under(world.repository) == []


def test_an_asset_packed_under_another_name_is_refused(world):
    (world.assets / "b.bundle").unlink()
    pack(world.assets, "c", {"results/b.sqlite": world.b}, asset="b.bundle")
    with pytest.raises(RestoreError, match="appworld unpack b failed|does not carry"):
        restore_records.restore(world.repository, world.assets, world.manifest)
    assert files_under(world.repository) == []


def test_an_asset_that_does_not_open_reports_the_unpack_failure(world):
    (world.assets / "b.bundle").write_bytes(b"\x00" * 4096)
    with pytest.raises(RestoreError, match="appworld unpack b failed"):
        restore_records.restore(world.repository, world.assets, world.manifest)
    assert files_under(world.repository) == []


def test_a_missing_asset_is_reported_and_the_others_are_restored(world):
    (world.assets / "b.bundle").unlink()
    outcome = restore_records.restore(world.repository, world.assets, world.manifest)
    assert outcome.written == ["results/a.sqlite"]
    assert outcome.missing == ["b.bundle"]
    assert files_under(world.repository) == ["results/a.sqlite"]


def test_a_directory_holding_none_of_the_assets_is_an_error(world):
    empty = world.root / "empty"
    empty.mkdir()
    with pytest.raises(RestoreError, match="holds none of the assets"):
        restore_records.restore(world.repository, empty, world.manifest)
    with pytest.raises(RestoreError, match="is not a directory"):
        restore_records.restore(world.repository, world.root / "absent", world.manifest)


@pytest.mark.parametrize(
    "change",
    [
        {"bundle_sha256": "0" * 64},
        {"asset": "other.bundle"},
        {"sha256": "XYZ"},
        {"bytes": -1},
        {"bytes": True},
        {"episodes": "62"},
        {"name": "../a"},
    ],
    ids=["extra field", "asset name", "sha256", "negative size", "bool size", "episodes", "name"],
)
def test_a_malformed_manifest_entry_is_refused(world, change):
    manifest = write_manifest(world.root / "bad.json", [{**entry("a", world.a), **change}])
    with pytest.raises(RestoreError):
        restore_records.read_manifest(manifest)


def test_a_database_listed_twice_is_refused(world):
    manifest = write_manifest(world.root / "twice.json", [entry("a", world.a)] * 2)
    with pytest.raises(RestoreError, match="listed twice"):
        restore_records.read_manifest(manifest)


def test_the_command_line_restores_and_reports_a_refusal(world):
    copy = world.root / "copy"
    (copy / "scripts").mkdir(parents=True)
    shutil.copyfile(SCRIPT, copy / "scripts" / "restore_records.py")
    (copy / "records").mkdir()
    shutil.copyfile(world.manifest, copy / "records" / "MANIFEST.json")
    command = [sys.executable, str(copy / "scripts" / "restore_records.py"), str(world.assets)]
    done = subprocess.run(command, capture_output=True, text=True, timeout=600)
    assert done.returncode == 0, done.stderr
    assert "restored results/a.sqlite" in done.stdout
    assert "restored 2 of 2 databases; 0 already in place, 0 missing" in done.stdout
    (copy / "results/a.sqlite").write_bytes(b"changed")
    (copy / "results/b.sqlite").unlink()
    refused = subprocess.run(command, capture_output=True, text=True, timeout=600)
    assert refused.returncode == 1
    assert "FAILED: results/a.sqlite exists with a different sha256" in refused.stderr
    assert not (copy / "results/b.sqlite").exists()


def test_placing_never_writes_over_a_file_that_appeared_after_the_check(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"restored")
    target = tmp_path / "results" / "a.sqlite"
    target.parent.mkdir()
    target.write_bytes(b"appeared meanwhile")
    with pytest.raises(RestoreError, match="appeared while restoring; it is not overwritten"):
        restore_records.place(source, target, digest(b"restored"))
    assert target.read_bytes() == b"appeared meanwhile"


def test_placing_removes_a_copy_that_does_not_match(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"restored")
    target = tmp_path / "results" / "a.sqlite"
    with pytest.raises(RestoreError, match="the copy does not match the manifest"):
        restore_records.place(source, target, "0" * 64)
    assert not target.exists()


def test_the_committed_manifest_lists_the_record_databases_this_checkout_can_check():
    entries = restore_records.read_manifest(COMMITTED)
    assert len(entries) == 4
    data = json.loads(COMMITTED.read_text(encoding="utf-8"))
    assert all("bundle" not in key for e in data["databases"] for key in e if key != "asset")
    for item in entries:
        assert item["path"] == f"results/{item['name']}.sqlite"
        local = REPOSITORY / item["path"]
        if not local.is_file():
            continue
        assert local.stat().st_size == item["bytes"]
        assert restore_records.sha256(local) == item["sha256"]
        connection = sqlite3.connect(f"file:{local}?mode=ro", uri=True)
        try:
            (episodes,) = connection.execute("SELECT COUNT(*) FROM episodes").fetchone()
        finally:
            connection.close()
        assert episodes == item["episodes"]
