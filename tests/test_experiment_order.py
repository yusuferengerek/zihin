"""The experiment's task order is declared, reproducible and not chosen as it goes (K-183)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from zihin.experiment import ORDER, OrderError, load_order, order_digest, task_order

REPOSITORY = Path(__file__).resolve().parents[1]


def _builder():
    path = REPOSITORY / "scripts/setup/build_experiment_order.py"
    spec = importlib.util.spec_from_file_location("build_experiment_order", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_committed_order_is_what_its_own_key_gives() -> None:
    document = load_order()
    assert document["seed"] == 123
    assert document["tasks"] == len(document["order"]) == 104


def test_regenerating_the_order_from_the_sample_and_the_seed_gives_the_committed_file() -> None:
    committed = (REPOSITORY / ORDER).read_text(encoding="utf-8")
    assert _builder().expected() == committed


def test_the_order_is_neither_the_listing_nor_another_seeds() -> None:
    order = load_order()["order"]
    assert order != sorted(order)
    assert task_order(order, 124) != order


def test_an_order_that_was_rearranged_is_refused(tmp_path) -> None:
    document = json.loads((REPOSITORY / ORDER).read_text(encoding="utf-8"))
    document["order"][0], document["order"][1] = document["order"][1], document["order"][0]
    document["digest"] = order_digest(document["order"])
    (tmp_path / "results").mkdir()
    (tmp_path / ORDER).write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(OrderError, match="is not what"):
        load_order(tmp_path)


def test_an_order_whose_digest_is_stale_is_refused(tmp_path) -> None:
    document = json.loads((REPOSITORY / ORDER).read_text(encoding="utf-8"))
    document["digest"] = "0" * 64
    (tmp_path / "results").mkdir()
    (tmp_path / ORDER).write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(OrderError, match="digest"):
        load_order(tmp_path)
