"""Voice management for nanmai-tts."""

from typing import List, Dict, Any, Optional


# Available voices for Nanmai TTS
_VOICES = [
    {
        "name": "DeepSeek",
        "short_name": "DeepSeek",
        "gender": "Female",  # Both voices are female
        "locale": "zh-CN",
        "display_name": "DeepSeek",
        "local_name": "DeepSeek",
    },
    {
        "name": "Kimi",
        "short_name": "Kimi",
        "gender": "Female",  # Both voices are female
        "locale": "zh-CN",
        "display_name": "Kimi",
        "local_name": "Kimi",
    },
]


async def list_voices() -> List[Dict[str, Any]]:
    """
    List all available voices for Nanmai TTS.

    Returns:
        List of voice dictionaries
    """
    return _VOICES.copy()


class VoicesManager:
    """
    Helper class to find and manage voices.
    Mimics the interface of edge-tts VoicesManager for consistency.
    """

    def __init__(self):
        self.voices: List[Dict[str, Any]] = []
        self.called_create: bool = False

    @classmethod
    async def create(cls) -> "VoicesManager":
        """
        Create a VoicesManager instance and populate it with available voices.

        Returns:
            VoicesManager instance
        """
        self = cls()
        self.voices = await list_voices()
        self.called_create = True
        return self

    def find(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Find voices matching the given criteria.

        Args:
            **kwargs: Key-value pairs to match against voice attributes

        Returns:
            List of matching voices
        """
        if not self.called_create:
            raise RuntimeError("VoicesManager.find() called before VoicesManager.create()")

        # Simple filtering logic
        matching_voices = []
        for voice in self.voices:
            if all(voice.get(key) == value for key, value in kwargs.items()):
                matching_voices.append(voice)

        return matching_voices
