"""Refuses the run unless the environment was measured and the model is resident.

**Why a script and not a human checkpoint alone.** The notebook asks a person to
read the measurement before the run starts, and that stays. But an
instruction is not a guard: "Run all" is one click away, and the first Colab
attempt showed a person meeting an unexplained failure rather than an explained
one. This makes the checkpoint mechanical as well — the run cannot start without
a measurement that passed, whatever anyone clicks.

**What it checks, and why each one.**

*The file exists.* No measurement means nothing is known about this runtime.

*It is for this model.* A measurement of a different tag says nothing about the
one about to run.

*The model is fully resident.* A partially offloaded model runs a different
computation at a different speed, and the step ceiling was calibrated on a
resident one (§15.3).

Usage:

    uv run python scripts/setup/require_colab_environment.py && <the run>
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

REPORT = pathlib.Path(os.environ.get("ZIHIN_ENV_REPORT", "results/colab-ortam.json"))


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


def require_readable_settings() -> None:
    """The five settings the manifest needs, read from where the runner will read.

    **Why here and not in the prerequisite check.** That check runs before the
    server starts, so the log does not exist yet. This runs at the last point
    before the run, when the server has been up and has written its
    configuration dump — and it resolves the path exactly the way
    `record_run.py` will, so agreement here is agreement there.

    **What it prevents.** A run that dies on its first episode because the
    manifest cannot be written. Measured: the preflight episode failed with
    "OLLAMA_FLASH_ATTENTION could not be read from the server dump", three
    layers away from the cause, which was a configured log path belonging to
    another machine.
    """
    from zihin.model_server import OLLAMA_SETTINGS, server_log, server_settings

    path = server_log()
    settings = server_settings(os.environ.get("MODEL_SERVER_URL", ""), path)
    unreadable = [name for name in OLLAMA_SETTINGS if settings.get(name) is None]
    if not unreadable:
        print(f"server settings     : all {len(OLLAMA_SETTINGS)} readable from {path}")
        return
    why = settings.get("log_error")
    sys.exit(
        f"the manifest's server settings cannot be read from {path}: "
        f"{', '.join(unreadable)} missing."
        + (f" The log could not be opened: {why}." if why else "")
        + " The run would fail on its first episode, when the manifest is written."
        " Set ZIHIN_SERVER_LOG to the file this environment's server writes to;"
        " the configured value is the development machine's and is a fallback."
    )


def main() -> None:
    if not REPORT.exists():
        sys.exit(
            f"{REPORT} does not exist. Run the environment measurement first:\n"
            "    uv run python scripts/setup/measure_colab_environment.py --repeats 3\n"
            "No episode may start on an unmeasured runtime (protocol §15.3)."
        )
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    measured = report.get("model")
    if measured != MODEL:
        sys.exit(
            f"the measurement is for {measured!r} but the run is for {MODEL!r}. "
            "Re-run the measurement for the model about to run."
        )

    require_readable_settings()

    residency = report.get("residency") or {}
    state = residency.get("state")
    if state is None or state == "undetermined":
        sys.exit(
            "the model residency could not be DETERMINED "
            f"({residency.get('detail') or 'the report carries no state'}). "
            "This is refused, but it is not the same refusal as 'not resident': "
            "the answer is missing, not negative. Re-run the environment "
            "measurement with the server up, and read what it says about the "
            "model list and the load. Reporting an absent answer as a negative "
            "one is the mistake this wording exists to prevent (K-131)."
        )
    if state != "resident":
        fraction = residency.get("resident_fraction")
        sys.exit(
            f"the model is not fully resident (resident fraction {fraction}). "
            "The run must not start: a partially offloaded model runs a different "
            "computation at a different speed, and the step ceiling was calibrated "
            "on a resident one (protocol §15.3)."
        )

    gpu = report.get("gpu") or {}
    load = report.get("load_times") or {}
    print(
        f"environment measured: {gpu.get('name')} {gpu.get('vram_total_mib')} MiB, "
        f"{MODEL} fully resident, load median {load.get('median')} s"
    )

    # Comparability is not a gate: a run under a different configuration is still
    # a run. It is printed here, at the last point before the run starts,
    # because the label belongs on the result and the label is decided now.
    verdict = report.get("comparability") or {}
    state = verdict.get("state", "undetermined")
    facts = report.get("runtime_facts") or {}
    print(
        f"configuration       : layers {facts.get('layers_offloaded')}/"
        f"{facts.get('layers_total')}, flash {facts.get('flash_attention_effective')}, "
        f"KV {facts.get('kv_cache_type_effective')}"
    )
    print(f"comparability       : {state.upper()}")
    if state != "comparable":
        print(
            "  the result of this run is to be labelled NOT COMPARABLE with the "
            "local measurement. The run may proceed; the label is not optional."
        )


if __name__ == "__main__":
    main()
