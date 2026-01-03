from typing import Any, Dict
from unittest.mock import patch

import pytest

from ta_cmi import RateLimitError
from ta_cmi.api import ApiError
from ta_cmi.cmi_api import CMIAPI

from . import MAKE_GET_REQUEST_PACKAGE

TEST_HOST = "http://localhost"
TEST_USER = "user"
TEST_PASS = "pass"
TEST_NODE_ID = "1"
TEST_PARAMS = "I,O"


def generate_response(status_code: int) -> Dict[str, Any]:
    """Generate a response with the provided status code."""
    return {
        "Header": {"Version": 6, "Device": "8F", "Timestamp": 1670960961},
        "Data": {"DL-Bus": []},
        "Status": "OK",
        "Status code": status_code,
    }


def generate_device_data_url() -> str:
    """Generate the device data url."""
    return (
        f"{TEST_HOST}/INCLUDE/api.cgi?jsonparam={TEST_PARAMS}&jsonnode={TEST_NODE_ID}"
    )


api = CMIAPI(TEST_HOST, TEST_USER, TEST_PASS)


@pytest.mark.asyncio
async def test_get_devices_ids_to_list_conversion():
    """Test the get_devices_ids method with a valid api response."""
    with patch(
        "ta_cmi.api.API._make_request_no_json", return_value="1;2;"
    ) as request_mock:
        ids = await api.get_devices_ids()

        assert ids == ["1", "2"]

        request_mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_device_data_successful_request():
    """Test the get_device_data function with a successful request."""
    sample_response: Dict[str, Any] = generate_response(0)

    with patch(MAKE_GET_REQUEST_PACKAGE, return_value=sample_response) as request_mock:
        result = await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert result == sample_response

        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_node_not_available():
    """Test the get_device_data function with a successful request but the cmi status code is 1."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(1)
    ) as request_mock:
        with pytest.raises(ApiError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert str(exc_info.value) == "Node not available"
        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_fail_can_bus():
    """Test the get_device_data function with a successful request but the cmi status code is 2."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(2)
    ) as request_mock:
        with pytest.raises(ApiError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert (
            str(exc_info.value)
            == "Failure during the CAN-request/parameter not available for this device"
        )
        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_rate_limit():
    """Test the get_device_data function with a successful request but the cmi status code is 4."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(4)
    ) as request_mock:
        with pytest.raises(RateLimitError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert str(exc_info.value) == "Only one request per minute is permitted"
        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_unsupported_device():
    """Test the get_device_data function with a successful request but the cmi status code is 5."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(5)
    ) as request_mock:
        with pytest.raises(ApiError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert str(exc_info.value) == "Device not supported"
        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_busy_can_bus():
    """Test the get_device_data function with a successful request but the cmi status code is 7."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(7)
    ) as request_mock:
        with pytest.raises(ApiError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert str(exc_info.value) == "CAN Bus is busy"
        request_mock.assert_called_once_with(generate_device_data_url())


@pytest.mark.asyncio
async def test_get_device_data_unknown_status_code():
    """Test the get_device_data function with a successful request but the cmi status code is unknown."""
    with patch(
        MAKE_GET_REQUEST_PACKAGE, return_value=generate_response(55)
    ) as request_mock:
        with pytest.raises(ApiError) as exc_info:
            await api.get_device_data(TEST_NODE_ID, TEST_PARAMS)

        assert str(exc_info.value) == "Unknown error"
        request_mock.assert_called_once_with(generate_device_data_url())
