"""Version information for nanmai-tts."""

import datetime


def get_version() -> str:
    """Get the version string with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y.%m.%d.%H%M%S")
    return timestamp


__version__ = get_version()
