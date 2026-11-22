"""Builds the documentation site with MkDocs, in strict mode.

The documents link to each other and to code by relative paths from the repository
root. MkDocs serves one directory, so this copies every tracked file into `site-src/`
first: each link then resolves exactly as it does in the repository, and a link to a
file that is not tracked fails the strict build instead of shipping broken.

Usage (the pinned dependencies are in requirements-site.txt):

    python -m pip install --require-hashes --no-deps -r requirements-site.txt
    python scripts/build_site.py
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site-src"


def tracked() -> list[str]:
    listed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=False
    )
    if listed.returncode != 0:
        sys.exit(f"git ls-files failed: {listed.stderr.decode('utf-8', 'replace')[-300:]}")
    paths = [path for path in listed.stdout.decode("utf-8").split("\0") if path]
    if not paths:
        sys.exit("git ls-files listed nothing; the site is built from a git checkout")
    return paths


def main() -> None:
    if SOURCE.exists():
        shutil.rmtree(SOURCE)
    copied = 0
    for relative in tracked():
        source = ROOT / relative
        if not source.is_file():
            continue
        target = SOURCE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    print(f"copied {copied} tracked files into {SOURCE.relative_to(ROOT)}")
    command = [sys.executable, "-m", "mkdocs", "build", "--strict"]
    command += ["--config-file", str(ROOT / "mkdocs.yml")]
    sys.exit(subprocess.run(command, cwd=ROOT, check=False).returncode)


if __name__ == "__main__":
    main()
