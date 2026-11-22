"""One naming scheme for the documents, and translation parity where it is claimed.

**The scheme.** A document is `NN-english-kebab.tr.md` (the Turkish source) plus
`NN-english-kebab.en.md` (the English translation). The root is English and
kebab-case, the number prefix is kept, and the language is the last suffix.

**Why the root is English even though the source is Turkish.** A file name is an
identifier, and identifiers are English in this repository (K-102). A file called
`sandbox-kapsami.en.md` — an English translation under a Turkish name — was
exactly the mixed state three sessions of work removed from the code; the
directory an outside reader opens should not carry the one surviving example.

**Two checks, and they fail for different reasons.**

1. *Naming.* Every file directly under `docs/` matches the scheme. A file that
   does not is a second rule the reader has to learn, and the parity check below
   cannot even be defined over it.

2. *Parity.* Every document declared bilingual has both halves. The declaration
   is explicit rather than "every `.tr.md` needs an `.en.md`", because the waves
   land one at a time and a check that is red for a whole wave is a check
   everybody learns to ignore.

**Three categories, and each one is a stated position.** `BILINGUAL` claims a
translation and is checked for it. `TURKISH_ONLY` says a document has no
translation and why. `PENDING` says a translation is owed and names the wave. A
document in none of the three is an omission and fails the check — that is what
keeps "we forgot this one" from looking like "we decided about this one".

**What is deliberately not covered.** `docs/reports/` holds measurement records
that are read alongside their numbers, not the design layer an outside reader is
handed; they stay Turkish and out of scope.

**`README` has its own rule**, because the platform names that file:
`README.md` is the English front door and `README.tr.md` the Turkish source
(K-105). `readme_problems` checks both halves exist and link to each other.

Usage:

    uv run python scripts/check_docs_parity.py
"""

from __future__ import annotations

import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))
DOCS = REPOSITORY / "docs"

NAME = re.compile(r"^\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.(tr|en)\.md$")
LOOSE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(tr|en)\.md$")

# The documents that claim a translation. Growing this list is what a wave does.
BILINGUAL = {
    # wave 1 — the design layer plus the pre-registration and the limits
    "docs/01-problem-definition",
    "docs/02-research-question",
    "docs/03-architecture",
    "docs/04-threat-model",
    "docs/05-experiment-design",
    "docs/06-skill-language",
    "docs/07-failure-taxonomy",
    # already bilingual before the wave
    "docs/12-sandbox-scope",
    # wave 2 — the largest document in the tree
    "docs/09-limitations",
    # wave 2 — the protocol that declares the checks
    "experiments/setup-protocol",
    # a report written bilingually from the start, rather than translated later
    "docs/reports/eksen-uzatma",
    # the alternatives ledger; it stays open and both halves stay with it
    "docs/14-alternatives-ledger",
}

# A translation is owed and the wave is named. Separate from TURKISH_ONLY so
# that "not translated yet" and "will not be translated" never look alike.
PENDING = {}

# In scope for the naming rule, not for parity, and not owed one. Written down so
# that "no translation" is a stated position rather than an oversight.
TURKISH_ONLY = {
    "docs/08-decisions": "the decision record is parsed by build_decisions_csv.py "
    "in Turkish; translating it needs the parser to move first",
    "docs/10-external-review": "a record of two review rounds, not part of the "
    "design layer a reader is handed",
    "docs/11-falsification": "wave 2",
    "docs/appworld-facts": "wave 2",
}


def naming_problems() -> list[str]:
    problems = []
    for path in sorted(DOCS.iterdir()):
        if path.is_dir():
            if path.name != "reports":
                problems.append(f"{path.relative_to(REPOSITORY)}: unexpected directory")
            continue
        if not (NAME.match(path.name) or LOOSE_NAME.match(path.name)):
            problems.append(
                f"{path.relative_to(REPOSITORY)}: does not match NN-english-kebab.(tr|en).md"
            )
    return problems


def parity_problems() -> list[str]:
    problems = []
    for stem in sorted(BILINGUAL):
        for language in ("tr", "en"):
            path = REPOSITORY / f"{stem}.{language}.md"
            if not path.exists():
                problems.append(f"{stem}.{language}.md: declared bilingual but missing")
    for stem in sorted(TURKISH_ONLY):
        if (REPOSITORY / f"{stem}.en.md").exists():
            problems.append(
                f"{stem}.en.md: exists, but the document is listed as Turkish-only. "
                "Move it into BILINGUAL."
            )
    for stem in sorted(PENDING):
        if (REPOSITORY / f"{stem}.en.md").exists():
            problems.append(
                f"{stem}.en.md: exists, so the translation is no longer pending. "
                "Move it from PENDING into BILINGUAL."
            )
    return problems


def uncategorized_problems() -> list[str]:
    """A document in none of the three categories is an omission, not a decision."""
    known = BILINGUAL | set(TURKISH_ONLY) | set(PENDING)
    problems = []
    # `docs/reports/` is scanned too. A bilingual pair placed there used to fall
    # outside every category, so its two halves were never compared with each
    # other — a translation nobody checks is the thing this file exists to
    # prevent (K-138: one source, and the check finds its own subject).
    candidates = sorted(DOCS.glob("*.tr.md")) + sorted((DOCS / "reports").glob("*.tr.md"))
    for path in candidates:
        stem = path.relative_to(REPOSITORY).as_posix()[: -len(".tr.md")]
        if stem not in known:
            problems.append(
                f"{stem}: in no category. Add it to BILINGUAL, PENDING or "
                "TURKISH_ONLY with a reason."
            )
    return problems


def readme_problems() -> list[str]:
    """The one file whose name the platform chooses.

    `README.md` is what a visitor sees first on the repository page, so it is the
    English front door and `README.tr.md` is the Turkish source. This inverts the
    "canonical name is the source" rule the rest of the tree follows, and the
    inversion is deliberate: that rule exists so that in a parsed or cited
    document it is obvious which half is authoritative. The README is neither
    parsed nor cited (K-105).

    Both halves have to exist and each has to link to the other, otherwise a
    reader who lands on one has no way to the other.
    """
    problems = []
    english = REPOSITORY / "README.md"
    turkish = REPOSITORY / "README.tr.md"
    for path in (english, turkish):
        if not path.exists():
            problems.append(f"{path.name}: missing")
    if english.exists() and "README.tr.md" not in english.read_text(encoding="utf-8"):
        problems.append("README.md: no link to README.tr.md")
    if turkish.exists() and "README.md" not in turkish.read_text(encoding="utf-8"):
        problems.append("README.tr.md: no link to README.md")
    return problems


def orphan_problems() -> list[str]:
    problems = []
    for path in sorted(DOCS.glob("*.en.md")):
        source = path.with_name(path.name.replace(".en.md", ".tr.md"))
        if not source.exists():
            problems.append(f"{path.relative_to(REPOSITORY)}: translation with no source")
    return problems


FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
CODE_SPAN = re.compile(r"`([^`]{1,160})`")
RECORD_ID = re.compile(r"\b([SKA]-\d+)\b")
BARE_PATH = re.compile(r"\b((?:[\w.-]+/)+[\w.-]+\.(?:md|py|json|jsonl|ya?ml|sqlite|csv|txt))")
LANGUAGE_SUFFIX = re.compile(r"\.(?:tr|en)\.md$")

# Backticked spans that are prose rather than interface, so a translation is
# expected to change them. Each one is written down instead of guessed at,
# because the whole point of the check is that silence means "unchanged".
TRANSLATED_SPANS = frozenset(
    {
        "statik ∪ ampirik",
        "static ∪ empirical",
        "min(max(2 × çapa, 20), 150)",
        "min(max(2 × anchor, 20), 150)",
        "(gözlenen adım sayısı − 1) × görev desteği × başarı oranı",
        "(observed step count − 1) × task support × success rate",
        # Placeholders inside otherwise-literal spans: the surrounding syntax is
        # code, the word in the angle brackets or the quoted path is prose.
        '@app.delete("/yol")',
        '@app.delete("/path")',
        "ADD COLUMN ... NOT NULL DEFAULT <sabit>",
        "ADD COLUMN ... NOT NULL DEFAULT <constant>",
        "appworld.apps.<uygulama>",
        "appworld.apps.<app>",
        "POST <uygulama>.auth/token",
        "POST <app>.auth/token",
    }
)


def add(counts: dict[str, int], span: str) -> None:
    """Counts one span, with the language suffix folded away.

    A cross-reference is the one anchor that is *supposed* to change: an English
    document links to `03-architecture.en.md` where the Turkish links to
    `03-architecture.tr.md`. Folding both to `.md` keeps the reference under
    check — a dropped link still fails — while letting the correct half of the
    change through.
    """
    # A code span may be wrapped across a line break, and the two languages wrap
    # in different places. Collapsing internal whitespace makes a span broken over
    # two lines the same anchor as the same span on one; without it the regex pairs
    # the wrong backticks and reports garbage on both sides.
    key = LANGUAGE_SUFFIX.sub(".md", " ".join(span.split()))
    if key in TRANSLATED_SPANS:
        return
    counts[key] = counts.get(key, 0) + 1


def anchors(text: str) -> dict[str, int]:
    """Every span a translation must carry through unchanged, counted.

    A translation rewrites prose and keeps interfaces. The interfaces here are
    the backticked spans (paths, field names, identifiers), the record
    identifiers (`S-36`, `K-107`), and bare file paths. None of them are
    language, so the counts have to match on both sides.

    **Why counted rather than checked for presence.** A document that mentions
    `S-05` four times and its translation twice has lost two references, and a
    set comparison calls that equal.

    **Measured need.** Mechanical translation dropped an embedded document name
    three times in this repository. The last one left `check_language.py` reading
    "It writes the map into , so the strings it emits are that document's text"
    for a whole wave, and it was found by eye, not by a check.

    **What it does not catch.** The first run found something bigger than a drop:
    an English document carrying a paragraph its Turkish source never had, so the
    source-to-translation direction had been violated and nothing objected. This
    check sees that only because the added paragraph cited `K-104`. Anchorless
    prose — a sentence with no identifier, path or backticked span — counts zero
    on both sides and passes. Checking direction properly needs each translation
    to record which version of its source it was made from (K-111, K-112).
    """
    counts: dict[str, int] = {}
    # Fenced blocks come out first. Their delimiters are backticks too, so an
    # inline-span regex that runs over them pairs a closing fence with the next
    # inline backtick and swallows whole paragraphs of prose as if they were code.
    for block in FENCE.findall(text):
        add(counts, block)
    inline = FENCE.sub(" ", text)
    prose = CODE_SPAN.sub(" ", inline)
    for span in CODE_SPAN.findall(inline):
        add(counts, span)
    for identifier in RECORD_ID.findall(prose):
        add(counts, identifier)
    for path in BARE_PATH.findall(prose):
        add(counts, path)
    return counts


def anchor_problems() -> list[str]:
    """Interfaces that a translation dropped, gained, or changed the count of."""
    problems = []
    for stem in sorted(BILINGUAL):
        source = REPOSITORY / f"{stem}.tr.md"
        target = REPOSITORY / f"{stem}.en.md"
        if not (source.exists() and target.exists()):
            # K-112: a check whose subject is missing fails, it does not skip.
            # `parity_problems` reports the missing file; this line reports that
            # the anchors went unchecked, which is a different fact and the one
            # a green run would otherwise imply was false.
            problems.append(f"{stem}: declared bilingual but a side is missing; anchors unchecked")
            continue
        left, right = (
            anchors(source.read_text(encoding="utf-8")),
            anchors(target.read_text(encoding="utf-8")),
        )
        own = f"{pathlib.PurePosixPath(stem).name}.md"
        for span in sorted(set(left) | set(right)):
            here, there = left.get(span, 0), right.get(span, 0)
            if here == there:
                continue
            # Every translation opens by naming its source, and the source does
            # not name itself. That one asymmetry is the convention, not a drop.
            if span == own and here == 0 and there == 1:
                continue
            where = "only in the source" if not there else "only in the translation"
            detail = f"{here}\u00d7 vs {there}\u00d7" if here and there else where
            problems.append(f"{stem}: `{span}` — {detail}")
    return problems


# A backticked token shaped like a Python identifier: snake_case or CamelCase,
# four characters or more. Short names (`api`, `url`) and dotted API names
# (`venmo.transactions`) are deliberately out — they are not Python identifiers
# and resolving them would need a different index.
IDENTIFIER_SHAPE = re.compile(r"^(?:_?[a-z][a-z0-9_]{3,}|[A-Z][A-Za-z0-9]{3,})$")

# Run prefixes and task identifiers have the same shape as a snake_case name
# (`bant2`, `sinir3`, `c77c005_3`). They are data keys — they live in the record
# and under `results/`, not in the code — so a trailing digit disqualifies a
# token. No Python identifier in this repository ends in a digit; when one does,
# this line is the thing to revisit.
DATA_KEY_SHAPE = re.compile(r"\d$")

# Commit hashes and trailing-underscore prefixes (`show_`, `get_`) also share the
# shape without being identifiers.
NOT_A_NAME = re.compile(r"^[0-9a-f]{7,40}$|_$")

# Identifiers that live outside the code we can search: the standard library,
# third-party packages, and words that merely look like identifiers. Written down
# one by one, because the check's value is that an unlisted miss means something.
FOREIGN_IDENTIFIERS = frozenset(
    {
        # standard library and third-party
        "defaultdict",
        "freezegun",
        "litellm",
        "urlopen",
        "pytest",
        "pathlib",
        "sitecustomize",
        "pyproject",
        "pythonpath",
        "subprocess",
        "socket",
        "requests",
        "collections",
        "dataclass",
        "frozenset",
        # AppWorld internals referenced by name but not imported by us
        "SafetyGuard",
        "TestTracker",
        "batch_execute",
        "raise_if_failure",
        "find_one",
        "find_all",
        "by_ids",
        "by_id_or_raise",
        "prepare",
        "import_apis_module",
        "non_cached_lm_call",
        "generation_kwargs",
        "max_prompt_length",
        "simplified_react_code_agent",
        "plan_execute",
        "account_passwords",
        "access_token",
        "login_result",
        "playlists",
        "delete_account",
        "signup",
        "verify_account",
        "reset_password",
        "send_verification_code",
        "update_account_name",
        "settle_up",
        "reply_to_email",
        "move_file",
        "move_directory",
        "show_projects",
        "show_contact_relationships",
        "show_card_balance",
        "validate_card",
        "show_current_song",
        "show_song_queue",
        "show_volume",
        "set_volume",
        "show_group_balance",
        "check_authorization_to_group",
        "does_file_exist",
        "enlist_files",
        "add_payment_card",
        "api_descriptions",
        "api_doc",
        "required_apps",
        "required_apis",
        "api_calls",
        "compiled_solution",
        "num_api_calls",
        "num_apps",
        "num_apis",
        "allowed_apps",
        "metadata",
        "auth",
        "token",
        "transactions",
        "profile",
        "logout",
        "instructions",
        "reference",
        "solution",
        "generator",
        "minimal",
        "full",
        # configuration keys and record columns, not Python identifiers of ours
        "networkingMode",
        "wslconfig",
        "temperature",
        "max_tokens",
        "cost_per_token",
        "retry_after_n_seconds",
        "max_retries",
        "use_cache",
        "api_key",
        "reasoning",
        "thinking",
        "reasoning_content",
        "reasoning_tokens",
        "content",
        "password",
        "username",
        "app_name",
        "api_name",
        "method",
        "data",
        "supervisor",
        "unreachable_rows",
        "failure_patterns",
        "mining_grid",
        "skills",
        "coverage",
        "per_split",
        "card_tokens",
        "context_cost",
        "block_rate",
        "false_positive_rate",
        "expected_saving",
        "corpus_diversity",
        "precondition_gate",
        "fired_on",
        "local_axis",
        "local_axis_stopping_rule_off",
        "boundary_control",
        "entry",
        "state_change",
        "termination_reason",
        "result_status",
        "error_class",
        "step_ceiling",
        "library_id",
        "code_commit",
        "working_tree",
        "model_server_env",
        "serving_mode",
        "num_ctx_requested",
        "context_verified",
        "distinct_endpoints",
        "distinct_resources",
        "text_message_id",
        "phone_number",
        "note_id",
        "user_email",
        "no_progress",
        "agent_finished",
        "no_op_pass",
        "no_op_fail",
        "postcondition_misses",
        "discriminating_count",
        "own_app_condition",
        "body_write",
        "write_within_allowed_apps",
        "endpoint_identity",
        "model_hashes",
        "to_db_home_path",
        "relationships",
        "project_dict",
        "download_data",
        # Names quoted in the decision record as what something used to be
        # called. They must not resolve — that is the point of quoting them.
        "KaydedenAjan",
        "SahteHata",
        "SahteDunya",
        "kayit_vekili",
        "notlar",
        "konteyner_girisi",
        "soket_koprusu",
        # Provider, packaging and upstream configuration names
        "DefaultInboundAction",
        "Block",
        "uv_build",
        "pyyaml",
        "extra_body",
        "LanguageModel",
        "trimmed_messages",
        "granite",
        # Container runtime, kernel and shell output quoted from a terminal
        "crun",
        "dmesg",
        "Killed",
        "restore",
        # Model names from the family sweep
        "mistral",
        "cogito",
        "codegemma",
        "opencoder",
        # A SQL alias, a task-id format description, an AppWorld API name, and a
        # directory: all shaped like identifiers, none of them ours
        "hukum",
        "senaryo_varyant",
        "get_all_notes",
        # AppWorld app-module and engine names. They live in what `appworld install`
        # writes, not in the package, so they are declared rather than resolved.
        "InteractiveShellEmbed",
        "LICENSE",
        "_delete_account",
        "_validate_card",
        "default_timeout_seconds",
        "maybe_raise_exception",
        "request_payment_card_balance",
        "request_payment_card_validation",
        "scenario_goal_completion",
        "search_notes",
        "task_goal_completion",
        "test_challenge",
        "timeout_call",
        "mind",
        # Quoted precisely because it resolves nowhere — the sweep's own finding
        "integrity_check",
        "install",
        # A transitive dependency of AppWorld, named in K-129 because it is the
        # package whose absence exposed the wrong-environment install. It is in
        # the venv, not in our tree, so it resolves nowhere by construction.
        "munch",
        # Run id prefixes are added below from the protocol's own conditions
        # headings, so they are not listed here one by one.
    }
)


def declared_prefixes() -> set[str]:
    """Run id prefixes, read from the protocol's own conditions headings.

    A prefix is not a name in the tree — the manifest's primary key carries it
    and no module defines it — so the identifier check would call every one of
    them unresolved. They are read from the single place that declares them
    rather than listed by hand, which is the same rule the runs themselves
    follow (K-138).
    """
    from zihin.declared import HEADING, PROTOCOL

    return {m.group(2) for m in HEADING.finditer(PROTOCOL.read_text(encoding="utf-8"))}


def source_identifiers() -> set[str]:
    """Every name that appears in the Python we ship or the package we pin."""
    found: set[str] = set()
    # Only our own tree. The installed package was in this set once and the check
    # then gave a different answer locally than in CI: the Lint job installs the
    # package but not `appworld install`, so app-module names resolved on one
    # machine and not the other. A check whose answer depends on the environment
    # is the S-49 class; every AppWorld-side name is declared instead.
    roots = [REPOSITORY / "src", REPOSITORY / "scripts", REPOSITORY / "tests"]
    for root in roots:
        for path in root.rglob("*.py"):
            found.update(re.findall(r"\b\w+\b", path.read_text(encoding="utf-8", errors="ignore")))
    for path in (REPOSITORY / "config").rglob("*.yaml"):
        found.update(re.findall(r"\b\w+\b", path.read_text(encoding="utf-8")))
    # File stems count too: a document referring to `test_appworld_reset` is
    # naming a module, and a module's name lives in its path, not in its text.
    for root in roots:
        found.update(path.stem for path in root.rglob("*.py"))
    for path in (REPOSITORY / "scripts").rglob("*.sh"):
        found.update(re.findall(r"\b\w+\b", path.read_text(encoding="utf-8")))
    found.update(
        re.findall(r"\b\w+\b", (REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))
    )
    return found


def documents() -> list[pathlib.Path]:
    """The written documents, with generated episode logs left out.

    `experiments/` holds 17286 `.md` files and 17282 of them are episode
    transcripts under `outputs/`, written by a run rather than by a person.
    Scanning them cost about twelve seconds per check and could only produce
    findings about generated text. Measured, then excluded.
    """
    found = sorted((REPOSITORY / "docs").rglob("*.md"))
    found += [
        path
        for path in sorted((REPOSITORY / "experiments").rglob("*.md"))
        if "outputs" not in path.parts
    ]
    return found


def identifier_problems() -> list[str]:
    """Backticked identifiers in the documents that resolve nowhere in the code.

    **Why it exists.** Renaming touches the code and leaves the documents behind.
    Three stale identifiers were found by hand in one translation pass — a
    function renamed to `preflight`, another to `_made_no_progress`, and a
    document name that fell out of a comment entirely. The class had bitten three
    times and the anchor machinery to catch it was already here.

    **What an unresolved reference means.** Either the name was renamed and the
    document was not updated, or the name never existed. Both are worth knowing,
    and the check does not try to tell them apart.

    **Its limit.** Resolution is by presence, not by definition: a token that
    appears anywhere in the source counts as resolved, including inside a comment
    or a string. That accepts some stale references whose name survives elsewhere.
    Requiring a `def`/`class` site instead would reject every attribute and
    method we do not own, and the exception list would swallow the check.
    """
    known = source_identifiers() | declared_prefixes()
    problems = []
    for path in documents():
        text = path.read_text(encoding="utf-8")
        seen: set[str] = set()
        for span in CODE_SPAN.findall(FENCE.sub(" ", text)):
            token = " ".join(span.split())
            if DATA_KEY_SHAPE.search(token) or NOT_A_NAME.search(token):
                continue
            if not IDENTIFIER_SHAPE.match(token) or token in seen:
                continue
            seen.add(token)
            if token in FOREIGN_IDENTIFIERS or token in known:
                continue
            problems.append(f"{path.relative_to(REPOSITORY)}: `{token}` resolves nowhere")
    return problems


def main() -> None:
    problems = (
        naming_problems()
        + parity_problems()
        + readme_problems()
        + orphan_problems()
        + uncategorized_problems()
        + anchor_problems()
        + identifier_problems()
    )
    declared = len(BILINGUAL) + len(TURKISH_ONLY) + len(PENDING)
    if problems:
        print(f"{len(problems)} problems:")
        for line in problems:
            print(f"  {line}")
        sys.exit(1)
    print(f"documents declared: {declared}  bilingual: {len(BILINGUAL)}")
    print(f"Turkish-only, with a written reason: {len(TURKISH_ONLY)}")
    print(f"translation pending: {len(PENDING)}")
    for stem, reason in sorted(PENDING.items()):
        print(f"    {stem}: {reason}")
    anchored = sum(
        len(anchors((REPOSITORY / f"{stem}.tr.md").read_text(encoding="utf-8")))
        for stem in BILINGUAL
    )
    print(f"naming and parity: clean; {anchored} anchors carried through")


if __name__ == "__main__":
    main()
