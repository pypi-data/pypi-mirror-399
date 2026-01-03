import json
from typing import Any, Dict

import yarl
from aiohttp import BasicAuth, ClientConnectionError, ClientSession

from .const import _LOGGER, HTTP_UNAUTHORIZED


class API:
    """Class to perform basic API requests."""

    def __init__(self, session: ClientSession = None, auth: BasicAuth = None) -> None:
        """Initialize."""
        self.session = session
        self._auth = auth

        self._internal_session = False

    @staticmethod
    def parse_json(data: str) -> Dict[str, Any]:
        if not len(data):
            return {}

        return json.loads(data)

    async def _make_request_get(self, url: str) -> Dict[str, Any]:
        """Retrieve json data from REST GET endpoint."""
        return self.parse_json(await self._make_request_no_json(url))

    async def _make_request_post(
        self, url: str, body: dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve json data from REST POST endpoint."""
        return self.parse_json(
            await self._make_request_no_json(url, method="POST", body=body)
        )

    async def _make_request_no_json(
        self, url: str, method: str = "GET", body: dict[str, Any] | None = None
    ) -> str:
        """Retrieve data from REST endpoint."""
        if self.session is None:
            self._internal_session = True
            self.session = ClientSession()

        try:
            _LOGGER.debug(f"Sending request to {url} with {body}")
            async with self.session.request(
                method, url, auth=self._auth, json=body
            ) as res:
                text = await res.text()
                await self._close_session()
                if res.status == HTTP_UNAUTHORIZED:
                    raise InvalidCredentialsError("Invalid credentials")
                elif res.status >= 300:
                    raise ApiError(
                        f"Invalid response from {res.url.host}: {res.status}"
                    )

                _LOGGER.debug(f"Received payload: {text}")
                return text
        except ClientConnectionError:
            await self._close_session()
            raise ApiError(f"Could not connect to {yarl.URL(url).host}")

    async def _close_session(self) -> None:
        """Close the internal session."""
        if self._internal_session:
            await self.session.close()
            self.session = None


class ApiError(Exception):
    """Raised when API request ended in error."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class InvalidCredentialsError(Exception):
    """Triggered when the credentials are invalid."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
