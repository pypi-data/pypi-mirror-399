from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_key_bytes(key: Any) -> bytes:
    """
    Convert a cache key to stable bytes.

    - bytes/bytearray/memoryview: used directly
    - otherwise: JSON with stable ordering, fallback to repr() for unknown objects
    """
    if isinstance(key, (bytes, bytearray, memoryview)):
        return bytes(key)

    def default(o: Any) -> str:
        return repr(o)

    return json.dumps(key, sort_keys=True, separators=(",", ":"), default=default).encode("utf-8")


def key_hash_hex(key: Any) -> str:
    return hashlib.sha256(stable_key_bytes(key)).hexdigest()


def key_hash32(key: Any) -> bytes:
    return hashlib.sha256(stable_key_bytes(key)).digest()
