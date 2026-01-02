from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MemoryBackend:
    max_items: int = 256
    _data: OrderedDict[Any, list] = None  # type: ignore

    def __post_init__(self) -> None:
        if self._data is None:
            self._data = OrderedDict()

    def get(self, key: Any) -> Optional[list]:
        v = self._data.get(key)
        if v is None:
            return None
        self._data.move_to_end(key)
        return v

    def put(self, key: Any, value: list) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        while len(self._data) > self.max_items:
            self._data.popitem(last=False)
