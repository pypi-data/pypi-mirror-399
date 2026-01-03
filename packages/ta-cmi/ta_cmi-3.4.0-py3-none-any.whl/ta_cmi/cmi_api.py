import json
from typing import Any, Dict, List

from aiohttp import BasicAuth, ClientSession

from .api import API, ApiError
from .const import _LOGGER


class CMIAPI(API):
    """Class to perform CMI API requests."""

    DEVICE_LIST = "/INCLUDE/can_nodes.cgi?_=1"
    DEVICE_DATA = "/INCLUDE/api.cgi?jsonparam=PARAMS&jsonnode=ID"

    def __init__(
        self, host: str, username: str, password: str, session: ClientSession = None
    ) -> None:
        """Initialize."""
        super().__init__(session, BasicAuth(username, password))

        self.host = host

    async def get_devices_ids(self) -> List[str]:
        """Get all id from devices connected to the CMI"""
        _LOGGER.debug("Receive list of nodes from C.M.I")

        url: str = f"{self.host}{self.DEVICE_LIST}"
        data: str = await self._make_request_no_json(url)

        _LOGGER.debug("Received list of nodes from C.M.I: %s", data)

        raw_ids: List[str] = data.split(";")

        return [x for x in raw_ids if len(x) != 0]

    async def get_device_data(self, node_id: str, parameter: str) -> Dict[str, Any]:
        """Get data from device."""
        _LOGGER.debug(
            "Make request to device %s with parameters: %s",
            node_id,
            parameter,
        )

        url: str = f"{self.host}{self.DEVICE_DATA.replace('PARAMS', parameter).replace('ID', node_id)}"

        return await self._make_data_request(url)

    async def _make_data_request(self, url: str) -> Dict[str, Any]:
        """Retrieve data from CMI API."""
        data = await self._make_request_get(url)

        STATUS_CODE = "Status code"

        if data[STATUS_CODE] != 0:
            _LOGGER.debug("Failed response received: %s", json.dumps(data))

        if data[STATUS_CODE] == 0:
            return data
        elif data[STATUS_CODE] == 1:
            raise ApiError("Node not available")
        elif data[STATUS_CODE] == 2:
            raise ApiError(
                "Failure during the CAN-request/parameter not available for this device"
            )
        elif data[STATUS_CODE] == 4:
            raise RateLimitError("Only one request per minute is permitted")
        elif data[STATUS_CODE] == 5:
            raise ApiError("Device not supported")
        elif data[STATUS_CODE] == 7:
            raise ApiError("CAN Bus is busy")
        else:
            raise ApiError("Unknown error")


class RateLimitError(Exception):
    """Triggered when the rate limit is reached."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
