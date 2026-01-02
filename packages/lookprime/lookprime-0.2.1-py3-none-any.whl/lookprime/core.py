# src/lookprime/core.py
from __future__ import annotations

import json
import os
import platform
import time
from pathlib import Path
from typing import Optional, Protocol, Tuple


class MaskLike(Protocol):
    limit: int
    def __getitem__(self, idx: int) -> int: ...


# ----------------------------
# Auto-tune + persistence
# ----------------------------

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
    Measures overhead of calling perf_counter() twice in a tight loop.
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
    """
    Baseline chunk based on bitset payload size (cache pressure proxy).
    """
    if mask_bytes <= 4_000_000:
        return 65536
    if mask_bytes <= 32_000_000:
        return 131072
    if mask_bytes <= 128_000_000:
        return 262144
    return 524288


def _tuning_path() -> Path:
    # Local import prevents circular imports.
    from .mask import cache_dir
    return cache_dir() / "tuning.json"


def _machine_key() -> str:
    parts = [
        platform.system(),
        platform.release(),
        platform.machine(),
        platform.processor() or "",
        platform.python_implementation(),
        platform.python_version(),
    ]
    return "|".join(parts)


def _load_persisted_chunk() -> Optional[int]:
    try:
        p = _tuning_path()
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("machine_key") != _machine_key():
            return None
        ch = data.get("best_chunk")
        if isinstance(ch, int) and ch > 0:
            return ch
    except Exception:
        return None
    return None


def _save_persisted_chunk(chunk: int) -> None:
    try:
        p = _tuning_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "machine_key": _machine_key(),
            "best_chunk": int(chunk),
            "saved_at_unix": int(time.time()),
        }
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        # best-effort
        pass


def autotune_chunk(
    mask_bytes: int,
    cpu_features: Optional[set[str]] = None,
    *,
    prefer_large: bool = True,
    micro_tune: bool = True,
    persist: bool = True,
) -> int:
    """
    Autotune chunk size for time-check amortization.

    Improvements:
      - loads persisted best chunk per machine
      - candidate sweep includes smaller chunks (often best)
      - micro-probe picks best in ~30ms
      - persists winner

    Override:
      - env LOOKPRIME_CHUNK=NN forces NN
    """
    env = os.environ.get("LOOKPRIME_CHUNK")
    if env and env.isdigit():
        return int(env)

    if persist:
        cached = _load_persisted_chunk()
        if cached is not None:
            return cached

    feats = cpu_features or set()
    base = _base_chunk_from_mask_bytes(mask_bytes)

    # Slight upward bias for SIMD, but we'll still test lower candidates
    if "avx512f" in feats:
        base = int(base * 1.5)
    elif "avx2" in feats:
        base = int(base * 1.25)

    # Timer overhead + cpu speed heuristic
    pc_cost = _measure_perf_counter_cost()
    ghz = _estimate_cpu_ghz()
    score = (pc_cost / 50e-9) * (ghz / 3.0)

    if prefer_large:
        if score > 2.5:
            base = int(base * 1.25)
        elif score < 0.7:
            base = int(base * 0.95)

    base = max(base, 32768)
    base = min(base, 1_048_576)
    base = (base // 1024) * 1024

    if not micro_tune:
        if persist:
            _save_persisted_chunk(base)
        return base

    # Key improvement: include smaller candidates aggressively
    candidates = sorted(set([
        32768,
        max(32768, base // 4),
        max(32768, base // 2),
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
        _save_persisted_chunk(best)
    return best


# ----------------------------
# Timed scan benchmark helper
# ----------------------------

def count_primes_for_duration(
    mask: MaskLike,
    duration: float,
    start_n: int = 1,
    chunk: int = 32768,
) -> Tuple[int, int]:
    """
    Counts prime hits by lookup for 'duration' seconds, starting at n=start_n.
    Avoids perf_counter() per iteration by checking time in chunks.
    Assumes mask supports odd index lookups: mask[n>>1] returns 0/1.
    """
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
