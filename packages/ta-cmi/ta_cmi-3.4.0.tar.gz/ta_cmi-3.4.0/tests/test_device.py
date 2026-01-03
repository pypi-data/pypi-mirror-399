from copy import deepcopy
from unittest.mock import patch

import pytest

from ta_cmi import ChannelType, Device, InvalidDeviceError
from ta_cmi.cmi_api import CMIAPI
from ta_cmi.cmi_channel import CMIChannel
from ta_cmi.const import DEVICES, SUPPORTED_PARAMS_FOR_DEVICE

from . import DEVICE_DATA_PACKAGE, sleep_mock

TEST_NODE_ID = "1"
TEST_HOST = "http://localhost"

TEST_API = CMIAPI(TEST_HOST, "user", "pass")

DUMMY_RESPONSE = {
    "Header": {"Version": 5, "Device": "87", "Timestamp": 1630764000},
    "Data": {
        "Inputs": [
            {"Number": 1, "AD": "A", "Value": {"Value": 92.2, "Unit": "1"}},
        ],
        "Outputs": [
            {"Number": 1, "AD": "D", "Value": {"Value": 1, "Unit": "43"}},
        ],
        "Logging Analog": [
            {"Number": 1, "AD": "A", "Value": {"Value": 12.2, "Unit": "1"}},
        ],
        "Logging Digital": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "DL-Bus": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "General": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Date": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Time": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Sun": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Electrical power": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Modbus": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Network Analog": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "Network Digital": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "MBus": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
        "KNX": [
            {"Number": 1, "AD": "D", "Value": {"Value": 0, "Unit": "43"}},
        ],
    },
    "Status": "OK",
    "Status code": 0,
}


@pytest.mark.asyncio
async def test_device_update_no_type():
    """Test the update function with no device type set."""

    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE) as device_data_mock:
        await device.update()

    # Request with default params
    device_data_mock.assert_called_once_with(TEST_NODE_ID, "I,O")

    assert device.device_id == DUMMY_RESPONSE["Header"]["Device"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "type_id, expected_params", SUPPORTED_PARAMS_FOR_DEVICE.items()
)
async def test_device_update_type_set(type_id, expected_params):
    """Test the update function with a device type set."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    device.device_id = type_id

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE) as device_data_mock:
        await device.update()

    if len(expected_params.split(",")) > 7:
        assert device_data_mock.call_count == 2
        return

    # Request with default params
    device_data_mock.assert_called_once_with(TEST_NODE_ID, expected_params)


@pytest.mark.asyncio
async def test_device_with_more_than_seven_parameters():
    TARGET_DELAY = 61

    async def custom_sleep_mock(delay: int):
        assert delay == TARGET_DELAY

    device = Device(TEST_NODE_ID, TEST_API, custom_sleep_mock, TARGET_DELAY)

    device.set_device_type("UVR16x2")

    DUMMY_RESPONSE_PART1 = deepcopy(DUMMY_RESPONSE)
    DUMMY_RESPONSE_PART2 = deepcopy(DUMMY_RESPONSE)

    DUMMY_RESPONSE_PART1["Data"]["Inputs"] = {}
    DUMMY_RESPONSE_PART1["Data"]["Outputs"] = {}

    with patch(
        DEVICE_DATA_PACKAGE, side_effect=[DUMMY_RESPONSE_PART1, DUMMY_RESPONSE_PART2]
    ) as device_data_mock:
        await device.update()

    calls = device_data_mock.mock_calls

    assert "I,O,D,Sg,Sd,St,Ss" in calls[0].args

    assert "La,Ld" in calls[1].args

    assert device.has_channel_type(ChannelType.INPUT)
    assert device.has_channel_type(ChannelType.OUTPUT)
    assert device.has_channel_type(ChannelType.ANALOG_LOGGING)


@pytest.mark.asyncio
async def test_device_update_data_parse():
    """Test the parsing of the received data."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE):
        await device.update()

    assert device.get_channels(ChannelType.INPUT) == {
        1: CMIChannel(ChannelType.INPUT, DUMMY_RESPONSE["Data"]["Inputs"][0])
    }
    assert device.get_channels(ChannelType.OUTPUT) == {
        1: CMIChannel(ChannelType.OUTPUT, DUMMY_RESPONSE["Data"]["Outputs"][0])
    }
    assert device.get_channels(ChannelType.ANALOG_LOGGING) == {
        1: CMIChannel(
            ChannelType.ANALOG_LOGGING, DUMMY_RESPONSE["Data"]["Logging Analog"][0]
        )
    }
    assert device.get_channels(ChannelType.DIGITAL_LOGGING) == {
        1: CMIChannel(
            ChannelType.DIGITAL_LOGGING, DUMMY_RESPONSE["Data"]["Logging Digital"][0]
        )
    }
    assert device.get_channels(ChannelType.DL_BUS) == {
        1: CMIChannel(ChannelType.DL_BUS, DUMMY_RESPONSE["Data"]["DL-Bus"][0])
    }

    assert device.get_channels(ChannelType.SYSTEM_VALUES_GENERAL) == {
        1: CMIChannel(
            ChannelType.SYSTEM_VALUES_GENERAL, DUMMY_RESPONSE["Data"]["General"][0]
        )
    }

    assert device.get_channels(ChannelType.SYSTEM_VALUES_TIME) == {
        1: CMIChannel(ChannelType.SYSTEM_VALUES_TIME, DUMMY_RESPONSE["Data"]["Time"][0])
    }

    assert device.get_channels(ChannelType.SYSTEM_VALUES_DATE) == {
        1: CMIChannel(ChannelType.SYSTEM_VALUES_DATE, DUMMY_RESPONSE["Data"]["Date"][0])
    }

    assert device.get_channels(ChannelType.SYSTEM_VALUES_SUN) == {
        1: CMIChannel(ChannelType.SYSTEM_VALUES_SUN, DUMMY_RESPONSE["Data"]["Sun"][0])
    }

    assert device.get_channels(ChannelType.SYSTEM_VALUES_E_POWER) == {
        1: CMIChannel(
            ChannelType.SYSTEM_VALUES_E_POWER,
            DUMMY_RESPONSE["Data"]["Electrical power"][0],
        )
    }

    assert device.get_channels(ChannelType.MODBUS) == {
        1: CMIChannel(ChannelType.MODBUS, DUMMY_RESPONSE["Data"]["Modbus"][0])
    }

    assert device.get_channels(ChannelType.NETWORK_ANALOG) == {
        1: CMIChannel(
            ChannelType.NETWORK_ANALOG, DUMMY_RESPONSE["Data"]["Network Analog"][0]
        )
    }

    assert device.get_channels(ChannelType.NETWORK_DIGITAL) == {
        1: CMIChannel(
            ChannelType.NETWORK_DIGITAL, DUMMY_RESPONSE["Data"]["Network Digital"][0]
        )
    }

    assert device.get_channels(ChannelType.MBUS) == {
        1: CMIChannel(ChannelType.MBUS, DUMMY_RESPONSE["Data"]["MBus"][0])
    }

    assert device.get_channels(ChannelType.KNX) == {
        1: CMIChannel(ChannelType.KNX, DUMMY_RESPONSE["Data"]["KNX"][0])
    }


@pytest.mark.asyncio
async def test_device_update_no_device_type():
    """Test the update function when no device type is given."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE) as device_data_mock:
        await device.update()

    device_data_mock.assert_called_once_with(TEST_NODE_ID, "I,O")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "type_id",
    {k: DEVICES[k] for k in set(DEVICES) - set(SUPPORTED_PARAMS_FOR_DEVICE)}.keys(),
)
async def test_device_update_default_params(type_id):
    """Test the update function with a device that supports only the default params."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    device.device_id = type_id

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE) as device_data_mock:
        await device.update()

    device_data_mock.assert_called_once_with(TEST_NODE_ID, "I,O")


@pytest.mark.parametrize("type_id, expected_type_name", DEVICES.items())
def test_get_device_type_with_known_types(type_id, expected_type_name):
    """Test the get device function with types that are known."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    device.device_id = type_id

    assert device.get_device_type() == expected_type_name


def test_get_device_type_with_unknown_type():
    """Test the get device function with an unknown type."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    assert device.get_device_type() == "Unknown"


@pytest.mark.parametrize(
    "type_name, expected_type_id", [(value, key) for key, value in DEVICES.items()]
)
def test_set_device_type_with_valid_type(type_name: str, expected_type_id: str):
    """Test the set device type function with a valid type."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    assert device.device_id == "00"

    device.set_device_type(type_name)

    assert device.device_id == expected_type_id


def test_set_device_type_with_invalid_type():
    """Test the set device type function with an invalid type."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    with pytest.raises(InvalidDeviceError) as exc_info:
        device.set_device_type("NoValidType")

    assert str(exc_info.value) == "Invalid device name: NoValidType"


@pytest.mark.asyncio
@pytest.mark.parametrize("type_id, expected_type_name", DEVICES.items())
async def test_fetch_type_valid_type(type_id, expected_type_name):
    """Test the fetch type function with a valid type."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    assert device.get_device_type() == "Unknown"

    response = deepcopy(DUMMY_RESPONSE)
    response["Header"]["Device"] = type_id

    with patch(DEVICE_DATA_PACKAGE, return_value=response) as device_data_mock:
        await device.fetch_type()

    device_data_mock.assert_called_once_with(TEST_NODE_ID, "I,O")

    assert device.get_device_type() == expected_type_name


@pytest.mark.asyncio
async def test_fetch_type_invalid_type():
    """Test the fetch type function with an invalid type."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    assert device.get_device_type() == "Unknown"

    response = deepcopy(DUMMY_RESPONSE)
    response["Header"]["Device"] = "00"

    with patch(
        DEVICE_DATA_PACKAGE, return_value=response
    ) as device_data_mock, pytest.raises(InvalidDeviceError) as exc_info:
        await device.fetch_type()

    device_data_mock.assert_called_once_with(TEST_NODE_ID, "I,O")

    assert str(exc_info.value) == "Invalid device id: 00"


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_type", list(ChannelType._member_map_.values()))
async def test_get_channels(channel_type):
    """Test the get channels function with all channel types."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    with patch(DEVICE_DATA_PACKAGE, return_value=DUMMY_RESPONSE):
        await device.update()

    channels = device.get_channels(channel_type)

    for ch in channels.values():
        assert ch.type == channel_type


def test_has_channel_type_exists():
    """Test the has channel type function with a type that was fetched."""
    device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    device._channels = {ChannelType.INPUT: {}}

    assert device.has_channel_type(ChannelType.INPUT)


def test_has_channel_type_non_exists():
    """Test the has channel type function with a type that was fetched."""
    device: Device = Device(TEST_NODE_ID, TEST_API, sleep_mock)

    device._channels = {ChannelType.INPUT: {}}

    assert not device.has_channel_type(ChannelType.OUTPUT)
