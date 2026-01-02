from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .mask import cache_dir, open_mask, sieve_to_cache

DEFAULT_LIMIT = 100_000_000
_mask = None  # global singleton MaskView


def _ensure_mask(limit: int):
    global _mask
    if _mask is not None:
        if limit <= _mask.limit:
            return _mask
        _mask.close()
        _mask = None

    path = sieve_to_cache(limit)
    _mask = open_mask(path)
    return _mask


def _ensure_for_n(n: int, *, min_limit: Optional[int] = None):
    need = max(n, min_limit or 0, DEFAULT_LIMIT if min_limit is None else 0)
    if need < 2:
        need = 2
    return _ensure_mask(need)


def isprime(n: int, *, limit: Optional[int] = None) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if (n & 1) == 0:
        return False
    mv = _ensure_mask(max(n, limit or 0, DEFAULT_LIMIT if limit is None else 0))
    return bool(mv[n >> 1])


def isprime_many(nums: Iterable[int], *, limit: Optional[int] = None) -> List[bool]:
    """
    Bulk primality checks. Opens/grows mask once and does O(1) lookups.
    """
    xs = list(nums)
    if not xs:
        return []
    mx = max(xs)
    mv = _ensure_mask(max(mx, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    out: List[bool] = []
    for n in xs:
        if n < 2:
            out.append(False)
        elif n == 2:
            out.append(True)
        elif (n & 1) == 0:
            out.append(False)
        elif n > mv.limit:
            # auto-grow if needed (rare if you passed a reasonable limit)
            mv = _ensure_mask(max(n, mv.limit * 2))
            out.append(bool(mv[n >> 1]))
        else:
            out.append(bool(mv[n >> 1]))
    return out


def primerange(a: int, b: int, *, limit: Optional[int] = None) -> List[int]:
    if b <= 2 or b <= a:
        return []
    hi = b - 1
    mv = _ensure_mask(max(hi, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    out: List[int] = []
    if a <= 2 < b:
        out.append(2)

    start = max(a, 3)
    if (start & 1) == 0:
        start += 1

    # scan odds
    for n in range(start, b, 2):
        if mv[n >> 1]:
            out.append(n)
    return out


def randprime(a: int, b: int, *, limit: Optional[int] = None, tries: int = 64) -> int:
    if b <= a:
        raise ValueError("randprime requires b > a")
    if b <= 2:
        raise ValueError("No primes in the given range")

    hi = b - 1
    mv = _ensure_mask(max(hi, limit or 0, DEFAULT_LIMIT if limit is None else 0))
    lo = max(a, 2)

    for _ in range(max(1, tries)):
        x = random.randrange(lo, b)
        if x == 2:
            return 2
        if x < 2 or (x & 1) == 0:
            continue
        if x > mv.limit:
            mv = _ensure_mask(max(x, mv.limit * 2))
        if mv[x >> 1]:
            return x

    primes = primerange(a, b, limit=mv.limit)
    if not primes:
        raise ValueError("No primes exist in the given range")
    return random.choice(primes)


def primepi(n: int, *, limit: Optional[int] = None) -> int:
    """
    Count primes <= n.
    Uses fast bit_count-based counting on the bitset.
    """
    if n < 2:
        return 0
    mv = _ensure_mask(max(n, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    total = 1  # prime 2
    last_odd = n if (n & 1) else (n - 1)
    if last_odd >= 3:
        idx = last_odd >> 1
        # count ones in [1..idx] => count_ones_upto(idx) - bit0
        total += mv.count_ones_upto(idx) - mv.count_ones_upto(0)
    return total


def _nth_prime_upper(n: int) -> int:
    if n <= 1:
        return 2
    if n < 6:
        return 15
    nn = float(n)
    return int(nn * (math.log(nn) + math.log(math.log(nn))) + 10)


def prime(nth: int, *, limit: Optional[int] = None) -> int:
    """
    Return the nth prime (1-indexed). Uses bit scanning to avoid per-bit Python loops.
    """
    if nth < 1:
        raise ValueError("prime(nth) requires nth >= 1")
    if nth == 1:
        return 2

    target = _nth_prime_upper(nth)
    if limit is not None:
        target = max(target, limit)

    mv = _ensure_mask(max(target, DEFAULT_LIMIT))

    while True:
        count = 1  # prime 2

        # iterate set bits for odd primes (i>=1 -> 3)
        for bit_idx in mv.iter_set_bits(1, mv.nbits):
            count += 1
            if count == nth:
                return (bit_idx << 1) + 1

        mv = _ensure_mask(mv.limit * 2)


def prevprime(n: int, *, limit: Optional[int] = None) -> int:
    if n <= 2:
        raise ValueError("No prime exists below 2")

    x = n - 1
    if x == 2:
        return 2
    if (x & 1) == 0:
        x -= 1

    mv = _ensure_mask(max(x, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    while x >= 3:
        if mv[x >> 1]:
            return x
        x -= 2
    return 2


def nextprime(n: int, *, limit: Optional[int] = None) -> int:
    if n < 2:
        return 2

    x = n + 1
    if x <= 2:
        return 2
    if (x & 1) == 0:
        x += 1

    mv = _ensure_mask(max(x, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    while True:
        if x <= mv.limit:
            if mv[x >> 1]:
                return x
            x += 2
        else:
            mv = _ensure_mask(max(x, mv.limit * 2))


def primes_up_to(n: int, *, limit: Optional[int] = None) -> List[int]:
    if n < 2:
        return []
    return primerange(2, n + 1, limit=limit)


def primes_upto(n: int, *, limit: Optional[int] = None) -> List[int]:
    return primes_up_to(n, limit=limit)


def primes(count: int, *, limit: Optional[int] = None) -> List[int]:
    """
    Return first `count` primes. Uses bit scanning for speed.
    """
    if count < 0:
        raise ValueError("primes(count) requires count >= 0")
    if count == 0:
        return []
    if count == 1:
        return [2]

    target = _nth_prime_upper(count)
    if limit is not None:
        target = max(target, limit)

    mv = _ensure_mask(max(target, DEFAULT_LIMIT))

    while True:
        out = [2]
        for bit_idx in mv.iter_set_bits(1, mv.nbits):
            out.append((bit_idx << 1) + 1)
            if len(out) == count:
                return out
        mv = _ensure_mask(mv.limit * 2)


def factorint(n: int, *, limit: Optional[int] = None) -> Dict[int, int]:
    if n == 0:
        raise ValueError("factorint(0) is undefined")

    factors: Dict[int, int] = {}

    if n < 0:
        factors[-1] = 1
        n = -n
    if n == 1:
        return factors

    # factor 2
    e = 0
    while (n & 1) == 0:
        n >>= 1
        e += 1
    if e:
        factors[2] = e
    if n == 1:
        return factors

    r = math.isqrt(n)
    mv = _ensure_mask(max(r, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    p = 3
    while p <= r and n > 1:
        if mv[p >> 1]:
            if n % p == 0:
                e = 0
                while n % p == 0:
                    n //= p
                    e += 1
                factors[p] = e
                r = math.isqrt(n)
        p += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


@dataclass(frozen=True)
class CacheInfo:
    cache_dir: str
    masks: List[Tuple[str, int]]
    current_mask_limit: Optional[int]
    default_limit: int


def cache_info() -> CacheInfo:
    cdir = cache_dir()
    masks: List[Tuple[str, int]] = []

    if cdir.exists():
        for p in sorted(cdir.glob("lookprime_mask_*.lpm")):
            lim = -1
            try:
                lim = int(p.stem.split("_")[-1])
            except Exception:
                lim = -1
            masks.append((str(p), lim))

    current = getattr(_mask, "limit", None) if _mask is not None else None
    return CacheInfo(
        cache_dir=str(cdir),
        masks=masks,
        current_mask_limit=current,
        default_limit=DEFAULT_LIMIT,
    )


def clear_cache(*, close_open_mask: bool = True) -> int:
    global _mask
    if close_open_mask and _mask is not None:
        try:
            _mask.close()
        finally:
            _mask = None

    cdir = cache_dir()
    deleted = 0
    if not cdir.exists():
        return 0

    for p in cdir.glob("lookprime_mask_*.lpm"):
        try:
            p.unlink()
            deleted += 1
        except Exception:
            pass
    return deleted
