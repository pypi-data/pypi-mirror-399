from __future__ import annotations

import mmap
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .core import sieve_odd_mask

# File format:
# [header][mask bytes...]
# header:
#   magic 8 bytes: b"LPMASK01"
#   version u32
#   limit   u64
#   size    u64  (mask length in bytes)
#
MAGIC = b"LPMASK01"
VERSION = 1
HEADER_STRUCT = struct.Struct("<8sIQQ")  # magic, version, limit, size
HEADER_SIZE = HEADER_STRUCT.size


def cache_dir() -> Path:
    """
    Auto-cache location:
      - Linux: $XDG_CACHE_HOME/lookprime or ~/.cache/lookprime
      - macOS: ~/Library/Caches/lookprime
      - Windows: %LOCALAPPDATA%\\lookprime\\Cache
    """
    # Windows
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "lookprime" / "Cache"
        return Path.home() / "AppData" / "Local" / "lookprime" / "Cache"

    # macOS
    if sys_platform() == "darwin":
        return Path.home() / "Library" / "Caches" / "lookprime"

    # Linux/Unix
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "lookprime"
    return Path.home() / ".cache" / "lookprime"


def sys_platform() -> str:
    # tiny helper to avoid importing platform in hot codepaths
    import sys
    return sys.platform


def default_mask_path(limit: int, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or cache_dir()
    return base / f"lookprime_mask_{limit}.lpm"


@dataclass
class MaskView:
    """
    Memory-mapped odd-only mask view.
    Index with i = n >> 1 (for odd n) to get 0/1.
    """
    limit: int
    _file: object
    _mmap: mmap.mmap
    _buf: memoryview
    _data_off: int
    _size: int

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, idx: int) -> int:
        # idx is the half-index
        return self._buf[self._data_off + idx]

    @property
    def max_n(self) -> int:
        return self.limit

    def close(self) -> None:
        # memoryview must be released before closing mmap on some platforms
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


def open_mask(path: Path) -> MaskView:
    """
    Open a mask file via mmap (read-only).
    """
    path = Path(path)
    f = path.open("rb")
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    buf = memoryview(mm)

    if len(buf) < HEADER_SIZE:
        mm.close()
        f.close()
        raise ValueError("Invalid mask file: too small")

    magic, ver, limit, size = HEADER_STRUCT.unpack_from(buf, 0)
    if magic != MAGIC:
        mm.close()
        f.close()
        raise ValueError("Invalid mask file: bad magic")
    if ver != VERSION:
        mm.close()
        f.close()
        raise ValueError(f"Unsupported mask file version: {ver}")

    data_off = HEADER_SIZE
    if data_off + size > len(buf):
        mm.close()
        f.close()
        raise ValueError("Invalid mask file: truncated")

    return MaskView(
        limit=int(limit),
        _file=f,
        _mmap=mm,
        _buf=buf,
        _data_off=data_off,
        _size=int(size),
    )


def write_mask_file(path: Path, limit: int, mask_bytes: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    header = HEADER_STRUCT.pack(MAGIC, VERSION, int(limit), int(len(mask_bytes)))

    with tmp.open("wb") as f:
        f.write(header)
        f.write(mask_bytes)
        f.flush()
        os.fsync(f.fileno())

    # atomic replace on POSIX; on Windows it's “best effort” but usually fine
    tmp.replace(path)


def sieve_to_cache(limit: int, base_dir: Optional[Path] = None, force: bool = False) -> Path:
    """
    Build the odd-only sieve and store it in the cache (or reuse if present).
    Returns the path to the cached mask file.
    """
    path = default_mask_path(limit, base_dir=base_dir)
    if path.exists() and not force:
        # quick sanity check: try opening & header validate
        try:
            mv = open_mask(path)
            mv.close()
            return path
        except Exception:
            # corrupt/outdated file -> rebuild
            pass

    mask = sieve_odd_mask(limit)
    write_mask_file(path, limit=limit, mask_bytes=bytes(mask))
    return path
