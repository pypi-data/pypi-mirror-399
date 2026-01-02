from __future__ import annotations

import mmap
import os
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

# Binary cache format:
# header:
#   magic   8 bytes  b"BLIST001"
#   version u32      1
#   flags   u32      bit0=zlib
#   codec   16 bytes ascii null-padded
#   keyhash 32 bytes sha256(key_bytes)
#   nitems  u64
#   paylen  u64 (bytes after compression if compressed)
# data:
#   payload bytes
MAGIC = b"BLIST001"
VERSION = 1
FLAG_ZLIB = 1 << 0

HEADER_STRUCT = struct.Struct("<8sII16s32sQQ")
HEADER_SIZE = HEADER_STRUCT.size


def _codec_field(codec_name: str) -> bytes:
    b = codec_name.encode("ascii", "strict")
    if len(b) > 16:
        raise ValueError("codec name too long (max 16 ascii bytes)")
    return b.ljust(16, b"\x00")


def _codec_from_field(b: bytes) -> str:
    return b.split(b"\x00", 1)[0].decode("ascii", "strict")


@dataclass
class CacheView:
    path: Path
    codec: str
    compressed: bool
    nitems: int
    keyhash32: bytes

    _file: object
    _mmap: mmap.mmap
    _buf: memoryview
    _data_off: int
    _paylen: int

    def payload_bytes(self) -> bytes:
        mv = self._buf[self._data_off : self._data_off + self._paylen]
        return bytes(mv)

    def close(self) -> None:
        try:
            self._buf.release()
        except Exception:
            pass
        try:
            self._mmap.close()
        finally:
            try:
                self._file.close()
            except Exception:
                pass


def open_cache_file(path: Path) -> CacheView:
    path = Path(path)
    f = path.open("rb")
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    buf = memoryview(mm)

    if len(buf) < HEADER_SIZE:
        mm.close()
        f.close()
        raise ValueError("Invalid cache file: too small")

    magic, ver, flags, codec16, keyhash32, nitems, paylen = HEADER_STRUCT.unpack_from(buf, 0)

    if magic != MAGIC or ver != VERSION:
        mm.close()
        f.close()
        raise ValueError("Invalid/unsupported cache file")

    data_off = HEADER_SIZE
    if data_off + paylen > len(buf):
        mm.close()
        f.close()
        raise ValueError("Invalid cache file: truncated")

    return CacheView(
        path=path,
        codec=_codec_from_field(codec16),
        compressed=bool(flags & FLAG_ZLIB),
        nitems=int(nitems),
        keyhash32=bytes(keyhash32),
        _file=f,
        _mmap=mm,
        _buf=buf,
        _data_off=data_off,
        _paylen=int(paylen),
    )


def _atomic_write(path: Path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")

    with tmp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

    tmp.replace(path)


def write_cache_file(
    path: Path,
    *,
    codec: str,
    keyhash32: bytes,
    nitems: int,
    payload: bytes,
    compression: str = "none",
) -> None:
    if len(keyhash32) != 32:
        raise ValueError("keyhash32 must be 32 bytes (sha256 digest)")

    flags = 0
    out_payload = payload

    if compression == "zlib":
        flags |= FLAG_ZLIB
        out_payload = zlib.compress(payload, level=6)
    elif compression in ("none", "", None):
        pass
    else:
        raise ValueError("compression must be 'none' or 'zlib'")

    header = HEADER_STRUCT.pack(
        MAGIC,
        VERSION,
        flags,
        _codec_field(codec),
        keyhash32,
        int(nitems),
        int(len(out_payload)),
    )
    _atomic_write(path, header + out_payload)


def read_cache_payload(view: CacheView) -> bytes:
    payload = view.payload_bytes()
    if view.compressed:
        payload = zlib.decompress(payload)
    return payload
