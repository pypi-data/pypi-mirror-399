"""Exceptions for the nanmai_tts package."""

import re


class NanmaiTTSException(Exception):
    """Base exception for Nanmai TTS."""
    pass


class NanmaiAPIError(NanmaiTTSException):
    """Exception raised when Nanmai API returns an error."""
    pass


class AuthenticationError(NanmaiTTSException):
    """Exception raised when authentication fails."""
    pass


class NetworkError(NanmaiTTSException, IOError):
    """Exception raised when network communication fails."""
    pass


class SessionExpiredError(NetworkError):
    """Exception raised when the provided session has expired."""
    pass


class RetryExhaustedError(NetworkError):
    """Exception raised when all retry attempts are exhausted."""
    pass


class NoAudioReceived(NanmaiTTSException, ValueError):
    """
    Raised when no audio is received from the service.

    This can happen if:
    1. The text contains only punctuation or whitespace (client-side check).
    2. The API returns an empty response body (server-side check).
    """
    pass


# Pattern for speakable characters (letters, numbers, CJK, Kana, Hangul)
SPEAKABLE_PATTERN = re.compile(r"[a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+")
