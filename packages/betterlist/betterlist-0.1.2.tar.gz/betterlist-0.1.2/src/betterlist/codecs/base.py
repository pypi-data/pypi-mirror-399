from __future__ import annotations

from typing import Any, Protocol


class Codec(Protocol):
    name: str

    def encode(self, obj: Any) -> bytes: ...
    def decode(self, payload: bytes) -> Any: ...
