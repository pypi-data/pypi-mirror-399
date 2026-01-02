from __future__ import annotations

import json
from typing import Any


class JsonCodec:
    name = "json"

    def encode(self, obj: Any) -> bytes:
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    def decode(self, payload: bytes) -> Any:
        return json.loads(payload.decode("utf-8"))
