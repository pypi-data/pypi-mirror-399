import mmap, os, struct
from pathlib import Path
from dataclasses import dataclass
from .core import sieve_odd_mask

MAGIC = b"LPMASK01"
VERSION = 1
HDR = struct.Struct("<8sIQQ")

def cache_dir() -> Path:
    return Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "lookprime"

def default_mask_path(limit: int) -> Path:
    return cache_dir() / f"lookprime_mask_{limit}.lpm"

@dataclass
class MaskView:
    limit: int
    _f: object
    _m: mmap.mmap
    _buf: memoryview
    _off: int
    def __len__(self): return self._m.size() - self._off
    def __getitem__(self, i): return self._buf[self._off + i]
    def close(self):
        self._buf.release()
        self._m.close()
        self._f.close()

def open_mask(path: Path) -> MaskView:
    f = path.open("rb")
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    buf = memoryview(m)
    magic, ver, limit, size = HDR.unpack_from(buf, 0)
    if magic != MAGIC or ver != VERSION:
        raise ValueError("Invalid mask file")
    return MaskView(limit, f, m, buf, HDR.size)

def sieve_to_cache(limit: int, force=False) -> Path:
    path = default_mask_path(limit)
    if path.exists() and not force:
        return path
    mask = sieve_odd_mask(limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(HDR.pack(MAGIC, VERSION, limit, len(mask)))
        f.write(mask)
    return path
