"""Finds Turkish left in the Python tree, and says which of it is allowed to stay.

**Why the criterion is not the diacritics.** The first sweep of the language
migration keyed on `çğıöşü`, and diacritic-free Turkish walked straight through
it: `kart: 1 beceri, 1 hata; slota giren 1+1, 457 karakter` was still being
printed after the branch merged. The word is the criterion here, folded to its
diacritic-free form before matching, so `Gerekçe` and `Gerekce` are the same
token to this scanner.

**Which Turkish is allowed to stay: the data rule.** A string that occurs in the
record or under `results/` is an interface. Translating it would make it a
different string, break its link to what is already written, and break the
resume guard that matches on run prefixes. So the test is mechanical: if the
string is a key or an identifier-shaped value in the record or in `results/`, it
is data and it stays; otherwise it is prose and it goes.

The rule is the same one that keeps `docs/08-decisions.tr.md`'s Turkish regexes in
`build_decisions_csv.py`: a parsed string is an interface.

**Its limit.** The vocabulary is a fixed list, so a Turkish word nobody has used
yet is invisible to this. It catches the words this repository actually writes,
which is what the two measured misses were made of.

Usage:

    uv run python scripts/check_language.py
"""

from __future__ import annotations

import ast
import io
import json
import keyword
import pathlib
import re
import sqlite3
import sys
import tokenize
import unicodedata

# Folded to their diacritic-free form at import; the scanner compares folded
# forms, so a missing cedilla does not hide a word.
VOCABULARY = """
acik acilis adim ad alan alinan anahtar ariza asama atilan ayni ayrisma
bant baska basarili baslik beceri beklenen benzer bilinmeyen bolum bos bosalt
buyuk cagri capa carpan cikis cikti dagilim damga deger degisti deneme denetim
dizin dogru dogrula dolu dosya dunya durum duzeltme
eksik ekleme epizot esik eslesme eski
fark farkli filtre
gecen gecerli gecersiz gecti gerekce girdi giris gorev gorulen gunluk govde
guvenli
hata hedef hepsi
icerik ikinci ilgili ilgisiz ilk istek iz izinli izleyici
jeton
kalan kaldi kalkan kapali kapsam karakter karar kart kategori kaynak kayit
kesilen kimlik kirli kisa kok koleksiyon kontrol konteyner kopru kosu kosul
kucuk kunye kural kurcalama kume kutuphane
liste
madde medyan modeller
neden nokta
okuma olan olcu olcum onek oran ornek ozet
payda pencere politika
sahte saniye satir sayac sayi sayim sebep secilen secim seri sifir sinama sinir
soket sonlanma sonuc sorulabilir sunulan sure surec
tabaka taban tarama tasiyan tavan tekduze tekrar temiz tepe tohum toplam
trafik tur
uc ucuncu uygulama uzun
varlik veri vekil verilen
yakalanan yanit yanlis yapilan yazildi yazma yeni yerel yokluk yol yonetim
yorunge yukleme
zorunlu
"""

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]

# The files whose Turkish is the subject rather than the medium: each one either
# parses or emits a Turkish document, so its strings are that document's text.
SUBJECT_FILES = frozenset(
    {
        "scripts/build_decisions_csv.py",
        "tests/test_decision_record.py",
        # Its vocabulary is a list of Turkish words; a scanner that flagged
        # itself would be a scanner nobody could keep green.
        "scripts/check_language.py",
        # It writes the map into `docs/09-limitations.tr.md`, so the strings
        # it emits are that document's text. When the English translation
        # lands, the generator emits both and the pair stays here for the same
        # reason. (The document name went missing from this comment during the
        # English migration and was restored by measurement, not memory.)
        "scripts/build_limitations_index.py",
        # Same shape, for the coverage summary in the presentation skeleton.
        "scripts/build_skeleton_coverage.py",
        # Its allowlist quotes spans from the Turkish sources verbatim, because
        # the check's whole job is that a quoted span must match byte for byte.
        # Translating the allowlist would break the thing it allows.
        "scripts/check_docs_parity.py",
        # Same shape again: the markers of a dated addendum are the Turkish
        # document's own words ("Ek", "Düzeltme", "Kapandı"). Translating them
        # would stop the check matching the documents it exists to read.
        "scripts/check_dates.py",
        # Its fixtures are lines lifted from the Turkish documents, for the same
        # reason `tests/test_decision_record.py` is here.
        "tests/test_dates.py",
    }
)

# The fixed code sequence in the transparency measurement. The digest recorded in
# `results/transparency.json` (`5e4812502f278f0b`, 5291 bytes) is a function of
# these exact bytes: the sequence is executed and the resulting
# `logs/environment_io.md` is hashed. Translating a variable name inside it would
# produce a different transcript and silently invalidate the recorded reference —
# the same reference the post-merge comparability gate is measured against. It is
# the strongest case of the data rule in the tree, so it is named here rather
# than left to the corpus test, which cannot see a string's consequences.
SUBJECT_LINES = {
    "scripts/setup/measure_transparency.py": range(55, 75),
}

WORD = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]+")
FAMILY = re.compile(r"\b[A-Za-z][A-Za-z_]*\d+(?:[-_][A-Za-z0-9_]+)*\b")
CAMEL = re.compile(r"[A-Z]{2,}(?![a-z])|[A-Z]?[a-zçğıöşü]+")


def fold(word: str) -> str:
    """Diacritic-free lowercase form. `Gerekçe` and `Gerekce` fold together."""
    word = word.replace("ı", "i").replace("İ", "I")
    stripped = unicodedata.normalize("NFD", word)
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


STEMS = frozenset(fold(w) for w in VOCABULARY.split() if w)


def turkish_words(text: str) -> list[str]:
    """The Turkish words in a piece of text, whatever its casing."""
    found = []
    for token in WORD.findall(text):
        for piece in CAMEL.findall(token):
            if fold(piece) in STEMS:
                found.append(piece)
    return found


def mask_data(text: str, turkish_data: list[str]) -> str:
    """Blanks the data strings a piece of prose mentions.

    A comment is allowed to name `sinir3-32616b5_1`; naming a run id is not
    writing Turkish. Without this, every reference to the record would look like
    a translation that was missed.
    """
    for member in turkish_data:
        if member in text:
            text = text.replace(member, " ")
    # A prefix family named in prose: a usage example writes `sinir2` where the
    # record holds `sinir3-g1-...`. Naming a run prefix is not writing Turkish.
    return FAMILY.sub(lambda m: " " if is_data(m.group(0), _CORPUS) else m.group(0), text)


# How many strings the record itself contributed, filled in by the builder.
_FROM_THE_RECORD: list[int] = []
_CORPUS: set[str] = set()


def data_corpus() -> set[str]:
    """Every key and identifier-shaped value in the record and under `results/`.

    Prose values are left out on purpose: a Turkish sentence sitting in a `"ne"`
    field of a results file would otherwise make every word in it look like data.
    Whitespace is the discriminator — an identifier does not contain a space.
    """
    corpus = _CORPUS

    def take(value: object) -> None:
        if isinstance(value, str) and value and not any(c.isspace() for c in value):
            corpus.add(value)

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                take(key)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        else:
            take(node)

    # File names are interfaces too: the reports cite `results/...json` by name,
    # and an experiment prefix is the head of a directory name.
    for directory in ("results", "experiments", "docs"):
        for path in sorted((REPOSITORY / directory).rglob("*")):
            corpus.add(path.name)
            corpus.add(path.stem)

    for path in sorted((REPOSITORY / "results").rglob("*.json")):
        try:
            walk(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    for path in sorted((REPOSITORY / "experiments").rglob("*.json")):
        try:
            walk(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

    # The protocol's conditions tables name their fields in Turkish, and the code
    # that reads those tables has to spell the field the same way. Those field
    # names are an interface between a Turkish document and the code, exactly as
    # a file name is; translating one would break the lookup.
    try:
        import re as _re

        from zihin.declared import HEADING, PROTOCOL, ROW

        protocol = PROTOCOL.read_text(encoding="utf-8")
        for match in HEADING.finditer(protocol):
            body = protocol[match.end() : match.end() + 4000]
            separator = body.find("\n|--")
            if separator != -1:
                body = body[body.index("\n", separator + 1) :]
            for field, _ in ROW.findall(body):
                corpus.add(field)
                corpus.add(field.lower())
        del _re
    except Exception:  # noqa: BLE001 - an unreadable protocol adds nothing
        pass

    before_the_record = len(corpus)
    for database in sorted((REPOSITORY / "results").glob("*.sqlite")):
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
        try:
            tables = [
                r[0]
                for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            ]
            for table in tables:
                for row in connection.execute(f"PRAGMA table_info({table})"):
                    corpus.add(row[1])
                for row in connection.execute(f"SELECT * FROM {table}"):
                    for value in row:
                        take(value)
        finally:
            connection.close()
    _FROM_THE_RECORD.append(len(corpus) - before_the_record)
    return corpus


def is_data(text: str, corpus: set[str]) -> bool:
    """Does this string name something already written down.

    Exact membership is not enough: `bant3` never appears alone in the record,
    only as the head of run ids like `bant3-g1-g1-7b`. A head segment counts.
    """
    if text in corpus:
        return True
    fragment = text.startswith(("-", "_")) or text.endswith(("-", "_"))
    family = text.rstrip("0123456789") if text[-1:].isdigit() else None
    return any(
        member.startswith(f"{text}-")
        or f"-{text}-" in member
        or (fragment and text in member)
        or (family and member.startswith(family))
        for member in corpus
    )


def scan(path: pathlib.Path, corpus: set[str], turkish_data: list[str]) -> list[str]:
    relative = path.relative_to(REPOSITORY).as_posix()
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    findings: list[str] = []

    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            text = ast.get_docstring(node)
            if text:
                docstrings.add(id(node.body[0].value))
                words = turkish_words(mask_data(text, turkish_data))
                if words:
                    label = getattr(node, "name", "<module>")
                    line = getattr(node, "lineno", 1)
                    findings.append(f"L{line} docstring [{label}]: {sorted(set(words))}")

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in docstrings:
            continue
        exempt = node.lineno in SUBJECT_LINES.get(relative, range(0))
        words = turkish_words(mask_data(node.value, turkish_data))
        if words and not exempt and not is_data(node.value, corpus):
            findings.append(f"L{node.lineno} string: {node.value[:70]!r} {sorted(set(words))}")

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            words = turkish_words(mask_data(token.string, turkish_data))
            if words:
                findings.append(f"L{token.start[0]} comment: {token.string.strip()[:70]}")
        elif token.type == tokenize.NAME and not keyword.iskeyword(token.string):
            words = turkish_words(token.string)
            if words:
                findings.append(f"L{token.start[0]} name: {token.string}")

    return findings


# Below this many known data strings the corpus is not present: a fresh clone has
# no `results/` and no record, so every Turkish data key would read as prose. The
# working repository carries eleven thousand; a clone carries about a hundred and
# fifty. A thousand separates the two by an order of magnitude either way.
# The floor is on what the RECORD contributes, not on the corpus's size.
#
# It used to be on the size, and the size is dominated by things every checkout
# has: file and directory names, and the tracked `results/*.json`. Measured on a
# fresh clone of the same commit — names 194, plus the tracked JSON 2026, floor
# 1000 — so the check answered on a corpus missing 12308 of its 16384 strings and
# reported 67 data keys as prose. Locally it reported none. K-117 says a check
# must not give a different answer in a different environment; the honest form of
# that is declining when the subject is absent, and the subject here is the
# record (K-152).
RECORD_FLOOR = 5000


def main() -> None:
    corpus = data_corpus()
    # Only the data strings that carry a Turkish word can mask anything, and
    # longest-first so a prefix does not eat its own extension.
    turkish_data = sorted((m for m in corpus if turkish_words(m)), key=len, reverse=True)
    files = sorted(
        p
        for p in list((REPOSITORY / "src").rglob("*.py"))
        + list((REPOSITORY / "tests").rglob("*.py"))
        + list((REPOSITORY / "scripts").rglob("*.py"))
        if "__pycache__" not in p.parts
    )

    total = 0
    for path in files:
        relative = path.relative_to(REPOSITORY).as_posix()
        if relative in SUBJECT_FILES:
            continue
        findings = scan(path, corpus, turkish_data)
        if findings:
            total += len(findings)
            print(f"{relative} ({len(findings)})")
            for line in findings:
                print(f"    {line}")

    print()
    from_the_record = _FROM_THE_RECORD[-1] if _FROM_THE_RECORD else 0
    print(
        f"data strings known from the record and results/: {len(corpus)} "
        f"({from_the_record} of them from the record)"
    )
    if from_the_record < RECORD_FLOOR:
        # K-112: the subject is missing, so the check falls rather than passing.
        # K-117: it must not give a different answer in a different environment,
        # and the honest form of that is declining to answer, not answering wrongly.
        sys.exit(
            f"the record contributed {from_the_record} string(s) and the floor is "
            f"{RECORD_FLOOR}. This check compares prose against the data keys under "
            "`results/` and in the record; the record is gitignored, so a fresh clone "
            "has the JSON but not the database, and the keys only the database carries "
            "would be reported as prose. It declines rather than answering differently "
            "in a different environment (K-117). Run it in a working tree that has the "
            "record, or run a measurement first."
        )
    print(f"files scanned: {len(files)}  ({len(SUBJECT_FILES)} skipped as subject files)")
    print(f"Turkish left: {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
