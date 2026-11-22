"""Verifies that the package can be imported from the installed environment.

CI's fourth check ("import and build") is built on this: if the package is not
installed or the src layout is broken, this test fails.
"""

from __future__ import annotations


def test_package_imports() -> None:
    import zihin

    assert zihin.__version__ == "0.1.0"


def test_top_level_interface_is_exposed() -> None:
    import zihin

    assert callable(zihin.load_condition_config)
    assert hasattr(zihin, "ConditionConfig")
