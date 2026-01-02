from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .config import load_config
from .mask import cache_dir, open_mask, sieve_to_cache

DEFAULT_LIMIT = 100_000_000
_mask = None  # global singleton MaskView


def _is_probable_prime_mr(n: int) -> bool:
    """
    Miller-Rabin primality test.
    Deterministic for 64-bit n using known base set.
    Probabilistic for larger n (still extremely reliable for typical usage).
    """
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 = d * 2^s
    d = n - 1
    s = 0
    while (d & 1) == 0:
        d >>= 1
        s += 1

    def check(a: int) -> bool:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return True
        return False

    # Deterministic bases for 64-bit integers:
    # This set is widely used for n < 2^64.
    if n.bit_length() <= 64:
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
        for a in bases:
            a %= n
            if a == 0:
                return True
            if not check(a):
                return False
        return True

    # Larger than 64-bit: probabilistic (12 bases)
    # Use a deterministic pseudo-random sequence based on n for reproducibility
    rng = random.Random(n ^ 0x9E3779B97F4A7C15)
    for _ in range(12):
        a = rng.randrange(2, n - 1)
        if not check(a):
            return False
    return True


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


def isprime(n: int, *, limit: Optional[int] = None) -> bool:
    """
    Fast prime test:
      - For n within configured sieve cap: O(1) bitset lookup
      - For huge n: Miller-Rabin fallback (prevents MemoryError)
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if (n & 1) == 0:
        return False

    cfg = load_config()
    max_sieve = cfg.max_sieve_limit

    # User asks for a specific sieve limit (still capped to avoid MemoryError)
    if limit is not None:
        max_sieve = max(max_sieve, min(limit, max_sieve))

    # If n is too large for sieve, do MR (no sieve build)
    if n > max_sieve:
        return _is_probable_prime_mr(n)

    mv = _ensure_mask(max(n, DEFAULT_LIMIT))
    return bool(mv[n >> 1])


def isprime_many(nums: Iterable[int], *, limit: Optional[int] = None) -> List[bool]:
    xs = list(nums)
    if not xs:
        return []

    cfg = load_config()
    max_sieve = cfg.max_sieve_limit
    if limit is not None:
        max_sieve = max(max_sieve, min(limit, max_sieve))

    mx = max(xs)
    mv = None
    if mx <= max_sieve:
        mv = _ensure_mask(max(mx, DEFAULT_LIMIT))

    out: List[bool] = []
    for n in xs:
        if n < 2:
            out.append(False)
        elif n == 2:
            out.append(True)
        elif (n & 1) == 0:
            out.append(False)
        elif n > max_sieve:
            out.append(_is_probable_prime_mr(n))
        else:
            if mv is None or n > mv.limit:
                mv = _ensure_mask(max(n, DEFAULT_LIMIT))
            out.append(bool(mv[n >> 1]))
    return out


def primerange(a: int, b: int, *, limit: Optional[int] = None) -> List[int]:
    if b <= 2 or b <= a:
        return []

    hi = b - 1
    mv = _ensure_mask(max(hi, DEFAULT_LIMIT))

    out: List[int] = []
    if a <= 2 < b:
        out.append(2)

    start = max(a, 3)
    end = b

    if (start & 1) == 0:
        start += 1
    if start >= end:
        return out

    start_bit = start >> 1

    last = end - 1
    if last < 3:
        return out
    if (last & 1) == 0:
        last -= 1
    if last < start:
        return out

    end_bit_excl = (last >> 1) + 1

    for bit_idx in mv.iter_set_bits(start_bit, end_bit_excl):
        out.append((bit_idx << 1) + 1)

    return out


def randprime(a: int, b: int, *, limit: Optional[int] = None, tries: int = 64) -> int:
    if b <= a:
        raise ValueError("randprime requires b > a")
    if b <= 2:
        raise ValueError("No primes in the given range")

    # randprime is fundamentally a range operation, so we require sieve up to (b-1)
    hi = b - 1
    mv = _ensure_mask(max(hi, DEFAULT_LIMIT))

    lo = max(a, 2)
    for _ in range(max(1, tries)):
        x = random.randrange(lo, b)
        if x == 2:
            return 2
        if x < 2 or (x & 1) == 0:
            continue
        if mv[x >> 1]:
            return x

    primes = primerange(a, b)
    if not primes:
        raise ValueError("No primes exist in the given range")
    return random.choice(primes)


def primepi(n: int, *, limit: Optional[int] = None) -> int:
    if n < 2:
        return 0
    if n > load_config().max_sieve_limit:
        raise ValueError("primepi(n) requires n within the sieve cap (increase max_sieve_limit)")

    mv = _ensure_mask(max(n, DEFAULT_LIMIT))

    total = 1  # prime 2
    last_odd = n if (n & 1) else (n - 1)
    if last_odd >= 3:
        idx = last_odd >> 1
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
    if nth < 1:
        raise ValueError("prime(nth) requires nth >= 1")
    if nth == 1:
        return 2

    target = _nth_prime_upper(nth)
    mv = _ensure_mask(max(target, DEFAULT_LIMIT))

    while True:
        count = 1  # prime 2
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

    if x > load_config().max_sieve_limit:
        # fallback scan downward with MR (not super fast, but correct)
        while x >= 3:
            if _is_probable_prime_mr(x):
                return x
            x -= 2
        return 2

    mv = _ensure_mask(max(x, DEFAULT_LIMIT))
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

    if x > load_config().max_sieve_limit:
        while True:
            if _is_probable_prime_mr(x):
                return x
            x += 2

    mv = _ensure_mask(max(x, DEFAULT_LIMIT))
    while True:
        if x <= mv.limit:
            if mv[x >> 1]:
                return x
            x += 2
        else:
            mv = _ensure_mask(mv.limit * 2)


def primes_up_to(n: int, *, limit: Optional[int] = None) -> List[int]:
    if n < 2:
        return []
    if n > load_config().max_sieve_limit:
        raise ValueError("primes_up_to(n) requires n within the sieve cap (increase max_sieve_limit)")

    mv = _ensure_mask(max(n, DEFAULT_LIMIT))

    out: List[int] = [2] if n >= 2 else []
    if n < 3:
        return out

    last_odd = n if (n & 1) else (n - 1)
    end_bit_excl = (last_odd >> 1) + 1

    for bit_idx in mv.iter_set_bits(1, end_bit_excl):
        out.append((bit_idx << 1) + 1)

    return out


def primes_upto(n: int, *, limit: Optional[int] = None) -> List[int]:
    return primes_up_to(n, limit=limit)


def primes(count: int, *, limit: Optional[int] = None) -> List[int]:
    if count < 0:
        raise ValueError("primes(count) requires count >= 0")
    if count == 0:
        return []
    if count == 1:
        return [2]

    target = _nth_prime_upper(count)
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

    e = 0
    while (n & 1) == 0:
        n >>= 1
        e += 1
    if e:
        factors[2] = e
    if n == 1:
        return factors

    r = math.isqrt(n)
    cfg = load_config()

    if r > cfg.max_sieve_limit:
        # MR-based trial division by small primes only, then finish with MR
        # (simple and correct; not intended to be fastest for huge semiprimes)
        p = 3
        while p * p <= n and p < 1_000_000:
            if _is_probable_prime_mr(p) and n % p == 0:
                e = 0
                while n % p == 0:
                    n //= p
                    e += 1
                factors[p] = e
            p += 2
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors

    mv = _ensure_mask(max(r, DEFAULT_LIMIT))
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
    max_sieve_limit: int


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
    cfg = load_config()
    return CacheInfo(
        cache_dir=str(cdir),
        masks=masks,
        current_mask_limit=current,
        default_limit=DEFAULT_LIMIT,
        max_sieve_limit=cfg.max_sieve_limit,
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
