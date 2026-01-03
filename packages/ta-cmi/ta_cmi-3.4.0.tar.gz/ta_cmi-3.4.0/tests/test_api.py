import json

import pytest
from aioresponses import aioresponses

from ta_cmi.api import API, ApiError, InvalidCredentialsError


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


TEST_URL = "http://localhost"

DUMMY_RESPONSE = {"message": "Ok"}
DUMMY_BODY = {"data": "value"}

api = API()


@pytest.mark.asyncio
async def test_make_request_no_json_successful_request_get(mock_aioresponse):
    """Test the _make_request_no_json method with a valid response and get method."""
    mock_aioresponse.get(TEST_URL, status=200, payload=DUMMY_RESPONSE)

    result = await api._make_request_no_json(TEST_URL)

    assert result == json.dumps(DUMMY_RESPONSE)


@pytest.mark.asyncio
async def test_make_request_no_json_successful_request_post(mock_aioresponse):
    """Test the _make_request_no_json method with a valid response and post method."""
    mock_aioresponse.post(TEST_URL, status=200, payload=DUMMY_RESPONSE)

    result = await api._make_request_no_json(TEST_URL, method="POST")

    assert result == json.dumps(DUMMY_RESPONSE)


@pytest.mark.asyncio
async def test_make_request_no_json_successful_empty_request(mock_aioresponse):
    """Test the _make_request_no_json method with a valid empty response."""
    mock_aioresponse.get(TEST_URL, status=204)

    result = await api._make_request_no_json(TEST_URL)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_make_request_no_json_unauthorized_request(mock_aioresponse):
    """Test the _make_request_no_json method with an unauthorized response."""
    mock_aioresponse.get(TEST_URL, status=401)

    with pytest.raises(InvalidCredentialsError) as exc_info:
        await api._make_request_no_json(TEST_URL)

    assert str(exc_info.value) == "Invalid credentials"


@pytest.mark.asyncio
async def test_make_request_no_json_invalid_request(mock_aioresponse):
    """Test the _make_request_no_json method with an invalid response."""
    mock_aioresponse.get(TEST_URL, status=404)

    with pytest.raises(ApiError) as exc_info:
        await api._make_request_no_json(TEST_URL)

    assert str(exc_info.value) == "Invalid response from localhost: 404"


@pytest.mark.asyncio
async def test_make_request_get_json_conversion(mock_aioresponse):
    """Test the _make_request_get method with a raw json response."""
    mock_aioresponse.get(TEST_URL, status=200, payload=DUMMY_RESPONSE)

    result = await api._make_request_get(TEST_URL)

    assert result == DUMMY_RESPONSE


@pytest.mark.asyncio
async def test_make_request_get_json_successful_empty_request(mock_aioresponse):
    """Test the _make_request_get method with a valid empty response."""
    mock_aioresponse.get(TEST_URL, status=204)

    result = await api._make_request_get(TEST_URL)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_make_request_post_json_conversion(mock_aioresponse):
    """Test the _make_request_post method with a raw json response."""
    mock_aioresponse.post(TEST_URL, status=200, payload=DUMMY_RESPONSE)

    result = await api._make_request_post(TEST_URL, DUMMY_BODY)

    mock_aioresponse.assert_called_once_with(
        TEST_URL, method="POST", json=DUMMY_BODY, auth=None
    )

    assert result == DUMMY_RESPONSE


@pytest.mark.asyncio
async def test_make_request_post_json_successful_empty_request(mock_aioresponse):
    """Test the _make_request_post method with a valid empty response."""
    mock_aioresponse.post(TEST_URL, status=204)

    result = await api._make_request_post(TEST_URL, DUMMY_BODY)

    mock_aioresponse.assert_called_once_with(
        TEST_URL, method="POST", json=DUMMY_BODY, auth=None
    )

    assert len(result) == 0
