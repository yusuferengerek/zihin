"""The manifest contract: an empty field means the run does not start.

K-46. The rule was born from a fault: the KV cache type, flash attention and
keep_alive were written to the manifest as `None`, because the settings live in
the environment of the server process on Windows and the read was done from
inside WSL. The run looked green.

Every value read across the WSL/Windows boundary carries the same risk.
"""

from __future__ import annotations

import sqlite3

import pytest

from zihin.records import (
    LOCAL_ONLY_MANIFEST_FIELDS,
    REQUIRED_MANIFEST_FIELDS,
    RecordError,
    boot_id,
    defines_measurement,
    insert_run_manifest,
    open_database,
    working_tree,
)


def _barindirilan(**degisiklik):
    """A hosted model's manifest: no local-specific fields."""
    fields = _manifest(
        run_id="run-hosted",
        serving_mode="hosted",
        num_ctx_requested=None,
        num_ctx_effective=None,
        context_verified=0,
        kv_cache_type=None,
        flash_attention=None,
        keep_alive=None,
        model_tag="openrouter/deepseek/deepseek-v4-flash-0731",
        model_server_env={"provider": "openrouter", "base_url": "https://openrouter.ai/api/v1"},
    )
    fields.update(degisiklik)
    return fields


def _manifest(**degisiklik):
    fields = {
        "run_id": "run-1",
        "created_at": "uptime:1.0",
        "model_tag": "qwen2.5-coder:1.5b-instruct-q4_K_M",
        "num_ctx_requested": 32768,
        "num_ctx_effective": 32768,
        "context_verified": 1,
        "kv_cache_type": "q8_0",
        "flash_attention": 1,
        "temperature": 0.2,
        "base_seed": 123,
        "keep_alive": "30m0s",
        "no_progress_limit": 4,
        "max_output_tokens": 400,
        "max_prompt_characters": 50000,
        "model_server_env": {
            "OLLAMA_CONTEXT_LENGTH": "32768",
            "OLLAMA_KV_CACHE_TYPE": "q8_0",
        },
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": "deadbeef",
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux 6.6 / 3.11.15",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }
    fields.update(degisiklik)
    return fields


@pytest.fixture
def connection(tmp_path):
    with open_database(tmp_path / "record.sqlite") as db:
        yield db


# The base fields of a raw INSERT that bypasses the Python layer. boot_id and the
# store settings are normally filled by the record layer, so they are supplied by
# hand here: without them the test hits NOT NULL and ends up checking that rather
# than the constraint it claims to check.
_RAW_BASE = {
    "created_at": "'uptime:1'",
    "boot_id": "'167c6e15-f3d3-4edf-84aa-56448c222377'",
    "model_tag": "'m'",
    "temperature": "0.2",
    "base_seed": "1",
    "no_progress_limit": "4",
    "max_output_tokens": "400",
    "max_prompt_characters": "50000",
    "model_server_env": "'{}'",
    "appworld_version": "'v'",
    "appworld_commit": "'c'",
    "code_commit": "'d'",
    "instruction_file_digest": "'e'",
    "os_environment": "'f'",
    "journal_mode": "'delete'",
    "synchronous_setting": "2",
    "working_tree": "'clean'",
}


def _ham_insert(connection, run_id, **degisiklik):
    fields = {"run_id": f"'{run_id}'", **_RAW_BASE, **degisiklik}
    columns = ", ".join(fields)
    values = ", ".join(fields.values())
    connection.execute(f"INSERT INTO run_manifests ({columns}) VALUES ({values})")


def test_valid_manifest_is_accepted(connection):
    assert insert_run_manifest(connection, **_manifest()) == "run-1"


def test_serving_mode_defaults_to_local(connection):
    fields = _manifest()
    fields.pop("serving_mode", None)
    insert_run_manifest(connection, **fields)
    kip = connection.execute("SELECT serving_mode FROM run_manifests").fetchone()["serving_mode"]
    assert kip == "local"


def test_unknown_serving_mode_is_rejected(connection):
    with pytest.raises(RecordError, match="serving_mode"):
        insert_run_manifest(connection, **_manifest(serving_mode="uzak"))


@pytest.mark.parametrize("field", LOCAL_ONLY_MANIFEST_FIELDS)
def test_local_specific_fields_are_required_in_local_mode(connection, field):
    with pytest.raises(RecordError, match="cannot be left empty"):
        insert_run_manifest(connection, **_manifest(**{field: None}))


def test_hosted_manifest_may_omit_local_specific_fields(connection):
    """The contract is not skipped but narrowed by mode.

    On a hosted model the effective context window cannot be verified, and the KV
    cache type and keep_alive are not our settings. They stay mandatory in local
    mode.
    """
    assert insert_run_manifest(connection, **_barindirilan()) == "run-hosted"


@pytest.mark.parametrize("field", REQUIRED_MANIFEST_FIELDS)
def test_shared_fields_stay_required_in_hosted_mode(connection, field):
    with pytest.raises(RecordError, match="cannot be left empty"):
        insert_run_manifest(connection, **_barindirilan(**{field: None}))


def test_hosted_mode_cannot_claim_verified_context(connection):
    """Presenting something unverifiable as verified is forbidden."""
    with pytest.raises(RecordError, match="context_verified"):
        insert_run_manifest(connection, **_barindirilan(context_verified=1))


def test_database_enforces_local_contract_without_python(connection):
    """The contract is kept by machine, not by convention.

    Even with the Python layer bypassed and a direct INSERT, the schema's CHECK
    refuses a missing field in local mode.
    """
    with pytest.raises(sqlite3.IntegrityError):
        _ham_insert(connection, "x", serving_mode="'local'", context_verified="1")


def test_database_rejects_unknown_serving_mode(connection):
    with pytest.raises(sqlite3.IntegrityError):
        _ham_insert(connection, "y", serving_mode="'uzak'")


def test_missing_column_is_added_when_an_existing_database_is_opened(tmp_path):
    """The schema is applied only to a fresh file; a column added later is absent
    from an old one.

    K-60's `max_output_tokens` field arrived by this path. Without the column
    being added, the recorder cannot write to an old database and the fault
    surfaces mid-run.
    """
    path = tmp_path / "old.sqlite"
    with open_database(path) as db:
        db.execute("ALTER TABLE run_manifests DROP COLUMN max_output_tokens")
        db.commit()
        assert "max_output_tokens" not in {
            s[1] for s in db.execute("PRAGMA table_info(run_manifests)")
        }

    with open_database(path) as db:
        assert "max_output_tokens" in {s[1] for s in db.execute("PRAGMA table_info(run_manifests)")}
        assert insert_run_manifest(db, **_manifest()) == "run-1"


@pytest.mark.parametrize("field", REQUIRED_MANIFEST_FIELDS)
def test_every_required_field_is_enforced(connection, field):
    with pytest.raises(RecordError, match="cannot be left empty"):
        insert_run_manifest(connection, **_manifest(**{field: None}))


def test_empty_string_counts_as_empty(connection):
    with pytest.raises(RecordError, match="cannot be left empty"):
        insert_run_manifest(connection, **_manifest(kv_cache_type=""))


def test_unverified_context_window_blocks_the_run(connection):
    """K-37's first condition is enforced at manifest level too."""
    with pytest.raises(RecordError, match="context_verified"):
        insert_run_manifest(connection, **_manifest(context_verified=0))


def test_unreadable_server_setting_blocks_the_run(connection):
    """This was the original fault: a server setting could not be read and stayed None."""
    with pytest.raises(RecordError, match="unreadable in the server environment"):
        insert_run_manifest(
            connection,
            **_manifest(
                model_server_env={
                    "OLLAMA_CONTEXT_LENGTH": "32768",
                    "OLLAMA_KV_CACHE_TYPE": None,
                }
            ),
        )


# ---------------------------------------------------------------------------
# Power-cut durability
# ---------------------------------------------------------------------------
# created_at is based on /proc/uptime and resets on restart. In an environment
# where power cuts are frequent, the start of the episode following a cut comes
# out smaller than the one before it; boot_id gives back the join point and the
# wall clock gives back the ordering across boots.


def test_boot_id_is_filled_by_the_record_layer(connection):
    """The caller does not supply it; the record layer reads it.

    Leaving the field to the caller would make S-28's fault possible again: while
    a manifest field was being added it was written at the wrong call site and
    thirty episodes died.
    """
    insert_run_manifest(connection, **_manifest())
    yazilan = connection.execute("SELECT boot_id FROM run_manifests").fetchone()["boot_id"]
    assert yazilan == boot_id()
    assert yazilan


def test_two_manifests_in_one_boot_share_the_boot_id(connection):
    insert_run_manifest(connection, **_manifest(run_id="run-1"))
    insert_run_manifest(connection, **_manifest(run_id="run-2"))
    kimlikler = {s["boot_id"] for s in connection.execute("SELECT boot_id FROM run_manifests")}
    assert len(kimlikler) == 1, "manifests written within one boot carry different boot ids"


def test_wall_clock_comes_from_sqlite(connection):
    """The database decides the value, not the process.

    AppWorld freezes the process-wide clock with freezegun, so a time computed in
    Python may be frozen without anyone noticing.
    """
    insert_run_manifest(connection, **_manifest())
    saat = connection.execute("SELECT wall_clock_utc FROM run_manifests").fetchone()[
        "wall_clock_utc"
    ]
    expected = connection.execute("SELECT CURRENT_TIMESTAMP AS t").fetchone()["t"]
    assert saat, "the wall clock is empty"
    # Same day and hour; there may be a difference in seconds from the moment the
    # test runs.
    assert saat[:13] == expected[:13]


def test_wall_clock_cannot_be_supplied_from_outside(connection):
    with pytest.raises(RecordError, match="wall_clock_utc"):
        insert_run_manifest(connection, **_manifest(wall_clock_utc="2020-01-01 00:00:00"))


def test_storage_durability_is_recorded(connection):
    insert_run_manifest(connection, **_manifest())
    row = connection.execute(
        "SELECT journal_mode, synchronous_setting FROM run_manifests"
    ).fetchone()
    assert row["journal_mode"] not in ("off", "memory")
    assert row["synchronous_setting"] in (1, 2, 3)


def test_a_database_with_synchronous_off_cannot_be_written_to(connection):
    """With synchronous OFF even a committed transaction can be lost in a hard
    power cut.

    The thinning of the record is biased by length: a cut is more likely to land
    on a long episode. That is why a non-durable store accepts no manifest.
    """
    connection.execute("PRAGMA synchronous = OFF")
    with pytest.raises(sqlite3.IntegrityError):
        insert_run_manifest(connection, **_manifest())


def test_a_memory_journal_cannot_be_written_to(connection):
    connection.execute("PRAGMA journal_mode = MEMORY")
    with pytest.raises(sqlite3.IntegrityError):
        insert_run_manifest(connection, **_manifest())


# ---------------------------------------------------------------------------
# Dirty working tree
# ---------------------------------------------------------------------------
# `code_commit` records HEAD, not the working tree. An episode run with an
# uncommitted change appeared under the same commit as a clean run.


def test_a_dirty_tree_blocks_the_run(connection, monkeypatch):
    monkeypatch.setattr("zihin.records.working_tree", lambda: "dirty")
    with pytest.raises(RecordError, match="working tree dirty"):
        insert_run_manifest(connection, **_manifest())
    assert connection.execute("SELECT COUNT(*) AS n FROM run_manifests").fetchone()["n"] == 0


def test_an_unverifiable_tree_is_not_treated_as_clean(connection, monkeypatch):
    """If git cannot be read, the tree cannot be verified clean; it is not assumed."""
    monkeypatch.setattr("zihin.records.working_tree", lambda: "unknown")
    with pytest.raises(RecordError, match="working tree unknown"):
        insert_run_manifest(connection, **_manifest())


def test_the_override_lets_the_run_through_and_is_recorded(connection, monkeypatch):
    """Setup exploration is not blocked, it is marked."""
    monkeypatch.setattr("zihin.records.working_tree", lambda: "dirty")
    insert_run_manifest(connection, allow_dirty_tree=True, **_manifest())
    assert connection.execute("SELECT working_tree FROM run_manifests").fetchone()[0] == "dirty"


def test_a_clean_tree_needs_no_override(connection, monkeypatch):
    monkeypatch.setattr("zihin.records.working_tree", lambda: "clean")
    insert_run_manifest(connection, **_manifest())
    assert connection.execute("SELECT working_tree FROM run_manifests").fetchone()[0] == "clean"


def test_the_database_rejects_an_unknown_tree_state(connection):
    with pytest.raises(sqlite3.IntegrityError):
        _ham_insert(connection, "z", working_tree="'belki'")


# ---------------------------------------------------------------------------
# The gate's scope: measurement-defining paths only (K-76)
# ---------------------------------------------------------------------------
# A gate over the whole tree also blocked touching a document while a run was in
# progress. Pilot runs take hours and translation work goes on in parallel
# (K-77).


def _paths(monkeypatch, rows: list[str]) -> None:
    monkeypatch.setattr("zihin.records.uncommitted_paths", lambda: rows)


def test_a_change_outside_the_list_does_not_block_the_run(monkeypatch):
    """A document, a report and an unrelated script do not change the measurement."""
    _paths(
        monkeypatch,
        ["docs/09-limitations.tr.md", "PILOT_REPORT.md", "scripts/build_decisions_csv.py"],
    )
    assert working_tree() == "clean"


def test_a_change_inside_the_list_still_blocks_the_run(monkeypatch):
    _paths(monkeypatch, ["docs/09-limitations.tr.md", "src/zihin/shield.py"])
    assert working_tree() == "dirty"


def test_a_directory_entry_covers_what_is_under_it(monkeypatch):
    """`config/` is a directory entry; every file under it defines the measurement."""
    _paths(monkeypatch, ["config/skills.yaml"])
    assert working_tree() == "dirty"


def test_the_prefix_is_a_path_prefix_not_a_substring(monkeypatch):
    """Mutation: membership by `in`.

    A file called `docs/src/zihin/shield.py` does not define the measurement; a
    substring search would count it as critical and the gate would close in the
    wrong place.
    """
    _paths(monkeypatch, ["docs/src/zihin/shield.py"])
    assert working_tree() == "clean"


def test_a_rename_counts_both_of_its_paths(monkeypatch):
    """A measurement-defining file leaving the list matters as much as one entering it."""
    monkeypatch.setattr(
        "zihin.records.subprocess.run",
        lambda *a, **k: type(
            "R", (), {"stdout": 'R  src/zihin/shield.py -> "src/zihin/old shield.py"\n'}
        )(),
    )
    assert working_tree() == "dirty"


def test_an_untracked_measurement_file_blocks_the_run(monkeypatch):
    """A `??` line carries a path too.

    An uncommitted new condition configuration is as decisive as a modified one:
    which file gets read is settled at run time.
    """
    monkeypatch.setattr(
        "zihin.records.subprocess.run",
        lambda *a, **k: type("R", (), {"stdout": "?? config/new_condition.yaml\n"})(),
    )
    assert working_tree() == "dirty"


def test_git_being_unreadable_is_not_clean(monkeypatch):
    def patlat() -> list[str]:
        raise OSError("git yok")

    monkeypatch.setattr("zihin.records.uncommitted_paths", patlat)
    assert working_tree() == "unknown"


def test_both_gates_share_one_membership_rule(monkeypatch):
    """`changed_files` and `working_tree` call the same predicate.

    Mutation: writing a separate membership rule for each. The two rules drift
    apart in silence and the same file becomes critical at one gate and not at the
    other.
    """
    monkeypatch.setattr("zihin.records.defines_measurement", lambda path: path.endswith(".md"))
    _paths(monkeypatch, ["docs/09-limitations.tr.md"])
    assert working_tree() == "dirty"
    _paths(monkeypatch, ["src/zihin/shield.py"])
    assert working_tree() == "clean"


def test_the_list_is_what_defines_measurement():
    assert defines_measurement("src/zihin/compiler.py")
    assert defines_measurement("config/baseline.yaml")
    assert not defines_measurement("docs/08-decisions.tr.md")
    assert not defines_measurement("results/card-tokens.json")


def test_what_the_conditions_see_is_inside_the_list():
    """The retriever and the card format were added to the list late; because the
    gate was narrowed, this blocks.

    The retriever picks which card goes to which task, the card format decides
    what the model reads. While neither was on the list, a run could be started
    with a dirty retriever.
    """
    assert defines_measurement("src/zihin/retriever.py")
    assert defines_measurement("src/zihin/cards.py")


def test_nothing_is_written_when_the_contract_fails(connection):
    with pytest.raises(RecordError):
        insert_run_manifest(connection, **_manifest(keep_alive=None))
    remaining = connection.execute("SELECT COUNT(*) AS n FROM run_manifests").fetchone()["n"]
    assert remaining == 0, "a row was written even though the contract failed"


# ---------------------------------------------------------------------------
# The shield's identity
# ---------------------------------------------------------------------------
# `shield_violations` rows carry meaning only relative to the write set that
# produced them, and that set changed twice in one day: once when the resolver
# started taking the method, once when `update` left the verb list. Violations
# produced by two different sets are incomparable.


def test_a_manifest_without_a_shield_mode_is_rejected(connection):
    """The mode is mandatory.

    The mutation it kills: removing the field from the mandatory-manifest-fields
    list. Then the mode falls silently to the 'off' default and an episode that
    ran in shadow mode appears in the record as unshielded.
    """
    with pytest.raises(RecordError, match="shield_mode"):
        insert_run_manifest(connection, **_manifest(shield_mode=None))


def test_an_unknown_shield_mode_is_rejected(connection):
    with pytest.raises(RecordError, match="shadow, enforce, off"):
        insert_run_manifest(connection, **_manifest(shield_mode="belki"))


def test_the_database_also_rejects_an_unknown_shield_mode(connection):
    """Do the Python layer and the schema say the same thing.

    They are checked separately because in a migrated file (series 2) the CHECK is
    not in force and only the Python layer guards there. If the schema's own
    constraint is not checked on a fresh file, S-29 repeats: the contract is
    written but not in force.
    """
    with pytest.raises(sqlite3.IntegrityError):
        _ham_insert(connection, "z", shield_mode="'belki'")


def test_a_running_shield_must_record_its_configuration(connection):
    """Fail-closed: if the shield is running, the configuration it ran under must
    be written down.

    If this field is not collected during the run it cannot be collected later —
    the write set file will have changed and a digest computed after the fact
    would be wrong.
    """
    with pytest.raises(RecordError, match="shield_config_digest"):
        insert_run_manifest(connection, **_manifest(shield_config_digest=None))


def test_a_shield_that_was_off_needs_no_configuration(connection):
    """A run without a shield has no configuration to digest.

    Forcing a digest here would be inventing the identity of something that does
    not exist.
    """
    insert_run_manifest(connection, **_manifest(shield_mode="off", shield_config_digest=None))
    row = connection.execute(
        "SELECT shield_mode, shield_config_digest FROM run_manifests"
    ).fetchone()
    assert (row["shield_mode"], row["shield_config_digest"]) == ("off", None)


def test_the_database_rejects_a_running_shield_without_a_digest(connection):
    with pytest.raises(sqlite3.IntegrityError):
        _ham_insert(connection, "z", shield_mode="'shadow'", shield_config_digest="NULL")
