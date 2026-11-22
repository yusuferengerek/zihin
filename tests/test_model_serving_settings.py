"""Manifest fields derived from a server setting produce no silent default.

The fault class was measured; it did not occur, but it could have: the
`1 if str(x) == "true" else 0` idiom wrote 0 to the manifest whenever the setting
could not be read. Zero is a **valid** value, so the schema's CHECK cannot object
and the manifest says "flash attention was off". A setting that was never
observed ends up recorded.

The scan that runs over `model_server_env` catches this case today, but then it
is the only line of defence. The guard moved to the source and the scan became
the second line.
"""

from __future__ import annotations

import pytest

from zihin.model_server import SettingUnreadable, setting_flag

NAME = "OLLAMA_FLASH_ATTENTION"


def test_true_and_false_are_read():
    assert setting_flag({NAME: "true"}, NAME) == 1
    assert setting_flag({NAME: "false"}, NAME) == 0


def test_case_and_whitespace_do_not_matter():
    assert setting_flag({NAME: "TRUE"}, NAME) == 1
    assert setting_flag({NAME: " false "}, NAME) == 0


def test_missing_setting_raises_instead_of_defaulting_to_zero():
    """The real check. The old idiom returned 0 here in silence."""
    with pytest.raises(SettingUnreadable, match="could not be read"):
        setting_flag({}, NAME)
    with pytest.raises(SettingUnreadable, match="could not be read"):
        setting_flag({NAME: None}, NAME)


def test_unexpected_value_raises():
    with pytest.raises(SettingUnreadable, match="unexpected value"):
        setting_flag({NAME: "1"}, NAME)
    with pytest.raises(SettingUnreadable, match="unexpected value"):
        setting_flag({NAME: "evet"}, NAME)


def test_the_old_idiom_would_have_recorded_zero():
    """Mutation evidence: it shows what the old idiom did.

    This test keeps the fix's rationale in the code. The old idiom recorded an
    unreadable setting as "off" and no constraint could object.
    """
    ayarlar: dict = {NAME: None}
    old_pattern = 1 if str(ayarlar.get(NAME)) == "true" else 0
    assert old_pattern == 0, "the old idiom wrote 0 for an unreadable setting"
    with pytest.raises(SettingUnreadable):
        setting_flag(ayarlar, NAME)
