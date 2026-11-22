"""Builds the public repository's tree (yusuferengerek/zihin) from one archive commit.

**What it produces.** The tracked tree at one archive commit, minus what the public
repository must not carry, plus the few files only the public repository has:

  1. Copy. Every blob of the commit with its mode, read with `git cat-file`.
  2. Exclude. The rules in `EXCLUSIONS` below, and every tracked path the commit's own
     `.gitignore` would ignore.
  3. Bundle. Every data file (not code, not a document) that carries an AppWorld route
     string, an (app, api) pair from AppWorld's own API list (`app.api` or
     `apis.app.api`), or task text leaves the tree and goes into one encrypted bundle,
     `derived/appworld-derived.bundle`, packed with AppWorld's own `pack_bundle` and the
     pinned package's constants (K-194). `derived/MANIFEST.json` lists each packed file's
     original path and sha256, nothing else.
  4. Add. `scripts/unpack_derived.py` restores the bundle to the original paths, the public
     `.gitignore` lists those paths, REPRODUCE gains the step, and `PROVENANCE.md` records
     where the tree came from.
  5. Patch. Lines that describe an excluded file are replaced or removed by exact anchor;
     a missing anchor fails the build, and PROVENANCE lists each patch with its removed
     lines and the number of lines it adds. The public CI workflow is the archive's,
     changed by the same mechanism.
  6. Write. `README.md`, `README.tr.md`, `mkdocs.yml`, the Pages workflow, the site
     builder and its pinned requirements come from the templates. Every count they cite
     is counted in the tree or taken from `measured.json`, which `--measure` writes: the
     experiment's episodes in the local records, and the public tree's test outcome as
     a fresh clone gets it, without the record databases and with them restored from
     their assets. The Turkish-only list is generated from the tree.

**Measurement freshness.** `measured.json` carries the sha256 of every file of the tree
it was measured on. A tree that differs is stale: `--out` refuses to build it and
`--check` reports it.

**What it verifies, failing on any hit.** A name from the private list; task text, as any
40-character window of any instruction in any split; a data file with route strings
outside the bundle; an assistant name; a gitleaks finding; and the bundle, opened through
the shipped `unpack_derived.py` and checked against the manifest. Binary files are
scanned too: zip and wheel archives member by member, other binaries as bytes. A hit
inside vendored third-party content passes only through
`scripts/public_templates/third-party-allowlist.json`, keyed by path, member and sha256,
and PROVENANCE prints each allowed member with its license.

**Ciphertext is not word-scanned.** A `*.bundle` file, our derived bundle included, is
ciphertext by construction. A word scan over ciphertext finds random hits, and the derived
bundle's bytes change on every build, so scanning it would fail the build at random. Its
path is still scanned. What guards its content is `seal`: every plaintext input is
scanned for names and assistant names before packing, and a hit fails the build before
anything is packed.

**Determinism.** Two builds of one commit are byte-identical except the bundle file: two
packs of one input were measured to give different sha256 values. PROVENANCE therefore
names the manifest's hash, not the bundle's, and `derived/MANIFEST.json` is the stable
identity of the derived data. A test builds twice and compares.

**--check.** Runs every gate against a commit in a temporary directory and leaves
nothing behind. CI runs it.

**--measure.** Builds the tree in a temporary directory, copies it, makes each copy a
one-commit git repository and unpacks the bundle in both. It runs the test suite in the
first copy as a fresh clone gets it. In the second it first restores the record
databases from the assets in `--record-assets` with the shipped
`scripts/restore_records.py`, then runs the suite again. It counts the experiment's
episodes in the local record databases and writes `measured.json`. It needs the
records, their assets and the AppWorld data, so it runs on the development machine,
not in CI.

Usage:

    uv run python scripts/build_public_tree.py --commit <archive commit> --out <empty dir>
        [--report <file.json>] [--appworld-data data] [--gitleaks <path>]
    uv run python scripts/build_public_tree.py --check [--commit HEAD]
    uv run python scripts/build_public_tree.py --measure --record-assets <dir> [--commit HEAD]
"""

from __future__ import annotations

import argparse
import codecs
import dataclasses
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import sqlite3
import string
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ElementTree
import zipfile

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES = REPOSITORY / "scripts" / "public_templates"
sys.path.insert(0, str(REPOSITORY / "src"))

PINNED_APPWORLD_VERSION = "0.2.0.dev0"
PINNED_APPWORLD_COMMIT = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"
BUNDLE_NAME = "appworld-derived"
BUNDLE_PATH = "derived/appworld-derived.bundle"
MANIFEST_PATH = "derived/MANIFEST.json"
RECORDS_MANIFEST = "records/MANIFEST.json"
SPLITS = ("train", "dev", "test_normal", "test_challenge")
# Characters of an instruction that make a quotation, after `words_only`. The owner chose
# 40; an instruction shorter than that is matched whole.
WINDOW = 40
GIT_TIMEOUT_SECONDS = 300  # chosen, unmeasured
# The public suite took about four minutes when measured by hand; this is the ceiling.
PYTEST_TIMEOUT_SECONDS = 1800  # chosen, unmeasured
MEASURED = "measured.json"

# Files only the public tree has, copied verbatim from the templates.
VERBATIM = {
    "pages.yml": ".github/workflows/pages.yml",
    "build_site.py": "scripts/build_site.py",
    "requirements-site.txt": "requirements-site.txt",
}
# Rendered from templates with counts from the tree and from `measured.json`.
RENDERED = {"README.en.md": "README.md", "README.tr.md": "README.tr.md", "mkdocs.yml": "mkdocs.yml"}
# What the measurement fingerprint leaves out: files rendered from the measurement or
# from the commit itself, and ciphertext whose bytes change with every build.
NOT_FINGERPRINTED = frozenset({*RENDERED.values(), "PROVENANCE.md", BUNDLE_PATH})

# A Markdown file with no English counterpart is Turkish-only when these letters, which
# English text does not use, make up at least this many per mille of its letters.
# Measured on the tree of df8a006: the only English file without a counterpart scored
# 3.5, the lowest Turkish one 57.9. The threshold sits in that gap (chosen from that
# measurement).
TURKISH_LETTERS = frozenset("ğışİĞŞ")
TURKISH_PER_MILLE = 20

# Every skip a correct public run produces falls in one of these groups, recognised by
# its reason: private templates, record databases, single-commit history, untracked
# AppWorld run outputs. A skip in none of them fails the measurement. The groups' names
# in each README's language are in the template `phrases.json`. A record-database skip
# must name the missing file and the restore script, in one of the two approved forms.
SKIP_GROUPS = (
    re.compile(r"scripts/public_templates/ is absent"),
    re.compile(
        r"^results/[\w.-]+\.sqlite is absent: restore it with scripts/restore_records\.py"
        r"(?:, or take a run with scripts/record_run\.py)?$"
    ),
    re.compile(r"no git history here"),
    re.compile(r"experiments/outputs holds no"),
)
PHRASES = "phrases.json"

# What the public tree never carries. Every rule is reported as applied, even when
# nothing matched it.
EXCLUSIONS = {
    "paths": [
        {
            "path": "docs/13-internship-report.tr.md",
            "reason": "names the hosting institution, the workplace, the university and the "
            "advisor (K-197)",
        },
        {
            "path": "docs/13-internship-report.en.md",
            "reason": "the English half of the same report (K-197)",
        },
        {
            "path": "vendor/appworld/appworld-0.2.0.dev0-py3-none-any.whl",
            "reason": "AppWorld's own package, built from the pinned commit; this repository "
            "redistributes no AppWorld binaries. The fallback mirror stays in the archive and "
            "is available to reviewers on request (K-205)",
        },
        {
            "path": "vendor/appworld/appworld_agents-0.1.0.dev0-py3-none-any.whl",
            "reason": "AppWorld's agents package; its agent prompts carry task-instruction "
            "text, from test_normal tasks among others. The fallback mirror stays in the "
            "archive and is available to reviewers on request (K-205)",
        },
    ],
    "suffixes": [
        {
            "suffix": ".sqlite",
            "reason": "record databases ship only as encrypted release assets (K-194)",
        }
    ],
    "prefixes": [
        {
            "prefix": "scripts/public_templates/",
            "reason": "the build's own inputs: rendered into the tree where needed, and the "
            "private names list must never ship",
        }
    ],
    "path_parts": [{"part": ".cache", "reason": "audit and tool caches"}],
}

DATA_SUFFIXES = frozenset({".json", ".jsonl", ".yaml", ".yml", ".csv", ".tsv", ".txt"})
BINARY_SUFFIXES = frozenset({".whl", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".bundle"})
ARCHIVE_SUFFIXES = frozenset({".whl", ".zip"})
# Ciphertext by construction: our derived bundle and any AppWorld bundle. Their content is
# never word-scanned; `seal` scans what goes into ours before it is packed.
CIPHERTEXT_SUFFIXES = frozenset({".bundle"})
# YAML under .github/ is workflow code, not data.
CODE_PREFIXES = (".github/",)
# AppWorld's open-source agents package ships these prompts; the encrypted bundle does not.
PLAINTEXT_EXCEPTIONS = frozenset(
    {
        "prompts/react_code_agent/instructions.txt",
        "prompts/react_code_agent/instructions.reference.txt",
    }
)
# Code and documents may mention a route; data files may not.
ROUTE_ALLOWED_SUFFIXES = frozenset({".py", ".md", ".sql", ".sh", ".ps1", ".ipynb"})

# The assistant names and attribution phrases the tree must not carry, ROT13-encoded:
# this repository carries no such name in plain text, the scanner that looks for them
# included. (word, whole word only)
ASSISTANT_ROT13 = (
    ("pynhqr", False),
    ("naguebcvp", False),
    ("pbcvybg", False),
    ("pungtcg", False),
    ("pbqrk", True),
    ("pb-nhguberq-ol", False),
    ("trarengrq jvgu", False),
)


def assistant_words() -> list[str]:
    return [codecs.decode(word, "rot13") for word, _ in ASSISTANT_ROT13]


ASSISTANT = re.compile(
    "|".join(
        rf"\b{re.escape(codecs.decode(word, 'rot13'))}\b"
        if whole
        else re.escape(codecs.decode(word, "rot13"))
        for word, whole in ASSISTANT_ROT13
    ),
    re.IGNORECASE,
)
# D5 replaced these instructions with their sha256 (S-78, S-79). The build proves each
# digest still belongs to its task before it trusts the instruction list.
D5_PLACEHOLDERS = (
    ("0de03ea_1", "97d2ae07f37901ada1385075a28412fa3799f9bdd7c13a40e16853aefb0fdcbb"),
    ("2a163ab_1", "8171d51f01bd488de4138feca6b3ffb19c89efb3b854da8f3e2729b19e156ca2"),
    ("afc0fce_1", "2b1127911151dd1e34ed76e403c1109b09a26be2a41769650c880141d85e2166"),
    ("692c77d_1", "a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf"),
)
TURKISH_FOLD = str.maketrans({"ı": "i", "İ": "i"})


class BuildError(Exception):
    """A precondition of the build does not hold."""


@dataclasses.dataclass(frozen=True)
class Entry:
    path: str
    mode: str
    data: bytes


# --- small helpers ------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str, input_bytes: bytes | None = None, cwd: pathlib.Path = REPOSITORY) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            input=input_bytes,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise BuildError(f"git {args[0]} did not finish in {error.timeout} s") from error
    if result.returncode not in (0, 1) or (result.returncode == 1 and args[0] != "check-ignore"):
        message = result.stderr.decode("utf-8", "replace")[-500:]
        raise BuildError(f"git {' '.join(args[:2])} failed: {message}")
    return result.stdout


def suffix_of(path: str) -> str:
    return pathlib.PurePosixPath(path).suffix


def kind_of(path: str) -> str:
    """data, code, doc or binary, by suffix and place."""
    suffix = suffix_of(path)
    if suffix in BINARY_SUFFIXES:
        return "binary"
    if suffix == ".md":
        return "doc"
    if suffix in DATA_SUFFIXES and not path.startswith(CODE_PREFIXES):
        return "data"
    return "code"


def words_only(text: str) -> str:
    """Lower case, every run of characters other than letters and digits one space.

    A quotation survives a line break, a blockquote marker, bold markers or changed
    punctuation; comparing words alone still finds it.
    """
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def fold(text: str) -> str:
    """Case, Turkish letters and accents folded to ASCII; whitespace collapsed."""
    decomposed = unicodedata.normalize("NFKD", text.translate(TURKISH_FOLD))
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", stripped.casefold())


def as_text(data: bytes) -> str:
    """UTF-8 when it decodes, Latin-1 otherwise: every byte stays scannable."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


# --- reading the commit --------------------------------------------------------------


def resolve_commit(reference: str) -> str:
    return git("rev-parse", "--verify", f"{reference}^{{commit}}").decode().strip()


def read_tree(commit: str) -> list[Entry]:
    listing = git("ls-tree", "-r", "-z", "--full-tree", commit).split(b"\0")
    rows = []
    for item in filter(None, listing):
        meta, path = item.split(b"\t", 1)
        mode, kind, sha = meta.decode().split()
        if kind != "blob":
            raise BuildError(f"{path.decode()} is a {kind}; only blobs are supported")
        rows.append((mode, sha, path.decode("utf-8")))
    output = git("cat-file", "--batch", input_bytes="".join(f"{s}\n" for _, s, _ in rows).encode())
    entries, offset = [], 0
    for mode, sha, path in rows:
        header_end = output.index(b"\n", offset)
        header = output[offset:header_end].decode().split()
        if header[0] != sha or header[1] != "blob":
            raise BuildError(f"cat-file returned {header} for {path}")
        size = int(header[2])
        start = header_end + 1
        entries.append(Entry(path, mode, output[start : start + size]))
        offset = start + size + 1
    return sorted(entries, key=lambda e: e.path)


def ignored_by_gitignore(entries: list[Entry]) -> set[str]:
    """Tracked paths the commit's own .gitignore files would ignore."""
    with tempfile.TemporaryDirectory() as scratch:
        root = pathlib.Path(scratch)
        git("init", "-q", cwd=root)
        for entry in entries:
            if pathlib.PurePosixPath(entry.path).name == ".gitignore":
                target = root / entry.path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(entry.data)
        paths = "".join(f"{e.path}\0" for e in entries).encode()
        output = git("check-ignore", "--no-index", "-z", "--stdin", input_bytes=paths, cwd=root)
    return {p.decode("utf-8") for p in output.split(b"\0") if p}


# --- rules -------------------------------------------------------------------------


def load_json(name: str) -> dict:
    return json.loads((TEMPLATES / name).read_text(encoding="utf-8"))


def apply_exclusions(
    entries: list[Entry], rules: dict, ignored: set[str]
) -> tuple[list[Entry], list[dict]]:
    """Returns the kept entries and one record per rule, with what it matched."""
    applied = []
    matched: dict[str, str] = {}

    def record(rule: str, reason: str, hits: list[str]) -> None:
        applied.append({"rule": rule, "reason": reason, "matched": sorted(hits)})
        for hit in hits:
            matched.setdefault(hit, rule)

    paths = [e.path for e in entries]
    for item in rules["paths"]:
        record(f"path {item['path']}", item["reason"], [p for p in paths if p == item["path"]])
    for item in rules["suffixes"]:
        hits = [p for p in paths if p.endswith(item["suffix"])]
        record(f"suffix {item['suffix']}", item["reason"], hits)
    for item in rules["prefixes"]:
        hits = [p for p in paths if p.startswith(item["prefix"])]
        record(f"prefix {item['prefix']}", item["reason"], hits)
    for item in rules["path_parts"]:
        hits = [p for p in paths if item["part"] in pathlib.PurePosixPath(p).parts]
        record(f"path part {item['part']}", item["reason"], hits)
    record("the commit's .gitignore", "tracked but ignored", sorted(ignored))
    return [e for e in entries if e.path not in matched], applied


@dataclasses.dataclass(frozen=True)
class Detectors:
    routes: list[re.Pattern[str]]
    apis: re.Pattern[str] | None
    # Every WINDOW-character window of every instruction -> every task that carries it.
    windows: dict[str, tuple[str, ...]]
    # Instructions shorter than WINDOW, whole -> every task with that instruction.
    short: dict[str, tuple[str, ...]]

    def route_hits(self, text: str) -> int:
        """Route strings: app-prefixed paths, bare multi-segment templates, quoted /templates."""
        prefixed, bare, quoted = self.routes
        rest = prefixed.sub(" ", text)
        count = len(prefixed.findall(text)) + len(bare.findall(rest))
        return count + len(quoted.findall(bare.sub(" ", rest)))

    def api_hits(self, text: str) -> int:
        return len(self.apis.findall(text)) if self.apis else 0

    def instruction_spans(self, normalized: str) -> list[tuple[int, int, str]]:
        """(start, end, task) of every window found in a `words_only` string.

        A window that several instructions share yields one span per task, so a report
        names every task that carries it. Whether there is a hit does not depend on this.
        """
        spans = []
        windows = self.windows
        for start in range(len(normalized) - WINDOW + 1):
            for task in windows.get(normalized[start : start + WINDOW], ()):
                spans.append((start, start + WINDOW, task))
        for whole, tasks in self.short.items():
            start = normalized.find(whole)
            while start >= 0:
                spans.extend((start, start + len(whole), task) for task in tasks)
                start = normalized.find(whole, start + 1)
        return spans

    def instruction_hits(self, text: str) -> list[str]:
        return sorted({task for _, _, task in self.instruction_spans(words_only(text))})


def route_patterns(table: dict) -> list[re.Pattern[str]]:
    """The three route shapes, from AppWorld's own route table."""
    segment = r"(?:\{[a-z_]+\}|[^/\s\"'`)<>,;|\]\[]+)"
    prefixed, bare, quoted = [], [], set()
    for app, records in table.items():
        for _, template, _ in records:
            template = template.strip("/")
            parts = template.split("/")
            body = "/".join(segment if p.startswith("{") else re.escape(p) for p in parts)
            prefixed.append((len(template), rf"/?{re.escape(app)}[./]{body}"))
            if "/" in template:
                bare.append((len(template), re.escape(template)))
            quoted.add(re.escape(template))
    prefixed.sort(reverse=True)
    bare.sort(reverse=True)
    return [
        re.compile(r"(?<![\w/.])(?:" + "|".join(p for _, p in prefixed) + r")(?![\w/{}])"),
        re.compile(r"(?<![\w/.{])(?:" + "|".join(p for _, p in bare) + r")(?![\w/{}])"),
        re.compile(
            r"(?<=[\"'`])/(?:" + "|".join(sorted(quoted, key=len, reverse=True)) + r")(?=[\"'`?])"
        ),
    ]


def api_pattern(pairs: set[tuple[str, str]]) -> re.Pattern[str] | None:
    """`app.api` or `apis.app.api`, for (app, api) pairs only."""
    if not pairs:
        return None
    names = sorted((f"{app}.{api}" for app, api in pairs), key=len, reverse=True)
    alternation = "|".join(re.escape(name) for name in names)
    return re.compile(r"(?<![\w.])(?:apis\.)?(?:" + alternation + r")(?!\w)")


def appworld_api_pairs() -> set[tuple[str, str]]:
    """Every (app, api) pair AppWorld's own app modules declare."""
    from appworld.apps import get_all_apps
    from appworld.common.imports import import_apis_module
    from fastapi.routing import APIRoute

    pairs = set()
    for app in get_all_apps():
        for route in import_apis_module(app).app.routes:
            if isinstance(route, APIRoute):
                pairs.add((app, route.name))
    if not pairs:
        raise BuildError("AppWorld declared no APIs; are its app modules installed?")
    return pairs


def load_instructions(data_root: pathlib.Path) -> dict[str, str]:
    """Every instruction of every split; the D5 placeholders must still match."""
    datasets, tasks = data_root / "datasets", data_root / "tasks"
    found = {}
    for split in SPLITS:
        listing = datasets / f"{split}.txt"
        if not listing.is_file():
            raise BuildError(f"{listing} is missing; the task-text check cannot run without it")
        for task in filter(None, (t.strip() for t in listing.read_text().splitlines())):
            spec = tasks / task / "specs.json"
            if not spec.is_file():
                raise BuildError(f"{spec} is missing")
            found[task] = json.loads(spec.read_text(encoding="utf-8"))["instruction"]
    for task, digest in D5_PLACEHOLDERS:
        if sha256_bytes(found.get(task, "").encode("utf-8")) != digest:
            raise BuildError(f"D5 placeholder for {task} no longer matches its instruction")
    return found


def instruction_windows(
    instructions: dict[str, str],
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    """Each window, or each short instruction, mapped to every task id that carries it."""
    windows: dict[str, list[str]] = {}
    short: dict[str, list[str]] = {}
    for task, instruction in sorted(instructions.items()):
        normalized = words_only(instruction)
        if len(normalized) < WINDOW:
            short.setdefault(normalized, []).append(task)
            continue
        seen: set[str] = set()
        for start in range(len(normalized) - WINDOW + 1):
            window = normalized[start : start + WINDOW]
            if window not in seen:
                seen.add(window)
                windows.setdefault(window, []).append(task)
    return (
        {window: tuple(tasks) for window, tasks in windows.items()},
        {whole: tuple(tasks) for whole, tasks in short.items()},
    )


def build_detectors(data_root: pathlib.Path) -> Detectors:
    from zihin.api_routes import route_table

    windows, short = instruction_windows(load_instructions(data_root))
    return Detectors(
        routes=route_patterns(route_table()),
        apis=api_pattern(appworld_api_pairs()),
        windows=windows,
        short=short,
    )


def load_names(path: pathlib.Path) -> list[tuple[str, re.Pattern[str]]]:
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        folded = fold(line).strip()
        body = r"\s+".join(re.escape(word) for word in folded.split(" "))
        names.append((line, re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])")))
    if not names:
        raise BuildError(f"{path} lists no names")
    return names


# --- scanning ----------------------------------------------------------------------


def is_ciphertext(name: str) -> bool:
    return suffix_of(name) in CIPHERTEXT_SUFFIXES


@dataclasses.dataclass(frozen=True)
class Unit:
    path: str
    member: str | None
    sha256: str
    text: str  # empty for ciphertext, whose content is not scanned
    ciphertext: bool


def unit(path: str, member: str | None, data: bytes) -> Unit:
    hidden = is_ciphertext(member or path)
    return Unit(path, member, sha256_bytes(data), "" if hidden else as_text(data), hidden)


def units(path: str, data: bytes) -> list[Unit]:
    """A file, or each member of a zip or wheel archive, as scannable text."""
    if is_ciphertext(path):
        return [unit(path, None, data)]
    if suffix_of(path) in ARCHIVE_SUFFIXES or data[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                return [
                    unit(path, info.filename, archive.read(info))
                    for info in sorted(archive.infolist(), key=lambda i: i.filename)
                    if not info.is_dir()
                ]
        except zipfile.BadZipFile:
            pass
    return [unit(path, None, data)]


def scan(
    files: dict[str, bytes],
    names: list[tuple[str, re.Pattern[str]]],
    detectors: Detectors,
    assistant: re.Pattern[str] = ASSISTANT,
    instructions: bool = True,
) -> dict[str, list]:
    """Names, assistant names and task text, in contents, paths and archive members.

    A ciphertext unit's path is scanned and its content is not; it is listed under
    `ciphertext` so the report shows what was left out.
    """
    found: dict[str, list] = {"names": [], "assistant": [], "instructions": [], "ciphertext": []}
    for path, data in sorted(files.items()):
        for item in units(path, data):
            where = {"path": path, "member": item.member, "sha256": item.sha256}
            label = f"{path}::{item.member}" if item.member else path
            subjects = [(label, "path")]
            if item.ciphertext:
                found["ciphertext"].append(where)
            else:
                subjects.append((item.text, "content"))
            for subject, kind in subjects:
                folded = fold(subject)
                for original, pattern in names:
                    if pattern.search(folded):
                        found["names"].append({**where, "in": kind, "name": original})
                if assistant.search(subject):
                    found["assistant"].append({**where, "in": kind})
            if instructions and not item.ciphertext:
                for task in detectors.instruction_hits(item.text):
                    found["instructions"].append({**where, "task": task})
    return found


def load_allowlist() -> list[dict]:
    return load_json("third-party-allowlist.json")["entries"]


def split_allowed(hits: list[dict], allowlist: list[dict]) -> tuple[list[dict], list[dict]]:
    """Hits inside an allowlisted archive member pass; every other hit fails."""
    keys = {(e["path"], e["member"], e["sha256"]) for e in allowlist}
    allowed, failing = [], []
    for hit in hits:
        key = (hit["path"], hit.get("member"), hit["sha256"])
        (allowed if hit.get("member") and key in keys else failing).append(hit)
    return allowed, failing


# --- producing the tree ------------------------------------------------------------


def check_appworld() -> dict[str, str]:
    version = importlib.metadata.version("appworld")
    direct = importlib.metadata.distribution("appworld").read_text("direct_url.json") or "{}"
    commit = json.loads(direct).get("vcs_info", {}).get("commit_id", "")
    if version != PINNED_APPWORLD_VERSION or commit != PINNED_APPWORLD_COMMIT:
        raise BuildError(
            f"appworld {version} at {commit or 'no commit'} is installed; the bundle must be "
            f"packed with {PINNED_APPWORLD_VERSION} at {PINNED_APPWORLD_COMMIT} (K-194)"
        )
    return {"version": version, "commit": commit}


def pack(files: dict[str, bytes], bundle: pathlib.Path) -> list[str]:
    """Packs `files` under `<BUNDLE_NAME>/` with AppWorld's own packer and constants."""
    import appworld.leaderboard as leaderboard
    from appworld.common.crypto import pack_bundle

    with tempfile.TemporaryDirectory() as scratch:
        base = pathlib.Path(scratch) / "experiments" / "outputs"
        for path, data in files.items():
            target = base / BUNDLE_NAME / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        packed = pack_bundle(
            bundle_file_path=str(pathlib.Path(scratch) / "derived.bundle"),
            base_directory=str(base),
            include_directories=[BUNDLE_NAME],
            password=leaderboard.PASSWORD,
            salt=leaderboard.SALT,
        )
        bundle.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pathlib.Path(scratch) / "derived.bundle", bundle)
    missing = {f"{BUNDLE_NAME}/{p}" for p in files} - set(packed)
    if missing:
        raise BuildError(f"pack_bundle left out {sorted(missing)}")
    return sorted(packed)


def seal(
    files: dict[str, bytes],
    names: list[tuple[str, re.Pattern[str]]],
    detectors: Detectors,
    bundle: pathlib.Path,
    assistant: re.Pattern[str] = ASSISTANT,
) -> list[str]:
    """Scans every plaintext input for names and assistant names, then packs.

    Once packed, the content is ciphertext that no later scan reads, so this is the only
    scan it gets. A hit fails the build before anything is packed. Task text is not a hit
    here: carrying it encrypted is what the bundle is for.
    """
    found = scan(files, names, detectors, assistant=assistant, instructions=False)
    hits = [f"{key}: {hit}" for key in ("names", "assistant") for hit in found[key]]
    if hits:
        raise BuildError(
            f"{len(hits)} hits in the bundle's plaintext inputs; nothing was packed:\n  "
            + "\n  ".join(hits)
        )
    return pack(files, bundle)


def load_unpacker():
    spec = importlib.util.spec_from_file_location("unpack_derived", TEMPLATES / "unpack_derived.py")
    if spec is None or spec.loader is None:
        raise BuildError("cannot load unpack_derived.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["unpack_derived"] = module
    spec.loader.exec_module(module)
    return module


def patch(out: pathlib.Path, patches: list[dict]) -> list[dict]:
    applied = []
    for item in patches:
        target = out / item["path"]
        if not target.is_file():
            raise BuildError(f"patch target {item['path']} is not in the tree")
        text = target.read_text(encoding="utf-8")
        if text.count(item["old"]) != 1:
            raise BuildError(
                f"patch anchor in {item['path']} matched {text.count(item['old'])} times"
            )
        target.write_text(text.replace(item["old"], item["new"]), encoding="utf-8")
        old, new = item["old"].splitlines(), item["new"].splitlines()
        removed = [line for line in old if line not in new]
        added = [line for line in new if line not in old]
        applied.append(
            {
                "path": item["path"],
                "removed": removed,
                "added": len(added),
                "reason": item["reason"],
            }
        )
    return applied


def insert_after(target: pathlib.Path, anchor: str, block: str) -> None:
    text = target.read_text(encoding="utf-8")
    if text.count(anchor) != 1:
        raise BuildError(f"anchor in {target.name} matched {text.count(anchor)} times")
    target.write_text(text.replace(anchor, anchor + block), encoding="utf-8")


def write_tree(out: pathlib.Path, entries: list[Entry]) -> None:
    for entry in entries:
        target = out / entry.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(entry.data)
        os.chmod(target, 0o755 if entry.mode == "100755" else 0o644)


def tree_files(out: pathlib.Path) -> dict[str, bytes]:
    return {
        p.relative_to(out).as_posix(): p.read_bytes()
        for p in sorted(out.rglob("*"))
        if p.is_file() and ".git" not in p.relative_to(out).parts
    }


def count_lines(number: int) -> str:
    return f"{number} line" if number == 1 else f"{number} lines"


def render_provenance(context: dict) -> str:
    patches = []
    for item in context["patches"]:
        entry = (
            f"- `{item['path']}`, {count_lines(len(item['removed']))} removed, "
            f"{count_lines(item['added'])} added. {item['reason']}"
        )
        if item["removed"]:
            lines = "\n".join(f"  {line}" for line in item["removed"])
            entry += f"\n\n  Removed:\n\n  ```\n{lines}\n  ```"
        patches.append(entry)
    third_party = [
        f"- `{e['path']}`, member `{e['member']}` (sha256 `{e['sha256']}`): {e['license']}. "
        f"{e['reason']}"
        for e in context["allowlist"]
    ] or ["- none"]
    template = string.Template((TEMPLATES / "PROVENANCE.md").read_text(encoding="utf-8"))
    return template.substitute(
        archive_commit=context["commit"],
        measured_commit=context["measured_commit"],
        build_script="scripts/build_public_tree.py",
        build_script_sha256=context["script_sha256"],
        appworld_version=context["appworld"]["version"],
        appworld_commit=context["appworld"]["commit"],
        bundled_count=context["bundled_count"],
        manifest_sha256=context["manifest_sha256"],
        exclusions="\n".join(
            f"- {r['rule']}: {r['reason']} ({len(r['matched'])} matched)"
            for r in context["exclusions"]
        ),
        patches="\n".join(patches),
        written="\n".join(f"- `{path}`" for path in context["written"]),
        third_party="\n".join(third_party),
    )


# --- the public tree's own files (Step 2) -------------------------------------------


def counterpart(path: str, paths: set[str]) -> str | None:
    """The other language's file: `x.tr.md` with `x.en.md` or `x.md`, and back."""
    if path.endswith(".tr.md"):
        stem = path[: -len(".tr.md")]
        return next((p for p in (f"{stem}.en.md", f"{stem}.md") if p in paths), None)
    stem = path[: -len(".en.md")] if path.endswith(".en.md") else path[: -len(".md")]
    return f"{stem}.tr.md" if f"{stem}.tr.md" in paths else None


def turkish_per_mille(text: str) -> float:
    letters = sum(character.isalpha() for character in text)
    turkish = sum(character in TURKISH_LETTERS for character in text)
    return 1000 * turkish / letters if letters else 0.0


def turkish_only(files: dict[str, bytes]) -> list[str]:
    """Markdown files with no English counterpart whose text is Turkish."""
    paths = {path for path in files if path.endswith(".md")}
    return sorted(
        path
        for path in paths
        if counterpart(path, paths) is None
        and turkish_per_mille(as_text(files[path])) >= TURKISH_PER_MILLE
    )


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPOSITORY / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:
        raise BuildError(f"cannot load scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def ledger_counts(files: dict[str, bytes]) -> dict[str, int]:
    """Entries counted the way their own maps count them, never the highest number."""
    limitations = load_script("build_limitations_index").records(
        as_text(files["docs/09-limitations.tr.md"])
    )
    headings = re.findall(r"^### (?:~~)?K-(\d+) ", as_text(files["docs/08-decisions.tr.md"]), re.M)
    rows = as_text(files["experiments/decisions.csv"]).splitlines()[1:]
    in_csv = sum(1 for row in rows if row.startswith("K-"))
    if len(set(headings)) != len(headings) or len(headings) != in_csv:
        raise BuildError(
            f"the decisions ledger has {len(headings)} K headings and the CSV {in_csv} K rows"
        )
    return {"limitations": len(limitations), "decisions": len(headings)}


def fingerprint(files: dict[str, bytes]) -> dict[str, str]:
    return {p: sha256_bytes(d) for p, d in sorted(files.items()) if p not in NOT_FINGERPRINTED}


def stale_paths(measured_tree: dict[str, str], current: dict[str, str]) -> list[str]:
    """Paths added, removed or changed since the measurement."""
    keys = set(measured_tree) | set(current)
    return sorted(k for k in keys if measured_tree.get(k) != current.get(k))


def skip_group(reason: str) -> int:
    """The index of the group a skip reason belongs to; any other reason fails."""
    for index, pattern in enumerate(SKIP_GROUPS):
        if pattern.search(reason):
            return index
    raise BuildError(f"a skip in none of the expected groups: {reason!r}")


def load_measured() -> dict:
    path = TEMPLATES / MEASURED
    if not path.is_file():
        raise BuildError(f"{path} is missing; run --measure first")
    return json.loads(path.read_text(encoding="utf-8"))


def phrases(language: str) -> dict:
    """The README's language-specific phrases; the code that uses them stays English."""
    found = load_json(PHRASES)[language]
    if len(found["groups"]) != len(SKIP_GROUPS):
        raise BuildError(f"{PHRASES} names {len(found['groups'])} skip groups for {language}")
    return found


def skip_table(skips: list[dict], language: str) -> str:
    words = phrases(language)
    lines = [words["table_head"], "|---|---|---|"]
    for skip in sorted(skips, key=lambda s: (skip_group(s["reason"]), s["test"])):
        group = words["groups"][skip_group(skip["reason"])]
        reason = re.sub(r"\s+", " ", skip["reason"]).replace("|", "\\|").strip()
        lines.append(f"| {group} | `{skip['test']}` | {reason} |")
    return "\n".join(lines)


def outcome_values(tests: dict, language: str, suffix: str = "") -> dict[str, object]:
    """One measured outcome as README placeholders: counts, skip groups, the skip table."""
    return {
        f"collected{suffix}": tests["collected"],
        f"passed{suffix}": tests["passed"],
        f"skipped{suffix}": len(tests["skipped"]),
        f"skip_groups{suffix}": len({skip_group(skip["reason"]) for skip in tests["skipped"]}),
        f"skip_table{suffix}": skip_table(tests["skipped"], language),
    }


def experiment_status(episodes: dict, language: str) -> str:
    """The status sentence, from the count: none, or how many and what they cover."""
    words = phrases(language)
    values = {
        "databases": len(episodes["databases"]),
        "count": episodes["count"],
        "tasks": episodes["tasks"],
        "runs": episodes["runs"],
        "conditions": ", ".join(f"`{c}`" for c in episodes["conditions"]),
    }
    return words["status_none" if episodes["count"] == 0 else "status_some"].format(**values)


def render(template: str, values: dict[str, object]) -> str:
    text = string.Template((TEMPLATES / template).read_text(encoding="utf-8")).substitute(values)
    if "${" in text:
        raise BuildError(f"{template}: a placeholder survived rendering")
    return text


def write_public_files(out: pathlib.Path, measured: dict) -> dict:
    """The files only the public tree has. Returns what was written and what it cites."""
    for template, target in VERBATIM.items():
        path = out / target
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TEMPLATES / template, path)
        os.chmod(path, 0o644)
    files = tree_files(out)
    turkish = turkish_only(files)
    counts = ledger_counts(files)
    tests = measured["public_tests"]
    restored = measured["public_tests_restored"]
    episodes = measured["experiment_episodes"]
    for language, target in (("en", "README.md"), ("tr", "README.tr.md")):
        values = {
            "experiment_status": experiment_status(episodes, language),
            "limitations": counts["limitations"],
            "decisions": counts["decisions"],
            "tests_commit": tests["commit"][:7],
            **outcome_values(tests, language),
            **outcome_values(restored, language, "_restored"),
            "turkish_count": len(turkish),
            "turkish_list": "\n".join(f"- `{path}`" for path in turkish),
        }
        template = "README.en.md" if language == "en" else "README.tr.md"
        (out / target).write_text(render(template, values), encoding="utf-8")
    nav = "\n".join(f"      - {path}" for path in turkish)
    (out / "mkdocs.yml").write_text(render("mkdocs.yml", {"turkish_nav": nav}), encoding="utf-8")
    return {
        "written": sorted([*VERBATIM.values(), *RENDERED.values()]),
        "turkish_only": turkish,
        "counts": counts,
    }


def produce(
    commit: str, out: pathlib.Path, detectors: Detectors, measured: dict | None = None
) -> dict:
    """Writes the public tree for `commit` into the empty directory `out`.

    `measured` defaults to `measured.json`; `--measure` passes the previous measurement,
    or a placeholder, because it is about to take a new one.
    """
    appworld = check_appworld()
    entries = read_tree(commit)
    kept, exclusions = apply_exclusions(entries, EXCLUSIONS, ignored_by_gitignore(entries))
    bundled, classified = {}, []
    for entry in kept:
        if kind_of(entry.path) != "data" or entry.path in PLAINTEXT_EXCEPTIONS:
            continue
        text = as_text(entry.data)
        routes, apis = detectors.route_hits(text), detectors.api_hits(text)
        tasks = detectors.instruction_hits(text)
        classified.append(
            {"path": entry.path, "routes": routes, "api": apis, "instructions": len(tasks)}
        )
        if routes or apis or tasks:
            bundled[entry.path] = entry.data

    out.mkdir(parents=True, exist_ok=True)
    names = load_names(TEMPLATES / "private-names.txt")
    packed = seal(bundled, names, detectors, out / BUNDLE_PATH)
    write_tree(out, [e for e in kept if e.path not in bundled])
    patches = patch(out, load_json("patches.json")["patches"])
    shutil.copyfile(TEMPLATES / "unpack_derived.py", out / "scripts" / "unpack_derived.py")
    os.chmod(out / "scripts" / "unpack_derived.py", 0o644)
    for item in load_json("reproduce-anchors.json")["anchors"]:
        step = (TEMPLATES / item["step"]).read_text(encoding="utf-8")
        insert_after(out / item["path"], item["anchor"], step)
    with (out / ".gitignore").open("a", encoding="utf-8") as handle:
        handle.write(
            "\n# AppWorld-derived data, restored from derived/appworld-derived.bundle by\n"
            "# scripts/unpack_derived.py (see PROVENANCE.md).\n"
        )
        handle.writelines(f"/{path}\n" for path in sorted(bundled))
        handle.write("\n# The documentation site: its assembled source and its output.\n")
        handle.write("/site-src/\n/site/\n")

    measurement = measured if measured is not None else load_measured()
    public = write_public_files(out, measurement)

    manifest = {
        "bundle": BUNDLE_PATH,
        "name": BUNDLE_NAME,
        "packer": "appworld.common.crypto.pack_bundle",
        "appworld": appworld,
        "files": [
            {"path": p, "sha256": sha256_bytes(d), "bytes": len(d)}
            for p, d in sorted(bundled.items())
        ],
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (out / MANIFEST_PATH).write_text(manifest_text, encoding="utf-8")
    context = {
        "commit": commit,
        "script_sha256": sha256_bytes(pathlib.Path(__file__).read_bytes()),
        "appworld": appworld,
        "bundled_count": len(bundled),
        "manifest_sha256": sha256_bytes(manifest_text.encode("utf-8")),
        "exclusions": exclusions,
        "patches": patches,
        "allowlist": load_allowlist(),
        "written": public["written"],
        "measured_commit": measurement["public_tests"]["commit"],
    }
    (out / "PROVENANCE.md").write_text(render_provenance(context), encoding="utf-8")
    current = fingerprint(tree_files(out))
    return {
        **context,
        "tracked": len(entries),
        "kept": {e.path: e.data for e in kept},
        "bundled": bundled,
        "packed": packed,
        "classified": classified,
        "public": public,
        "fingerprint": current,
        "stale": stale_paths(measurement.get("tree", {}), current),
    }


# --- verifying the tree ------------------------------------------------------------


def inventory(files: dict[str, bytes], detectors: Detectors) -> list[dict]:
    rows = []
    for path, data in sorted(files.items()):
        if kind_of(path) == "binary":
            continue
        text = as_text(data)
        routes, apis = detectors.route_hits(text), detectors.api_hits(text)
        if routes or apis:
            rows.append({"path": path, "kind": kind_of(path), "routes": routes, "api": apis})
    return rows


def gitleaks(out: pathlib.Path, binary: str) -> dict:
    executable = shutil.which(binary) or binary
    if not pathlib.Path(executable).is_file():
        raise BuildError(f"gitleaks not found at {binary}; the secret gate cannot run")
    with tempfile.TemporaryDirectory() as scratch:
        report = pathlib.Path(scratch) / "gitleaks.json"
        command = [executable, "dir", str(out), "--no-banner", "--redact", "--exit-code", "1"]
        command += ["--report-format", "json", "--report-path", str(report)]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS
        )
        if result.returncode not in (0, 1):
            raise BuildError(f"gitleaks failed: {result.stderr[-500:]}")
        findings = json.loads(report.read_text() or "[]") if report.exists() else []
    return {"findings": len(findings), "files": sorted({f.get("File", "") for f in findings})}


def verify(out: pathlib.Path, product: dict, detectors: Detectors, gitleaks_path: str) -> dict:
    names = load_names(TEMPLATES / "private-names.txt")
    allowlist = load_allowlist()
    # Names and assistant names may not ship even encrypted; task text may, inside the bundle.
    before = scan(product["kept"], names, detectors, instructions=False)
    files = tree_files(out)
    after = scan(files, names, detectors)
    findings = {}
    for key in ("names", "assistant", "instructions"):
        hits = (before[key] if key != "instructions" else []) + after[key]
        unique = {json.dumps(h, sort_keys=True): h for h in hits}
        findings[key] = split_allowed(list(unique.values()), allowlist)
    rows = inventory(files, detectors)
    failures = []
    for key, (_, failing) in findings.items():
        failures += [f"{key}: {hit}" for hit in failing]
    for row in rows:
        allowed = suffix_of(row["path"]) in ROUTE_ALLOWED_SUFFIXES or row["path"] in (
            PLAINTEXT_EXCEPTIONS
        )
        if not allowed:
            failures.append(f"route strings outside the bundle: {row}")
    with tempfile.TemporaryDirectory() as scratch:
        restored = load_unpacker().restore(
            pathlib.Path(scratch), out / BUNDLE_PATH, out / MANIFEST_PATH, force=False
        )
    if sorted(restored) != sorted(product["bundled"]):
        failures.append(f"unpack restored {len(restored)} of {len(product['bundled'])} files")
    leaks = gitleaks(out, gitleaks_path)
    if leaks["findings"]:
        failures.append(f"gitleaks: {leaks}")
    return {
        "files": files,
        "inventory": rows,
        "allowed_third_party": {k: allowed for k, (allowed, _) in findings.items()},
        "ciphertext_not_scanned": before["ciphertext"] + after["ciphertext"],
        "restored": len(restored),
        "gitleaks": leaks,
        "failures": failures,
    }


def report_of(product: dict, checked: dict, detectors: Detectors, out: pathlib.Path) -> dict:
    bundle = (out / BUNDLE_PATH).read_bytes()
    docs13 = [
        f"{path}:{number}"
        for path, data in sorted(checked["files"].items())
        if kind_of(path) != "binary"
        for number, line in enumerate(as_text(data).splitlines(), 1)
        if "13-internship-report" in line
    ]
    return {
        "archive_commit": product["commit"],
        "build_script_sha256": product["script_sha256"],
        "appworld": product["appworld"],
        "counts": {
            "tracked": product["tracked"],
            "excluded": product["tracked"] - len(product["kept"]),
            "bundled": len(product["bundled"]),
            "plaintext_from_archive": len(product["kept"]) - len(product["bundled"]),
            "files_in_output": len(checked["files"]),
            "instruction_windows": len(detectors.windows),
            "short_instructions": len(detectors.short),
        },
        "exclusions": product["exclusions"],
        "patches": product["patches"],
        "data_files_classified": product["classified"],
        "bundle": {
            "path": BUNDLE_PATH,
            "bytes": len(bundle),
            "sha256_of_this_build": sha256_bytes(bundle),
            "packed_entries": product["packed"],
            "restored_by_unpack_derived": checked["restored"],
        },
        "manifest_sha256": product["manifest_sha256"],
        "inventory_of_output": checked["inventory"],
        "docs13_references": docs13,
        "allowed_third_party": checked["allowed_third_party"],
        "ciphertext_not_scanned": checked["ciphertext_not_scanned"],
        "gitleaks": checked["gitleaks"],
        "public_files": product["public"],
        "measurement": {"commit": product["measured_commit"], "stale_paths": product["stale"]},
        "failures": checked["failures"],
    }


def run(
    commit: str,
    out: pathlib.Path,
    data_root: pathlib.Path,
    gitleaks_path: str,
    require_fresh: bool,
) -> dict:
    if REPOSITORY in out.parents or out == REPOSITORY:
        raise BuildError("the output directory must be outside the archive")
    if out.exists() and any(out.iterdir()):
        raise BuildError(f"{out} is not empty")
    detectors = build_detectors(data_root)
    product = produce(commit, out, detectors)
    if require_fresh and product["stale"]:
        raise BuildError(
            f"measured.json was measured on another tree: {len(product['stale'])} paths "
            f"differ ({product['stale'][:5]}); run --measure"
        )
    checked = verify(out, product, detectors, gitleaks_path)
    return report_of(product, checked, detectors, out)


# --- measuring (development machine only) ------------------------------------------


def measure_experiment_episodes() -> dict:
    """The experiment's episodes in the local records, by the boundary K-178 declares."""
    from zihin.declared import EXPERIMENT_PREFIX, NON_MEASUREMENT_MARKERS

    paths = sorted((REPOSITORY / "results").glob("*.sqlite"))
    if not paths:
        raise BuildError("no record database under results/; the count needs the local records")
    databases, runs, tasks, conditions, count = [], set(), set(), set(), 0
    for path in paths:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            rows = connection.execute("SELECT run_id, task_id, condition FROM episodes").fetchall()
        finally:
            connection.close()
        mine = [
            row
            for row in rows
            if row[0].split("-", 1)[0] == EXPERIMENT_PREFIX
            and not any(marker in row[0] for marker in NON_MEASUREMENT_MARKERS)
        ]
        count += len(mine)
        runs.update(row[0] for row in mine)
        tasks.update(row[1] for row in mine)
        conditions.update(row[2] for row in mine)
        databases.append(
            {
                "path": path.relative_to(REPOSITORY).as_posix(),
                "sha256": sha256_bytes(path.read_bytes()),
                "episodes": len(rows),
                "experiment_episodes": len(mine),
            }
        )
    return {
        "rule": f"run id's first segment is `{EXPERIMENT_PREFIX}` and it carries none of "
        f"{list(NON_MEASUREMENT_MARKERS)} (zihin.declared, K-178)",
        "count": count,
        "runs": len(runs),
        "tasks": len(tasks),
        "conditions": sorted(conditions),
        "databases": databases,
    }


def prepare_public_tree(tree: pathlib.Path, data_root: pathlib.Path) -> dict[str, str]:
    """A fresh clone's state: one commit, AppWorld's data, the derived files unpacked."""
    git("init", "-q", "-b", "main", cwd=tree)
    git("add", "-A", cwd=tree)
    identity = ("-c", "user.name=public-measure", "-c", "user.email=public-measure@localhost")
    git(*identity, "commit", "-q", "-m", "Initial public release", cwd=tree)
    (tree / "data").symlink_to(data_root, target_is_directory=True)
    environment = {**os.environ, "PYTHONPATH": str(tree / "src")}
    unpacked = subprocess.run(
        [sys.executable, "scripts/unpack_derived.py"],
        cwd=tree,
        env=environment,
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
    )
    if unpacked.returncode != 0:
        raise BuildError(f"unpack_derived.py failed: {unpacked.stderr[-500:]}")
    return environment


def restore_public_records(
    tree: pathlib.Path, environment: dict[str, str], assets: pathlib.Path
) -> list[str]:
    """Restores every record database with the tree's own script; each must match."""
    restored = subprocess.run(
        [sys.executable, "scripts/restore_records.py", str(assets)],
        cwd=tree,
        env=environment,
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
    )
    if restored.returncode != 0:
        raise BuildError(f"restore_records.py failed: {restored.stderr[-500:]}")
    manifest = json.loads((tree / RECORDS_MANIFEST).read_text(encoding="utf-8"))
    paths = []
    for entry in manifest["databases"]:
        path = tree / entry["path"]
        if not path.is_file() or sha256_bytes(path.read_bytes()) != entry["sha256"]:
            raise BuildError(f"{entry['path']} was not restored as {RECORDS_MANIFEST} lists it")
        paths.append(entry["path"])
    return paths


def run_public_suite(tree: pathlib.Path, environment: dict[str, str]) -> dict:
    """The suite as the README tells a reader to run it, skips grouped by reason."""
    junit = tree.parent / f"junit-{tree.name}.xml"
    command = [sys.executable, "-m", "pytest", "-m", "not model_server and not sandbox"]
    command += ["-q", "-p", "no:cacheprovider", f"--junitxml={junit}"]
    try:
        subprocess.run(
            command,
            cwd=tree,
            env=environment,
            capture_output=True,
            text=True,
            timeout=PYTEST_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise BuildError(f"the public suite did not finish in {error.timeout} s") from error
    if not junit.is_file():
        raise BuildError("the public suite wrote no JUnit report")
    root = ElementTree.parse(junit).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise BuildError("the JUnit report has no test suite")
    skipped, broken = [], []
    for case in suite.iter("testcase"):
        test = f"{case.get('classname', '').replace('.', '/')}.py::{case.get('name')}"
        for kind in ("failure", "error"):
            if case.find(kind) is not None:
                broken.append(f"{kind}: {test}")
        node = case.find("skipped")
        if node is not None:
            reason = node.get("message", "")
            skip_group(reason)
            skipped.append({"test": test, "reason": reason})
    if broken:
        raise BuildError(f"the public suite is not clean: {broken[:10]}")
    collected = int(suite.get("tests", "0"))
    return {
        "command": "pytest -m 'not model_server and not sandbox'",
        "collected": collected,
        "passed": collected - len(skipped),
        "skipped": sorted(skipped, key=lambda s: (skip_group(s["reason"]), s["test"])),
    }


def measure_public_tests(
    tree: pathlib.Path, data_root: pathlib.Path, assets: pathlib.Path
) -> tuple[dict, dict]:
    """The suite in two fresh clones of one tree: as built, and with the records restored."""
    twin = tree.with_name(f"{tree.name}-restored")
    shutil.copytree(tree, twin, symlinks=True)
    without = run_public_suite(tree, prepare_public_tree(tree, data_root))
    environment = prepare_public_tree(twin, data_root)
    restored = restore_public_records(twin, environment, assets)
    return without, {**run_public_suite(twin, environment), "restored": restored}


def measure(commit: str, data_root: pathlib.Path, assets: pathlib.Path) -> dict:
    """Builds the tree for `commit`, then takes every measurement on it.

    The tree's READMEs and PROVENANCE are rendered from a placeholder, not from the
    previous measurement: they are not fingerprinted and no test reads them, and the
    previous measurement may carry a skip reason the groups no longer accept.
    """
    path = TEMPLATES / MEASURED
    empty = {"commit": "0" * 40, "collected": 0, "passed": 0, "skipped": []}
    placeholder = {
        "experiment_episodes": {
            "count": 0,
            "databases": [],
            "conditions": [],
            "runs": 0,
            "tasks": 0,
        },
        "public_tests": empty,
        "public_tests_restored": empty,
    }
    detectors = build_detectors(data_root)
    with tempfile.TemporaryDirectory() as scratch:
        tree = pathlib.Path(scratch) / "zihin"
        product = produce(commit, tree, detectors, measured=placeholder)
        episodes = measure_experiment_episodes()
        without, restored = measure_public_tests(tree, data_root.resolve(), assets.resolve())
    measured = {
        "comment": "Written by scripts/build_public_tree.py --measure; the READMEs cite these "
        "numbers. `tree` is the sha256 of every file of the measured tree, so a later build "
        "can tell whether the measurement still describes it. `public_tests` is a fresh "
        "clone; `public_tests_restored` is the same clone with the record databases restored "
        "from their assets by scripts/restore_records.py.",
        "experiment_episodes": episodes,
        "public_tests": {"commit": commit, **without},
        "public_tests_restored": {"commit": commit, **restored},
        "tree": product["fingerprint"],
    }
    path.write_text(json.dumps(measured, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return measured


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--commit", help="the archive commit to build from (default HEAD)")
    parser.add_argument("--out", help="an empty directory outside the archive")
    parser.add_argument("--check", action="store_true", help="run every gate, keep no tree")
    parser.add_argument(
        "--measure", action="store_true", help="measure the public suite and the records"
    )
    parser.add_argument("--report", help="write the build report as JSON here")
    parser.add_argument("--appworld-data", default=str(REPOSITORY / "data"))
    parser.add_argument("--gitleaks", default=str(pathlib.Path.home() / ".cache/gitleaks/gitleaks"))
    parser.add_argument(
        "--record-assets", help="with --measure: the directory holding the record assets"
    )
    args = parser.parse_args()
    if not args.check and not args.measure and not args.out:
        parser.error("--out is required unless --check or --measure is given")
    if args.measure and not args.record_assets:
        parser.error("--measure needs --record-assets: the restored outcome is measured too")
    data_root = pathlib.Path(args.appworld_data).resolve()
    try:
        commit = resolve_commit(args.commit or "HEAD")
        if args.measure:
            measured = measure(commit, data_root, pathlib.Path(args.record_assets))
            for label, key in (("as built", "public_tests"), ("restored", "public_tests_restored")):
                tests = measured[key]
                print(
                    f"measured {commit} {label}: {tests['collected']} collected, "
                    f"{tests['passed']} passed, {len(tests['skipped'])} skipped"
                )
            print(
                f"experiment episodes {measured['experiment_episodes']['count']}; "
                f"written {TEMPLATES / MEASURED}"
            )
            return
        if args.check:
            with tempfile.TemporaryDirectory() as scratch:
                tree = pathlib.Path(scratch) / "tree"
                report = run(commit, tree, data_root, args.gitleaks, require_fresh=False)
        else:
            out = pathlib.Path(args.out).resolve()
            report = run(commit, out, data_root, args.gitleaks, require_fresh=True)
    except BuildError as error:
        sys.exit(f"FAILED: {error}")
    if args.report:
        pathlib.Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    print(f"archive commit {report['archive_commit']}")
    print(
        f"tracked {counts['tracked']}, excluded {counts['excluded']}, bundled {counts['bundled']},"
        f" plaintext {counts['plaintext_from_archive']}, output files {counts['files_in_output']},"
        f" instruction windows {counts['instruction_windows']}"
    )
    print(f"bundle {report['bundle']['bytes']} bytes; manifest sha256 {report['manifest_sha256']}")
    stale = report["measurement"]["stale_paths"]
    print(
        f"measurement of {report['measurement']['commit'][:7]}: "
        + (f"STALE, {len(stale)} paths differ {stale[:5]}" if stale else "fresh")
    )
    if report["failures"]:
        print(f"FAILED: {len(report['failures'])} verification hits")
        for line in report["failures"]:
            print(f"  {line}")
        sys.exit(1)
    print("verification: clean")


if __name__ == "__main__":
    main()
