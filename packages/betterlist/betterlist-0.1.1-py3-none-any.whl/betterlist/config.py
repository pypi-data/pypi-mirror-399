from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterator, Optional


def default_cache_dir(app_name: str = "betterlist") -> Path:
    """
    Cross-platform cache directory:
      - Linux: $XDG_CACHE_HOME/betterlist or ~/.cache/betterlist
      - macOS: ~/Library/Caches/betterlist
      - Windows: %LOCALAPPDATA%\betterlist\Cache
    """
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / app_name / "Cache"
        return Path.home() / "AppData" / "Local" / app_name / "Cache"

    if os.sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / app_name

    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / app_name
    return Path.home() / ".cache" / app_name


@dataclass(frozen=True)
class BetterListConfig:
    # layers
    memory: bool = True
    disk: bool = True

    # disk
    cache_dir: Path = default_cache_dir()
    compression: str = "none"  # "none" | "zlib"

    # memory LRU
    max_memory_items: int = 256

    # behavior/safety
    trust_disk_cache: bool = True  # if False, refuses loading pickle from disk
    eager_write: bool = True       # write immediately on miss


_lock = threading.RLock()
_cfg = BetterListConfig()


def get_config() -> BetterListConfig:
    with _lock:
        return _cfg


def configure(
    *,
    memory: Optional[bool] = None,
    disk: Optional[bool] = None,
    cache_dir: Optional[Path] = None,
    compression: Optional[str] = None,
    max_memory_items: Optional[int] = None,
    trust_disk_cache: Optional[bool] = None,
    eager_write: Optional[bool] = None,
) -> None:
    global _cfg
    with _lock:
        _cfg = replace(
            _cfg,
            memory=_cfg.memory if memory is None else bool(memory),
            disk=_cfg.disk if disk is None else bool(disk),
            cache_dir=_cfg.cache_dir if cache_dir is None else Path(cache_dir),
            compression=_cfg.compression if compression is None else str(compression),
            max_memory_items=_cfg.max_memory_items if max_memory_items is None else int(max_memory_items),
            trust_disk_cache=_cfg.trust_disk_cache if trust_disk_cache is None else bool(trust_disk_cache),
            eager_write=_cfg.eager_write if eager_write is None else bool(eager_write),
        )


@contextmanager
def configured(**kwargs) -> Iterator[None]:
    """
    Temporary override.

    Example:
        with configured(disk=False):
            ...
    """
    global _cfg
    with _lock:
        old = _cfg
        configure(**kwargs)
    try:
        yield
    finally:
        with _lock:
            _cfg = old
