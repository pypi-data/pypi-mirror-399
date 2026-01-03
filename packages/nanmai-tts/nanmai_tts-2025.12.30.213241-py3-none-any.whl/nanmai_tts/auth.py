"""Authentication module for Nanmai TTS API."""

import hashlib
import random
import time
from datetime import datetime

from .constants import USER_AGENT


def _e(nt: str) -> int:
    """Hash function used in Nanmai API authentication."""
    HASH_MASK_1 = 268435455
    HASH_MASK_2 = 266338304
    at = 0
    for st in reversed(nt):
        st = ord(st)
        at = (at << 6 & HASH_MASK_1) + st + (st << 14)
        it = at & HASH_MASK_2
        if it != 0:
            at ^= it >> 21
    return at


def generate_mid() -> str:
    """Generate MID token for authentication."""
    def generate_unique_hash():
        nt = f"chrome1.0zh-CNWin32{USER_AGENT}1920x108024https://bot.n.cn/chat"
        at = len(nt)
        it = 1
        while it:
            nt += chr(it ^ at)
            it -= 1
            at += 1
        return (round(random.random() * 2147483647) ^ _e(nt)) * 2147483647

    return f"{_e('https://bot.n.cn')}{generate_unique_hash()}{time.time() + random.random() + random.random()}".replace(
        ".", "e"
    )[
        :32
    ]


def get_iso8601_time() -> str:
    """Get current time in ISO 8601 format."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def generate_headers() -> dict:
    """Generate authentication headers for Nanmai API requests."""
    device = "Web"
    ver = "1.2"
    time_str = get_iso8601_time()
    access_token = generate_mid()
    zm_ua = hashlib.md5(USER_AGENT.encode("utf-8")).hexdigest()

    return {
        "device-platform": device,
        "timestamp": time_str,
        "access-token": access_token,
        "zm-token": hashlib.md5(
            f"{device}{time_str}{ver}{access_token}{zm_ua}".encode()
        ).hexdigest(),
        "zm-ver": ver,
        "zm-ua": zm_ua,
        "Content-Type": "application/x-www-form-urlencoded",
    }
