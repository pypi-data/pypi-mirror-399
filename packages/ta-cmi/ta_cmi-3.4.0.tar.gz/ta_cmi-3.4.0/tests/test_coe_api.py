from unittest.mock import patch

import pytest

from ta_cmi import ChannelMode, CoEChannel
from ta_cmi.coe_api import CoEAPI, CoEServerConfig

from . import MAKE_GET_REQUEST_PACKAGE, MAKE_POST_REQUEST_PACKAGE

TEST_HOST = "http://localhost"

DATA_RESPONSE = {
    "digital": [{"value": True, "unit": 43}],
    "analog": [{"value": 34.4, "unit": 1}],
    "last_update_unix": 1680410064.03764,
    "last_update": "2023-04-01T12:00:00",
}

VERSION_RESPONSE = {"version": "1.1.0"}

CONFIG_RESPONSE = {"coe_version": 2}

api = CoEAPI(TEST_HOST)


@pytest.mark.asyncio
async def test_get_coe_data_with_data_response():
    """Test the get_coe_data with a valid data response."""
    can_id = 42

    with patch(MAKE_GET_REQUEST_PACKAGE, return_value=DATA_RESPONSE) as request_mock:
        result = await api.get_coe_data(can_id)

        assert result == DATA_RESPONSE

        request_mock.assert_called_once_with(f"{TEST_HOST}/receive/{can_id}")


@pytest.mark.asyncio
async def test_get_coe_data_with_empty_response():
    """Test the get_coe_data with a valid empty response."""
    can_id = 42

    with patch(MAKE_GET_REQUEST_PACKAGE, return_value={}) as request_mock:
        result = await api.get_coe_data(can_id)

        assert result is None

        request_mock.assert_called_once_with(f"{TEST_HOST}/receive/{can_id}")


@pytest.mark.asyncio
async def test_get_server_version_with_data_response():
    """Test the get_coe_version with a valid data response."""
    with patch(MAKE_GET_REQUEST_PACKAGE, return_value=VERSION_RESPONSE) as request_mock:
        result = await api.get_coe_version()

        assert result == VERSION_RESPONSE["version"]

        request_mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_server_version_with_empty_response():
    """Test the get_coe_version with a valid empty response."""
    with patch(MAKE_GET_REQUEST_PACKAGE, return_value={}) as request_mock:
        result = await api.get_coe_version()

        assert result is None

        request_mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_server_version():
    """Test the get_coe_version response."""
    with patch(MAKE_GET_REQUEST_PACKAGE, return_value=CONFIG_RESPONSE) as request_mock:
        result = await api.get_coe_server_config()

        server_config = CoEServerConfig(**CONFIG_RESPONSE)

        assert result == server_config

        request_mock.assert_called_once()


def test_check_channel_mode_valid_channels():
    """Test the check_channel_mode with only valid channels."""
    test_data = [
        CoEChannel(ChannelMode.DIGITAL, 0, 0, ""),
        CoEChannel(ChannelMode.DIGITAL, 0, 0, ""),
    ]

    result = api._check_channel_mode(ChannelMode.DIGITAL, test_data)

    assert result


def test_check_channel_mode_invalid_channels():
    """Test the check_channel_mode with invalid channels."""
    test_data = [
        CoEChannel(ChannelMode.ANALOG, 0, 0, ""),
        CoEChannel(ChannelMode.DIGITAL, 0, 0, ""),
    ]

    result = api._check_channel_mode(ChannelMode.ANALOG, test_data)

    assert not result


@pytest.mark.asyncio
async def test_send_digital_value():
    """Test the send_digital_value ."""

    expected_data = {
        "values": [
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
        "page": 1,
    }

    test_data = [CoEChannel(ChannelMode.DIGITAL, 0, 1, "")]

    test_data = test_data + [
        CoEChannel(ChannelMode.DIGITAL, 0, 0, "") for _ in range(15)
    ]

    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        await api.send_digital_values(test_data, True)

        request_mock.assert_called_once_with(f"{TEST_HOST}/send/digital", expected_data)


@pytest.mark.asyncio
async def test_send_analog_value():
    """Test the send_digital_value ."""

    expected_data = {
        "values": [
            {"value": 15.5, "unit": 46},
            {"value": 0, "unit": 0},
            {"value": 15.5, "unit": 46},
            {"value": 0, "unit": 0},
        ],
        "page": 1,
    }

    test_data = [
        CoEChannel(ChannelMode.ANALOG, 0, 15.5, "46"),
        CoEChannel(ChannelMode.ANALOG, 0, 0, "0"),
        CoEChannel(ChannelMode.ANALOG, 0, 15.5, "46"),
        CoEChannel(ChannelMode.ANALOG, 0, 0, "0"),
    ]

    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        await api.send_analog_values(test_data, 1)

        request_mock.assert_called_once_with(f"{TEST_HOST}/send/analog", expected_data)


@pytest.mark.asyncio
async def test_send_analog_value_v2_invalid_channel():
    """Test the send_analog_value_v2 with an invalid channel."""
    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.DIGITAL, 1, 1, "46")
        await api.send_analog_values_v2([test_channel])

        request_mock.assert_not_called()


@pytest.mark.asyncio
async def test_send_analog_value_v2_invalid_channel_index():
    """Test the send_analog_value_v2 with an invalid channel index."""
    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.ANALOG, 0, 1, "46")
        await api.send_analog_values_v2([test_channel])

        request_mock.assert_not_called()


@pytest.mark.asyncio
async def test_send_analog_value_v2_valid():
    """Test the send_analog_value_v2 with valid data."""
    expected_data = {"values": [{"channel": 1, "value": 16.4, "unit": "46"}]}

    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.ANALOG, 1, 16.4, "46")
        await api.send_analog_values_v2([test_channel])

        request_mock.assert_called_once_with(
            f"{TEST_HOST}/send/v2/analog", expected_data
        )


@pytest.mark.asyncio
async def test_send_digital_value_v2_invalid_channel():
    """Test the send_digital_value_v2 with an invalid channel."""
    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.ANALOG, 1, 1, "46")
        await api.send_digital_values_v2([test_channel])

        request_mock.assert_not_called()


@pytest.mark.asyncio
async def test_send_digital_value_v2_invalid_channel_index():
    """Test the send_digital_value_v2 with an invalid channel index."""
    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.DIGITAL, 0, 1, "46")
        await api.send_digital_values_v2([test_channel])

        request_mock.assert_not_called()


@pytest.mark.asyncio
async def test_send_digital_value_v2_valid():
    """Test the send_digital_value_v2 with valid data."""
    expected_data = {"values": [{"channel": 1, "value": 0, "unit": "46"}]}

    with patch(MAKE_POST_REQUEST_PACKAGE) as request_mock:
        test_channel = CoEChannel(ChannelMode.DIGITAL, 1, 0, "46")
        await api.send_digital_values_v2([test_channel])

        request_mock.assert_called_once_with(
            f"{TEST_HOST}/send/v2/digital", expected_data
        )
