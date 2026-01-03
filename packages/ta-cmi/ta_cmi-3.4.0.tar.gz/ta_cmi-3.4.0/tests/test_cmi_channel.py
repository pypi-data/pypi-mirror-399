import pytest

from ta_cmi.cmi_channel import CMIChannel
from ta_cmi.const import UNITS_DE, UNITS_EN, ChannelType, Languages


@pytest.mark.parametrize("unit_number, expected_unit", UNITS_DE.items())
def test_units_german(unit_number: str, expected_unit: str):
    """Test the translation from a unit number to a string with german units."""
    test = {"Number": 1, "AD": "A", "Value": {"Value": 0, "Unit": unit_number}}

    channel: CMIChannel = CMIChannel(ChannelType.INPUT, test)

    assert channel.get_unit(Languages.DE) == expected_unit


@pytest.mark.parametrize("unit_number, expected_unit", UNITS_EN.items())
def test_units_english(unit_number: str, expected_unit: str):
    """Test the translation from a unit number to a string with english units."""
    test = {"Number": 1, "AD": "A", "Value": {"Value": 0, "Unit": unit_number}}

    channel: CMIChannel = CMIChannel(ChannelType.INPUT, test)

    assert channel.get_unit(Languages.EN) == expected_unit
