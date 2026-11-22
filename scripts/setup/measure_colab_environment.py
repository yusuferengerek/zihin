"""Measures the Colab runtime before any episode is spent.

**Why before.** Three numbers decide whether the run means anything, and all
three are properties of the machine rather than of the model:

*The GPU and its memory* say whether the 14B at Q4_K_M can be held at all.

*Whether the model sits entirely in VRAM.* Locally all three sizes were measured
fully resident (29/29 layers at 7B). A partially offloaded model runs a different
computation at a different speed, and a step ceiling calibrated on a resident
model would then be measuring the disk.

*Model load time.* K-21's cold regime rests on the locally measured 2.72 / 3.01 /
3.55 seconds. Colab's disk is not that disk. If loading costs ten times more, the
regime's price changes and the protocol has to say so before the run rather than
after.

**It calls the production helpers.** `load_model` and `vram_footprint` are the
same functions the runners use. A measurement that reimplements what it measures
produces two right answers and nothing to choose between them (setup protocol §6).

Usage:

    uv run python scripts/setup/measure_colab_environment.py
    uv run python scripts/setup/measure_colab_environment.py --repeats 5
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import re
import shutil
import statistics
import subprocess
import sys
import urllib.parse
import urllib.request

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.model_server import (  # noqa: E402
    load_model,
    server_log,
    server_settings,
    unload_model,
    vram_footprint,
)

BASE_URL = os.environ.get("MODEL_SERVER_URL", "http://127.0.0.1:11434")


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
OUTPUT = pathlib.Path(os.environ.get("ZIHIN_OUTPUT", "results/colab-ortam.json"))
# One resolution for every reader, and it is the runner's. This script used to
# read `ZIHIN_SERVER_LOG` with its own default while `record_run.py` resolved the
# path through `server_log()` and the configuration. Both worked here and they
# disagreed on Colab: the measurement read the runtime's log and the runner
# looked for a Windows path that does not exist there, so the environment
# measurement passed and the run failed on the same file (K-135).
SERVER_LOG = server_log()

# The lines llama.cpp writes about what it actually did. Taken from a real load
# on the development machine rather than from documentation, so the shapes are
# the ones the parser will meet:
#
#   load_tensors: offloaded 29/29 layers to GPU
#   llama_context: flash_attn    = enabled
#   llama_kv_cache: size = 476.00 MiB ( 32768 cells, 28 layers, ... ),
#                   K (q8_0): 238.00 MiB, V (q8_0): 238.00 MiB
#
# and, from the command line the server logs when it starts llama-server:
#
#   --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on
LAYERS = re.compile(r"offloaded (\d+)/(\d+) layers to GPU")
FLASH_EFFECTIVE = re.compile(r"flash_attn\s*=\s*(\w+)")
KV_EFFECTIVE = re.compile(r"K \(([\w.]+)\):.*?V \(([\w.]+)\):")
KV_SIZE = re.compile(r"llama_kv_cache: size =\s*([\d.]+) MiB")
FLASH_REQUESTED = re.compile(r"--flash-attn (\w+)")
KV_REQUESTED = re.compile(r"--cache-type-k ([\w.]+)")


def gpu() -> dict:
    """What the driver reports. Absent GPU is a failure, not a missing field."""
    try:
        raw = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"nvidia-smi did not answer ({error!r}). This runtime has no GPU.")
    name, total, used, driver = (part.strip() for part in raw.split(",")[:4])
    return {
        "name": name,
        "vram_total_mib": int(total),
        "vram_used_mib": int(used),
        "driver": driver,
    }


def require_server() -> None:
    """Stops with a sentence if the model server is not there.

    Measured the hard way. Ollama had not been installed at all, and this
    script's first server call raised a urllib traceback naming a socket and a
    refused connection — a symptom shared by "not installed", "installed but not
    running", "running on another port" and "running but not answering". Those
    four questions had to be asked by hand afterwards; they are asked here
    instead and each prints its own answer (K-125).

    It runs before anything else touches the server, so an absent server costs a
    sentence rather than a stack trace.
    """
    binary = shutil.which("ollama")
    processes = subprocess.run(
        ["pgrep", "-a", "ollama"], capture_output=True, text=True
    ).stdout.strip()

    answered = False
    detail = ""
    names: list[str] = []
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/tags", timeout=5) as answer:
            tags = json.load(answer)
        answered = True
        names = sorted(entry.get("name", "?") for entry in tags.get("models", []))
    except Exception as error:
        detail = f"{type(error).__name__}: {error}"

    here = urllib.parse.urlsplit(BASE_URL).hostname in {"127.0.0.1", "localhost", "::1"}
    where = "this host" if here else "this host, but the server is elsewhere"
    print(f"ollama binary    : {binary or 'NOT ON PATH'}  ({where})")
    print(f"ollama processes : {len(processes.splitlines()) if processes else 0}  ({where})")
    print(f"model list       : {'answered' if answered else 'no answer'} at {BASE_URL}")
    if answered:
        print(f"models present   : {names or 'none'}")

    if not answered:
        if not here:
            # Measured on the development machine, where Ollama runs on Windows
            # and this code runs in WSL: the binary and the process are on the
            # other side of a boundary, so both questions answer "no" while the
            # server is perfectly healthy. A check whose answer depends on the
            # environment is not a check (K-117), so where the address is not
            # loopback the two local questions are reported and not interpreted.
            what = (
                f"the address is not loopback, so whether ollama is installed on "
                f"this host says nothing about it. Check the host serving "
                f"{BASE_URL}, and whether the port is reachable from here."
            )
        elif not binary:
            what = (
                "ollama is not on PATH, so it was never installed. Step F of "
                "scripts/colab_bootstrap.sh did not run or did not finish; run the "
                "bootstrap cell again and read where it stops, it names the step."
            )
        elif not processes:
            what = (
                "ollama is installed but no process is running. Start it with "
                "nohup ollama serve > /tmp/zihin-ollama.log 2>&1 & and read that "
                "log if it exits again."
            )
        else:
            what = (
                "ollama is installed and a process is running, but the port is not "
                "answering. Read /tmp/zihin-ollama.log, and check that OLLAMA_HOST "
                f"is the address this script is asking: {BASE_URL}."
            )
        print()
        sys.exit(f"the model server did not answer ({detail}). {what}")

    if MODEL not in names:
        print()
        sys.exit(
            f"the server answers but {MODEL} is not in its model list. "
            f"Present: {names or 'none'}. Pull it with `ollama pull {MODEL}`, or "
            "check that OLLAMA_MODELS points at the cache the bootstrap filled."
        )


def residency() -> dict:
    """Whether the model is held entirely in VRAM, asked while it is loaded.

    **Two defects were measured here, and both produced the same wrong answer.**

    The first was the question's timing: the footprint was asked of a server that
    had never been told to load the model. On a fresh runtime `/api/ps` is empty,
    so the answer was about nothing. The model is loaded here first, which also
    makes the question the right one — not "is it loaded now" but "does it fit".

    The second was worse and silent. `vram_footprint` maps Ollama's `size` and
    `size_vram` onto `total_bytes` and `vram_bytes`; this function read `size`
    and `size_vram` off the mapped dictionary, where they do not exist. So the
    total was always zero, `fully_resident` was always False and the fraction was
    always None — on every machine, for every model, under every condition.
    Measured against a live server holding a model with size == size_vram: the
    footprint said `fully_on_gpu: true` and this function said False.

    **Undetermined is not the same as no.** When the server reports nothing the
    state is `undetermined`, and the guard that reads this must not turn that
    into "not resident" (K-131).
    """
    footprint = vram_footprint(BASE_URL, MODEL)
    if "error" in footprint:
        # One retry after an explicit load: the model may simply not be held yet.
        try:
            load_model(BASE_URL, MODEL)
        except Exception as error:
            footprint["load_error"] = str(error)[:160]
        footprint = vram_footprint(BASE_URL, MODEL)

    if "error" in footprint:
        return {
            "state": "undetermined",
            "fully_resident": None,
            "resident_fraction": None,
            "detail": footprint.get("error"),
        }

    total = footprint.get("total_bytes") or 0
    in_vram = footprint.get("vram_bytes") or 0
    if not total:
        return {
            "state": "undetermined",
            "fully_resident": None,
            "resident_fraction": None,
            "detail": "the server reported a footprint with no total size",
            **footprint,
        }
    fraction = round(in_vram / total, 4)
    return {
        "state": "resident" if in_vram >= total else "partial",
        "fully_resident": in_vram >= total,
        "resident_fraction": fraction,
        **footprint,
    }


def runtime_facts(log_path: str | None = None) -> dict:
    """What the server actually did with the settings it was given.

    **Why asking the settings is not enough.** `server_settings` reads what was
    requested: `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`. Whether the
    hardware honoured them is a different question, and on a GPU that does not
    support a q8_0 KV cache the request is accepted and the cache is kept in
    f16 instead — twice the memory, and an arithmetic that no longer holds. A
    configuration that was requested but not applied means the environment is
    running a different measurement, not a slower one.

    The lines come from llama.cpp's own output, parsed here rather than believed:

        load_tensors: offloaded 29/29 layers to GPU
        llama_context: flash_attn    = enabled
        llama_kv_cache: size = 476.00 MiB ( ... ), K (q8_0): ..., V (q8_0): ...

    and the requested side from the command line the server logs when it starts
    llama-server (`--cache-type-k`, `--flash-attn`).
    """
    # No default path: `server_log()` is the one resolution, and a default here
    # would be a second answer to the same question (K-135, K-138).
    log_path = log_path or server_log()
    facts: dict = {"source": log_path}
    try:
        with open(log_path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError as error:
        facts["log_error"] = str(error)[:160]
        return facts

    layers = LAYERS.findall(text)
    if layers:
        offloaded, total = layers[-1]
        facts["layers_offloaded"] = int(offloaded)
        facts["layers_total"] = int(total)
        facts["all_layers_on_gpu"] = int(offloaded) >= int(total)

    effective_flash = FLASH_EFFECTIVE.findall(text)
    if effective_flash:
        facts["flash_attention_effective"] = effective_flash[-1]

    kv = KV_EFFECTIVE.findall(text)
    if kv:
        key_type, value_type = kv[-1]
        facts["kv_cache_type_effective"] = key_type
        facts["kv_cache_type_effective_value"] = value_type

    size = KV_SIZE.findall(text)
    if size:
        facts["kv_cache_mib"] = float(size[-1])

    requested_flash = FLASH_REQUESTED.findall(text)
    if requested_flash:
        facts["flash_attention_requested"] = requested_flash[-1]
    requested_kv = KV_REQUESTED.findall(text)
    if requested_kv:
        facts["kv_cache_type_requested"] = requested_kv[-1]

    # The comparison is the point. Both sides are reported so a disagreement can
    # be read without recomputing it, and neither is asserted when it is absent.
    asked = facts.get("kv_cache_type_requested")
    got = facts.get("kv_cache_type_effective")
    if asked and got:
        facts["kv_cache_type_honoured"] = asked == got
    asked_flash = facts.get("flash_attention_requested")
    got_flash = facts.get("flash_attention_effective")
    if asked_flash and got_flash:
        facts["flash_attention_honoured"] = (asked_flash in ("on", "1", "true")) == (
            got_flash == "enabled"
        )
    return facts


def load_times(repeats: int) -> dict:
    """Cold load duration, unloaded and verified before each timing.

    Unloading is verified rather than assumed: `unload_model` asks the server
    again and raises if the model is still listed. A timing taken over a model
    that never left memory is not a cold load, and it would silently make the
    regime look cheap.
    """
    seconds = []
    for _ in range(repeats):
        unload_model(BASE_URL, MODEL, verify=True)
        seconds.append(round(load_model(BASE_URL, MODEL), 3))
    return {
        "repeats": repeats,
        "seconds": seconds,
        "median": round(statistics.median(seconds), 3),
        "min": min(seconds),
        "max": max(seconds),
        # The local reference this is compared against, so the comparison is in
        # the file rather than in someone's memory.
        "local_reference_median_seconds": {"1.5b": 2.72, "3b": 3.01, "7b": 3.55},
    }


def comparability(facts: dict) -> dict:
    """Is this environment running the configuration the local one ran.

    **Why it is a separate verdict.** The model fitting in VRAM and the model
    running *our* configuration are different questions, and only the second one
    decides whether a number from here can be put next to a number from there.
    If the GPU does not honour a q8_0 KV cache the request is accepted silently
    and the cache is kept in f16: the run still happens, but it is a different
    measurement, not a slower one.

    **Three states, not two.** A fact that could not be read makes the verdict
    `undetermined`, never `differs`. Reporting an absent answer as a negative one
    is the mistake K-131 exists to prevent, and this function is one of the
    places that could make it.

    The local reference these are compared against, measured on the development
    machine at 7B: 29/29 layers, flash attention requested `on` and effective
    `enabled`, KV requested `q8_0` and effective `q8_0`, 952 MiB of KV cache.
    """
    checks = {
        "all layers on the GPU": facts.get("all_layers_on_gpu"),
        "KV cache type honoured": facts.get("kv_cache_type_honoured"),
        "flash attention honoured": facts.get("flash_attention_honoured"),
    }
    missing = [name for name, value in checks.items() if value is None]
    differing = [name for name, value in checks.items() if value is False]
    if differing:
        state = "differs"
    elif missing:
        state = "undetermined"
    else:
        state = "comparable"
    return {
        "state": state,
        "checks": checks,
        "unreadable": missing,
        "differing": differing,
        "local_reference": {
            "layers": "29/29 at 7B",
            "flash_attention": "requested on, effective enabled",
            "kv_cache_type": "requested q8_0, effective q8_0",
            "kv_cache_mib_at_7b": 952.0,
        },
        "meaning": {
            "comparable": (
                "the environment ran the locked configuration; numbers can sit "
                "beside the local ones"
            ),
            "differs": (
                "the environment ran a DIFFERENT configuration; the run may proceed "
                "but the result is labelled not comparable with the local measurement"
            ),
            "undetermined": ("a fact could not be read; this is not the same as a difference"),
        }[state],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    arguments = parser.parse_args()

    require_server()

    report = {
        "model": MODEL,
        "base_url": BASE_URL,
        "host": {"platform": platform.platform(), "python": platform.python_version()},
        "gpu": gpu(),
        "server_settings": server_settings(BASE_URL, SERVER_LOG),
    }
    report["residency"] = residency()
    report["load_times"] = load_times(arguments.repeats)
    # Read after the loads, so the log carries the lines a load writes.
    report["runtime_facts"] = runtime_facts(SERVER_LOG)
    report["comparability"] = comparability(report["runtime_facts"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    g, r, t = report["gpu"], report["residency"], report["load_times"]
    print(f"GPU              : {g['name']}  {g['vram_total_mib']} MiB  driver {g['driver']}")
    print(f"model            : {MODEL}")
    print(f"fully in VRAM    : {r['fully_resident']}  (resident {r['resident_fraction']})")
    print(f"load time median : {t['median']} s   range {t['min']}–{t['max']} s")
    print(f"local reference  : 7B was {t['local_reference_median_seconds']['7b']} s")

    f, c = report["runtime_facts"], report["comparability"]
    print("--- what the server actually ran, read from its own log")
    print(
        f"layers on GPU    : {f.get('layers_offloaded')}/{f.get('layers_total')}"
        "  (local: 29/29 at 7B)"
    )
    print(
        f"flash attention  : requested {f.get('flash_attention_requested')}, "
        f"effective {f.get('flash_attention_effective')}"
    )
    print(
        f"KV cache type    : requested {f.get('kv_cache_type_requested')}, "
        f"effective {f.get('kv_cache_type_effective')}"
    )
    print(f"KV cache size    : {f.get('kv_cache_mib')} MiB  (local: 952.0 MiB at 7B)")
    print(f"comparability    : {c['state'].upper()}")
    print(f"  meaning        : {c['meaning']}")
    if c["unreadable"]:
        print(f"  unreadable     : {', '.join(c['unreadable'])}")
    if c["differing"]:
        print(f"  DIFFERING      : {', '.join(c['differing'])}")
    print(f"written          : {OUTPUT}")

    # K-131 applies to the producer as well: an undetermined residency is not a
    # negative one, and the two do not share a sentence.
    if r["state"] == "undetermined":
        print(
            "\nRESIDENCY UNDETERMINED. The run must not start, but not because the "
            f"answer is no — the answer is missing ({r.get('detail')}). "
            "Read the model list and the load above."
        )
        sys.exit(1)
    if r["state"] != "resident":
        print(
            "\nNOT FULLY RESIDENT. The run must not start: a partially offloaded model "
            "runs a different computation at a different speed, and the step ceiling "
            "was calibrated on a resident one."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
