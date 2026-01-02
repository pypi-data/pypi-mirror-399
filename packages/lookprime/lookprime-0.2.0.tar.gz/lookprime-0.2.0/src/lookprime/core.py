import os
import time
from typing import Optional, Protocol, Tuple

from .config import load_config, save_best_chunk


class MaskLike(Protocol):
    limit: int
    def __getitem__(self, idx: int) -> int: ...


def sieve_odd_mask(limit: int) -> bytearray:
    """
    Returns a bytearray mask for odd numbers only:
      mask[i] == 1  <=>  (2*i + 1) is prime
    """
    if limit < 2:
        return bytearray(b"\x00")

    size = (limit // 2) + 1
    mask = bytearray(b"\x01") * size
    mask[0] = 0  # 1 is not prime

    p = 3
    while p * p <= limit:
        if mask[p >> 1]:
            start = p * p
            step = 2 * p
            for x in range(start, limit + 1, step):
                mask[x >> 1] = 0
        p += 2

    return mask


def _read_linux_cpu_mhz() -> Optional[float]:
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.lower().startswith("cpu mhz"):
                    return float(line.split(":")[1].strip())
    except Exception:
        return None
    return None


def _estimate_cpu_ghz() -> float:
    mhz = _read_linux_cpu_mhz()
    if mhz and mhz > 100:
        return mhz / 1000.0
    return 3.0


def _measure_perf_counter_cost(iterations: int = 120_000) -> float:
    """
    Average seconds per perf_counter call.
    """
    t0 = time.perf_counter()
    x = 0.0
    for _ in range(iterations):
        x += time.perf_counter()
        x += time.perf_counter()
    t1 = time.perf_counter()
    _ = x
    return (t1 - t0) / (2.0 * iterations)


def _base_chunk_from_mask_bytes(mask_bytes: int) -> int:
    # High-biased base, but not insane.
    if mask_bytes <= 4_000_000:
        return 65536
    if mask_bytes <= 32_000_000:
        return 131072
    if mask_bytes <= 128_000_000:
        return 262144
    return 524288


def autotune_chunk(
    mask_bytes: int,
    cpu_features: Optional[set[str]] = None,
    *,
    prefer_large: bool = True,
    micro_tune: bool = True,
    persist: bool = True,
) -> int:
    """
    Autotune time-check chunk size.
    Improvements:
      - considers cached best chunk for this machine
      - candidate search is skewed downward (since your data shows optimum can be smaller)
      - can persist best chunk to cache/config.json
    """

    # User override wins
    env = os.environ.get("LOOKPRIME_CHUNK")
    if env and env.isdigit():
        return int(env)

    # Persisted best chunk per machine
    cfg = load_config()
    if cfg.best_chunk and cfg.best_chunk > 0:
        return int(cfg.best_chunk)

    feats = cpu_features or set()
    base = _base_chunk_from_mask_bytes(mask_bytes)

    if "avx512f" in feats:
        base = int(base * 1.5)
    elif "avx2" in feats:
        base = int(base * 1.25)

    pc_cost = _measure_perf_counter_cost()
    ghz = _estimate_cpu_ghz()

    score = (pc_cost / 50e-9) * (ghz / 3.0)

    if prefer_large:
        if score > 2.5:
            base = int(base * 1.5)
        elif score > 1.5:
            base = int(base * 1.25)
        elif score < 0.7:
            base = int(base * 1.1)
    else:
        if score > 2.5:
            base = int(base * 1.25)
        elif score < 0.7:
            base = int(base * 0.9)

    base = max(base, 16384)
    base = min(base, 1_048_576)
    base = (base // 1024) * 1024

    if not micro_tune:
        if persist:
            save_best_chunk(base)
        return base

    # Key improvement: search downward more aggressively
    candidates = sorted(set([
        max(16384, base // 4),
        max(16384, base // 2),
        base,
        min(1_048_576, int(base * 1.25)),
        min(1_048_576, int(base * 1.5)),
    ]))

    probe_seconds = 0.03
    best = base
    best_rate = -1.0

    for ch in candidates:
        t_end = time.perf_counter() + probe_seconds
        n = 3
        loops = 0
        dummy = 0
        while True:
            stop = n + 2 * ch
            while n < stop:
                dummy ^= (n & 1)
                n += 2
            loops += 1
            if time.perf_counter() >= t_end:
                break
        _ = dummy
        rate = (loops * ch) / probe_seconds
        if rate > best_rate:
            best_rate = rate
            best = ch

    best = (best // 1024) * 1024
    if persist:
        save_best_chunk(best)
    return best


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
