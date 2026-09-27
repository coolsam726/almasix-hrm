"""Time-based one-time codes for the authenticator factor (RFC 6238, SHA-1)."""

from __future__ import annotations

import hashlib
import hmac
import struct


def totp(secret: bytes, at: int, *, step: int = 30, digits: int = 6) -> str:
    counter = int(at // step)
    digest = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 10**digits).zfill(digits)


def confirm_totp(secret: bytes, code: str, at: int) -> bool:
    if not code.isdigit() or len(code) != 6:
        return False
    return hmac.compare_digest(totp(secret, at), code)
