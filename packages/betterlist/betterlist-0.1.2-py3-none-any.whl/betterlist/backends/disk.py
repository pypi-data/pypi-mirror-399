from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..cachefile import open_cache_file, read_cache_payload, write_cache_file
from ..keying import key_hash32, key_hash_hex


@dataclass(frozen=True)
class DiskBackend:
    cache_dir: Path

    def path_for(self, key: Any) -> Path:
        h = key_hash_hex(key)
        return self.cache_dir / h[:2] / f"{h}.blc"  # betterlist cache

    def get_payload(self, key: Any) -> Optional[tuple[str, bytes, int]]:
        """
        Returns (codec_name, payload_bytes(decompressed), nitems) or None.
        Also validates stored keyhash matches key.
        """
        path = self.path_for(key)
        if not path.exists():
            return None

        view = open_cache_file(path)
        try:
            if view.keyhash32 != key_hash32(key):
                # Wrong key for this file (corruption or collision). Treat as miss.
                return None
            payload = read_cache_payload(view)
            return (view.codec, payload, view.nitems)
        finally:
            view.close()

    def put_payload(
        self,
        key: Any,
        *,
        codec: str,
        payload: bytes,
        nitems: int,
        compression: str,
    ) -> Path:
        path = self.path_for(key)
        write_cache_file(
            path,
            codec=codec,
            keyhash32=key_hash32(key),
            nitems=nitems,
            payload=payload,
            compression=compression,
        )
        return path
