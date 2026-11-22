"""Do the declared conditions and the conditions the run will use agree.

**Why this exists, and it is the third time.** A condition has drifted from its
declaration three times: twice because it was written relatively ("the same as
the boundary control"), and once because it was written absolutely but in a
different place from where the runner reads it. The protocol declared
`max_output_tokens` 400 and `no_progress_limit` 15; the runner read
`config/recording.yaml`, which carries 4000 and 40; and the notebook's
`--stop-threshold 15` went to a script that had no such flag and dropped it in
silence. Everything was absolute and everything disagreed (S-58, K-136).

**What it compares.** The value column of the conditions table the run's own
prefix names, against the value the run will actually use: the flags in the run
command first, `config/recording.yaml` and `config/models.yaml` second.

**Where the parsing lives.** In `zihin.declared`, not here. This script had its
own copy of the table regex once, and the copy fell behind the module's — the
same defect it exists to catch, in itself (K-138).

Usage:

    uv run python scripts/check_declared_conditions.py          # the notebook's run
    uv run python scripts/check_declared_conditions.py b7l      # a named run
"""

from __future__ import annotations

import pathlib
import sys

import yaml

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
RECORD_RUN = REPOSITORY / "scripts/record_run.py"
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.declared import (  # noqa: E402
    EXPERIMENT_PREFIX,
    NOTEBOOK,
    Undeclared,
    conditions,
    declared_command,
    experiment_command_problems,
    run_command,
    run_prefix,
    section_for,
)

RECORDING = REPOSITORY / "config/recording.yaml"
MODELS = REPOSITORY / "config/models.yaml"

# The declared name on the left, how the run resolves it on the right. A field
# with no resolver is reported rather than skipped: an unchecked declaration is
# what this guard exists to prevent.
FLAG_FOR = {
    "no_progress_limit": "--stop-threshold",
    "max_output_tokens": "--max-output-tokens",
}
CONFIG_FOR = {
    "no_progress_limit": (RECORDING, "no_progress_limit"),
    "max_output_tokens": (RECORDING, "max_output_tokens"),
    "temperature": (MODELS, "temperature"),
    "base_seed": (MODELS, "base_seed"),
    "seed_count": (MODELS, "seed_count"),
    "num_ctx_requested": (MODELS, "num_ctx"),
    "kv_cache_type": (MODELS, "kv_cache_type"),
    "flash_attention": (MODELS, "flash_attention"),
}
# Rows that describe the run rather than name a condition value.
# Rows that describe the run rather than name a condition value. The table's
# head is dropped by `zihin.declared`, structurally, so it is not listed here.
NOT_A_CONDITION = {"komut", "command"}


def from_flags(command: list[str], flag: str) -> str | None:
    if flag in command:
        index = command.index(flag)
        if index + 1 < len(command):
            return command[index + 1]
    return None


def shield_mode_of_the_runner() -> str:
    """What the runner will record, read from the runner rather than assumed.

    `record_run.py` mounts the shield with `mount_for_task`'s default, and
    `ShieldMode` has no `off` member at all — only `shadow` and `enforce`. So a
    declaration of `off` names a state this runner cannot reach, which is a
    measurement decision and not a mechanical repair.
    """
    import inspect

    from zihin.shield_mount import mount_for_task

    default = inspect.signature(mount_for_task).parameters["mode"].default
    return str(getattr(default, "value", default))


def condition_of_the_runner(prefix: str) -> str | None:
    """What condition the run will record, read from the runner that starts it.

    `record_run.py` writes `CONDITION` and only leaves `baseline` when a card
    flag is passed. So the question is whether the runner named by this prefix's
    command passes one; the answer is in that runner's source, not in a habit.
    """
    import re

    # `declared_command` returns the command as a list of words. A
    # notebook-driven run keeps its command in the notebook cell rather than in
    # the table, so that is where the fallback looks.
    try:
        words = declared_command(prefix) or []
    except Exception:  # noqa: BLE001 - a table with no command row says nothing here
        words = []
    if not words:
        # A notebook-driven run keeps its command in the notebook cell rather than
        # in the table. It is only this run's command if it names this prefix;
        # reading another run's command would answer about the wrong run, which is
        # the defect this whole resolver exists to avoid.
        try:
            candidate = run_command()
        except Exception:  # noqa: BLE001 - no command anywhere is an answer of its own
            candidate = []
        words = candidate if prefix in candidate else []
    command = " ".join(words)
    found = re.search(r"scripts/[\w/]+\.py", command)
    if not found:
        return None
    runner = REPOSITORY / found.group(0)
    if not runner.exists():
        return None
    text = runner.read_text(encoding="utf-8")
    if "--cards" in text or "--irrelevant-cards" in text or "--condition" in text:
        return None  # it can carry cards; which one it uses is not a constant
    default = re.search(r'^CONDITION = "([^"]+)"', RECORD_RUN.read_text(encoding="utf-8"), re.M)
    return default.group(1) if default else None


def _load(relative: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        pathlib.Path(relative).stem, REPOSITORY / relative
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _step_ceiling(want: str) -> tuple[str, str]:
    import re

    driver = _load("scripts/run_experiment.py")
    numbers = (driver.MULTIPLIER, driver.FLOOR_CEILING, driver.CEILING_CAP)
    declared = tuple(int(n) for n in re.findall(r"\d+", want))
    got = want if declared == numbers else "multiplier {}, floor {}, cap {}".format(*numbers)
    return got, "scripts/run_experiment.py, MULTIPLIER / FLOOR_CEILING / CEILING_CAP"


def _saving_floor(want: str) -> tuple[str, str]:
    from zihin.slots import EXPERIMENT_CONDITIONS, condition_config

    floors = {condition_config(c).min_expected_saving for c in EXPERIMENT_CONDITIONS}
    got = str(floors.pop()) if len(floors) == 1 else f"differs across conditions: {sorted(floors)}"
    return got, "config/<condition>.yaml:retrieval.min_expected_saving, all five"


def _from_sets(key: str):
    def resolve(want: str) -> tuple[str, str]:
        from zihin.experiment import SETS, load_sets

        return str(load_sets()[key]), f"{SETS}:{key}"

    return resolve


def _from_order(key: str):
    def resolve(want: str) -> tuple[str, str]:
        from zihin.experiment import ORDER, OrderError, load_order

        try:
            return str(load_order()[key]), f"{ORDER}:{key}"
        except OrderError as error:
            return f"unreadable: {error}", ORDER

    return resolve


def _phase_one(want: str) -> tuple[str, str]:
    from zihin.experiment import PHASE_ONE
    from zihin.slots import EXPERIMENT_CONDITIONS

    unknown = [c for c in PHASE_ONE if c not in EXPERIMENT_CONDITIONS]
    got = ", ".join(PHASE_ONE) if not unknown else f"not conditions the runner builds: {unknown}"
    return got, "zihin.experiment.PHASE_ONE, which the driver runs"


def _runtime(want: str) -> tuple[str, str]:
    """The runtime every selection line tells the reader to pick."""
    import re

    notebook = _load("scripts/check_colab_notebook.py")
    texts = ["\n".join(text for _, kind, text in notebook.cells() if kind == "markdown")]
    texts += [(REPOSITORY / name).read_text(encoding="utf-8") for name in notebook.ALSO_SELECTS]
    named = {
        runtime
        for text in texts
        for line in notebook.SELECTION.findall(text)
        for runtime in notebook.RUNTIMES
        if re.search(r"\b" + re.escape(runtime) + r"\b", line)
    }
    got = want if named == {want} else ", ".join(sorted(named)) or "no selection line"
    return got, "the runtime selection lines of the notebook and experiments/colab/README.md"


def _model_file(want: str) -> tuple[str, str]:
    """One source: the bootstrap reads this row for the pull it announces."""
    bootstrap = (REPOSITORY / "scripts/colab_bootstrap.sh").read_text(encoding="utf-8")
    reads = 'declared_field("model_file_gb")' in bootstrap
    got = want if reads else "the bootstrap does not read this row"
    return got, "one source: scripts/colab_bootstrap.sh reads this row"


# The experiment's own rows, each with the place its value actually lives. Every
# row of the experiment's table must resolve: an unchecked row there fails the
# check rather than being listed (K-187).
RESOLVERS = {
    "step_ceiling": _step_ceiling,
    "min_expected_saving": _saving_floor,
    "library_id": _from_sets("library_id"),
    "index_id": _from_sets("index_id"),
    "covered_tasks": _from_sets("covered"),
    "task_set": _from_order("tasks"),
    "task_order_seed": _from_order("seed"),
    "task_order": _from_order("digest"),
    "conditions": _phase_one,
    "runtime": _runtime,
    "model_file_gb": _model_file,
}


def unread_rows(prefix: str) -> list[str]:
    """Table rows the parser did not read: a key with a space is silently skipped."""
    import re

    _, body = section_for(prefix)
    _, table = conditions(prefix)
    separator = body.find("\n|--")
    rows = []
    for line in body[body.index("\n", separator + 1) + 1 :].splitlines():
        if not line.startswith("|"):
            break
        key = line.split("|")[1].strip().strip("`*")
        rows.append(key)
    return [key for key in rows if key.lower() not in table and not re.fullmatch(r"-+", key)]


def normalise(value: str) -> str:
    """Turkish decimal commas and English points describe the same number."""
    text = str(value).strip().strip("`*").replace(",", ".")
    if text.lower() in ("true", "1"):
        return "1"
    if text.lower() in ("false", "0"):
        return "0"
    try:
        number = float(text)
    except ValueError:
        return text
    return str(int(number)) if number == int(number) else str(number)


def main() -> None:
    asked = [a for a in sys.argv[1:] if not a.startswith("-")]
    try:
        if asked:
            # A named run: the command is declared in the table itself, because
            # a local run has no notebook cell to read it from.
            prefix = asked[0]
            number, table = conditions(prefix)
            command = declared_command(prefix)
        else:
            command = run_command()
            if not command:
                sys.exit(f"no measure_band.py invocation found in {NOTEBOOK}")
            prefix = run_prefix(command)
            number, table = conditions(prefix)
    except Undeclared as error:
        sys.exit(str(error))

    # Asked before any value is compared: an experiment command that may start on
    # a dirty tree is refused whatever its values say (K-180).
    forbidden = experiment_command_problems(prefix, command)
    if forbidden:
        print(f"run prefix: {prefix}")
        for line in forbidden:
            print(f"  - {line}")
        sys.exit(
            "REFUSED: the experiment's command carries a flag it may not. The dirty-tree "
            "gate is how a change stops the run (A.9, K-177, K-180)."
        )

    problems: list[str] = []
    unchecked: list[str] = []
    print(f"run prefix               : {prefix}")
    print(f"declared in section {number:<5}: {len(table)} field(s)")
    print(f"the run command          : {' '.join(command)}")
    print()

    for name, want in sorted(table.items()):
        if name in NOT_A_CONDITION:
            continue
        source = None
        got = None
        flag = FLAG_FOR.get(name)
        if flag:
            got = from_flags(command, flag)
            source = f"the run command, {flag}"
        if got is None and name == "model_tag":
            # Nothing to compare, and that is the point: every reader resolves
            # the model from this table, so there is no second place to drift.
            got, source = want, "one source: no other place names the model"
        if got is None and name == "serving_mode":
            hosted = table.get("model_tag", "").startswith("openrouter/")
            got, source = ("hosted" if hosted else "local"), "derived from the model tag"
        if got is None and name in ("koşul", "condition"):
            got = condition_of_the_runner(prefix)
            source = "the runner named in the command passes no card flag"
        if got is None and name == "shield_mode":
            got = shield_mode_of_the_runner()
            source = "record_run.py, the mount default in mount_for_task"
        if got is None and name in RESOLVERS and prefix == EXPERIMENT_PREFIX:
            got, source = RESOLVERS[name](want)
        if got is None and name in CONFIG_FOR:
            path, key = CONFIG_FOR[name]
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if key in loaded:
                got = str(loaded[key])
                source = f"{path.relative_to(REPOSITORY)}:{key}"
        if got is None:
            unchecked.append(name)
            print(f"  ??   {name:22} declared {want!r}, no resolver here")
            continue
        agree = normalise(got) == normalise(want)
        print(
            f"  {'ok  ' if agree else 'DIFF'} {name:22} declared {want!r}, "
            f"run uses {got!r}  ({source})"
        )
        if not agree:
            problems.append(
                f"{name}: the protocol declares {want!r}, the run would use {got!r} from {source}"
            )

    print()
    if unchecked:
        print(f"not resolvable here: {', '.join(unchecked)}")
    if prefix == EXPERIMENT_PREFIX:
        # The experiment's table has no row that goes unread or unchecked (K-187).
        problems += [f"{name}: declared and not compared with any source" for name in unchecked]
        problems += [f"{key}: a row the parser does not read" for key in unread_rows(prefix)]
    if not problems:
        print("declared conditions and the run agree")
        return
    print(f"{len(problems)} CONDITION(S) DISAGREE:")
    for line in problems:
        print(f"  - {line}")
    print(
        "\nA condition that is declared in one place and read from another is not a "
        "condition. Either pass it where the run reads it, or change the declaration "
        "deliberately (S-58, K-136)."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
