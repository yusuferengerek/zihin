"""Thin layer facing the model server.

The server runs on the Windows side, this process runs inside WSL. Reading the
settings through `os.environ` yields empty values, so the server's own
configuration dump is read instead. The source is the server's declaration,
not the launcher's claim (K-37).
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from typing import Any

# `scripts/serve_models.ps1` starts the server logging into this file. The path
# is configuration rather than a constant: it carries a user name, and a hardcoded
# one makes REPRODUCE.md wrong for everyone except the machine it was written on.
MODEL_CONFIG = "config/models.yaml"


def server_log(path: str = MODEL_CONFIG) -> str:
    """Where the server writes its log. The environment first, configuration second.

    Read lazily rather than at import: the module is imported by tests that never
    touch the server, and a missing configuration file should fail where the value
    is used, not where the module is loaded.

    **Why the environment wins.** The path is a property of the machine the
    server runs on, not of the project. The configured value is right for the
    development machine, where the server runs on Windows and this code runs in
    WSL, and it is wrong everywhere else — it carries a Windows user directory.
    Measured the hard way on Colab: the manifest could not be written because
    the settings were read from a file that does not exist there, and the
    failure surfaced three layers away as "OLLAMA_FLASH_ATTENTION could not be
    read". `ZIHIN_SERVER_LOG` lets an environment say where its own server
    logs, which is the only place that knows.
    """
    from zihin.records import load_model_config

    return os.environ.get("ZIHIN_SERVER_LOG") or load_model_config(path).server_log


OLLAMA_SETTINGS = (
    "OLLAMA_CONTEXT_LENGTH",
    "OLLAMA_KV_CACHE_TYPE",
    "OLLAMA_FLASH_ATTENTION",
    "OLLAMA_KEEP_ALIVE",
    "OLLAMA_HOST",
)

GIB = 1024**3


def _post(base_url: str, path: str, body: dict, timeout: int = 600) -> dict:
    raw = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}", data=raw, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def loaded_models(base_url: str) -> list[dict]:
    with urllib.request.urlopen(f"{base_url}/api/ps", timeout=30) as response:
        return json.load(response).get("models") or []


def load_model(base_url: str, tag: str) -> float:
    """Loads the model into memory and returns the load time in seconds.

    The duration is measured with `/proc/uptime`: AppWorld freezes
    `time.monotonic` process-wide with freezegun, and this module can run in
    that same process.
    """
    started = kernel_clock()
    _post(
        base_url,
        "/api/chat",
        {
            "model": tag,
            "messages": [{"role": "user", "content": "ok"}],
            "stream": False,
            "options": {"num_predict": 1},
        },
    )
    return kernel_clock() - started


class ModelServerError(RuntimeError):
    """The server is not in the expected state."""


def count_tokens(base_url: str, tag: str, text: str) -> int:
    """Tokens in `text`, counted by the model's own tokenizer.

    `raw` skips the chat template, so the number is the text's own length and
    nothing the server wraps around it. This is a tokenizer query dressed as a
    generate call, because the server exposes no tokenizer endpoint.

    `num_predict` is **1, not 0**. Measured: 0 does not mean "generate nothing"
    here — the server ran on to forty thousand tokens on a three-line prompt.
    One token is the cheapest honest way to get `prompt_eval_count`, and the
    count is a property of the prompt, not of what follows it.

    The alternative — bytes divided by a constant, or somebody else's BPE — would
    be an estimate, and the budgets it would be compared against are the budgets
    of this model's context window.
    """
    if not text:
        return 0
    answer = _post(
        base_url,
        "/api/generate",
        {
            "model": tag,
            "prompt": text,
            "raw": True,
            "stream": False,
            "options": {"num_predict": 1, "temperature": 0},
        },
    )
    count = answer.get("prompt_eval_count")
    if not isinstance(count, int) or count <= 0:
        raise ModelServerError(
            f"the server reported no prompt token count for {tag}: {count!r}. "
            "A card measurement cannot rest on a guessed number."
        )
    return count


def count_chat_tokens(base_url: str, tag: str, messages: list[dict[str, str]]) -> int:
    """Tokens in a message list, chat template included.

    What reaches the model is not the prompt text but the messages wrapped in the
    template, and the wrapper costs tokens per message. The context budget is
    spent on the wrapped form, so that is what gets counted.
    """
    answer = _post(
        base_url,
        "/api/chat",
        {
            "model": tag,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 1, "temperature": 0},
        },
    )
    count = answer.get("prompt_eval_count")
    if not isinstance(count, int) or count <= 0:
        raise ModelServerError(f"the server reported no prompt token count for {tag}: {count!r}.")
    return count


def unload_model(base_url: str, tag: str, verify: bool = True, attempts: int = 5) -> None:
    """Unloads the model from memory and verifies that it is really gone.

    Verification is mandatory (the second condition of K-21). If unloading
    fails silently, the episode starts in the warm regime, the two regimes mix
    and nobody notices. The protocol has to be a measurement, not a claim.
    """
    _post(base_url, "/api/chat", {"model": tag, "messages": [], "keep_alive": 0}, timeout=120)
    if not verify:
        time.sleep(3)
        return
    for _ in range(attempts):
        time.sleep(1.5)
        if not any(m.get("name") == tag for m in loaded_models(base_url)):
            return
    raise ModelServerError(
        f"{tag} still appears loaded despite the unload request. "
        "The episode cannot be started in the cold regime."
    )


def is_loaded(base_url: str, tag: str) -> bool:
    return any(m.get("name") == tag for m in loaded_models(base_url))


def kernel_clock() -> float:
    with open("/proc/uptime", encoding="ascii") as handle:
        return float(handle.read().split()[0])


def server_settings(base_url: str, log_path: str | None = None) -> dict[str, Any]:
    """Settings read from the server's own configuration dump.

    The `OLLAMA_*` keys go into the manifest and the resume check inspects
    them; their names are fixed. The diagnostic keys around them are ours.
    """
    log_path = log_path or server_log()
    settings: dict[str, Any] = {"source": log_path}
    try:
        with open(log_path, encoding="utf-8", errors="replace") as handle:
            dump = next((line for line in handle if "server config" in line), "")
        for name in OLLAMA_SETTINGS:
            match = re.search(rf"{name}:(\S*?)[ \]]", dump)
            settings[name] = match.group(1) if match else None
    except OSError as error:
        settings["log_error"] = str(error)[:160]
        for name in OLLAMA_SETTINGS:
            settings[name] = None
    try:
        with urllib.request.urlopen(f"{base_url}/api/version", timeout=30) as response:
            settings["ollama_version"] = json.load(response).get("version")
    except Exception as error:
        settings["ollama_version_error"] = str(error)[:120]
    return settings


class SettingUnreadable(RuntimeError):
    """A server setting that the manifest needs could not be read."""


def setting_flag(settings: dict[str, Any], name: str) -> int:
    """A boolean server setting as 0/1, raising when the source is missing.

    Replaces the `1 if str(x) == "true" else 0` idiom, which is a silent
    default: when the setting cannot be read, `str(None) == "true"` is False and
    the manifest records 0, meaning "flash attention was off". That is a
    *plausible* value, so nothing looks wrong and the CHECK cannot object —
    0 is a legal value.

    The guard belongs at the source rather than at the scan that reads
    `model_server_env` afterwards. That scan does catch this case today, but
    then it is the only line of defence; here it becomes the second one.
    """
    value = settings.get(name)
    if value is None:
        # The source is named. Without it the message says which setting is
        # missing but not which file was searched, and the same sentence covers
        # "the log has no such line" and "the log is not there at all" - two
        # different problems with two different fixes (K-125).
        source = settings.get("source", "an unnamed log")
        why = settings.get("log_error")
        detail = f" The log could not be opened: {why}." if why else ""
        raise SettingUnreadable(
            f"{name} could not be read from the server dump at {source}.{detail} "
            "The manifest cannot be written with a default: a default would record "
            "a setting that was never observed. Set ZIHIN_SERVER_LOG to the file "
            "this environment's server writes to."
        )
    text = str(value).strip().lower()
    if text not in ("true", "false"):
        raise SettingUnreadable(f"{name} has an unexpected value: {value!r}")
    return 1 if text == "true" else 0


def vram_footprint(base_url: str, tag: str) -> dict[str, Any]:
    """The model's memory footprint. The source is Ollama's own report."""
    for m in loaded_models(base_url):
        if m.get("name") == tag:
            total = m.get("size") or 0
            vram = m.get("size_vram") or 0
            return {
                "total_bytes": total,
                "vram_bytes": vram,
                "total_gib": round(total / GIB, 3),
                "vram_gib": round(vram / GIB, 3),
                "fully_on_gpu": bool(total) and vram >= total,
                "context_window": m.get("context_length"),
            }
    return {"error": "the model does not appear to be loaded"}
