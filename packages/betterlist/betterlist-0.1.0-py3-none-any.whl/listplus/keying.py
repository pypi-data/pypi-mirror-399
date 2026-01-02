from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_key_bytes(key: Any) -> bytes:
    """
    Convert a cache key to stable bytes.

    - If you pass bytes, we use them.
    - Otherwise, we JSON-encode with a conservative fallback to repr().
    """
    if isinstance(key, (bytes, bytearray, memoryview)):
        return bytes(key)

    def default(o: Any) -> str:
        return repr(o)

    payload = json.dumps(key, sort_keys=True, separators=(",", ":"), default=default).encode("utf-8")
    return payload


def key_hash_hex(key: Any) -> str:
    return hashlib.sha256(stable_key_bytes(key)).hexdigest()


def short_key_hash(key: Any, n: int = 16) -> str:
    h = key_hash_hex(key)
    return h[: max(8, min(n, len(h)))]
