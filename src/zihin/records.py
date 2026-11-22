"""Opens the record database and writes rows.

The schema is in `schema.sql`. This module is the thin layer that applies it and
offers the write surface. No ORM; for a tool that runs on one machine with no
concurrent writer it would be a dependency for nothing.

Architectural rule: writing to the record happens on the host side, in the
runner's process. Nothing writes here from inside the code the agent runs (K-14).
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
import sqlite3
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# The active measurement series. Series 1 (`results/zihin.sqlite`) was run under
# the old stopping rule and without the machine half of the manifest contract
# (S-27, S-29); it is still read, not written. It refuses new writes anyway,
# because the new columns cannot be migrated into it.
#
# The path sits in one place: if the runner and the scanner each carried their
# own constant, one of them could summarise a different file from the one it
# wrote, and the fault would be silent.
# Series 3 opened when the 32B measurement was refused by the manifest guard:
# `results/zihin-2.sqlite` carries twelve CHECK constraints but not
# `shield_mode IN ('shadow', 'enforce', 'off')`, because the column was added by
# `ALTER TABLE` and SQLite's ALTER TABLE carries no constraints (S-29, measured).
# A new file is the only way the contract comes into force, and that is what
# opened series 2 as well. Series 2 stays readable and is still quoted; every
# number says which series it came from (protocol §6).
ACTIVE_SERIES = "results/zihin-3.sqlite"

# Where the skill library and the failure index live — a different question from
# ACTIVE_SERIES, and since series 3 opened the two answers are different files.
#
# A series opens for a *schema* reason: a CHECK constraint that ALTER TABLE
# cannot add. The library has nothing to do with that. It is mined once from a
# body of episodes and belongs to the series those episodes are in; it does not
# move when a new file opens for the next run. Reading it from ACTIVE_SERIES
# asks "where are we writing" when the question is "where was it mined", and the
# two coincided until series 3, so the fault was invisible for exactly as long
# as they agreed (K-143).
#
# It is a constant rather than "whichever file has rows", because a search would
# make the answer depend on what happens to be on the disk. If the library is
# ever re-mined into a newer series, this line changes and the change is a
# commit someone can read.
# Where the library the retriever reads lives. It moved here when the
# accumulation run re-mined the library into the active series: the builders
# write into `ACTIVE_SERIES`, and until this line followed them a carded run
# would have resolved the old four-skill library from series 2 while eleven
# skills sat in series 3. The preflight said so at every block boundary (K-143,
# closed in K-164).
LIBRARY_SERIES = ACTIVE_SERIES

# The series the compiler's thresholds were calibrated on: the DeepSeek
# bootstrap corpus. It is not "where the library lives" and it never moves with
# it - two setup measurements read it by name, and while one constant served
# both meanings, moving the library pointer would have repointed them without a
# word (K-164).
CALIBRATION_SERIES = "results/zihin-2.sqlite"

# K-36's five categories. The same set as the CHECK constraint in the schema.
STEP_OUTCOMES = (
    "no_code",
    "unparseable",
    "context_overflow",
    "execution_error_no_action",
    "execution_ok_no_action",
)


class RecordError(RuntimeError):
    """A record-layer rule was violated."""


@dataclass(frozen=True)
class ModelServingConfig:
    """Contents of `config/models.yaml`."""

    models: tuple[str, ...]
    num_ctx: int
    temperature: float
    base_seed: int
    seed_count: int
    keep_alive: str
    kv_cache_type: str
    flash_attention: bool
    server_log: str

    def seed_for(self, task_id: str, seed_index: int) -> int:
        """The episode seed is derived from the task id and the seed index (K-20).

        Model and condition deliberately stay out. In a paired design the seed is
        a blocking factor: the same task and the same seed index must give the
        same seed under every model and every condition. Otherwise the model
        difference and the seed difference interleave and cannot be separated.

        This rule was learned through a mistake. The seed used to carry `run_id`
        as well, and `run_id` contained the model name, so every model ran on a
        different seed.
        """
        if not 0 <= seed_index < self.seed_count:
            raise RecordError(
                f"seed_index must be between 0 and {self.seed_count - 1}, got {seed_index}"
            )
        ham = f"{self.base_seed}:{task_id}:{seed_index}".encode()
        return int.from_bytes(hashlib.sha256(ham).digest()[:4], "big")


def load_model_config(path: str | Path) -> ModelServingConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    expected = {
        "models",
        "num_ctx",
        "temperature",
        "base_seed",
        "seed_count",
        "keep_alive",
        "kv_cache_type",
        "flash_attention",
        "server_log",
    }
    missing = expected - set(raw)
    fazla = set(raw) - expected
    if missing:
        raise RecordError(f"missing field in model config: {sorted(missing)}")
    if fazla:
        raise RecordError(f"unrecognised field in model config: {sorted(fazla)}")
    # The design says "at least three dense sizes" (K-61). The configuration
    # cannot encode a stricter constraint than the design: a family that fits
    # four sizes used to fail here.
    if len(raw["models"]) < 3:
        raise RecordError(f"the scale axis carries at least three points, got {len(raw['models'])}")
    for tag in raw["models"]:
        if ":" not in tag or "-q" not in tag:
            raise RecordError(
                f"the model tag must be complete, size and quantisation included: {tag!r}"
            )
    if not 0 < raw["temperature"] < 1:
        raise RecordError(
            f"temperature must be greater than zero and less than one, got {raw['temperature']}"
        )
    raw["models"] = tuple(raw["models"])
    return ModelServingConfig(**raw)


@dataclass(frozen=True)
class RecordingLimits:
    """Contents of `config/recording.yaml`."""

    observation_max_bytes: int
    run_disk_quota_bytes: int
    on_quota_exceeded: str
    no_progress_limit: int
    max_output_tokens: int
    max_prompt_characters: int


def load_recording_limits(path: str | Path) -> RecordingLimits:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    expected = {
        "observation_max_bytes",
        "run_disk_quota_bytes",
        "on_quota_exceeded",
        "no_progress_limit",
        "max_output_tokens",
        "max_prompt_characters",
    }
    missing = expected - set(raw)
    fazla = set(raw) - expected
    if missing:
        raise RecordError(f"missing field in recording config: {sorted(missing)}")
    if fazla:
        raise RecordError(f"unrecognised field in recording config: {sorted(fazla)}")
    if raw["on_quota_exceeded"] != "stop":
        raise RecordError(f"on_quota_exceeded can only be 'stop', got {raw['on_quota_exceeded']!r}")
    if not isinstance(raw["no_progress_limit"], int) or raw["no_progress_limit"] < 1:
        raise RecordError(
            f"no_progress_limit must be a positive integer, got {raw['no_progress_limit']!r}"
        )
    # No silent default: this value is part of the measurement's definition and
    # getting it wrong moves the result between 6/30 and 20/30 (S-26).
    if not isinstance(raw["max_output_tokens"], int) or raw["max_output_tokens"] < 1:
        raise RecordError(
            f"max_output_tokens must be a positive integer, got {raw['max_output_tokens']!r}"
        )
    # The scaffold's character ceiling (S-47). -1 means "no ceiling" and matches
    # the agent's `None`; every other negative value is meaningless. Zero is
    # refused too: a zero ceiling would mean no context at all and would break
    # every episode in silence.
    ceiling = raw["max_prompt_characters"]
    if not isinstance(ceiling, int) or (ceiling != -1 and ceiling < 1):
        raise RecordError(
            f"max_prompt_characters must be a positive integer or -1 (no ceiling), got {ceiling!r}"
        )
    return RecordingLimits(**raw)


def open_database(path: str | Path) -> sqlite3.Connection:
    """Opens the database, applying the schema when there is none.

    Foreign keys are enabled explicitly on every connection. In SQLite the
    default is off and the setting is not stored in the file, so the PRAGMA line
    in the schema is not enough on its own.
    """
    path = Path(path)
    fresh = not path.exists()
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if fresh:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.commit()
    else:
        _add_missing_columns(connection)
        _add_missing_tables(connection)
        _rebuild_changed_projections(connection)
    return connection


# Unlike adding a column, adding a **table** does not weaken the contract. ALTER
# TABLE cannot carry constraints, so a column migration is left without its CHECK
# (the S-29 lesson); but a missing table is created by the schema's own `CREATE
# TABLE` statement and brings all of its CHECKs with it. It is no different from
# its form in a fresh file.
#
# The statements are read from the schema itself and not rewritten here: a DDL
# that lives in two places drifts sooner or later.
def _schema_statements() -> list[str]:
    """The schema's statements, comments removed first and then split on `;`.

    One reader for every caller: the migration, the projection rebuild and the
    prerequisite check all ask the schema what a table should look like, and a
    second parser of the same file would drift from the first (K-171).
    """
    stripped = "\n".join(
        row
        for row in SCHEMA_PATH.read_text(encoding="utf-8").splitlines()
        if not row.strip().startswith("--")
    )
    return [statement.strip() for statement in stripped.split(";") if statement.strip()]


def schema_statement(name: str) -> str | None:
    """The schema's own CREATE statement for a table or an index, or None."""
    for statement in _schema_statements():
        matches = re.match(r"CREATE (TABLE|INDEX)\s+(\w+)", statement, re.IGNORECASE)
        if matches and matches.group(2) == name:
            return statement
    return None


def table_matches_schema(connection: sqlite3.Connection, name: str) -> bool | None:
    """None if the file has no such table; else whether its DDL is the schema's.

    Asked without opening the file for writing: `open_database` would create a
    missing table as a side effect, and a check that repairs what it inspects
    cannot report what it found.
    """
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)
    ).fetchone()
    if row is None:
        return None
    expected = schema_statement(name)
    return expected is not None and _sadelestir(row[0]) == _sadelestir(expected)


def _add_missing_tables(connection: sqlite3.Connection) -> list[str]:
    """Creates tables that the schema has and the file does not. Returns their names."""
    existing = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'index')"
        )
    }
    # **Comments are stripped first, then the text is split on `;`.** The
    # reverse order does not work, and this surfaced while the migration was
    # being tested against a copy of the real file: the schema's comments are
    # prose and prose contains semicolons ("derivation; the compiler is
    # offline"), so splitting on `;` cut a statement in the middle of a comment.
    # The cut fragment did not start with `CREATE TABLE`, so the table was
    # skipped, but the `CREATE INDEX` that followed it did match and tried to
    # index a table that did not exist. None of this would show in a freshly
    # created file.
    kurulan: list[str] = []
    for ifade in _schema_statements():
        matches = re.match(r"CREATE (TABLE|INDEX)\s+(\w+)", ifade, re.IGNORECASE | re.DOTALL)
        if not matches or matches.group(2) in existing:
            continue
        # Only the entirely missing ones are created. A missing index belonging
        # to an existing table also arrives by this path and is harmless.
        connection.execute(ifade)
        kurulan.append(matches.group(2))
    if kurulan:
        connection.commit()
    return kurulan


# Derived projections (`03-architecture.tr.md`). They are not the record: they can
# be deleted and regenerated from it, so when their schema changes they are
# rebuilt rather than migrated. The same **cannot** be done to record tables and
# is not done; this list is what that distinction looks like in code.
PROJECTION_TABLES = ("skills", "failure_patterns")


def _sadelestir(ddl: str) -> str:
    """A comparison form that removes comment and whitespace differences.

    In a fresh file the table is created with `executescript` and keeps its
    comments; on the migration path it is created without them. Same table,
    different text.
    """
    body = "\n".join(s for s in ddl.splitlines() if not s.strip().startswith("--"))
    return re.sub(r"\s+", " ", body).strip()


def _rebuild_changed_projections(connection: sqlite3.Connection) -> list[str]:
    """Drops and recreates projection tables whose schema has changed.

    Rebuilding the table rather than adding a column is the **right** move for a
    projection: migration carries no constraints, and a new column has no meaning
    on old rows — those rows are going to be regenerated anyway. The same move on
    a record table would be data loss, which is why the list is explicit and
    short.

    Regenerating is the caller's job: here the table is only emptied. Without the
    compiler running the library stays empty, and an empty library cannot produce
    a wrong result in silence.
    """
    expected: dict[str, list[str]] = {}
    for ifade in _schema_statements():
        matches = re.match(r"CREATE (TABLE|INDEX)\s+(\w+)(.*)", ifade, re.IGNORECASE | re.DOTALL)
        if not matches:
            continue
        name = matches.group(2)
        sahip = name if matches.group(1).upper() == "TABLE" else None
        if sahip is None:
            target = re.search(r"\bON\s+(\w+)", ifade, re.IGNORECASE)
            sahip = target.group(1) if target else None
        if sahip in PROJECTION_TABLES:
            expected.setdefault(sahip, []).append(ifade)

    yenilenen: list[str] = []
    for tablo, ifadeler in expected.items():
        row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (tablo,)
        ).fetchone()
        if row is None:
            continue
        if _sadelestir(row["sql"]) == _sadelestir(ifadeler[0]):
            continue
        connection.execute(f"DROP TABLE {tablo}")
        for ifade in ifadeler:
            connection.execute(ifade)
        yenilenen.append(tablo)
    if yenilenen:
        connection.commit()
    return yenilenen


# The schema is applied only to a fresh file, so a column added later is absent
# from an old database. Migration is limited to adding columns: the append-only
# rule already forbids touching rows (K-14).
#
# boot_id, wall_clock_utc, journal_mode and synchronous_setting are not on this
# list, and deliberately so. SQLite's ALTER TABLE was measured: it adds a NOT
# NULL column only with a constant default, it refuses a CURRENT_TIMESTAMP
# default and a CHECK, and there is no ADD CONSTRAINT. The boot id and the wall
# clock under which the old manifests ran cannot be recovered; a constant default
# would be inventing them, and an invented value breaks the very thing the
# append-only rule protects.
#
# The consequence is intended: these columns are not added to an old database, so
# an old file does not accept a new manifest. The new measurement series is
# written to a file built from the schema from scratch, and the old file stays as
# it is under the weaker contract it was recorded with. working_tree IS here,
# because its default is correct for old rows: series 2's episodes ran before the
# gate existed and the tree's state genuinely was not recorded. The column's
# CHECK cannot be migrated, so in series 2 the field is enforced only at the
# Python layer. That cost is small: the field's truth cannot be verified by
# machine anyway, and a raw INSERT could write 'clean' on a dirty tree. The CHECK
# only guards the value set, and that was not put on the list that blocks a run.
MIGRATED_COLUMNS = (
    ("run_manifests", "max_output_tokens", "INTEGER NOT NULL DEFAULT -1"),
    ("run_manifests", "serving_mode", "TEXT NOT NULL DEFAULT 'local'"),
    ("run_manifests", "working_tree", "TEXT NOT NULL DEFAULT 'unknown'"),
    # Both are nullable and without a default: for old rows the correct value is
    # "not recorded", and NULL says exactly that.
    ("run_manifests", "library_id", "TEXT"),
    # The shield's identity. The 'off' default is not an invention for old rows
    # but the truth: those episodes ran before the shield existed. The digest is
    # nullable, because a run without a shield has no configuration to digest.
    # The columns' CHECKs cannot be migrated (the S-29 lesson), so in series 2 the
    # value set is enforced only at the Python layer; the same known limit as
    # working_tree.
    ("run_manifests", "shield_mode", "TEXT NOT NULL DEFAULT 'off'"),
    ("run_manifests", "shield_config_digest", "TEXT"),
    # The scaffold's character ceiling (S-47). Nullable and without a default:
    # old rows ran with 50000, but the manifest is append-only, so writing the
    # number after the fact is impossible — and even if it were possible it would
    # not be a record. NULL says "not recorded", -1 says "no ceiling", and the two
    # are different.
    ("run_manifests", "max_prompt_characters", "INTEGER"),
    # Sandbox fields. All nullable and without a default: old rows ran without a
    # sandbox and NULL says exactly that. The limits are in the manifest because
    # when they bind it is the sandbox, not the model, that decides the result
    # (K-D).
    ("run_manifests", "sandbox_image", "TEXT"),
    ("run_manifests", "sandbox_network_mode", "TEXT"),
    ("run_manifests", "sandbox_memory_bytes", "INTEGER"),
    ("run_manifests", "sandbox_pids_limit", "INTEGER"),
    ("run_manifests", "sandbox_step_timeout_seconds", "INTEGER"),
    ("run_manifests", "sandbox_tmpfs_bytes", "INTEGER"),
    ("run_manifests", "sandbox_cpus", "REAL"),
    ("run_manifests", "sandbox_version", "TEXT"),
    ("run_manifests", "sandbox_proxy_digest", "TEXT"),
    # Digest-based state measurement (K-93). Beside `state_change`, not inside
    # it: one carries a signed row delta, the other which model changed. Putting
    # two meanings in one column would tie a value's meaning to the mode that
    # produced it.
    ("steps", "state_hashes", "TEXT"),
    ("episodes", "step_ceiling", "INTEGER"),
    # The `skills` table is not on the migration list and cannot be: ALTER TABLE
    # adds columns, not tables. Old series carry no library and should not — the
    # library is a derived projection tied to the compiler's version, and mixing
    # it with rows another compiler produced would break the measurement.
    ("episodes", "distinct_endpoints", "INTEGER"),
    ("episodes", "distinct_resources", "INTEGER"),
)

# The constraints that carry the manifest's machine half. They are searched for
# as text, because what is measured is the file's own definition: a constraint
# being written in `schema.sql` does not mean it is in force (S-29).
MANIFEST_CONSTRAINTS = (
    "serving_mode IN ('local', 'hosted')",
    "boot_id <> ''",
    "wall_clock_utc <> ''",
    "synchronous_setting IN (1, 2, 3)",
    "context_verified = 1",
    "shield_mode IN ('shadow', 'enforce', 'off')",
)


def missing_manifest_constraints(connection: sqlite3.Connection) -> list[str]:
    """Which manifest constraints are not in force in this file.

    The schema is applied only to a file created from scratch, and SQLite's
    `ALTER TABLE` carries no constraints. In series 1 the contract was written but
    not in force; two tests checked it at schema level and could not see this,
    because they built a fresh database.
    """
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'run_manifests'"
    ).fetchone()
    if row is None:
        return list(MANIFEST_CONSTRAINTS)
    return [k for k in MANIFEST_CONSTRAINTS if k not in row[0]]


BOOT_ID_YOLU = "/proc/sys/kernel/random/boot_id"


def boot_id(path: str = BOOT_ID_YOLU) -> str:
    """The kernel's boot id; it changes on every restart.

    It makes a join across a power cut visible. `created_at` is based on
    /proc/uptime and resets on restart, so whether two manifests ran within the
    same boot can only be known from this value.
    """
    try:
        value = Path(path).read_text(encoding="ascii").strip()
    except OSError as error:
        raise RecordError(f"the boot id could not be read ({path}): {error}") from error
    if not value:
        raise RecordError(f"the boot id came back empty ({path})")
    return value


def completed_runs(connection: sqlite3.Connection, run_idler: Iterable[str]) -> set[str]:
    """Which of the given run ids were written completely.

    An interrupted run resumes from here. The source is the **database**, not the
    filesystem: the experiment output directory survives an interrupted episode,
    and a task that left a trace there would look completed.

    Completeness is what is checked, not existence — an episode row with no step
    or no verdict row does not count as completed. An episode is written in a
    single transaction, so a half-written row set is not expected; measuring the
    unexpected anyway is K-49.

    Run ids are given in full, not matched as a prefix: the pattern `bant3-` also
    catches `bant3-kapali-...` ids and two separate runs would be mixed together.
    """
    kimlikler = list(run_idler)
    if not kimlikler:
        return set()
    yer = ", ".join("?" for _ in kimlikler)
    sorgu = (
        f"SELECT e.run_id FROM episodes e WHERE e.run_id IN ({yer}) "
        "  AND (SELECT COUNT(*) FROM steps s WHERE s.episode_id = e.episode_id) > 0 "
        "  AND (SELECT COUNT(*) FROM verifier_results v WHERE v.episode_id = e.episode_id) > 0"
    )
    return {row[0] for row in connection.execute(sorgu, tuple(kimlikler))}


# The fields that must match when resuming: the ones that are part of the
# condition's definition. If they do not match, the set becomes a mixture of two
# different measurements; the manifest records that but does not by itself
# prevent it. It was caught during an explicit setup run (S-30): resuming with
# 4000 on top of two episodes whose budget was 400 would have mixed the set of
# thirty.
MANIFEST_CONDITION_FIELDS = (
    "model_tag",
    "serving_mode",
    "temperature",
    "base_seed",
    "max_output_tokens",
    # The scaffold's character ceiling (S-47). This is what decides the effective
    # context, not the token window: 50000 characters is 12799 tokens on measured
    # content, i.e. 39% of the window. Changed mid-run, half the episodes run with
    # a different context length and the difference shows up only here.
    "max_prompt_characters",
    "no_progress_limit",
    "num_ctx_requested",
    "num_ctx_effective",
    "kv_cache_type",
    "flash_attention",
    "appworld_commit",
    "instruction_file_digest",
    "library_id",
    # If the shield's mode or configuration changes mid-run the violations it
    # produces cannot be compared. The write set changed twice in one day, so this
    # is not a theoretical risk.
    "shield_mode",
    "shield_config_digest",
    # A different commit is definable, a dirty tree is not. If the first half runs
    # clean and the second half dirty, which code the second half ran on is
    # undetermined.
    "working_tree",
)

# The condition fields that come from the episode table.
EPISODE_CONDITION_FIELDS = ("condition", "split", "step_ceiling")

# The code that decides what happens inside an episode. If one of these paths
# changed between two commits, resuming is refused; if none did, a commit
# difference is only a warning. The distinction buys this: "a different commit"
# and "a different commit that changes the measurement" are separated, and the
# decision is made by machine.
#
# The code that decides which episode runs is outside the list. `src/zihin/records.py`
# is outside it too, and that is a known coarseness: this module carries both the
# recorder's write path and the run-orchestration helpers, and a legitimate
# resume-affecting change can land in the second. Protecting the write path as
# well would require splitting the module.
MEASUREMENT_DEFINING_PATHS = (
    "src/zihin/recording_agent.py",
    "src/zihin/api_capture.py",
    "src/zihin/scaffold.py",
    "src/zihin/state_probe.py",
    "src/zihin/verification.py",
    "src/zihin/model_server.py",
    "src/zihin/schema.sql",
    # The shield's predicate and the proxy that derives the allowed app set. The
    # proxy is not an approximation but the specification itself: the shield's
    # allowed set is derived from the task text, not from ground truth. Changing
    # it changes what the shield blocks.
    "src/zihin/shield.py",
    "src/zihin/allowed_apps.py",
    # The mount point. As decisive as the predicate: this is where resolution
    # happens, and which endpoint a call resolves to decides which decision is
    # made (S-36 was exactly this).
    "src/zihin/shield_mount.py",
    # The compiler and the index. The library and the index are derived
    # projections, so they are not measurements themselves; but they decide what
    # a condition is given, and changing them changes what a run with mechanisms
    # sees.
    "src/zihin/compiler.py",
    "src/zihin/failure_index.py",
    # The retriever and the card format. A continuation of the same rationale,
    # and they were added to the list late: the retriever decides which card goes
    # to which task, the card format decides what the model reads. Because the
    # gate was narrowed to the list (K-76), a missing entry is no longer just
    # coarseness but a gate that does not close.
    "src/zihin/retriever.py",
    "src/zihin/cards.py",
    # What each condition puts in the slot (K-181): which pool each kind comes
    # from and the count it is cut to. The runner and the analysis sets both read
    # it, so a change here changes what every card-carrying condition is given.
    "src/zihin/slots.py",
    # Endpoint resolution. The third entry added to the list late, and for a
    # reason of the same class: which endpoint a call resolves to decides the
    # record's identity, and S-32 broke exactly here. With the sandbox it took on
    # a second job — the code that converts a query parameter's type from the
    # route signature lives here (K-92) — so changing it can change the identity
    # of 1090 actions.
    "src/zihin/api_routes.py",
    # The recording proxy and the sandbox. The proxy enters the list as one of
    # K-A's three conditions: the recording itself passes through it. The sandbox
    # enforces the limits, and when a limit binds it is the sandbox, not the
    # model, that decides the result (K-D).
    "src/zihin/recording_proxy.py",
    "src/zihin/sandbox.py",
    "src/zihin/socket_bridge.py",
    "src/zihin/container_entry.py",
    "Containerfile",
    "scripts/record_run.py",
    "config/",
)


@dataclass(frozen=True)
class DevamDenetimi:
    """Whether an interrupted run can be resumed."""

    reddet: tuple[str, ...]
    uyar: tuple[str, ...]
    # How many run ids were actually compared. An empty comparison is not an
    # agreement, and a caller that needs the difference between "compared and
    # agreed" and "found nothing to compare" cannot get it from `passed` alone.
    karsilastirilan: int = 0

    @property
    def passed(self) -> bool:
        return not self.reddet


def defines_measurement(path: str) -> bool:
    """Does this path define the measurement (K-76).

    It sits in one place because two gates use the same distinction: the
    between-commits difference check and the working-tree gate. Two separate
    membership rules would mean the two gates drifting apart in silence.
    """
    return any(path == p or path.startswith(p) for p in MEASUREMENT_DEFINING_PATHS)


def changed_files(a: str, b: str) -> tuple[list[str], list[str]]:
    """The files that changed between two commits, and their measurement-defining subset."""
    try:
        every_row = subprocess.run(
            ["git", "diff", "--name-only", a, b], capture_output=True, text=True, check=True
        ).stdout.split()
    except Exception as error:
        return (
            [f"git could not be read: {str(error)[:80]}"],
            [f"git could not be read: {str(error)[:80]}"],
        )
    kritik = [y for y in every_row if defines_measurement(y)]
    return every_row, kritik


def os_environment_text() -> str:
    """The environment string the manifest carries.

    Beyond the platform and the Python version it names **where AppWorld was
    installed from**. That is not decoration. On 2026-08-20 the upstream
    repository's Git LFS budget ran out, its bundle objects stopped being served,
    and a fresh install had to come from the mirror in `vendor/appworld/`. The
    artefact is the same one — each bundle's sha256 is its LFS object id and both
    match — but "the same" is a claim, and a claim nobody recorded cannot be
    checked afterwards. A silent fallback hides the source of the measurement.

    When `results/appworld-kaynak.json` is absent the string is what it always
    was. Absence means the bootstrap did not run here, not that the source is
    upstream: this function does not invent an answer it was not given.
    """
    base = f"{platform.system()} {platform.release()} / {platform.python_version()}"
    report = Path(__file__).resolve().parents[2] / "results/appworld-kaynak.json"
    if not report.exists():
        return base
    try:
        written = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return base
    source = written.get("source")
    if source in (None, "upstream"):
        return f"{base} / appworld: upstream"
    commit = (written.get("commit") or "bilinmiyor")[:9]
    taken = written.get("mirror_taken") or "bilinmiyor"
    return f"{base} / appworld: {source} {commit} ({taken})"


def resume_check(
    connection: sqlite3.Connection,
    expected: dict[str, dict[str, Any]],
    current_commit: str | None = None,
    require_episode: bool = True,
) -> DevamDenetimi:
    """Whether the written episodes' condition matches the one about to run.

    `beklenen`: run id -> the field values that run will use **now**. Only the
    fields supplied are compared; a field left out passes in silence, because the
    caller need not know every one of them.

    A condition-field mismatch is refused. A difference in `code_commit` or
    `model_server_env` is not: the first escalates to a refusal when a
    measurement-defining path changed, the second lists which keys differ.

    `require_episode`: by default a manifest is compared only when an episode was
    written under it, which is what the episode-level resume wants. The manifest
    write wants the opposite case and it is the one that bites: a session killed
    between the manifest and the episode leaves a manifest with no episode, and an
    inner join would compare nothing there and report agreement (K-155).
    """
    reddet: list[str] = []
    uyar: list[str] = []
    if not expected:
        return DevamDenetimi((), (), 0)

    yer = ", ".join("?" for _ in expected)
    birlestirme = "JOIN" if require_episode else "LEFT JOIN"
    sorgu = (
        "SELECT m.*, e.condition, e.split, e.step_ceiling "
        f"FROM run_manifests m {birlestirme} episodes e USING(run_id) "
        f"WHERE m.run_id IN ({yer})"
    )
    karsilastirilan = 0
    for row in connection.execute(sorgu, tuple(expected)):
        karsilastirilan += 1
        run_id = row["run_id"]
        istenen = expected[run_id]
        for field in MANIFEST_CONDITION_FIELDS + EPISODE_CONDITION_FIELDS:
            if field not in istenen:
                continue
            if row[field] != istenen[field]:
                reddet.append(f"{run_id}: {field} written={row[field]!r} now={istenen[field]!r}")

        if current_commit and row["code_commit"] not in (current_commit, "bilinmiyor"):
            every_row, kritik = changed_files(row["code_commit"], current_commit)
            if kritik:
                reddet.append(
                    f"{run_id}: commit {row['code_commit'][:7]} -> {current_commit[:7]}, "
                    f"measurement-defining paths changed: {kritik}"
                )
            else:
                uyar.append(
                    f"{run_id}: commit {row['code_commit'][:7]} -> {current_commit[:7]}, "
                    f"{len(every_row)} files changed, no measurement-defining path among them"
                )

        if "model_server_env" in istenen:
            distinct = _server_environment_diff(
                row["model_server_env"], istenen["model_server_env"]
            )
            if distinct:
                uyar.append(f"{run_id}: key(s) differing in the server environment: {distinct}")

    return DevamDenetimi(tuple(reddet), tuple(uyar), karsilastirilan)


def _server_environment_diff(yazili: str | None, simdiki: Any) -> list[str]:
    try:
        a = json.loads(yazili) if isinstance(yazili, str) else (yazili or {})
        b = json.loads(simdiki) if isinstance(simdiki, str) else (simdiki or {})
    except (TypeError, ValueError):
        return ["could not be read"]
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def uncommitted_paths() -> list[str]:
    """The paths inside `git status --porcelain`.

    A rename line carries two paths (`R  old -> new`) and both are counted:
    a measurement-defining file leaving the list matters as much as one entering
    it. Paths containing spaces are quoted by git, and the quotes are stripped
    here.
    """
    output = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout
    paths: list[str] = []
    for row in output.splitlines():
        if not row.strip():
            continue
        remainder = row[3:] if len(row) > 3 else ""
        for part in remainder.split(" -> "):
            path = part.strip().strip('"')
            if path:
                paths.append(path)
    return paths


def working_tree() -> str:
    """Whether measurement-defining paths carry uncommitted changes.

    Returns `clean`, `dirty` or `unknown`.

    A measurement run is not started with uncommitted changes. The reason is the
    manifest's structure: `code_commit` records HEAD, not the working tree. An
    episode run on a dirty tree appears under the same commit as a clean run and
    cannot be told apart. An edit made mid-sweep falls in the same class — half
    the episodes run on different code and nothing about it reaches the data.

    **The gate looks at `MEASUREMENT_DEFINING_PATHS`, not at the whole tree
    (K-76).** A gate over the whole tree also blocked touching a document, a
    report or an unrelated script while a run was in progress; that distinction
    is the reason the list exists in the first place. A change outside the list
    is **not written to the manifest either**: written, every run would look
    "dirty" and the signal would drown in noise, and a noisy signal is worse than
    none because nobody looks at it.

    `unknown` does not count as clean: if git cannot be read, the tree cannot be
    verified clean, and what cannot be verified is not assumed.
    """
    try:
        paths = uncommitted_paths()
    except Exception:
        return "unknown"
    return "dirty" if any(defines_measurement(p) for p in paths) else "clean"


def storage_durability(connection: sqlite3.Connection) -> dict[str, Any]:
    """The record store's durability against a hard power cut, read off the
    connection itself.

    With synchronous OFF even a committed transaction can be lost. In an
    environment where power cuts are frequent that means the episode record
    thinning out in silence, and the thinning is biased by length: a cut is more
    likely to land on a long episode. The value is a measurement, not a claim;
    the CHECK in the schema refuses a non-durable setting.
    """
    return {
        "journal_mode": str(connection.execute("PRAGMA journal_mode").fetchone()[0]),
        "synchronous_setting": int(connection.execute("PRAGMA synchronous").fetchone()[0]),
    }


def _add_missing_columns(connection: sqlite3.Connection) -> None:
    for table, name, tanim in MIGRATED_COLUMNS:
        mevcut = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if name not in mevcut:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} {tanim}")
            connection.commit()


def _insert(connection: sqlite3.Connection, table: str, row: dict[str, Any]) -> int:
    columns = ", ".join(row)
    yer_tutucular = ", ".join("?" for _ in row)
    imlec = connection.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({yer_tutucular})",
        tuple(row.values()),
    )
    return int(imlec.lastrowid or 0)


# The fields that cannot be left empty in the manifest (K-46). Every value read
# across the WSL/Windows boundary carries the risk of arriving silently as None,
# and that happened once: the KV cache type, flash attention and keep_alive were
# written to the manifest as None. A silent gap, noticed after the run has
# finished, makes the run worthless.
#
# This list is the caller's contract. boot_id, journal_mode and
# synchronous_setting are not here because the record layer fills them itself and
# raises if they cannot be read; wall_clock_utc is not here because SQLite decides
# its value. The validity of all three lives in the schema's CHECKs; their
# emptiness is not checked here.
REQUIRED_MANIFEST_FIELDS = (
    "run_id",
    "model_tag",
    "temperature",
    "base_seed",
    "no_progress_limit",
    "max_output_tokens",
    "model_server_env",
    "appworld_commit",
    "code_commit",
    "instruction_file_digest",
    "os_environment",
    # The shield's mode is mandatory. Its default is 'off' and that default is
    # correct only for old rows; a new manifest has to state the mode, otherwise
    # the regime under which the `shield_violations` rows were produced goes
    # unrecorded.
    "shield_mode",
    # The scaffold's character ceiling. This is the number that decides the
    # effective context, and leaving it empty means "not recorded" — exactly the
    # gap S-47 uncovered. Running without a ceiling is a valid choice and in that
    # case the value is -1.
    "max_prompt_characters",
)

# The ones mandatory only under local serving. A hosted model has no counterpart
# for them: the effective context window cannot be verified, and the KV cache type
# and keep_alive are not our settings on the server side. The contract is not
# skipped but narrowed by mode; its fail-closed property stays as it is in local
# mode (K-46).
LOCAL_ONLY_MANIFEST_FIELDS = (
    "num_ctx_requested",
    "num_ctx_effective",
    "kv_cache_type",
    "keep_alive",
)

SUNUM_KIPLERI = ("local", "hosted")


def insert_run_manifest(
    connection: sqlite3.Connection, *, allow_dirty_tree: bool = False, **fields: Any
) -> str:
    """Writes the run manifest.

    If one of the mandatory fields is empty it does not write, it raises (K-46).
    These fields cannot be collected after the fact if they were not collected
    during the run, so an incomplete manifest makes the run worthless.

    `allow_dirty_tree` is an explicit override. Setup exploration is not blocked,
    it is marked: given the flag the run passes and the manifest says the tree was
    dirty.
    """
    kip = fields.setdefault("serving_mode", "local")
    if kip not in SUNUM_KIPLERI:
        raise RecordError(f"serving_mode {kip!r} is invalid; allowed: {list(SUNUM_KIPLERI)}")

    # The wall clock cannot come from outside: SQLite's CURRENT_TIMESTAMP default
    # decides its value. The column never enters the INSERT, so the default
    # fires; the refusal here stops someone later passing an in-process time "for
    # convenience". In-process time may be frozen by freezegun and the freeze
    # goes unnoticed.
    if "wall_clock_utc" in fields:
        raise RecordError(
            "wall_clock_utc cannot be supplied from outside; the value comes from "
            "SQLite's CURRENT_TIMESTAMP default."
        )

    # The boot id and the store's durability are not left to the caller. Both are
    # facts about the machine at write time, not declarations by the caller; and
    # writing a manifest field at the wrong call site has happened once in this
    # repository (S-28).
    fields["boot_id"] = boot_id()
    fields.update(storage_durability(connection))

    agac = working_tree()
    if agac != "clean" and not allow_dirty_tree:
        # `unknown` means git cannot be read, so the list cannot be read either;
        # the error message goes out with an empty list rather than a second
        # exception.
        try:
            dirty = [p for p in uncommitted_paths() if defines_measurement(p)]
        except Exception:
            dirty = []
        raise RecordError(
            f"working tree {agac}: measurement-defining paths carry uncommitted "
            f"changes {dirty}. A measurement run is not started this way: code_commit "
            "records HEAD, not the working tree, so the difference cannot be read off "
            "the manifest. Changes outside the list do not concern this gate at all "
            "(K-76). To run deliberately, pass the override flag and it is written to "
            "the manifest."
        )
    fields["working_tree"] = agac

    expected = REQUIRED_MANIFEST_FIELDS
    if kip == "local":
        expected = expected + LOCAL_ONLY_MANIFEST_FIELDS

    blank = [
        name
        for name in expected
        if fields.get(name) is None or fields.get(name) == "" or fields.get(name) == {}
    ]
    if blank:
        raise RecordError(
            f"manifest field(s) that cannot be left empty: {blank}. "
            "The run cannot start with this manifest."
        )
    # The Python counterpart of the schema's CHECK. In a migrated file such as
    # series 2 the CHECK is not in force (ALTER TABLE carries no constraints), and
    # that is exactly where runs happen. If the configuration a shielded run used
    # is not recorded, its `shield_violations` rows become incomparable.
    shield_mode = fields.get("shield_mode")
    if shield_mode not in ("shadow", "enforce", "off"):
        raise RecordError(f"shield_mode {shield_mode!r} is invalid; allowed: shadow, enforce, off.")
    if shield_mode != "off" and not fields.get("shield_config_digest"):
        raise RecordError(
            "the shield is running but shield_config_digest is empty. When the write "
            "set or the allowed-app inferrer changes, the violations produced become "
            "incomparable, so a run cannot start without the configuration it ran "
            "under being written to the manifest."
        )

    if kip == "local" and fields.get("context_verified") != 1:
        raise RecordError(
            "context_verified is not 1. A run cannot start before the effective "
            "context window has been verified (K-37)."
        )
    if kip == "hosted" and fields.get("context_verified") == 1:
        raise RecordError(
            "context_verified cannot be 1 in hosted mode. The effective context "
            "window cannot be verified on a hosted model; writing 1 would present an "
            "unverified value as verified."
        )
    if "model_server_env" in fields and isinstance(fields["model_server_env"], dict):
        missing = [
            name
            for name, value in fields["model_server_env"].items()
            if name.startswith("OLLAMA_") and value is None
        ]
        if missing:
            raise RecordError(f"setting(s) unreadable in the server environment: {missing}")
        fields["model_server_env"] = json.dumps(
            fields["model_server_env"], ensure_ascii=False, sort_keys=True
        )
    if _manifest_already_written(connection, fields):
        return str(fields["run_id"])
    _insert(connection, "run_manifests", fields)
    return str(fields["run_id"])


def _manifest_already_written(connection: sqlite3.Connection, fields: dict[str, Any]) -> bool:
    """Is this run id already carrying a manifest, and does it say the same thing?

    **Why this exists.** The resume was built at the episode level and stopped
    there. `completed_runs` counts an episode as done only when it has a step and
    a verdict, so a session killed part-way leaves a task in the work list and the
    runner starts it again - and the manifest for that run id is already in the
    file. The insert then failed on `UNIQUE constraint failed: run_manifests.run_id`
    and the resume, which is the whole point of a Colab run, could not proceed.
    Two things had to agree and only one of them had been made resume-aware
    (K-155).

    **The comparison is not written again here.** `resume_check` is the one place
    that knows which fields define a condition and how a `code_commit` difference
    escalates; a second copy of that knowledge is the defect this module keeps
    recording. This function only decides which run id to ask about and what to do
    with the answer.

    Returns True when the written manifest matches and the caller should not
    insert. Raises when it differs: continuing would put two conditions under one
    run id, and nothing downstream could tell them apart.
    """
    run_id = fields.get("run_id")
    if not run_id:
        return False
    existing = connection.execute(
        "SELECT 1 FROM run_manifests WHERE run_id = ?", (run_id,)
    ).fetchone()
    if existing is None:
        return False

    comparable = {
        name: fields[name]
        for name in MANIFEST_CONDITION_FIELDS + EPISODE_CONDITION_FIELDS
        if name in fields
    }
    check = resume_check(
        connection,
        {str(run_id): comparable},
        current_commit=fields.get("code_commit"),
        require_episode=False,
    )
    if not check.karsilastirilan:
        raise RecordError(
            f"a manifest for {run_id} is already written but it could not be read back "
            "for comparison. Nothing is compared, and an empty comparison is not an "
            "agreement."
        )
    if not check.passed:
        raise RecordError(
            f"a manifest for {run_id} is already written and its conditions are not the "
            "ones about to run:\n  "
            + "\n  ".join(check.reddet)
            + "\nThe run is not resumed onto a different condition. Use a new run id, "
            "or run the set that is already written."
        )
    for line in check.uyar:
        print(f"manifest resume: {line}")
    return True


class AlreadyRecorded(RecordError):
    """This episode identity is already in the record, under the same conditions.

    An exception rather than a returned flag, because the caller must not go on
    to write the steps and the verdict: those key off `episode_id` and the rows
    for this episode are already there. A flag can be ignored; this cannot.
    """

    def __init__(self, episode_id: int, run_id: str) -> None:
        super().__init__(
            f"{run_id} is already recorded as episode {episode_id} under the same "
            "conditions; nothing was written"
        )
        self.episode_id = episode_id
        self.run_id = run_id


def insert_episode(connection: sqlite3.Connection, **fields: Any) -> int:
    """Writes one episode row, or says it is already there.

    **Why this is not a plain insert.** The episode identity is
    `(run_id, task_id, condition, seed)` and a restart re-attempts it: the
    accumulation run was interrupted three times and the third interruption
    surfaced here, as `UNIQUE constraint failed: episodes.run_id, task_id,
    condition, seed`. The manifest learned to compare in K-155 and the episode
    row is the next write in the same transaction, so it learned the same thing
    the hard way one restart later (K-157).

    Same rule as the manifest: identical conditions mean the write has already
    happened and `AlreadyRecorded` is raised; different conditions are refused
    with the difference named, because two conditions under one identity is a
    set nothing downstream can separate.
    """
    run_id = fields.get("run_id")
    existing = None
    if run_id:
        existing = connection.execute(
            "SELECT episode_id FROM episodes WHERE run_id = ? AND task_id = ? "
            "AND condition IS ? AND seed IS ?",
            (run_id, fields.get("task_id"), fields.get("condition"), fields.get("seed")),
        ).fetchone()
    if existing is None:
        return _insert(connection, "episodes", fields)

    episode_id = existing[0]
    comparable = {name: fields[name] for name in EPISODE_CONDITION_FIELDS if name in fields}
    if comparable:
        row = connection.execute(
            "SELECT * FROM episodes WHERE episode_id = ?", (episode_id,)
        ).fetchone()
        differing = [
            f"{name}: written={row[name]!r} now={value!r}"
            for name, value in comparable.items()
            if row[name] != value
        ]
        if differing:
            raise RecordError(
                f"{run_id} is already recorded as episode {episode_id} and its conditions "
                "are not the ones about to be written:\n  "
                + "\n  ".join(differing)
                + "\nOne identity cannot carry two conditions. Use a new run id."
            )
    raise AlreadyRecorded(episode_id, str(run_id))


def insert_step(connection: sqlite3.Connection, **fields: Any) -> int:
    category = fields.get("outcome_category")
    if category is not None and category not in STEP_OUTCOMES:
        raise RecordError(f"unrecognised step category: {category!r}")
    # Two columns carry the state and they cannot both be filled: one is a signed
    # row delta, the other is which model changed (K-93). Written together, a
    # step's state would be recorded in two different senses and which one to read
    # would be left to the reader. Because the CHECK cannot be migrated (S-29) the
    # rule is enforced here.
    if fields.get("state_change") is not None and fields.get("state_hashes") is not None:
        raise RecordError(
            "state_change and state_hashes cannot be written together on one step: "
            "one is a row delta, the other a model digest, and the two carry separate "
            "meanings"
        )
    return _insert(connection, "steps", fields)


def insert_action(connection: sqlite3.Connection, **fields: Any) -> int:
    for name in ("raw_parameters", "normalized_parameters"):
        if isinstance(fields.get(name), dict):
            fields[name] = json.dumps(fields[name], ensure_ascii=False, sort_keys=True)
    return _insert(connection, "actions", fields)


def insert_observation(
    connection: sqlite3.Connection,
    *,
    step_id: int,
    full_text: str,
    limits: RecordingLimits,
    full_output_path: str | None = None,
    token_count: int | None = None,
) -> int:
    """Truncates the observation and writes it.

    Truncation is applied as the text enters the context, not at the moment of
    overflow. The full text stays on disk and the database carries only a
    reference to it (K-17).
    """
    ham = full_text.encode("utf-8")
    kesildi = len(ham) > limits.observation_max_bytes
    kesilmis = ham[: limits.observation_max_bytes].decode("utf-8", errors="ignore")
    return _insert(
        connection,
        "observations",
        {
            "step_id": step_id,
            "full_output_path": full_output_path,
            "truncated_text": kesilmis,
            "truncated_bytes": len(kesilmis.encode("utf-8")),
            "full_bytes": len(ham),
            "token_count": token_count,
            "was_truncated": int(kesildi),
        },
    )


def insert_verifier_result(connection: sqlite3.Connection, **fields: Any) -> int:
    return _insert(connection, "verifier_results", fields)


def insert_shield_violation(connection: sqlite3.Connection, **fields: Any) -> int:
    if isinstance(fields.get("raw_parameters"), dict):
        fields["raw_parameters"] = json.dumps(
            fields["raw_parameters"], ensure_ascii=False, sort_keys=True
        )
    return _insert(connection, "shield_violations", fields)


JSON_SKILL_FIELDS = (
    "effect_suffix",
    "body",
    "supporting_tasks",
    "supporting_episodes",
    "bound_arguments",
    "free_parameters",
    "constants",
    "postcondition",
)


JSON_LEDGER_FIELDS = ("effect_suffixes", "new_effect_suffixes")


def insert_ledger_row(connection: sqlite3.Connection, **fields: Any) -> int:
    """Writes one block boundary of an accumulation run.

    **Why it is in the record and not in a file.** The ledger was a JSON under
    `results/`, and on Colab that directory is inside a checkout the notebook
    re-clones every session, while the record is symlinked to Drive. The run's
    state was split across one durable store and one ephemeral one, and the half
    the stopping rule reads was the ephemeral one (K-162).

    Append-only, and the identity is `(prefix, block)`: a restart that re-closes
    a block it already closed is a collision, not a second row, and it is
    reported rather than silently doubling the ledger.
    """
    for name in JSON_LEDGER_FIELDS:
        value = fields.get(name)
        if isinstance(value, dict | list | tuple | set):
            fields[name] = json.dumps(sorted(value), ensure_ascii=False)
    return _insert(connection, "run_ledger", fields)


def insert_experiment_slice(connection: sqlite3.Connection, **fields: Any) -> int:
    """Writes one task's membership of a slice, when the slice opens (K-182)."""
    return _insert(connection, "experiment_slices", fields)


def experiment_slice_of(connection: sqlite3.Connection, task_id: str) -> int | None:
    """The slice a task was opened in, or None if no slice holds it."""
    row = connection.execute(
        "SELECT slice FROM experiment_slices WHERE task_id = ?", (task_id,)
    ).fetchone()
    return None if row is None else int(row[0])


def insert_experiment_episode(
    connection: sqlite3.Connection, *, task_id: str, **fields: Any
) -> int:
    """Writes what an experiment episode belongs to, in the episode's transaction.

    The slice is checked against the record rather than trusted: an episode whose
    task the slice does not hold would put it in a slice nobody opened, and the
    per-slice analysis would read a task that was never part of it.
    """
    opened = experiment_slice_of(connection, task_id)
    if opened is None or opened != fields.get("slice"):
        raise RecordError(
            f"{task_id} is in slice {opened}, not in slice {fields.get('slice')}: an "
            "experiment episode belongs to the slice that opened its task"
        )
    return _insert(connection, "experiment_episodes", fields)


def ledger_rows(connection: sqlite3.Connection, prefix: str) -> list[dict[str, Any]]:
    """Every block boundary of one run, in order, with the JSON fields read back."""
    rows = connection.execute(
        "SELECT * FROM run_ledger WHERE prefix = ? ORDER BY block", (prefix,)
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        for name in JSON_LEDGER_FIELDS:
            item[name] = json.loads(item[name]) if item.get(name) else []
        out.append(item)
    return out


def insert_skill(connection: sqlite3.Connection, **fields: Any) -> str:
    """Writes one row into the skill library.

    JSON fields are serialised with `sort_keys=True`: the library is a derived
    projection and the same record has to give the same rows. A serialisation
    that depended on dict order would change the digest when nothing had changed.

    `postcondition` is special: None means "could not attribute", `{}` means
    "attributed, nothing changed", and the two are different (K-79). None leaves
    the column NULL; `{}` writes `"{}"`.
    """
    for name in JSON_SKILL_FIELDS:
        value = fields.get(name)
        if value is None:
            continue
        if isinstance(value, dict | list | tuple | set):
            if isinstance(value, set):
                value = sorted(value)
            fields[name] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    _insert(connection, "skills", fields)
    return str(fields["skill_id"])


JSON_FAILURE_FIELDS = ("argument_shape", "condition", "supporting_tasks")


def insert_failure_pattern(connection: sqlite3.Connection, **fields: Any) -> str:
    """Writes one row into the failure index.

    The same serialisation rule as `skills`: dict keys sorted, because the index
    is a derived projection too and the same record must give the same rows.
    """
    for name in JSON_FAILURE_FIELDS:
        value = fields.get(name)
        if isinstance(value, dict | list | tuple | set):
            if isinstance(value, set):
                value = sorted(value)
            fields[name] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    _insert(connection, "failure_patterns", fields)
    return str(fields["pattern_id"])


def replace_index(connection: sqlite3.Connection, index_id: str) -> int:
    """Deletes one failure index's rows. The counterpart of `replace_library`."""
    cursor = connection.execute("DELETE FROM failure_patterns WHERE index_id = ?", (index_id,))
    return cursor.rowcount


def replace_library(connection: sqlite3.Connection, library_id: str) -> int:
    """Deletes one library's rows so the compiler can regenerate it.

    `skills` sits outside the append-only rule, and deliberately so: the library
    is a derived projection and has to be deletable and rebuildable from the
    record (`03-architecture.tr.md`). A library that could not be deleted would turn
    into a second source of truth.

    It returns the number of rows deleted, because the difference between
    "regenerated" and "generated for the first time" is something the caller has
    to see.
    """
    cursor = connection.execute("DELETE FROM skills WHERE library_id = ?", (library_id,))
    return cursor.rowcount


def latest_library_and_index(connection: sqlite3.Connection) -> tuple[str, str]:
    """The ids of the library and index the retriever will read.

    The criterion is row count: the build with the most rows. Not the date,
    because projections can be deleted and regenerated, and a regeneration can
    bring an old id back with a new timestamp.

    It sits in one place because the retrieval measurement, the card measurement
    and the pilot dataset all have to pick the same pair. Three separate queries
    would mean three results measuring three different libraries, and the
    difference would stay silent.
    """
    library = connection.execute(
        "SELECT library_id FROM skills GROUP BY library_id ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()
    index = connection.execute(
        "SELECT index_id FROM failure_patterns GROUP BY index_id ORDER BY COUNT(*) DESC LIMIT 1"
    ).fetchone()
    if library is None or index is None:
        where = database_path(connection)
        raise RecordError(
            f"{where} carries no skill library or no failure index. The library "
            f"lives in the series it was mined from ({LIBRARY_SERIES}), which is "
            f"not the series runs are written to ({ACTIVE_SERIES}); open the "
            "first with `open_library()`. If neither carries one, run "
            "build_skill_library.py and build_failure_index.py."
        )
    return library[0], index[0]


def database_path(connection: sqlite3.Connection) -> str:
    """The file behind a connection, so a refusal can name what it looked in."""
    for _, name, file in connection.execute("PRAGMA database_list"):
        if name == "main":
            return file or "an in-memory database"
    return "an unnamed database"


def open_library(path: str | None = None) -> tuple[sqlite3.Connection, str, str]:
    """A read-only connection to the library's series, with its two ids.

    Every caller that needs cards goes through this rather than through whatever
    connection it happens to be writing episodes to. The two are separate
    questions and the answers stopped agreeing when series 3 opened.
    """
    source = path or LIBRARY_SERIES
    if not Path(source).exists():
        raise RecordError(
            f"{source} does not exist, and it is where the skill library lives. "
            "It is named in `zihin.records.LIBRARY_SERIES`; if the library moved, "
            "that line moves with it."
        )
    connection = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    library_id, index_id = latest_library_and_index(connection)
    return connection, library_id, index_id


def read_episode_timeline(connection: sqlite3.Connection, episode_id: int) -> list[sqlite3.Row]:
    """Reads the whole episode in one query, in order."""
    return list(
        connection.execute(
            "SELECT * FROM episode_timeline WHERE episode_id = ? ORDER BY step_index, action_index",
            (episode_id,),
        )
    )
