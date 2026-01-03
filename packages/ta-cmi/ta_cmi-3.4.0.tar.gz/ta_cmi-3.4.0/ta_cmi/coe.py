from typing import Any, Dict, List

from aiohttp import ClientSession
from packaging import version

from .coe_api import CoEAPI, CoEServerConfig
from .coe_channel import CoEChannel
from .const import _LOGGER, ChannelMode


class CoE:
    _min_required_server_version_ = "2.1.0"
    _version_check: bool | None = None

    def __init__(self, host: str, session: ClientSession = None):
        """Initialize."""
        self._channels: Dict[int, Dict[ChannelMode, Dict[int, CoEChannel]]] = {}

        self._api = CoEAPI(host, session)
        self.last_update: Dict[int, float] = {}

    async def check_version(self) -> bool:
        """Check if the library has support for the server."""
        if self._version_check is None:
            ver = await self._api.get_coe_version()

            if ver is None:
                return False

            server_version = version.parse(ver)
            required_version = version.parse(self._min_required_server_version_)

            self._version_check = (
                required_version.major <= server_version.major
                and required_version.minor <= server_version.minor
            )

        if not self._version_check:
            _LOGGER.warning(
                f"This version of the library requires at least the CoE server with version: {self._min_required_server_version_}."
            )

        return self._version_check

    @staticmethod
    def _extract_channels(
        mode: ChannelMode, raw_channels: List[Dict[str, Any]]
    ) -> Dict[int, CoEChannel]:
        """Extract channel info from data array from request."""
        channels: Dict[int, CoEChannel] = {}

        for index, channel_raw in enumerate(raw_channels):
            if channel_raw["unit"] == 0 and channel_raw["value"] == 0:
                continue

            channels[index + 1] = CoEChannel(
                mode, index + 1, float(channel_raw["value"]), str(channel_raw["unit"])
            )

        return channels

    async def update(self, can_id: int) -> None:
        """Update data."""
        await self.check_version()
        _LOGGER.debug("Update CoE data")

        data = await self._api.get_coe_data(can_id)

        if data is None:
            _LOGGER.debug("Received no data from CoE")
            return

        if data["last_update_unix"] <= self.last_update.get(can_id, 0):
            _LOGGER.debug("Received old data from CoE")
            return

        if self._channels.get(can_id, None) is None:
            self._channels[can_id] = {}

        self._channels[can_id][ChannelMode.DIGITAL] = self._extract_channels(
            ChannelMode.DIGITAL, data["digital"]
        )

        self._channels[can_id][ChannelMode.ANALOG] = self._extract_channels(
            ChannelMode.ANALOG, data["analog"]
        )

        self.last_update[can_id] = data["last_update_unix"]

    def get_channels(
        self, can_id: int, channel_mode: ChannelMode
    ) -> Dict[int, CoEChannel]:
        """Get all the fetched channels from a type."""
        return self._channels.get(can_id, {}).get(channel_mode, {})

    async def get_server_version(self) -> str:
        """Get the server version."""
        await self.check_version()
        return await self._api.get_coe_version()

    async def get_server_config(self) -> CoEServerConfig:
        """Get the coe server config."""
        await self.check_version()
        return await self._api.get_coe_server_config()

    async def send_analog_values(self, data: list[CoEChannel], page: int):
        """Send analog values to CoE server."""
        await self.check_version()
        await self._api.send_analog_values(data, page)

    async def send_digital_values(self, data: list[CoEChannel], second_page: bool):
        """Send digital values to CoE server."""
        await self.check_version()
        await self._api.send_digital_values(data, second_page)

    async def send_analog_values_v2(self, channel: list[CoEChannel]):
        """Send a analog values to CoE server (V2)."""
        await self.check_version()
        await self._api.send_analog_values_v2(channel)

    async def send_digital_values_v2(self, channel: list[CoEChannel]):
        """Send a digital values to CoE server (V2)."""
        await self.check_version()
        await self._api.send_digital_values_v2(channel)
