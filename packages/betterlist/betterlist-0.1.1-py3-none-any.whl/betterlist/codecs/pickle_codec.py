from __future__ import annotations

import pickle
from typing import Any


class PickleCodec:
    name = "pickle"

    def encode(self, obj: Any) -> bytes:
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    def decode(self, payload: bytes) -> Any:
        return pickle.loads(payload)
