"""The decision record's structure, and the projection built from it.

**Why this file exists.** The completeness check in `build_decisions_csv.py`
tests existence: every identity in the document reaches the CSV. It cannot see a
row that is present but wrong. K-102 was written with `**Gerekçe ölçüldü.**`, the
literal split on `**Gerekçe.**` did not match, and the CSV carried "Karar." as
the rationale summary while the suite stayed green. Regenerating the CSV after
the fix showed the same silent failure in sixteen other records.

So the guard cannot be a check on that one heading. These tests fix the schema
itself: which headings a decision entry may carry, how they are spelled, and that
the rationale is read as a family rather than as one literal string.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[1]
DOCUMENT = REPOSITORY / "docs" / "08-decisions.tr.md"


def _builder():
    """Imports the script by path: `scripts/` is not a package."""
    path = REPOSITORY / "scripts" / "build_decisions_csv.py"
    spec = importlib.util.spec_from_file_location("build_decisions_csv", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def builder():
    return _builder()


@pytest.fixture(scope="module")
def document() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_the_real_document_satisfies_the_heading_schema(builder, document):
    """The guard is worth nothing if it is not green on the real document."""
    builder.check_heading_schema(document)


def test_a_misspelled_structural_heading_is_caught(builder):
    """A heading that folds onto a structural stem without being it.

    This is the class the rule is for: `Gerekce` without the cedilla reads as
    correct to a hurried eye and produces a heading the tooling does not know.
    """
    text = (
        "## Aşama 1\n\n"
        "### K-500 — Bir karar\n\n"
        "**Karar.** Bir şey.\n\n"
        "**Gerekce.** Diakritik düştü.\n"
    )
    with pytest.raises(SystemExit) as error:
        builder.check_heading_schema(text)
    assert "Gerekce" in str(error.value)
    assert "Gerekçe" in str(error.value)


def test_a_record_without_a_decision_heading_is_caught(builder):
    """An entry that never says what was decided."""
    text = "## Aşama 1\n\n### K-501 — Bir karar\n\n**Gerekçe.** Sebebi var, kararı yok.\n"
    with pytest.raises(SystemExit) as error:
        builder.check_heading_schema(text)
    assert "K-501" in str(error.value)


def test_the_listed_exceptions_stay_exceptions(builder):
    """Three records predate the decision-heading rule.

    The set is pinned so that growing it is a deliberate edit. An exception that
    can be added silently is not an exception, it is a hole.
    """
    assert builder.WITHOUT_DECISION_HEADING == frozenset({"K-53", "K-84", "K-85"})


def test_free_prose_headings_are_allowed(builder):
    """The schema constrains the structural vocabulary, not the prose.

    `**Ayna bulgusu.**` is a real heading in the document. A schema that rejected
    it would be a schema nobody could keep.
    """
    text = (
        "## Aşama 1\n\n"
        "### K-502 — Bir karar\n\n"
        "**Karar.** Bir şey.\n\n"
        "**Ayna bulgusu.** Serbest metin.\n"
    )
    builder.check_heading_schema(text)


@pytest.mark.parametrize(
    "heading",
    ["**Gerekçe.**", "**Gerekçe — neden üç kol.**", "**Gerekçe üç parçalı.**", "**Sebep.**"],
)
def test_the_rationale_is_read_as_a_family(builder, heading):
    """Every member of the family opens a rationale.

    All four forms are in the document. Split on the single literal
    `**Gerekçe.**`, sixteen of them silently returned the entry's first sentence
    instead — which was the word "Karar." for seventeen rows in the CSV.
    """
    content = f"**Karar.** Kararın kendisi.\n\n{heading} Asıl sebep burada.\n"
    assert builder.rationale_summary(content) == "Asıl sebep burada."


def test_the_rationale_falls_back_past_the_first_heading(builder):
    """Eleven records carry no rationale-family heading at all.

    They are not an error, but the fallback has to skip the heading it lands
    on. Taking the entry's first sentence verbatim returned the word
    "Karar." — the heading itself — for thirteen records, which is a row that
    looks filled and says nothing.
    """
    content = "**Karar.** Tek başına duran bir karar. İkinci cümle.\n"
    assert builder.rationale_summary(content) == "Tek başına duran bir karar."


def test_the_csv_carries_no_bare_heading_as_a_rationale(builder, document):
    """The measured symptom, pinned as a criterion.

    "Karar." as a rationale summary means the split missed and the fallback ate
    the heading. Seventeen rows looked like that before the family fix, and
    thirteen more before the fallback learned to skip the heading.
    """
    rows = [
        (identity, builder.rationale_summary(content))
        for _, identity, _, content in builder.all_records(document)
    ]
    empty = {"Karar.", "Gerekçe.", "Sebep.", ""}
    bare = [identity for identity, summary in rows if summary in empty]
    # The open questions carry a question, not a rationale; they are the only
    # records allowed to leave the column empty.
    assert all(identity.startswith("A-") for identity in bare), bare
