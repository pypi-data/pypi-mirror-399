from unittest.mock import patch

import pytest

from ta_cmi import CMI

TEST_HOST = "http://localhost"


@pytest.mark.asyncio
async def test_get_devices_create_all_provided_devices():
    """Fetch create devices that are provided."""
    cmi: CMI = CMI(TEST_HOST, "user", "pass")

    with patch(
        "ta_cmi.cmi_api.CMIAPI.get_devices_ids", return_value=["2", "3", "4"]
    ) as device_mock:
        devices = await cmi.get_devices()

        device_mock.assert_called_once()

        assert len(devices) == 3

        assert devices[0].id == "2"
        assert devices[1].id == "3"
        assert devices[2].id == "4"
