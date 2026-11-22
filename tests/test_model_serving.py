"""Is the server really running with the settings in the configuration?

The configuration itself is checked in `test_model_config.py`. The tests here
connect to the server and verify that the settings are actually applied.

The distinction matters. 32768 being written in the configuration does not mean
the server uses 32768; that is K-37's entire rationale.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import pytest

from zihin.records import load_model_config

pytestmark = pytest.mark.model_server

CONFIG = load_model_config("config/models.yaml")


def _base() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        pytest.skip("MODEL_SERVER_URL is not defined.")
    return address.rstrip("/")


def _request(body: dict, path: str, zaman_asimi: int = 600) -> dict:
    ham = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        f"{_base()}{path}", data=ham, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(r, timeout=zaman_asimi) as response:
        return json.load(response)


def _yuklu() -> list[dict]:
    with urllib.request.urlopen(f"{_base()}/api/ps", timeout=30) as response:
        return json.load(response).get("models") or []


@pytest.fixture(scope="module")
def server():
    base = _base()
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=10) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError) as error:
        pytest.skip(f"the Ollama server could not be reached: {error}")


def test_all_three_models_are_present(server):
    mevcut = {m["name"] for m in server.get("models", [])}
    missing = [tag for tag in CONFIG.models if tag not in mevcut]
    assert not missing, f"model not downloaded: {missing}"


@pytest.mark.parametrize("tag", CONFIG.models)
def test_effective_context_window_matches_the_design(server, tag):
    """K-37's first condition, per model.

    If the server restarts without the environment variable, the window silently
    falls back to 4096. What is checked is the value read from the server, not the
    value in the configuration.
    """
    _request(
        {
            "model": tag,
            "messages": [{"role": "user", "content": "ok"}],
            "stream": False,
            "options": {"num_predict": 1},
        },
        "/api/chat",
    )
    window = next((m.get("context_length") for m in _yuklu() if m.get("name") == tag), None)
    assert window == CONFIG.num_ctx, (
        f"{tag}: effective context window {window}, expected {CONFIG.num_ctx}. "
        "The server may have been started without OLLAMA_CONTEXT_LENGTH."
    )


@pytest.mark.parametrize("tag", CONFIG.models)
def test_model_fits_entirely_in_vram(server, tag):
    """The 7B fitting in 8 GB is what keeps the scale axis' third point alive."""
    _request(
        {
            "model": tag,
            "messages": [{"role": "user", "content": "ok"}],
            "stream": False,
            "options": {"num_predict": 1},
        },
        "/api/chat",
    )
    record = next((m for m in _yuklu() if m.get("name") == tag), None)
    assert record is not None, f"{tag} does not appear to be loaded"
    total = record.get("size") or 0
    vram = record.get("size_vram") or 0
    assert total > 0
    assert vram >= total, (
        f"{tag}: {vram} bytes in VRAM, {total} bytes total. The model has partly "
        "spilled to the CPU."
    )


def test_seed_controls_generation(server):
    """If the seed does not get through, the seed axis dies.

    The same seed must give the same output and a different seed a different one.
    Without the second half the check proves nothing: a low temperature can fix
    the output too.
    """
    tag = CONFIG.models[0]
    istem = "Name three sorting algorithms and say which is stable."

    def uret(seed: int) -> str:
        response = _request(
            {
                "model": tag,
                "messages": [{"role": "user", "content": istem}],
                "stream": False,
                "options": {
                    "temperature": CONFIG.temperature,
                    "seed": seed,
                    "num_predict": 120,
                },
            },
            "/api/chat",
        )
        return response["message"]["content"]

    # The first call warms the model up; the cold and warm regimes give different
    # output (S-13), so the comparison is made in the warm state.
    uret(CONFIG.base_seed)
    bir = uret(CONFIG.base_seed)
    two = uret(CONFIG.base_seed)
    distinct = uret(CONFIG.base_seed + 977)

    assert bir == two, "the same seed does not give the same output"
    assert bir != distinct, (
        "a different seed gives the same output too; what fixes it is not the seed"
    )
