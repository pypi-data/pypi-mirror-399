from dataclasses import dataclass
from typing import Any, Dict

from aiohttp import ClientSession

from .api import API
from .coe_channel import CoEChannel
from .const import _LOGGER, ChannelMode


@dataclass
class CoEServerConfig:
    coe_version: int


class CoEAPI(API):
    """Class to perform API requests to the CoE Addon."""

    COE_VERSION = "/version"
    COE_CONFIG = "/config"
    COE_DATA = "/receive/{id}"
    COE_SEND_ANALOG = "/send/analog"
    COE_SEND_DIGITAL = "/send/digital"
    COE_SEND_ANALOG_V2 = "/send/v2/analog"
    COE_SEND_DIGITAL_V2 = "/send/v2/digital"

    DIGITAL_VALUES_PER_PAGE = 16
    ANALOG_VALUES_PER_PAGE = 4

    V2_MIN_CHANNEL_INDEX = 1

    def __init__(self, host: str, session: ClientSession = None) -> None:
        """Initialize."""
        super().__init__(session)

        self.host = host

    async def get_coe_data(self, can_id: int) -> Dict[str, Any] | None:
        """Get the CoE data."""
        url = f"{self.host}{self.COE_DATA.replace('{id}', str(can_id))}"

        _LOGGER.debug("Receive data from CoE server: %s", url)

        data = await self._make_request_get(url)

        _LOGGER.debug("Received data from CoE server: %s", data)

        if len(data) == 0:
            return None

        return data

    async def get_coe_version(self) -> str | None:
        """Get the version of the CoE server."""
        url = f"{self.host}{self.COE_VERSION}"

        _LOGGER.debug("Receive current version from CoE server: %s", url)

        data = await self._make_request_get(url)

        _LOGGER.debug("Received version from CoE server: %s", data)

        if len(data) == 0:
            return None

        return data.get("version", None)

    async def get_coe_server_config(self) -> CoEServerConfig:
        """Get the CoE config from the server."""
        url = f"{self.host}{self.COE_CONFIG}"

        _LOGGER.debug("Receive current config from CoE server: %s", url)

        data = await self._make_request_get(url)

        _LOGGER.debug("Received version from CoE server: %s", data)

        return CoEServerConfig(coe_version=data.get("coe_version", 0))

    @staticmethod
    def _check_channel_mode(
        target_mode: ChannelMode, channel_to_check: list[CoEChannel]
    ) -> bool:
        """Check if the channel type equals the target."""
        for channel in channel_to_check:
            if channel.mode != target_mode:
                _LOGGER.warning(
                    f"Channel has wrong mode. Expected mode: {target_mode}, actual mode: {channel.mode}"
                )
                return False

        return True

    @staticmethod
    def _check_array_length(array: list, target_size: int) -> bool:
        """Check if a list has the required length."""
        if len(array) != target_size:
            _LOGGER.warning(
                f"List has wrong length. Expected length: {target_size}, actual length: {len(array)}"
            )
            return False

        return True

    @staticmethod
    def _check_analog_page_size(provided: int) -> bool:
        """Check if the page is in the right number range."""
        if not (0 < provided < 9):
            _LOGGER.warning(
                f"Page is not in the expected range. Expected range: 0 < page < 9, actual value: {provided}"
            )
            return False

        return True

    @staticmethod
    def _convert_analog_channel_to_dict(channel: CoEChannel) -> dict[str, Any]:
        """Convert a analog coe channel to a dict."""
        return {"value": channel.value, "unit": int(channel.unit)}

    async def send_analog_values(self, channels: list[CoEChannel], page: int):
        """Send analog values to the CoE server."""
        _LOGGER.debug("Send analog values to CoE server")

        if (
            not self._check_channel_mode(ChannelMode.ANALOG, channels)
            or not self._check_array_length(channels, self.ANALOG_VALUES_PER_PAGE)
            or not self._check_analog_page_size(page)
        ):
            _LOGGER.error("Could not send analog values. Please see logs for details.")
            return

        data = {
            "values": [
                self._convert_analog_channel_to_dict(channel) for channel in channels
            ],
            "page": page,
        }

        url = f"{self.host}{self.COE_SEND_ANALOG}"

        await self._make_request_post(url, data)

    async def send_digital_values(
        self, channels: list[CoEChannel], second_page: bool = False
    ) -> None:
        """Send digital values to the CoE server."""
        _LOGGER.debug("Send digital values to CoE server")

        if not self._check_channel_mode(
            ChannelMode.DIGITAL, channels
        ) or not self._check_array_length(channels, self.DIGITAL_VALUES_PER_PAGE):
            _LOGGER.error("Could not send digital values. Please see logs for details.")
            return

        data = {"values": [bool(x.value) for x in channels], "page": int(second_page)}

        url = f"{self.host}{self.COE_SEND_DIGITAL}"
        await self._make_request_post(url, data)

    @staticmethod
    def _map_channels_to_v2_body(channels: list[CoEChannel]) -> dict[str, Any]:
        """Map a channels to a v2 request body."""
        return {
            "values": [
                {"channel": channel.index, "value": channel.value, "unit": channel.unit}
                for channel in channels
            ],
        }

    @staticmethod
    def _check_channels_min_index(channels: list[CoEChannel], min_index: int) -> bool:
        """Check if the channel indexes are greate then the minimum."""
        for channel in channels:
            if channel.index < min_index:
                _LOGGER.warning(
                    f"Channel index must be greater than zero. Channel index: {channel.index}"
                )
                return False
        return True

    async def send_analog_values_v2(self, channel: list[CoEChannel]) -> None:
        """Send analog values to the CoE server (Version 2)."""
        _LOGGER.debug("Send analog value to CoE server (V2)")

        if not self._check_channel_mode(
            ChannelMode.ANALOG, channel
        ) or not self._check_channels_min_index(channel, self.V2_MIN_CHANNEL_INDEX):
            _LOGGER.error("Could not send analog values. Please see logs for details.")
            return

        data = self._map_channels_to_v2_body(channel)

        url = f"{self.host}{self.COE_SEND_ANALOG_V2}"
        await self._make_request_post(url, data)

    async def send_digital_values_v2(self, channel: list[CoEChannel]) -> None:
        """Send digital values to the CoE server (Version 2)."""
        _LOGGER.debug("Send digital value to CoE server (V2)")

        if not self._check_channel_mode(
            ChannelMode.DIGITAL, channel
        ) or not self._check_channels_min_index(channel, self.V2_MIN_CHANNEL_INDEX):
            _LOGGER.error("Could not send digital values. Please see logs for details.")
            return

        data = self._map_channels_to_v2_body(channel)

        url = f"{self.host}{self.COE_SEND_DIGITAL_V2}"
        await self._make_request_post(url, data)
