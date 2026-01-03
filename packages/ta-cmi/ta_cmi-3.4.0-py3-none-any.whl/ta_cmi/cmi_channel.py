from typing import Any, Dict

from . import Channel
from .const import ChannelType, ReadOnlyClass


class CMIChannel(Channel, metaclass=ReadOnlyClass):
    """Class to display an input or output."""

    def __init__(self, channel_type: ChannelType, json: Dict[str, Any]) -> None:
        """Initialize and parse json to get properties."""
        super().__init__(
            channel_type,
            json["AD"],
            json["Number"],
            json["Value"]["Value"],
            json["Value"]["Unit"],
        )
