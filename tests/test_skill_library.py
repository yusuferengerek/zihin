"""The skill library table: a derived projection, not a record.

Three properties, and each fails in a way that would not announce itself.

**It is replaceable.** `skills` deliberately carries no append-only trigger. A
library that could not be rebuilt would become a second source of truth, which
is the thing the projection rule exists to prevent (`03-architecture.tr.md`).

**It arrives in an existing database.** Series 2 was created before this table
existed. Column migration cannot carry constraints (S-29), but table creation
can, and that difference is what makes this safe — so it is checked, not
assumed.

**Provenance travels with every row.** The same episodes give different skills
at a different gap. A library without its gap, support, thresholds, compiler
commit and write-set digest cannot be reproduced or compared.
"""

from __future__ import annotations

import sqlite3

import pytest

from zihin.records import insert_skill, open_database, replace_library


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        yield connection


def _skill(**degisiklik):
    fields = {
        "skill_id": "abc123",
        "library_id": "v0-test",
        "effect_suffix": ["POST venmo.auth/token"],
        "body": ["GET api_docs.api_doc", "POST venmo.auth/token"],
        "body_length": 2,
        "support": 8,
        "supporting_tasks": ["g1", "g2"],
        "supporting_episodes": [1, 2],
        "merged_from": 19,
        "bound_arguments": {},
        "free_parameters": ["1.password", "1.username"],
        "constants": {},
        "postcondition": {},
        "expected_saving": 8,
        "expected_saving_calls": 8,
        "observed_steps": 2,
        "max_gap": 2,
        "min_support": 3,
        "constant_threshold": 3,
        "compiler_commit": "deadbeef",
        "write_set_digest": "a" * 64,
    }
    fields.update(degisiklik)
    return fields


# --- the projection is replaceable ---


def test_a_library_can_be_deleted_and_rebuilt(db):
    """No append-only trigger, deliberately (K-16 protects the record, not this).

    Mutation: adding the trigger for symmetry with the other tables. Then a
    compiler change could never be applied and the library would drift away from
    the episodes it claims to summarise.
    """
    insert_skill(db, **_skill())
    assert replace_library(db, "v0-test") == 1
    assert db.execute("SELECT COUNT(*) c FROM skills").fetchone()["c"] == 0
    insert_skill(db, **_skill())
    assert db.execute("SELECT COUNT(*) c FROM skills").fetchone()["c"] == 1


def test_replacing_one_library_leaves_the_others_alone(db):
    insert_skill(db, **_skill(skill_id="a", library_id="v0-a"))
    insert_skill(db, **_skill(skill_id="b", library_id="v0-b"))
    assert replace_library(db, "v0-a") == 1
    remaining = [r["library_id"] for r in db.execute("SELECT library_id FROM skills")]
    assert remaining == ["v0-b"]


def test_the_same_effect_suffix_cannot_appear_twice_in_one_library(db):
    """Identity is the effect suffix (K-75). Two rows for it would mean the
    merge did not run, and the count would be an artefact of the prefixes."""
    insert_skill(db, **_skill(skill_id="a"))
    with pytest.raises(sqlite3.IntegrityError):
        insert_skill(db, **_skill(skill_id="b"))


def test_the_same_effect_suffix_may_appear_in_two_libraries(db):
    """Two configurations produce two libraries and they coexist."""
    insert_skill(db, **_skill(skill_id="a", library_id="v0-gap2"))
    insert_skill(db, **_skill(skill_id="b", library_id="v0-gap5"))
    assert db.execute("SELECT COUNT(*) c FROM skills").fetchone()["c"] == 2


# --- what the table refuses ---


def test_a_one_call_skill_is_rejected(db):
    """Minimum length two (`06-skill-language.tr.md`).

    It matters here because K-80 removes the scaffold's completion call from
    bodies, and the corpus's one environment-action pattern fell to a single
    call that way. It must not slip back in.
    """
    with pytest.raises(sqlite3.IntegrityError):
        insert_skill(db, **_skill(body=["POST venmo.payment_requests"], body_length=1))


def test_an_empty_effect_suffix_is_rejected(db):
    """A discovery prefix is not a skill (K-75), and the table says so too.

    The rule lives in the compiler; the CHECK is here because a projection that
    can be rebuilt by any future script needs the invariant at the storage
    layer as well.
    """
    with pytest.raises(sqlite3.IntegrityError):
        insert_skill(db, **_skill(effect_suffix=[]))


# --- the postcondition's three states ---


def test_an_unattributable_postcondition_is_null_not_empty(db):
    """None means "could not attribute", `{}` means "attributed, nothing
    changed" (K-79). Collapsing them would read a missing measurement as
    evidence of no effect."""
    insert_skill(db, **_skill(skill_id="a", postcondition=None))
    insert_skill(db, **_skill(skill_id="b", library_id="v0-other", postcondition={}))
    rows = {
        r["skill_id"]: r["postcondition"]
        for r in db.execute("SELECT skill_id, postcondition FROM skills")
    }
    assert rows["a"] is None
    assert rows["b"] == "{}"


def test_the_shape_is_stored_as_written(db):
    insert_skill(
        db, **_skill(postcondition={"venmo.PaymentRequest": "+", "venmo.Notification": "+"})
    )
    stored = db.execute("SELECT postcondition FROM skills").fetchone()["postcondition"]
    assert stored == '{"venmo.Notification": "+", "venmo.PaymentRequest": "+"}'


def test_json_fields_are_written_in_a_stable_order(db):
    """The library is a projection: the same episodes must give the same rows.

    Mutation: dropping `sort_keys`. Nothing would break visibly, but a digest
    over the library would change when nothing had.
    """
    insert_skill(db, **_skill(bound_arguments={"1": ["b", "a"], "0": ["c"]}))
    stored = db.execute("SELECT bound_arguments FROM skills").fetchone()["bound_arguments"]
    assert stored == '{"0": ["c"], "1": ["b", "a"]}'


# --- provenance ---


@pytest.mark.parametrize(
    "field",
    ["max_gap", "min_support", "constant_threshold", "compiler_commit", "write_set_digest"],
)
def test_provenance_columns_are_mandatory(db, field):
    """Without these the library cannot be reproduced or compared.

    The gap in particular: the same episodes give a different library at a
    different gap, and the gap's upper bound is set by executability (K-81).
    """
    fields = _skill()
    del fields[field]
    with pytest.raises(sqlite3.IntegrityError):
        insert_skill(db, **fields)


# --- the table reaches an existing database ---


def test_the_table_is_created_in_a_database_that_predates_it(tmp_path):
    """Series 2 was created before `skills` existed.

    Column migration cannot carry constraints and that is recorded as a known
    limit (S-29); creating a whole table can, so the migrated table has to be
    the same table. Checked rather than assumed.
    """
    path = tmp_path / "old.sqlite"
    with open_database(path) as first:
        first.execute("DROP TABLE skills")
        first.execute("DROP INDEX IF EXISTS idx_skills_library")
        first.commit()
        assert not first.execute(
            "SELECT COUNT(*) c FROM sqlite_master WHERE name = 'skills'"
        ).fetchone()["c"]

    with open_database(path) as second:
        row = second.execute("SELECT sql FROM sqlite_master WHERE name = 'skills'").fetchone()
        assert row is not None
        assert row["sql"].count("CHECK") == 4
        assert "UNIQUE (library_id, effect_suffix)" in row["sql"]
        indexes = {
            r["name"]
            for r in second.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'skills'"
            )
        }
        assert {"idx_skills_library", "idx_skills_support", "idx_skills_saving"} <= indexes
        # And it works: the constraints are in force, not merely written.
        with pytest.raises(sqlite3.IntegrityError):
            insert_skill(second, **_skill(body_length=1))
