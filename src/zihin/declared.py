"""The conditions a run was declared with, resolved from the run itself.

**Why this is a module and not a constant.** The model tag was written in six
places: twice in the notebook and four times as a default in a script. The
bootstrap ran before the notebook set the environment variable, fell back to its
own default, and pulled 14B; the prerequisite check fell back to the same default
and reported that twenty-nine questions were answered — correctly, and about the
wrong model. A check that runs correctly on the wrong subject is worse than one
that fails, because it reports success (K-138).

**The single source is the protocol's condition table**, and the run selects its
own row: the notebook's command carries the prefix, the prefix names a section,
and the section declares the values. Nothing has to agree with anything, because
nothing is written twice.
"""

from __future__ import annotations

import json
import pathlib
import re
import shlex

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL = REPOSITORY / "experiments/setup-protocol.tr.md"
NOTEBOOK = REPOSITORY / "experiments/colab/zihin-colab.ipynb"

# A conditions section names the run it declares: `### 16.2 Şartlar (`b32c`)`.
HEADING = re.compile(r"^### (\d+\.\d+) [^\n]*?\(`([a-z0-9]+)`\)[^\n]*$", re.M)
# The key is lowercased so `Komut` and `Command` reach the same name; the
# table is written in two languages and the reader should not care which.
ROW = re.compile(r"^\| `?([A-Za-zçğıöşü_]+)`? \| \*{0,2}`?([^`*|]+?)`?\*{0,2} \|", re.M)
# The floor makes an unread table visible. A regex that stops matching returns an
# empty table, and an empty table agrees with everything.
FLOOR = 8


# The experiment's runs carry this prefix as the first segment of their run id,
# and nothing else does (protocol section 19, K-178). The boundary is a prefix and
# not a commit because the code may change during the experiment - a fix stops a
# run and a new one resumes at a later commit - while the prefix does not.
EXPERIMENT_PREFIX = "dny"
# What belongs to the experiment but measures nothing - a preflight, a health
# check, a smoke run - carries this one instead. Every runner in this repository
# wrote its preflight under its own prefix (`<prefix>-onkontrol`); under `dny`
# that would put a health check inside the boundary.
EXPERIMENT_CONTROL_PREFIX = "dnyk"
# The one family marker this repository's runners write for a non-measurement
# episode. A `dny` run whose id carries it is a preflight inside the boundary.
NON_MEASUREMENT_MARKERS = ("onkontrol",)


# What an experiment run's command may not carry, and why. The dirty-tree gate
# is how a change to a measurement-defining path stops the run (A.9, K-177); this
# flag starts the run anyway and only writes "dirty" into the manifest (K-180).
EXPERIMENT_FORBIDDEN_FLAGS = {
    "--allow-dirty-tree": "it lets a run start on uncommitted measurement-defining changes",
}


def experiment_command_problems(prefix: str, command: list[str]) -> list[str]:
    """What the experiment's command carries that it may not (K-180).

    Matched the way argparse matches, not by equality: a long option may be given
    as any unambiguous prefix of itself, so `--allow` reaches `--allow-dirty-tree`
    in the runners that define it, and a check for the full spelling alone would
    let the abbreviation through.
    """
    if prefix != EXPERIMENT_PREFIX:
        return []
    problems = []
    for token in command:
        name = token.split("=", 1)[0]
        if not name.startswith("--") or len(name) <= 2:
            continue
        for flag, why in EXPERIMENT_FORBIDDEN_FLAGS.items():
            if flag.startswith(name):
                problems.append(f"the experiment's command carries {token} ({flag}): {why}")
    return problems


def experiment_run_problems(
    run_id: str,
    *,
    allow_dirty_tree: bool,
    named_condition: str | None,
    split: str,
    slice_number: int | None,
    session_id: str | None,
    path_change_accepted: bool,
) -> list[str]:
    """What the runner refuses before an episode starts, given its parsed options.

    **The parsed option, not the command line.** `check_declared_conditions`
    refuses the flag in the declared command (K-180); a runner called directly
    skips that check. Here argparse has already resolved every abbreviation, so
    `--allow`, `--allow-dirty` and `--allow-dirty-tree` all arrive as the one
    option they reach.

    Outside the experiment the three experiment options are refused instead: a
    slice or a session written for a run that is not in the experiment would put
    it in the experiment's tables.
    """
    first = run_id.split("-", 1)[0]
    if first != EXPERIMENT_PREFIX:
        stray = [
            name
            for name, given in (
                ("--slice", slice_number is not None),
                ("--session", session_id is not None),
                ("--path-change-accepted", path_change_accepted),
            )
            if given
        ]
        return [f"{name} belongs to an experiment run and {run_id} is not one" for name in stray]
    problems = []
    if allow_dirty_tree:
        problems.append(
            "the run carries --allow-dirty-tree: the dirty-tree gate is how a "
            "measurement-defining change stops the experiment (K-180)"
        )
    if not named_condition:
        problems.append(
            "the condition is not named with --condition: the experiment's episodes "
            "carry the declared condition names"
        )
    if split != "test_normal":
        problems.append(f"the split is {split!r}: the experiment runs the evaluation sample")
    if slice_number is None or slice_number < 1:
        problems.append("no slice: every experiment episode belongs to one (--slice)")
    if not session_id:
        problems.append("no session: every experiment episode names the one that ran it")
    return problems


class Undeclared(RuntimeError):
    """A run whose conditions nobody wrote down before it started."""


def declared_prefixes() -> set[str]:
    """Every prefix the protocol declares a conditions section for."""
    return {match.group(2) for match in HEADING.finditer(PROTOCOL.read_text(encoding="utf-8"))}


def run_command() -> list[str]:
    """The command the notebook actually runs, as a token list.

    **Found by what it names, not by which runner it is.** This used to look for
    `measure_band.py`, so the day the notebook moved to another runner the lookup
    silently returned nothing and every caller fell back to a default. The rule
    now is the one that cannot go stale: a run command is a shell line that names
    a prefix the protocol has declared a conditions section for.
    """
    prefixes = declared_prefixes()
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        source = "".join(cell.get("source") or [])
        for line in source.splitlines():
            stripped = line.lstrip()
            if not stripped.startswith("!") or "scripts/" not in stripped:
                continue
            # A shell line may chain a guard to the run with `&&`, because a
            # failing `!` line does NOT stop the next one in the same cell -
            # measured against IPython 9.16, where the refusing guard printed
            # and the runner started anyway. The declared command is one
            # segment of that line, so the segments are read separately.
            for segment in stripped[1:].split("&&"):
                tokens = shlex.split(segment)
                if any(token in prefixes for token in tokens):
                    return tokens
    return []


def run_prefix(command: list[str] | None = None) -> str:
    """The run id prefix: the first positional after the script."""
    command = run_command() if command is None else command
    if not command:
        raise Undeclared(
            f"no run command found in {NOTEBOOK}: no shell line there names a prefix "
            "the protocol declares a conditions section for"
        )
    for token in command:
        if token in declared_prefixes():
            return token
    seen_script = False
    skip_next = False
    for token in command:
        if skip_next:
            skip_next = False
            continue
        if token.endswith("measure_band.py"):
            seen_script = True
            continue
        if not seen_script:
            continue
        if token.startswith("-"):
            skip_next = token in ("--stop-threshold", "--max-output-tokens")
            continue
        return token
    raise Undeclared("the run command carries no prefix; the manifest's key needs one")


def section_for(prefix: str) -> tuple[str, str]:
    """(section number, its body) for the run with this prefix."""
    text = PROTOCOL.read_text(encoding="utf-8")
    matches = [(m.group(1), m.group(2), m.end()) for m in HEADING.finditer(text)]
    for number, declared_prefix, end in matches:
        if declared_prefix != prefix:
            continue
        following = [m.start() for m in re.finditer(r"^### ", text[end:], re.M)]
        stop = end + following[0] if following else len(text)
        return number, text[end:stop]
    named = ", ".join(f"{n} ({p})" for n, p, _ in matches) or "none"
    raise Undeclared(
        f"no conditions section declares the prefix {prefix!r}. Sections found: "
        f"{named}. A run without a declaration is a run whose conditions nobody "
        "wrote down before it started."
    )


def conditions(prefix: str | None = None) -> tuple[str, dict[str, str]]:
    """(section number, field -> declared value) for the run about to happen."""
    prefix = run_prefix() if prefix is None else prefix
    number, body = section_for(prefix)
    # The table's head is dropped structurally, not by matching the word it
    # contains: a markdown head is the row above the `|---|` separator, and that
    # is true in both languages. Naming it would put a Turkish word in the code
    # and a second place for the table's shape to live.
    separator = body.find("\n|--")
    if separator != -1:
        body = body[body.index("\n", separator + 1) :]
    found = {name.lower(): value.strip() for name, value in ROW.findall(body)}
    if len(found) < FLOOR:
        raise Undeclared(
            f"only {len(found)} field(s) parsed out of section {number}, and the "
            f"floor is {FLOOR}. The table's shape changed and this parser no longer "
            "reads it. Nothing is compared: an empty comparison is not an agreement."
        )
    return number, found


def declared_field(name: str, prefix: str | None = None) -> str:
    """One declared field, by name. Raises rather than defaulting.

    The same rule as `declared_model`: a default here would be a second place
    the value lives. Callers that can carry on without the field catch
    `Undeclared` and say so; they do not substitute a number of their own.
    """
    _, table = conditions(prefix)
    value = table.get(name.lower())
    if not value:
        raise Undeclared(f"the conditions table declares no {name}")
    return value.strip().strip("`*")


def declared_model(prefix: str | None = None) -> str:
    """The model tag the run was declared with. No default, ever.

    A default here would be a second place the name lives, which is the whole
    defect this module exists to remove.
    """
    _, table = conditions(prefix)
    tag = table.get("model_tag")
    if not tag:
        raise Undeclared("the conditions table declares no model_tag")
    return tag


def declared_command(prefix: str | None = None) -> list[str]:
    """The run command the conditions table declares, as a token list.

    A local run has no notebook cell to read, so the command itself is declared
    next to the values it carries. That keeps one source rather than two: the
    runner executes what the table says, and the check reads the same row.
    """
    _, table = conditions(prefix)
    line = table.get("komut") or table.get("command")
    if not line:
        raise Undeclared(
            f"the conditions table for {prefix or 'this run'} declares no command "
            "row. A notebook-driven run keeps its command in the notebook cell, so "
            "run this check with no argument and it will read the command from "
            "there. A local run has no cell, and its command belongs in the table."
        )
    return shlex.split(line)
