"""Channel typeclass with a cleaner default prefix."""

from evennia.comms.comms import DefaultChannel


class Channel(DefaultChannel):
    """Base channel class used by the game template."""

    channel_prefix_string = "[TIME-EVE {channelname}]"

    def format_message(self, msg, emit=False):
        """Normalize channel output and avoid blank messages."""
        text = super().format_message(msg, emit=emit)
        return (text or "").strip() or "..."
