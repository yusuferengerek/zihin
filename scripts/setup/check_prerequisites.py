"""Checks what every remaining step needs, before the first of them starts.

**Why it exists.** The Colab bootstrap has been repaired one failure at a time,
and each failure cost a round: the tokenless clone, the upstream LFS budget, the
empty data cache, the wrong Python environment, and then zstd, which the Ollama
installer needs and the Colab image does not carry. Every one of them was a
missing precondition that could have been named before anything ran. In an
N-step chain, asking the preconditions up front turns N rounds into one.

**Everything is reported at once.** No check stops the others. A first missing
item that hides a second missing item is the shape of the problem, not a detail
of it.

**This is K-125 turned around.** There the rule was that a failure must name
itself. Here the rule is that a missing precondition must name itself before
there is a failure.

**What it does not do.** It installs nothing and starts nothing. Items the
bootstrap installs by itself are reported as such rather than as failures, and
what is checked in those cases is whether the installer they need is available.

Usage:

    uv run python scripts/setup/check_prerequisites.py
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import socket
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]


# The model tag has ONE source: the conditions table the run's own prefix names.
# It used to be a default here, and three other scripts carried the same default;
# the bootstrap then pulled one model while the run asked for another and every
# check answered about the wrong one (K-138).
def _model() -> str:
    from zihin.declared import Undeclared, declared_model

    named = os.environ.get("ZIHIN_MODEL")
    try:
        declared = declared_model()
    except Undeclared as error:
        if named:
            return named
        sys.exit(f"the model tag could not be resolved and none was given: {error}")
    if named and named != declared:
        sys.exit(
            f"ZIHIN_MODEL is {named!r} but the run declares {declared!r} "
            "(protocol conditions table). Two names for one run is the defect this "
            "check exists to catch; remove the environment override or change the "
            "declaration deliberately."
        )
    return declared


MODEL = _model()
WORKDIR = pathlib.Path(os.environ.get("ZIHIN_WORKDIR", "/content/zihin"))
DRIVE_ROOT = pathlib.Path(os.environ.get("ZIHIN_DRIVE_ROOT", "/content/drive/MyDrive/zihin"))
BASE_URL = os.environ.get("MODEL_SERVER_URL", "http://127.0.0.1:11434")
# The model cache is on the runtime disk, not on Drive; Drive keeps the record
# database. The check follows the cache, otherwise it would measure free space
# on a volume nothing writes to.
MODEL_CACHE = pathlib.Path(os.environ.get("ZIHIN_MODEL_CACHE", "/content/ollama"))
REGISTRY = "https://registry.ollama.ai/v2/library"

# Room for the Ollama binary and the CUDA libraries bundled with it. Not measured
# on Colab; a ceiling chosen high enough that being wrong shows up here as a
# warning rather than as an install that dies halfway through.
OLLAMA_INSTALL_BYTES = 2_500_000_000
# The record database, the episode logs and the AppWorld data under the checkout.
WORKDIR_BYTES = 3_000_000_000
# The VRAM need is derived from the model's measured size rather than written
# down for one model. It was 11800, which is section 15.8's estimate for 14B; on
# a 32B run that number would have passed a card that could not hold the model.
# The multiplier covers the KV cache and the compute buffers: measured locally at
# 7B, weights 5.16 GiB and a 32K q8_0 KV cache 0.93 GiB, so about 1.2 with room.
# It is an estimate and it does not decide - residency does (section 15.3).
VRAM_MULTIPLIER = 1.25

results: list[tuple[str, str, str, str]] = []


def note(state: str, name: str, detail: str, remedy: str = "") -> None:
    """One line of the report. State is ok, MISSING, will-install or unknown."""
    results.append((state, name, detail, remedy))


def binary(name: str, why: str, package: str) -> None:
    found = shutil.which(name)
    if found:
        note("ok", name, f"{found} - {why}")
    else:
        note("MISSING", name, why, f"apt-get install -y {package}")


def model_bytes() -> int | None:
    """The model size, asked of the registry rather than estimated."""
    name, _, version = MODEL.partition(":")
    request = urllib.request.Request(
        f"{REGISTRY}/{name}/manifests/{version}",
        headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as answer:
            manifest = json.load(answer)
    except (urllib.error.URLError, OSError, ValueError) as error:
        note(
            "unknown",
            "model size",
            f"the registry did not answer for {MODEL} ({type(error).__name__})",
            "check the runtime network; the pull in step G needs the same host",
        )
        return None
    total = sum(layer.get("size", 0) for layer in manifest.get("layers", []))
    note("ok", "model size", f"{MODEL} is {total / 1e9:.2f} GB, asked of the registry")
    return total


def space(where: pathlib.Path, needed: int, why: str) -> None:
    probe = where
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        free = shutil.disk_usage(probe).free
    except OSError as error:
        note("unknown", f"space at {where}", f"could not be read ({error})")
        return
    detail = f"{free / 1e9:.1f} GB free, {needed / 1e9:.1f} GB needed - {why}"
    if free >= needed:
        note("ok", f"space at {where}", detail)
    else:
        remedy = "free space up, or move the path to a volume with room"
        note("MISSING", f"space at {where}", detail, remedy)


def writable(where: pathlib.Path, why: str) -> None:
    try:
        where.mkdir(parents=True, exist_ok=True)
        probe = where / ".zihin-write-probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
    except OSError as error:
        remedy = "check the mount and its permissions"
        note("MISSING", f"write to {where}", f"{why} ({error})", remedy)
        return
    note("ok", f"write to {where}", why)


def port_state() -> None:
    address, _, port = BASE_URL.rpartition(":")
    host = address.split("//")[-1]
    try:
        number = int(port)
    except ValueError:
        note("unknown", "server port", f"{BASE_URL} carries no port")
        return
    probe = socket.socket()
    probe.settimeout(3)
    taken = probe.connect_ex((host, number)) == 0
    probe.close()
    if not taken:
        note("ok", "server port", f"{host}:{number} is free for the server to take")
        return
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/tags", timeout=5):
            note("ok", "server port", f"{host}:{number} is already serving the model API")
    except Exception:
        note(
            "MISSING",
            "server port",
            f"{host}:{number} is held by something that is not the model API",
            "stop what holds the port, or set OLLAMA_HOST to a free one",
        )


def interpreter() -> None:
    python = WORKDIR / ".venv/bin/python"
    if not python.exists():
        note(
            "MISSING",
            "project environment",
            f"{python} does not exist",
            "step 2 of scripts/bootstrap_repo.sh did not build the environment",
        )
        return
    for module in ("zihin", "appworld", "appworld_agents"):
        done = subprocess.run(
            [str(python), "-c", f"import {module}"], capture_output=True, text=True
        )
        if done.returncode == 0:
            note("ok", f"import {module}", f"resolves in {python}")
        else:
            last = done.stderr.strip().splitlines()[-1:] or ["no message"]
            note(
                "MISSING",
                f"import {module}",
                f"{python} cannot import it: {last[0][:90]}",
                "the package landed in another environment; see K-129",
            )


def gpu(model_bytes: int | None = None) -> None:
    if not shutil.which("nvidia-smi"):
        note(
            "MISSING",
            "nvidia-smi",
            "the environment measurement refuses to run without a GPU",
            "switch the runtime type to a GPU",
        )
        return
    done = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        note("MISSING", "nvidia-smi", f"it did not answer: {done.stderr.strip()[:80]}")
        return
    name, total = (part.strip() for part in done.stdout.strip().splitlines()[0].split(",")[:2])
    if model_bytes is None:
        note("unknown", "GPU", f"{name}, {total} MiB total; the model size is unknown")
        return
    needed = int(model_bytes / 1024**2 * VRAM_MULTIPLIER)
    detail = f"{name}, {total} MiB total, {needed} MiB estimated for {MODEL}"
    note("ok" if int(total) >= needed else "MISSING", "GPU", detail, "use a larger GPU")


def zstd() -> None:
    """Measured absent from the Colab image, and the Ollama installer needs it.

    The bootstrap installs it, so the question here is not whether zstd is
    present but whether the thing that installs it is.
    """
    if shutil.which("zstd"):
        note("ok", "zstd", "present - the Ollama installer unpacks a zstd bundle")
    elif shutil.which("apt-get"):
        note("will-install", "zstd", "absent; step F installs it with apt-get before Ollama")
    else:
        note(
            "MISSING",
            "zstd",
            "absent, and apt-get is not here to install it",
            "install zstd by whatever means this image has; the Ollama installer needs it",
        )


# Every file the run reads, with who reads it and where it comes from. Written
# after the third time a fresh environment exposed a derived artefact the local
# machine had accumulated and the repository did not carry: first the appworld
# LFS objects, then the data cache, then the shield's write set. The class is
# always the same and it is invisible where the file happens to exist, so the
# remedy is a list rather than another repair.
#
# Not here: `config/analysis.yaml`, which the analysis reads after the run, and
# `results/zihin-3.sqlite`, which the run creates. A check that demanded an
# output would refuse to let the first run start.
REQUIRED_FILES = (
    (
        "inputs/write-set-static.json",
        "the shield's write set; the compiler and the miner read it too",
        "the repository, verified against the installed appworld package",
    ),
    (
        "config/models.yaml",
        "the scale axis, temperature, seeds, context window",
        "the repository",
    ),
    (
        "config/recording.yaml",
        "the recording limits the manifest carries",
        "the repository",
    ),
    (
        "config/scaffold.yaml",
        "the slot position and the prompt ceiling",
        "the repository",
    ),
    (
        "config/skills_failures.yaml",
        "the slots of the conditions above baseline",
        "the repository",
    ),
    (
        "config/sandbox.yaml",
        "the sandbox limits, read when the sandbox is on",
        "the repository",
    ),
    (
        "prompts/react_code_agent/instructions.txt",
        "the slotted prompt each episode renders from",
        "the repository",
    ),
    (
        "prompts/react_code_agent/instructions.reference.txt",
        "the byte anchor the unmodified reference prompt is compared against",
        "the repository",
    ),
    (
        "data/tasks",
        "the AppWorld tasks themselves",
        "appworld download data, or the Drive cache the bootstrap links",
    ),
)


def required_files() -> None:
    """Presence of every input, by name, with where a missing one comes from."""
    scan = os.environ.get("ZIHIN_SCAN", "results/bant-taramasi.json")
    entries = REQUIRED_FILES + (
        (
            scan,
            "which tasks run and in which band (ZIHIN_SCAN)",
            "the repository: a measurement output that a later measurement reads",
        ),
    )
    for name, who, where in entries:
        path = REPOSITORY / name
        if path.exists():
            note("ok", name, who)
        else:
            note("MISSING", name, f"{who} - absent", f"comes from: {where}")


def declared_conditions() -> None:
    """Do the protocol's declared conditions match what the run will use.

    Third instance of the same drift, and the reason it is asked here: the two
    earlier ones were found in the manifest *after* the run, which is one whole
    round too late. The check reads the protocol's table and the run's command,
    and compares them as numbers rather than as prose (S-58).
    """
    done = subprocess.run(
        [sys.executable, "scripts/check_declared_conditions.py"],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
    )
    if done.returncode == 0:
        note("ok", "declared conditions", "the protocol's table and the run agree")
        return
    disagreeing = [line[4:].strip() for line in done.stdout.splitlines() if line.startswith("  - ")]
    note(
        "MISSING",
        "declared conditions",
        disagreeing[0] if disagreeing else "the check reported a disagreement",
        "run scripts/check_declared_conditions.py and read the whole table",
    )


def server_log_path() -> None:
    """Which file the manifest's settings will be read from.

    It cannot exist yet - the server starts after this check - so what is asked
    is whether the run will look in a place that can exist here. The configured
    fallback is the development machine's Windows path; if it is what resolves
    and its directory is absent, the run will fail at its first episode and the
    message will name a setting rather than a path.
    """
    resolved = os.environ.get("ZIHIN_SERVER_LOG")
    if resolved:
        note("ok", "server log path", f"{resolved} (from ZIHIN_SERVER_LOG)")
        return
    try:
        import yaml

        configured = yaml.safe_load(
            (REPOSITORY / "config/models.yaml").read_text(encoding="utf-8")
        )["server_log"]
    except Exception as error:
        note("MISSING", "server log path", f"could not be resolved ({error})")
        return
    parent = pathlib.Path(configured).parent
    if parent.exists():
        note("ok", "server log path", f"{configured} (configured fallback)")
        return
    note(
        "MISSING",
        "server log path",
        f"{configured} is the configured fallback and {parent} does not exist here",
        "export ZIHIN_SERVER_LOG to the file this environment's server writes to",
    )


def write_set_matches() -> None:
    """The shield's input is verified, not assumed.

    Re-derived from the installed appworld package and compared byte for byte
    with the committed file. Regenerating instead would leave a silent
    difference between environments: a slightly different package derives a
    slightly different write set, the shield blocks different calls, and nobody
    is told.
    """
    if not (REPOSITORY / "inputs/write-set-static.json").exists():
        note("MISSING", "write set contents", "the file is absent, so nothing to compare")
        return
    done = subprocess.run(
        [sys.executable, "scripts/setup/derive_write_set.py", "--check"],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
    )
    if done.returncode == 0:
        note("ok", "write set contents", "byte for byte what the installed appworld derives")
        return
    last = [
        line
        for line in done.stdout.splitlines()
        if "does NOT match" in line or "does not exist" in line
    ]
    note(
        "MISSING",
        "write set contents",
        last[0] if last else "the derivation disagrees with the committed file",
        "run scripts/setup/derive_write_set.py --check and read what it says",
    )


def working_copy() -> None:
    """How far behind `origin/main` this checkout is, said by name.

    `S-64` wrote the question down — "how many commits are there between the
    branch and origin/main is a single command, and no check asks it" — and then
    it bit: a Colab session cloned a branch that had merged and gone stale, the
    files added after it were simply absent, and Python reported a
    `FileNotFoundError`. That error names the wrong thing. It reads as "this file
    was never written", and the first reading was that the work had not been
    done. A stale copy has to say it is stale.

    **It fetches.** Comparing against a `origin/main` that is itself old answers
    nothing, so the check refreshes the remote ref first. The fetch is read-only
    and best effort: if there is no network or no remote, the answer is *unknown*,
    which is not the same as *up to date* (K-131).
    """

    def git(*arguments: str) -> tuple[int, str]:
        try:
            done = subprocess.run(
                ["git", *arguments], cwd=REPOSITORY, capture_output=True, text=True
            )
        except FileNotFoundError:
            return 127, ""
        return done.returncode, done.stdout.strip()

    code, _ = git("rev-parse", "--is-inside-work-tree")
    if code != 0:
        note("unknown", "working copy", "not a git checkout, so it cannot be compared")
        return

    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    _, head = git("rev-parse", "--short", "HEAD")
    fetched, _ = git("fetch", "--quiet", "origin", "main")
    if fetched != 0:
        note(
            "unknown",
            "working copy",
            f"on {branch} at {head}; origin could not be fetched, so how far behind "
            "it is could not be answered",
        )
        return

    code, behind = git("rev-list", "--count", "HEAD..origin/main")
    if code != 0 or not behind.isdigit():
        note("unknown", "working copy", f"on {branch} at {head}; origin/main is not readable")
        return
    _, ahead = git("rev-list", "--count", "origin/main..HEAD")
    count = int(behind)
    if count == 0:
        extra = f", {ahead} ahead" if ahead.isdigit() and int(ahead) else ""
        note("ok", "working copy", f"{branch} at {head} carries everything in origin/main{extra}")
        return
    note(
        "MISSING",
        "working copy",
        f"{branch} at {head} is {count} commit(s) BEHIND origin/main; files added in "
        "those commits are absent here and will look like they were never written",
        "git fetch origin && git checkout main && git reset --hard origin/main",
    )


def reads_the_library(prefix: str | None) -> tuple[str | None, bool | None]:
    """(prefix, will the run read the library). None for either when not known.

    A card-free run never resolves a library, so requiring one of it is the right
    question about the wrong run. The answer is declared: the prefix names its
    conditions section and that section names the condition (K-152).

    **Three sources, in order, and no default.** The prefix given on the command
    line; failing that the notebook's own run command, which is where a
    notebook-driven run declares itself; failing that nothing. The condition
    comes from the section when it declares one, and otherwise from the runner
    the command names — read by the same function the conditions check uses, so
    there is no second copy of the rule. When neither answers, the answer is
    *unknown*: undetermined is not a no, and a default is not an answer (K-131).
    """
    if not prefix:
        try:
            from zihin.declared import run_prefix

            prefix = run_prefix()
        except Exception:  # noqa: BLE001 - no run command is an answer of its own
            return None, None
    try:
        import importlib.util

        from zihin.declared import conditions

        _, table = conditions(prefix)
        # The experiment declares its conditions as a list; it reads the library when
        # any one of them carries cards.
        declared = (
            (table.get("koşul") or table.get("condition") or table.get("conditions") or "")
            .strip()
            .strip("`*")
        )
        if not declared:
            spec = importlib.util.spec_from_file_location(
                "check_declared_conditions", REPOSITORY / "scripts/check_declared_conditions.py"
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["check_declared_conditions"] = module
            spec.loader.exec_module(module)
            declared = module.condition_of_the_runner(prefix) or ""
    except Exception:  # noqa: BLE001 - an unreadable declaration answers nothing
        return prefix, None
    if not declared:
        return prefix, None
    return prefix, {name.strip() for name in declared.split(",")} != {"baseline"}


# The run whose section declares the delivered library. Named once: the
# identities belong to the accumulation, and every later run - carded or not -
# has to resolve that same pair.
DELIVERED_BY = "bir1"


def delivered_library() -> None:
    """Is the library that resolves the one the accumulation delivered?

    `latest_library_and_index` picks by row count, so a library mined later
    would take this one's place with nothing said. The library is the
    experiment's input, so its identity is declared and compared rather than
    discovered (K-164).

    Asked of every run, not only a carded one: a baseline run does not read the
    library, but a pointer that has drifted is worth knowing about before the
    carded run starts, not during it.
    """
    try:
        from zihin.declared import declared_field
        from zihin.records import LIBRARY_SERIES, open_library
    except Exception as error:  # noqa: BLE001 - the import itself is the answer
        note("unknown", "delivered library", f"could not be read ({error})")
        return
    try:
        declared_library = declared_field("delivered_library_id", DELIVERED_BY)
        declared_index = declared_field("delivered_index_id", DELIVERED_BY)
    except Exception:  # noqa: BLE001 - nothing declared is not a mismatch
        note("unknown", "delivered library", f"{DELIVERED_BY} declares no delivered identity")
        return
    if not (REPOSITORY / LIBRARY_SERIES).exists():
        note(
            "unknown",
            "delivered library",
            f"{LIBRARY_SERIES} is not here, so what resolves cannot be compared",
        )
        return
    try:
        connection, library_id, index_id = open_library(str(REPOSITORY / LIBRARY_SERIES))
        connection.close()
    except Exception as error:  # noqa: BLE001 - a refusal is the answer
        note("MISSING", "delivered library", str(error).split(". ")[0])
        return
    for name, resolved, declared in (
        ("delivered library", library_id, declared_library),
        ("delivered index", index_id, declared_index),
    ):
        if resolved == declared:
            note("ok", name, f"{resolved} resolves from {LIBRARY_SERIES}")
        else:
            note(
                "MISSING",
                name,
                f"{LIBRARY_SERIES} resolves {resolved!r}; the protocol declares {declared!r}",
                "re-mine, or move the declaration with a dated addendum",
            )


def run_ledger_table(path: pathlib.Path | None = None) -> None:
    """Does the record carry the ledger table that branch A of a run reads?

    K-162 moved the ledger into the record, and the table is created the first
    time the record is opened for writing by code that knows it. The accumulation
    run's last episode was written an hour before that code existed, so the real
    record never went through the migration; the merge did not either, because
    `merge_series.py` does not open through `open_database`. Branch A reads this
    table, and without it the stopping rule is half a rule again (K-171).

    Asked read-only and asked of every run: the migration would repair the file
    as a side effect, and a check that repairs what it inspects reports nothing.
    """
    try:
        from zihin.records import ACTIVE_SERIES, table_matches_schema
    except Exception as error:  # noqa: BLE001 - the import itself is the answer
        note("unknown", "run ledger", f"could not be read ({error})")
        return
    path = REPOSITORY / ACTIVE_SERIES if path is None else path
    if not path.exists():
        note("unknown", "run ledger", f"{path.name} is not here, so its tables cannot be read")
        return
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        verdict = table_matches_schema(connection, "run_ledger")
    finally:
        connection.close()
    remedy = (
        "open the record once through zihin.records.open_database; it creates the "
        "table from the schema's own CREATE TABLE, constraints included"
    )
    if verdict is None:
        note(
            "MISSING",
            "run ledger",
            f"{path.name} has no run_ledger table; branch A could not be evaluated (K-171)",
            remedy,
        )
    elif not verdict:
        note(
            "MISSING",
            "run ledger",
            f"run_ledger in {path.name} is not the schema's table; its constraints may be gone",
            remedy,
        )
    else:
        note("ok", "run ledger", f"present in {path.name}, with the schema's constraints")


def skill_library(prefix: str | None = None) -> None:
    """Is there a library where the code says the library is?

    A carded run resolves the library at the moment it needs a card, which is
    after the episode has started. Asking here moves the refusal to before the
    run. The question is not "is there a library somewhere" but "is there one in
    `LIBRARY_SERIES`", because that constant is what every caller reads (K-143).

    **And only when the run reads it.** A `baseline` run carries no cards, so a
    missing library stops nothing. Asked unconditionally, this line was the right
    question about the wrong run and it blocked a clean Colab setup (K-152).
    """
    prefix, needed = reads_the_library(prefix)
    if needed is None:
        # K-131: undetermined is not a no, and a default is not an answer. Asking
        # every requirement of every run type would block a run that does not have
        # them; passing them silently would clear a run that does.
        note(
            "unknown",
            "skill library",
            (
                f"{prefix} declares no condition and its runner could not be read, so "
                "whether it needs the library is not known"
                if prefix
                else "no run prefix was given and the notebook names none, so which "
                "requirements apply is not known"
            ),
            "declare a condition row for this prefix, or pass --prefix",
        )
        note("unknown", "library pointer", "not asked: the run type is not known")
        return
    if needed is False:
        note(
            "ok",
            "skill library",
            f"not read by {prefix}: its declared condition is baseline, so no card is retrieved",
        )
        note("ok", "library pointer", f"not read by {prefix}")
        return
    try:
        from zihin.records import ACTIVE_SERIES, LIBRARY_SERIES, open_library
    except Exception as error:  # noqa: BLE001 - the import itself is the answer
        note("unknown", "skill library", f"zihin.records did not import: {error}")
        return

    if not (REPOSITORY / LIBRARY_SERIES).exists():
        note(
            "MISSING",
            "skill library",
            f"{LIBRARY_SERIES} is not here, and it is where the library lives",
            "carry the series over, or re-mine the library and move LIBRARY_SERIES with it",
        )
        return
    try:
        connection, library_id, index_id = open_library(str(REPOSITORY / LIBRARY_SERIES))
    except Exception as error:  # noqa: BLE001 - a refusal is the answer
        note("MISSING", "skill library", str(error).split(". ")[0], "build_skill_library.py")
        return
    skills = connection.execute(
        "SELECT COUNT(*) FROM skills WHERE library_id = ?", (library_id,)
    ).fetchone()[0]
    patterns = connection.execute(
        "SELECT COUNT(*) FROM failure_patterns WHERE index_id = ?", (index_id,)
    ).fetchone()[0]
    connection.close()
    where = (
        "the same series runs are written to" if LIBRARY_SERIES == ACTIVE_SERIES else LIBRARY_SERIES
    )
    # K-143 wrote this gap down and left it open: re-mining puts the library in
    # whichever series is active, and the constant does not follow on its own. The
    # accumulation run mines every thirty episodes, so the first block is where it
    # would bite. Asking here moves the answer to before a carded run.
    if LIBRARY_SERIES != ACTIVE_SERIES and (REPOSITORY / ACTIVE_SERIES).exists():
        try:
            newer = sqlite3.connect(f"file:{REPOSITORY / ACTIVE_SERIES}?mode=ro", uri=True)
            elsewhere = newer.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
            newer.close()
        except Exception:  # noqa: BLE001 - an unreadable series answers nothing
            elsewhere = 0
        if elsewhere:
            note(
                "MISSING",
                "library pointer",
                f"{ACTIVE_SERIES} now carries {elsewhere} skill(s) but LIBRARY_SERIES "
                f"still names {LIBRARY_SERIES}",
                "move zihin.records.LIBRARY_SERIES to the series it was re-mined into (K-143)",
            )
        else:
            note("ok", "library pointer", f"{LIBRARY_SERIES}; nothing newer elsewhere")
    else:
        note("ok", "library pointer", "one series; nothing to keep in step")

    note("ok", "skill library", f"{skills} skills, {patterns} patterns in {where}")


PARSER = argparse.ArgumentParser(description="Prerequisites for the run about to happen.")
PARSER.add_argument(
    "--prefix",
    default=None,
    help="the run prefix, so requirements can be read from its declared conditions",
)
OPTIONS = PARSER.parse_args()


def main() -> None:
    print(f"model   : {MODEL}")
    print(f"workdir : {WORKDIR}")
    print(f"drive   : {DRIVE_ROOT}")
    print()

    binary("curl", "fetches the Ollama installer", "curl")
    binary("tar", "the Ollama installer unpacks with it", "tar")
    binary("git", "the dirty-tree gate and the results push read it", "git")
    zstd()
    # The registry is asked first: the GPU check needs the model's real size, and
    # a need written for one model is a need that passes the wrong card.
    size = model_bytes()
    gpu(size)
    interpreter()
    working_copy()
    required_files()
    skill_library(OPTIONS.prefix)
    delivered_library()
    run_ledger_table()
    write_set_matches()
    server_log_path()
    declared_conditions()

    space(MODEL_CACHE, (size or 9_000_000_000) + 500_000_000, "the model cache")
    space(pathlib.Path("/usr/local"), OLLAMA_INSTALL_BYTES, "the Ollama install")
    space(WORKDIR, WORKDIR_BYTES, "the record database and the episode logs")

    writable(MODEL_CACHE, "the model is pulled into it once per session")
    writable(DRIVE_ROOT / "results", "the record database has to survive the session")
    writable(WORKDIR / "results", "the run writes its database here")

    port_state()

    width = max(len(name) for _, name, _, _ in results)
    marks = {"ok": "  ok  ", "will-install": " will ", "unknown": "  ??  "}
    for state, name, detail, _ in results:
        print(f"[{marks.get(state, ' MISS ')}] {name.ljust(width)}  {detail}")

    missing = [(n, d, r) for state, n, d, r in results if state == "MISSING"]
    unknown = [n for state, n, _, _ in results if state == "unknown"]
    print()
    if unknown:
        print(f"could not be answered: {', '.join(unknown)}")
    if not missing:
        print(f"prerequisites: all {len(results)} answered, nothing missing")
        return
    print(f"{len(missing)} PREREQUISITE(S) MISSING. All of them, not the first one:")
    for name, detail, remedy in missing:
        print(f"  - {name}: {detail}")
        if remedy:
            print(f"      fix: {remedy}")
    sys.exit(1)


if __name__ == "__main__":
    main()
