from __future__ import annotations

from .base import Codec
from .pickle_codec import PickleCodec
from .json_codec import JsonCodec

_CODECS = {
    "pickle": PickleCodec(),
    "json": JsonCodec(),
}


def get_codec(name: str) -> Codec:
    try:
        return _CODECS[name]
    except KeyError:
        raise ValueError(f"Unknown codec: {name!r}. Available: {sorted(_CODECS)}")
