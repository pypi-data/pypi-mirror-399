from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Protocol, TypeVar, runtime_checkable

from .backends import DiskBackend, MemoryBackend
from .codecs import get_codec
from .config import get_config

T = TypeVar("T")


@runtime_checkable
class CacheableIterable(Protocol[T]):
    def cache_key(self) -> Any: ...
    def build(self) -> Iterable[T]: ...
    def preferred_codec(self) -> str | None: ...


@dataclass(frozen=True)
class _Wrapped(CacheableIterable[T]):
    key: Any
    it: Iterable[T]
    codec: Optional[str] = None

    def cache_key(self) -> Any:
        return self.key

    def build(self) -> Iterable[T]:
        return self.it

    def preferred_codec(self) -> str | None:
        return self.codec


def cached(key: Any, iterable: Iterable[T], *, codec: str | None = None) -> CacheableIterable[T]:
    """
    Wrap any iterable with a stable cache key so betterlist can cache it.

    Example:
        import betterlist
        from betterlist import cached

        xs = betterlist[cached(("expensive", 1), gen())]
    """
    return _Wrapped(key=key, it=iterable, codec=codec)


_mem_backend: Optional[MemoryBackend] = None


def _memory_backend() -> MemoryBackend:
    global _mem_backend
    cfg = get_config()
    if _mem_backend is None or _mem_backend.max_items != cfg.max_memory_items:
        _mem_backend = MemoryBackend(max_items=cfg.max_memory_items)
    return _mem_backend


def listp(iterable: Iterable[T] = ()) -> list[T]:
    """
    list+ implementation with the same call signature as list(iterable=()).

    Primary user syntax is:
        import betterlist
        xs = betterlist[iterable]
    """
    cfg = get_config()

    # Not cacheable => behave like list()
    if not isinstance(iterable, CacheableIterable):
        return list(iterable)

    key = iterable.cache_key()
    codec_name = iterable.preferred_codec() or "pickle"

    # Memory cache
    if cfg.memory:
        mem = _memory_backend()
        hit = mem.get(key)
        if hit is not None:
            return hit

    # Disk cache
    if cfg.disk:
        disk = DiskBackend(cfg.cache_dir)
        got = disk.get_payload(key)
        if got is not None:
            disk_codec_name, payload, _nitems = got

            # Safety: refuse pickle load if cache dir is untrusted
            if (not cfg.trust_disk_cache) and disk_codec_name == "pickle":
                pass
            else:
                codec = get_codec(disk_codec_name)
                obj = codec.decode(payload)
                if not isinstance(obj, list):
                    obj = list(obj)

                if cfg.memory:
                    _memory_backend().put(key, obj)
                return obj

    # Miss => build
    out = list(iterable.build())

    if cfg.memory:
        _memory_backend().put(key, out)

    if cfg.disk and cfg.eager_write:
        disk = DiskBackend(cfg.cache_dir)
        codec = get_codec(codec_name)
        payload = codec.encode(out)
        disk.put_payload(
            key,
            codec=codec_name,
            payload=payload,
            nitems=len(out),
            compression=cfg.compression,
        )

    return out
