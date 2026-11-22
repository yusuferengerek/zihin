"""Restores the AppWorld-derived data files to their original paths.

**Why the files are not in the tree.** AppWorld asks that its protected data and anything
derived from it be shared only in encrypted form. The data files of this repository that
carry AppWorld route strings, API identities or task text therefore ship in one bundle,
`derived/appworld-derived.bundle`, packed with AppWorld's own `pack_bundle`.
`derived/MANIFEST.json` lists every packed file's original path and sha256.

**What this does.** It opens the bundle with AppWorld's documented `appworld unpack`
command in a temporary directory, checks every file listed in the manifest against its
sha256, and only when all of them match copies each one to its original path. No code or
configuration path changes: the files land exactly where the code reads them. A file
already in place with the right hash is left alone; one in place with a different hash
stops the run unless `--force` is given.

Usage:

    uv run python scripts/unpack_derived.py
    uv run python scripts/unpack_derived.py --force
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = pathlib.Path("derived/appworld-derived.bundle")
MANIFEST = pathlib.Path("derived/MANIFEST.json")
# The directory name inside the bundle. `appworld unpack <name>` refuses a bundle whose
# files do not all sit under `<name>/`, so the name is fixed at packing time.
NAME = "appworld-derived"
UNPACK_TIMEOUT_SECONDS = 600  # chosen, unmeasured: the bundle is a few megabytes


class RestoreError(Exception):
    """The bundle could not be opened, or a file did not match the manifest."""


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def appworld_command() -> pathlib.Path:
    """The `appworld` executable of the environment running this script."""
    beside = pathlib.Path(sys.executable).with_name("appworld")
    if beside.exists():
        return beside
    found = shutil.which("appworld")
    if found is None:
        raise RestoreError("the `appworld` command is not installed; run `uv sync` first")
    return pathlib.Path(found)


def read_manifest(path: pathlib.Path) -> list[dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RestoreError(f"cannot read {path}: {error}") from error
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise RestoreError(f"{path} lists no files")
    for entry in files:
        if not (
            isinstance(entry, dict)
            and isinstance(entry.get("path"), str)
            and isinstance(entry.get("sha256"), str)
        ):
            raise RestoreError(f"{path}: malformed entry {entry!r}")
        relative = pathlib.PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RestoreError(f"{path}: path escapes the repository: {entry['path']}")
    return files


def restore(
    repository: pathlib.Path, bundle: pathlib.Path, manifest: pathlib.Path, force: bool = False
) -> list[str]:
    """Unpacks, checks every file, then writes. Returns the paths written."""
    files = read_manifest(manifest)
    if not bundle.is_file():
        raise RestoreError(f"{bundle} is missing")
    with tempfile.TemporaryDirectory() as scratch:
        root = pathlib.Path(scratch)
        target = root / "experiments" / "outputs" / NAME
        target.mkdir(parents=True)
        shutil.copyfile(bundle, target / "leaderboard.bundle")
        try:
            result = subprocess.run(
                [str(appworld_command()), "unpack", NAME, "--root", str(root)],
                capture_output=True,
                text=True,
                timeout=UNPACK_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            raise RestoreError(f"appworld unpack did not finish in {error.timeout} s") from error
        if result.returncode != 0:
            raise RestoreError(f"appworld unpack failed:\n{result.stderr[-2000:]}")
        unpacked = {}
        for entry in files:
            source = target / entry["path"]
            if not source.is_file():
                raise RestoreError(f"the bundle does not carry {entry['path']}")
            if sha256(source) != entry["sha256"]:
                raise RestoreError(f"{entry['path']}: sha256 does not match the manifest")
            unpacked[entry["path"]] = source
        for entry in files:
            destination = repository / entry["path"]
            if destination.exists() and not force and sha256(destination) != entry["sha256"]:
                raise RestoreError(
                    f"{entry['path']} exists with different content; pass --force to replace it"
                )
        written = []
        for entry in files:
            destination = repository / entry["path"]
            if destination.exists() and sha256(destination) == entry["sha256"]:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(unpacked[entry["path"]], destination)
            written.append(entry["path"])
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace files whose hash differs")
    args = parser.parse_args()
    try:
        written = restore(REPOSITORY, REPOSITORY / BUNDLE, REPOSITORY / MANIFEST, args.force)
    except RestoreError as error:
        sys.exit(f"FAILED: {error}")
    total = len(read_manifest(REPOSITORY / MANIFEST))
    print(f"restored {len(written)} of {total} files; the rest were already in place")


if __name__ == "__main__":
    main()
