from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Encoded:
    codec: str
    payload: bytes


class Codec(Protocol):
    name: str

    def encode(self, obj: Any) -> bytes: ...
    def decode(self, payload: bytes) -> Any: ...
