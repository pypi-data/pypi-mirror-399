import asyncio
from typing import List

from aiohttp import ClientSession

from .cmi_api import CMIAPI
from .const import SLEEP_FUNCTION_TYPE, ReadOnlyClass
from .device import Device


class CMI(metaclass=ReadOnlyClass):
    """Main class to interact with CMI."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: ClientSession = None,
        sleep_function: SLEEP_FUNCTION_TYPE = asyncio.sleep,
        rate_limit_wait_time: int = 75,
    ) -> None:
        """Initialize."""
        self._api = CMIAPI(host, username, password, session)
        self._sleep_function = sleep_function
        self._rate_limit_wait_time = rate_limit_wait_time

    async def get_devices(self) -> List[Device]:
        """List connected devices."""
        device_ids = await self._api.get_devices_ids()

        return [
            Device(
                x,
                self._api,
                sleep_function=self._sleep_function,
                rate_limit_wait_time=self._rate_limit_wait_time,
            )
            for x in device_ids
        ]
