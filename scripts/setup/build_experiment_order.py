"""Writes the experiment's task order, or checks the committed one (K-183).

The sample is the action stratum, taken from the threshold derivation's own
definition (`derive_pass_threshold.action_stratum`) rather than written again;
the seed is `base_seed` from `config/models.yaml`.

Usage:

    uv run python scripts/setup/build_experiment_order.py           # write
    uv run python scripts/setup/build_experiment_order.py --check   # compare
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.experiment import ORDER, order_document, render  # noqa: E402
from zihin.records import load_model_config  # noqa: E402


def action_stratum() -> list[str]:
    path = REPOSITORY / "scripts/setup/derive_pass_threshold.py"
    spec = importlib.util.spec_from_file_location("derive_pass_threshold", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["derive_pass_threshold"] = module
    spec.loader.exec_module(module)
    return [task for task, _ in module.action_stratum()]


def expected() -> str:
    seed = load_model_config(REPOSITORY / "config/models.yaml").base_seed
    return render(order_document(action_stratum(), seed))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    options = parser.parse_args()
    text = expected()
    path = REPOSITORY / ORDER
    if options.check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            sys.exit(f"{ORDER} is not what the sample and the seed give; regenerate it")
        print(f"{ORDER} matches the sample and the seed")
        return
    path.write_text(text, encoding="utf-8")
    print(f"wrote {ORDER}")


if __name__ == "__main__":
    main()
