from __future__ import annotations

import mmap
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from .core import sieve_odd_mask

# Bitset file format:
# header:
#   magic   8 bytes: b"LPMASK02"
#   version u32     : 2
#   limit   u64     : max n supported
#   nbits   u64     : number of bits in bitset (== (limit//2)+1)
# data:
#   bitset bytes little-endian within each byte:
#     bit i corresponds to odd number (2*i + 1)
#     i=0 -> 1 (not prime)
#
MAGIC = b"LPMASK02"
VERSION = 2
HEADER_STRUCT = struct.Struct("<8sIQQ")
HEADER_SIZE = HEADER_STRUCT.size


def _platform() -> str:
    return sys.platform


def cache_dir() -> Path:
    """
    Auto-cache location:
      - Linux: $XDG_CACHE_HOME/lookprime or ~/.cache/lookprime
      - macOS: ~/Library/Caches/lookprime
      - Windows: %LOCALAPPDATA%\\lookprime\\Cache
    """
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "lookprime" / "Cache"
        return Path.home() / "AppData" / "Local" / "lookprime" / "Cache"

    if _platform() == "darwin":
        return Path.home() / "Library" / "Caches" / "lookprime"

    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "lookprime"
    return Path.home() / ".cache" / "lookprime"


def default_mask_path(limit: int, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or cache_dir()
    return base / f"lookprime_mask_{limit}.lpm"


def _pack_odd_mask_to_bitset(mask01: bytearray) -> bytes:
    """
    Convert odd-only 0/1 byte mask to bitset bytes.
    bit i corresponds to mask01[i].
    """
    nbits = len(mask01)
    nbytes = (nbits + 7) // 8
    out = bytearray(nbytes)
    for i, v in enumerate(mask01):
        if v:
            out[i >> 3] |= 1 << (i & 7)
    return bytes(out)


@dataclass
class MaskView:
    """
    Memory-mapped bitset view.
    Index with i = n >> 1 (odd half-index) -> returns 0 or 1
    """
    limit: int
    nbits: int

    _file: object
    _mmap: mmap.mmap
    _buf: memoryview
    _data_off: int
    _nbytes: int

    def __len__(self) -> int:
        # number of bits is nbits; but len() used elsewhere as bytes proxy
        return self._nbytes

    def __getitem__(self, idx: int) -> int:
        # idx is half-index; return bit
        if idx < 0 or idx >= self.nbits:
            return 0
        b = self._buf[self._data_off + (idx >> 3)]
        return (b >> (idx & 7)) & 1

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

    # ---------- Fast bit counting/scanning helpers ----------

    def _data_slice(self) -> memoryview:
        return self._buf[self._data_off : self._data_off + self._nbytes]

    def count_ones_upto(self, bit_idx_inclusive: int) -> int:
        """
        Count set bits in [0..bit_idx_inclusive] (inclusive).
        Uses int.from_bytes(...).bit_count() in chunks.
        """
        if bit_idx_inclusive < 0:
            return 0
        if bit_idx_inclusive >= self.nbits:
            bit_idx_inclusive = self.nbits - 1

        end_bit = bit_idx_inclusive
        end_byte = end_bit >> 3
        end_in_byte = end_bit & 7

        data = self._data_slice()

        # Full bytes before end_byte
        full = 0
        if end_byte > 0:
            # count bytes [0:end_byte)
            # chunk to avoid huge int allocations
            CH = 8192
            i = 0
            while i < end_byte:
                j = min(end_byte, i + CH)
                full += int.from_bytes(data[i:j], "little").bit_count()
                i = j

        # Partial last byte [end_byte]
        last = data[end_byte]
        mask = (1 << (end_in_byte + 1)) - 1
        full += (last & mask).bit_count()

        return full

    def iter_set_bits(self, start_bit: int, end_bit_exclusive: int) -> Iterator[int]:
        """
        Yield set bit indices in [start_bit, end_bit_exclusive).
        Efficient scanning by bytes; only visits nonzero bytes.
        """
        if start_bit < 0:
            start_bit = 0
        if end_bit_exclusive > self.nbits:
            end_bit_exclusive = self.nbits
        if start_bit >= end_bit_exclusive:
            return

        data = self._data_slice()
        start_byte = start_bit >> 3
        end_byte = (end_bit_exclusive + 7) >> 3

        # handle first byte with mask
        b = int(data[start_byte])
        first_mask = 0xFF & (~((1 << (start_bit & 7)) - 1))
        b &= first_mask

        byte_i = start_byte
        while byte_i < end_byte:
            if byte_i != start_byte:
                b = int(data[byte_i])

            if b:
                # enumerate set bits in this byte
                while b:
                    lsb = b & -b
                    bit_pos = (lsb.bit_length() - 1)
                    bit_idx = (byte_i << 3) + bit_pos
                    if bit_idx >= end_bit_exclusive:
                        return
                    yield bit_idx
                    b ^= lsb

            byte_i += 1
            if byte_i == end_byte:
                break

            # if last byte, apply end mask at end in loop top next cycle

        # If end_bit_exclusive not aligned, iter_set_bits may yield bits beyond.
        # We check bit_idx >= end_bit_exclusive above, so OK.


def open_mask(path: Path) -> MaskView:
    path = Path(path)
    f = path.open("rb")
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    buf = memoryview(mm)

    if len(buf) < HEADER_SIZE:
        mm.close()
        f.close()
        raise ValueError("Invalid mask file: too small")

    magic, ver, limit, nbits = HEADER_STRUCT.unpack_from(buf, 0)
    if magic != MAGIC or ver != VERSION:
        mm.close()
        f.close()
        raise ValueError("Invalid/unsupported mask file")

    nbytes = (int(nbits) + 7) // 8
    data_off = HEADER_SIZE
    if data_off + nbytes > len(buf):
        mm.close()
        f.close()
        raise ValueError("Invalid mask file: truncated")

    return MaskView(
        limit=int(limit),
        nbits=int(nbits),
        _file=f,
        _mmap=mm,
        _buf=buf,
        _data_off=data_off,
        _nbytes=nbytes,
    )


def write_mask_file(path: Path, limit: int, bitset_bytes: bytes, nbits: int) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    header = HEADER_STRUCT.pack(MAGIC, VERSION, int(limit), int(nbits))

    with tmp.open("wb") as f:
        f.write(header)
        f.write(bitset_bytes)
        f.flush()
        os.fsync(f.fileno())

    tmp.replace(path)


def sieve_to_cache(limit: int, base_dir: Optional[Path] = None, force: bool = False) -> Path:
    """
    Build the sieve and store it in the cache (bitset format).
    If present and valid, reuse.
    """
    path = default_mask_path(limit, base_dir=base_dir)
    if path.exists() and not force:
        try:
            mv = open_mask(path)
            mv.close()
            return path
        except Exception:
            pass

    mask01 = sieve_odd_mask(limit)  # bytearray of 0/1 for odd indices
    bitset = _pack_odd_mask_to_bitset(mask01)
    nbits = len(mask01)
    write_mask_file(path, limit=limit, bitset_bytes=bitset, nbits=nbits)
    return path
