from __future__ import annotations

from .base import Codec
from .json_codec import JsonCodec
from .pickle_codec import PickleCodec

_CODECS: dict[str, Codec] = {
    "pickle": PickleCodec(),
    "json": JsonCodec(),
}


def get_codec(name: str) -> Codec:
    try:
        return _CODECS[name]
    except KeyError:
        raise ValueError(f"Unknown codec: {name!r}. Available: {sorted(_CODECS)}")
