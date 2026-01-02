import time
from typing import Protocol, Tuple

class MaskLike(Protocol):
    limit: int
    def __getitem__(self, idx: int) -> int: ...

def sieve_odd_mask(limit: int) -> bytearray:
    if limit < 2:
        return bytearray(b"\x00")
    size = (limit // 2) + 1
    mask = bytearray(b"\x01") * size
    mask[0] = 0
    p = 3
    while p * p <= limit:
        if mask[p >> 1]:
            for x in range(p * p, limit + 1, 2 * p):
                mask[x >> 1] = 0
        p += 2
    return mask

def autotune_chunk(mask_bytes: int, cpu_features: set[str] | None = None) -> int:
    feats = cpu_features or set()
    if mask_bytes < 8_000_000:
        base = 16384
    elif mask_bytes < 64_000_000:
        base = 32768
    elif mask_bytes < 256_000_000:
        base = 65536
    else:
        base = 131072
    if "avx512f" in feats:
        base *= 2
    elif "avx2" in feats:
        base = int(base * 1.5)
    return min(max((base // 1024) * 1024, 8192), 262144)

def count_primes_for_duration(
    mask: MaskLike, duration: float, start_n: int = 1, chunk: int = 32768
) -> Tuple[int, int]:
    end = time.perf_counter() + duration
    n = start_n
    count = 0
    if n <= 2:
        count += 1
        n = 3
    if n % 2 == 0:
        n += 1
    while True:
        stop = n + 2 * chunk
        while n < stop:
            if n > mask.limit:
                return count, n
            count += mask[n >> 1]
            n += 2
        if time.perf_counter() >= end:
            return count, n
