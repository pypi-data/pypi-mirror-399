"""Nanmai TTS - Async Python library for Nanmai TTS (DeepSeek/Kimi voices)."""

from .communicate import Communicate
from .voices import list_voices, VoicesManager
from .exceptions import (
    NanmaiAPIError,
    NanmaiTTSException,
    NoAudioReceived,
    SessionExpiredError,
    RetryExhaustedError,
    NetworkError
)

# Backward compatibility: import AVAILABLE_VOICES from voices module
import asyncio
_AVAILABLE_VOICES = None

async def _get_available_voices():
    global _AVAILABLE_VOICES
    if _AVAILABLE_VOICES is None:
        _AVAILABLE_VOICES = await list_voices()
    return _AVAILABLE_VOICES

# Synchronous version for backward compatibility
def _get_available_voices_sync():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, we need to handle this differently
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _get_available_voices())
                return future.result()
        else:
            return loop.run_until_complete(_get_available_voices())
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(_get_available_voices())

AVAILABLE_VOICES = _get_available_voices_sync()

__version__ = "0.0.1"
__all__ = [
    "Communicate",
    "list_voices",
    "VoicesManager",
    "AVAILABLE_VOICES",  # Backward compatibility
    "NanmaiAPIError",
    "NanmaiTTSException",
    "NoAudioReceived",
    "SessionExpiredError",
    "RetryExhaustedError",
    "NetworkError"
]
