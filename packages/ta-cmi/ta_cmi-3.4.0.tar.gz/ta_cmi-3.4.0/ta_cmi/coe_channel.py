from .channel import Channel
from .const import ChannelMode, ReadOnlyClass


class CoEChannel(Channel, metaclass=ReadOnlyClass):
    """Class to display an digital or analog datapoint."""

    def __init__(self, mode: ChannelMode, index: int, value: float, unit: str) -> None:
        """Initialize and parse json to get properties."""
        super().__init__(None, mode, index, value, unit)
