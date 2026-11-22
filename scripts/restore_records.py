"""Restores the record databases from the downloaded release assets to results/.

**Why the databases are not in the tree.** The record databases carry AppWorld task text
and AppWorld's responses, and AppWorld asks that its protected data and anything derived
from it be shared only in encrypted form (K-194). They are published as encrypted assets
in the repository's releases, one bundle per database, packed with AppWorld's own
`pack_bundle`. `records/MANIFEST.json` lists, for each database, the asset's file name,
the name it was packed under, the path it restores to, and the restored file's size,
sha256 and episode count. It lists no bundle sha256: a bundle's bytes change with every
packing (K-205), so the restored file is the stable identity.

**What this does.** Given a directory holding the downloaded assets, it opens every asset
the manifest names with the installed `appworld unpack`, in a temporary directory, and
checks each restored file's size and sha256 against the manifest. Only when every asset
found has passed does it write anything, and each database goes to its path under
`results/`. A file already in place with the right sha256 is left alone. A file in place
with any other content stops the run before anything is written: nothing is ever
overwritten. A manifest path outside the repository's `results/` is refused, whether it
says so in the text or reaches there through a link. An asset missing from the directory
is reported and skipped. A directory holding none of them is an error.

The `appworld` command of the environment running this script does the unpacking. The
git-pinned 0.2.0.dev0 and the PyPI release 0.1.3.post1 both carry
`appworld unpack <name> --root <root>`, so the script works with either.

Usage:

    uv run python scripts/restore_records.py <directory with the downloaded assets>
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = pathlib.Path("records/MANIFEST.json")
FIELDS = frozenset({"asset", "name", "path", "sha256", "bytes", "episodes"})
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")
RESULTS = "results"
UNPACK_TIMEOUT_SECONDS = 600  # chosen, unmeasured: the largest asset is a few megabytes


class RestoreError(Exception):
    """An asset did not open, a file did not match the manifest, or a write was refused."""


@dataclasses.dataclass(frozen=True)
class Outcome:
    written: list[str]
    in_place: list[str]
    missing: list[str]


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


def is_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def read_manifest(path: pathlib.Path) -> list[dict]:
    """The manifest's entries, each checked field by field; any doubt is an error."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RestoreError(f"cannot read {path}: {error}") from error
    entries = data.get("databases") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise RestoreError(f"{path} lists no databases")
    names: set[str] = set()
    paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != FIELDS:
            raise RestoreError(f"{path}: an entry must carry exactly {sorted(FIELDS)}: {entry!r}")
        name, relative = entry["name"], entry["path"]
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise RestoreError(f"{path}: malformed name {name!r}")
        if entry["asset"] != f"{name}.bundle":
            raise RestoreError(f"{path}: asset {entry['asset']!r} is not {name}.bundle")
        if not isinstance(entry["sha256"], str) or not SHA256.fullmatch(entry["sha256"]):
            raise RestoreError(f"{path}: {name}: malformed sha256")
        if not is_count(entry["bytes"]) or not is_count(entry["episodes"]):
            raise RestoreError(f"{path}: {name}: bytes and episodes must be counts")
        if not isinstance(relative, str):
            raise RestoreError(f"{path}: {name}: malformed path")
        pure = pathlib.PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise RestoreError(f"{path}: {relative!r} escapes the repository")
        if len(pure.parts) < 2 or pure.parts[0] != RESULTS:
            raise RestoreError(f"{path}: {relative!r} is not a path under {RESULTS}/")
        if name in names or relative in paths:
            raise RestoreError(f"{path}: {name} or {relative} is listed twice")
        names.add(name)
        paths.add(relative)
    return entries


def destination(repository: pathlib.Path, relative: str) -> pathlib.Path:
    """Where `relative` lands once every link is followed; it must stay under results/."""
    root = repository.resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to((root / RESULTS).resolve()) or not target.is_relative_to(root):
        raise RestoreError(f"{relative} resolves to {target}, outside the repository's {RESULTS}/")
    return target


def unpack(asset: pathlib.Path, name: str, root: pathlib.Path) -> pathlib.Path:
    """Opens one asset with `appworld unpack` under `root`; returns the directory it fills."""
    target = root / "experiments" / "outputs" / name
    target.mkdir(parents=True)
    shutil.copyfile(asset, target / "leaderboard.bundle")
    try:
        result = subprocess.run(
            [str(appworld_command()), "unpack", name, "--root", str(root)],
            capture_output=True,
            text=True,
            timeout=UNPACK_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RestoreError(f"appworld unpack {name} did not finish in {error.timeout} s") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout)[-2000:]
        raise RestoreError(f"appworld unpack {name} failed:\n{detail}")
    return target


def place(source: pathlib.Path, target: pathlib.Path, expected: str) -> None:
    """Copies into a file that must not exist yet, then checks the copy."""
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with source.open("rb") as reader, target.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
    except FileExistsError as error:
        raise RestoreError(f"{target} appeared while restoring; it is not overwritten") from error
    except OSError:
        target.unlink(missing_ok=True)
        raise
    if sha256(target) != expected:
        target.unlink()
        raise RestoreError(f"{target}: the copy does not match the manifest")


def restore(repository: pathlib.Path, assets: pathlib.Path, manifest: pathlib.Path) -> Outcome:
    """Unpacks and checks every asset found, then writes. Nothing is written on any error."""
    entries = read_manifest(manifest)
    if not assets.is_dir():
        raise RestoreError(f"{assets} is not a directory")
    present = [entry for entry in entries if (assets / entry["asset"]).is_file()]
    missing = [entry["asset"] for entry in entries if not (assets / entry["asset"]).is_file()]
    if not present:
        listed = ", ".join(entry["asset"] for entry in entries)
        raise RestoreError(f"{assets} holds none of the assets the manifest lists: {listed}")
    targets = {entry["path"]: destination(repository, entry["path"]) for entry in present}
    with tempfile.TemporaryDirectory() as scratch:
        root = pathlib.Path(scratch)
        restored = {}
        for entry in present:
            source = unpack(assets / entry["asset"], entry["name"], root) / entry["path"]
            if not source.is_file():
                raise RestoreError(
                    f"{entry['asset']} does not carry {entry['name']}/{entry['path']}"
                )
            size = source.stat().st_size
            if size != entry["bytes"]:
                raise RestoreError(
                    f"{entry['path']}: {size} bytes restored, the manifest says {entry['bytes']}"
                )
            if sha256(source) != entry["sha256"]:
                raise RestoreError(f"{entry['path']}: sha256 does not match the manifest")
            restored[entry["path"]] = source
        in_place = []
        for entry in present:
            target = targets[entry["path"]]
            if target.exists():
                if not target.is_file() or sha256(target) != entry["sha256"]:
                    raise RestoreError(
                        f"{entry['path']} exists with a different sha256; it is not overwritten"
                    )
                in_place.append(entry["path"])
        written = []
        for entry in present:
            if entry["path"] in in_place:
                continue
            place(restored[entry["path"]], targets[entry["path"]], entry["sha256"])
            written.append(entry["path"])
    return Outcome(written=written, in_place=in_place, missing=missing)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("assets", type=pathlib.Path, help="the directory holding the assets")
    args = parser.parse_args()
    try:
        outcome = restore(REPOSITORY, args.assets, REPOSITORY / MANIFEST)
    except RestoreError as error:
        sys.exit(f"FAILED: {error}")
    for path in outcome.written:
        print(f"restored {path}")
    for path in outcome.in_place:
        print(f"already in place: {path}")
    for asset in outcome.missing:
        print(f"not in {args.assets}: {asset}")
    total = len(outcome.written) + len(outcome.in_place) + len(outcome.missing)
    print(
        f"restored {len(outcome.written)} of {total} databases; "
        f"{len(outcome.in_place)} already in place, {len(outcome.missing)} missing"
    )


if __name__ == "__main__":
    main()
