"""Produces `experiments/decisions.csv` from `docs/08-decisions.tr.md`.

The CSV is a projection, not a second source. Kept by hand it would drift from
the decision document, and once drifted there would be no telling which one was
right.

The columns were fixed in A-04: `decision_id,stage,title,status,supersedes,
rationale_summary`. `status` carries three states — `active`, `superseded`,
`open`. `supersedes` points at the record this one replaced.

The supersession relation is read from the document, not from a hand-kept
table. Two patterns are machine-readable in the prose:

    ### A-01 — ... Cevaplandı, K-28.      → K-28 supersedes A-01
    **Karar.** ~~...~~ ... karar K-34'e taşındı.  → K-34 supersedes K-03

The document holds a third state that does not count as supersession: a record
struck through and rewritten in place (K-11, K-13, K-20). The decision keeps
its number, so it stays `active`.

**The parser is bound to the Turkish source and must stay that way.** The
patterns above match Turkish words (`Cevaplandı`, `taşındı`, `**Gerekçe.**`).
When the English translation of the decision record appears, this script keeps
reading the Turkish file. Pointing it at an English translation would make the
CSV silently empty — which has happened once already, for a different reason.
`SOURCE` is pinned below for exactly this reason.

**Two checks, and they look at different things.** `check_completeness` asks
whether every identity in the source reached the CSV — an existence check. It
cannot see a row that is present but wrong. `check_heading_schema` asks whether
the headings inside each record match the expected schema — a structure check.
The second one exists because the first one let a wrong row through: K-102 was
written with `**Gerekçe ölçüldü.**`, the literal split on `**Gerekçe.**` did not
match, and the CSV silently carried "Karar." as the rationale summary while every
test stayed green.

**Known fragility, deliberately not fixed at this stage.** A machine-readable
decision record produced by parsing prose is structurally fragile: an ordinary
prose edit can break the parsing. The two checks below are the mitigation for
now, not a fix (S-33).

Usage:

    uv run python scripts/build_decisions_csv.py
"""

from __future__ import annotations

import csv
import io
import re
import sys
import unicodedata
from pathlib import Path

# Pinned to the Turkish source. See the note above: the parsing patterns are
# Turkish, so pointing this at a translation empties the CSV without an error.
SOURCE = Path("docs/08-decisions.tr.md")
TARGET = Path("experiments/decisions.csv")
COLUMNS = ("decision_id", "stage", "title", "status", "supersedes", "rationale_summary")

ANSWERED = re.compile(r"Cevaplandı,\s*(K-\d+)")
MOVED = re.compile(r"karar (K-\d+)['’][ae] taşındı")

# The rationale heading family. `Gerekçe` and `Sebep` both open a rationale, and
# both take free continuations (`— neden üç kol`, `üç parçalı`).
RATIONALE_HEADING = re.compile(r"^\*\*(?:Gerekçe|Sebep)\b[^*]*\*\*", flags=re.M)

# A bold run at the start of a line is a heading inside a record.
HEADING = re.compile(r"^\*\*([^*]+?)\*\*", flags=re.M)
FIRST_WORD = re.compile(r"^([A-Za-zÇĞİÖŞÜçğıöşü]+)")

# The structural headings. These are spelled exactly; anything that folds onto
# one without being it is a typo.
STRUCTURAL_STEMS = (
    "Karar",
    "Gerekçe",
    "Sebep",
    "Bağlam",
    "Sonuç",
    "Bağlantı",
    "Sınırı",
    "Ölçüm",
    "Düzeltme",
)

# Records that predate the "every decision carries a decision heading" rule.
# K-53 opens with `**Düzeltme.**`, K-84 with `**Sonuç görülmeden ilan
# ediliyor.**` and K-85 with `**Üç karar, S-45'in cevabı.**`. They are not
# rewritten: the decision record is append-only in spirit, and an exception
# written down is visible where a silently skipped one is not.
WITHOUT_DECISION_HEADING = frozenset({"K-53", "K-84", "K-85"})

# Identity pattern for the completeness check. Deliberately independent of any
# Turkish word: the guard must be less fragile than what it guards.
IDENTITY = re.compile(r"\b([KA]-\d+)\b")


def sections(text: str) -> list[tuple[str, str]]:
    """Yields the `## Heading` blocks as (heading, body)."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)[1:]
    return list(zip(parts[0::2], parts[1::2], strict=True))


def records(section_name: str, body: str):
    for block in re.split(r"^### ", body, flags=re.M)[1:]:
        heading, _, content = block.partition("\n")
        identity, _, title = heading.partition(" — ")
        yield section_name, identity.strip(), title.strip(), content


def rationale_summary(content: str) -> str:
    """First sentence of the rationale; failing that, the body's first non-empty
    line.

    The rationale heading is matched as a **family**, not as one literal string.
    The document carries `**Gerekçe.**`, `**Gerekçe — neden üç kol.**`,
    `**Gerekçe üç parçalı.**` and `**Sebep.**`, and all of them open a rationale.
    Splitting on the single literal `**Gerekçe.**` silently missed sixteen
    records, which then took their first sentence from the top of the entry
    instead — the same silent-wrong-row class the heading schema check guards.
    """
    match = RATIONALE_HEADING.search(content) or HEADING.search(content)
    text = content[match.end() :] if match else content
    text = re.sub(r"~~.*?~~", "", text, flags=re.S)
    text = re.sub(r"[*`]", "", text)
    flat = " ".join(text.split())
    if not flat:
        return ""
    sentence = re.split(r"(?<=[.!?])\s", flat)[0]
    return sentence.strip()


def check_completeness(text: str, rows: list[dict]) -> None:
    """Every identity in the source must appear in the CSV.

    Stronger than a lower bound on the record count: a bound catches total
    failure but not partial loss. If the section pattern stopped matching forty
    of seventy records, any threshold would be either too loose or too tight.
    This check also maintains itself — no threshold to update as decisions
    accumulate.
    """
    in_source = set(IDENTITY.findall(text))
    in_csv = {row["decision_id"] for row in rows}
    missing = sorted(in_source - in_csv)
    if missing:
        sys.exit(
            f"{len(missing)} identity present in {SOURCE} but missing from the CSV: "
            f"{missing}. The parsing patterns have probably stopped matching; "
            "the CSV was not written."
        )


def _fold(word: str) -> str:
    """Diacritic-free lowercase form, for catching misspelled headings."""
    word = word.replace("ı", "i").replace("İ", "I")
    stripped = unicodedata.normalize("NFD", word)
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


STEM_FOLDS = {_fold(stem): stem for stem in STRUCTURAL_STEMS}


def check_heading_schema(text: str) -> None:
    """Every record's heading set must match the expected schema.

    Two rules, and both of them are about a whole class rather than one case.

    **Every decision carries a decision heading.** A `K-` record without a
    heading whose first word is `Karar` is an entry that does not say what was
    decided. Three records predate the rule and are listed by identity: writing
    an exception down is a deliberate act, silently allowing one is not.

    **A structural heading is spelled the way the structural heading is
    spelled.** A first word that folds onto a structural stem — same letters
    once diacritics are removed — but is not spelled as that stem is a typo:
    `Gerekce`, `Olcum`, `Baglam`. This is the check that would have caught the
    K-102 case if the rationale parser had not been fixed to read the heading
    family in the first place.

    **The limit.** This does not catch a heading that is meaningful prose
    starting with a word the schema has never seen. The schema constrains the
    structural vocabulary, not the prose.
    """
    problems: list[str] = []
    for _, identity, _, content in all_records(text):
        headings = HEADING.findall(content)
        first_words = [m.group(1) for m in map(FIRST_WORD.match, headings) if m]

        for word in first_words:
            expected = STEM_FOLDS.get(_fold(word))
            if expected and word != expected:
                problems.append(f"{identity}: heading '{word}' should be '{expected}'")

        if identity.startswith("K-") and identity not in WITHOUT_DECISION_HEADING:
            if "Karar" not in first_words:
                problems.append(f"{identity}: no '**Karar' heading")

    if problems:
        sys.exit(
            f"{len(problems)} heading schema violations in {SOURCE}:\n  "
            + "\n  ".join(problems)
            + "\nThe CSV was not written."
        )


def all_records(text: str):
    """Every record in the document, section by section."""
    return [r for name, body in sections(text) for r in records(name, body)]


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"{SOURCE} does not exist. Run this script from the repository root.")
    text = SOURCE.read_text(encoding="utf-8")

    raw = all_records(text)

    # The supersession relation is written in the other direction: a record
    # names its successor, and we put "what it replaced" under the successor.
    supersedes: dict[str, str] = {}
    for _, identity, title, content in raw:
        match = ANSWERED.search(title) or MOVED.search(content)
        if match:
            supersedes[match.group(1)] = identity

    rows = []
    for section, identity, title, content in raw:
        if identity.startswith("A-"):
            status = "superseded" if ANSWERED.search(title) else "open"
            title = ANSWERED.sub("", title).strip().rstrip(".")
        elif MOVED.search(content):
            status = "superseded"
        else:
            status = "active"
        rows.append(
            {
                "decision_id": identity,
                "stage": section,
                "title": title,
                "status": status,
                "supersedes": supersedes.get(identity, ""),
                "rationale_summary": rationale_summary(content),
            }
        )

    # Checked before writing: a CSV that is written and then found wanting has
    # already replaced the good one.
    check_completeness(text, rows)
    check_heading_schema(text)

    buffer = io.StringIO()
    # LF, not the csv module's default CRLF: git normalises the committed
    # file to LF, so a CRLF generator matched the working copy locally and
    # reported the CI checkout as stale. A check whose answer depends on the
    # environment is not a check.
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    rendered = buffer.getvalue()

    # The projection had no staleness guard until a sweep of declared-versus-wired
    # checks found it (K-114). Every other generated view in this repository is
    # checked in CI; this one — the view whose drift already cost thirty silently
    # wrong rationales (K-103) and sixty-eight lost rows (S-33) — was rebuilt only
    # when someone remembered to run the script. A guard that depends on being
    # remembered is not a guard (K-99).
    if "--check" in sys.argv:
        # Compared as bytes: reading text translates CRLF to LF and the CSV
        # writer emits CRLF, so a text comparison reports every file as stale.
        current = TARGET.read_bytes() if TARGET.exists() else b""
        if current != rendered.encode("utf-8"):
            sys.exit(f"{TARGET}: stale against {SOURCE}. Run scripts/build_decisions_csv.py.")
        print(f"decisions CSV: current, {len(rows)} records")
        return

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(rendered.encode("utf-8"))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"{TARGET}: {len(rows)} records  {counts}")
    for row in rows:
        if row["supersedes"]:
            print(f"  {row['decision_id']} <- {row['supersedes']}")


if __name__ == "__main__":
    main()
