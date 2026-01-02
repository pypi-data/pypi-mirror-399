# src/lookprime/api.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .mask import cache_dir, open_mask, sieve_to_cache

DEFAULT_LIMIT = 100_000_000

# Hard safety cap: building a sieve up to huge n (e.g., 1e13) is impossible.
# For n > MAX_SIEVE_LIMIT we fall back to Miller–Rabin primality testing.
MAX_SIEVE_LIMIT = 200_000_000

_mask = None  # global singleton MaskView


# ----------------------------
# Miller–Rabin for large n
# ----------------------------

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def _miller_rabin_witness(a: int, s: int, d: int, n: int) -> bool:
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return False
    return True


def _isprime_mr(n: int) -> bool:
    """
    Deterministic Miller–Rabin for 64-bit integers (and strong probabilistic beyond).
    """
    if n < 2:
        return False

    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    # n-1 = d * 2^s
    d = n - 1
    s = 0
    while (d & 1) == 0:
        s += 1
        d >>= 1

    # Deterministic set for 64-bit
    if n < (1 << 64):
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    else:
        # fallback bases for big ints (probabilistic)
        bases = (2, 3, 5, 7, 11, 13, 17)

    for a in bases:
        a %= n
        if a == 0:
            continue
        if _miller_rabin_witness(a, s, d, n):
            return False
    return True


# ----------------------------
# Mask management
# ----------------------------

def _ensure_mask(limit: int):
    """
    Ensure an mmap mask exists up to min(limit, MAX_SIEVE_LIMIT).
    Prevents catastrophic attempts to sieve up to enormous n.
    """
    global _mask

    want = min(int(limit), MAX_SIEVE_LIMIT)

    if _mask is not None:
        if want <= _mask.limit:
            return _mask
        _mask.close()
        _mask = None

    path = sieve_to_cache(want)
    _mask = open_mask(path)
    return _mask


# ----------------------------
# Public API
# ----------------------------

def isprime(n: int, *, limit: Optional[int] = None) -> bool:
    """
    Test if n is prime.

    - If n <= MAX_SIEVE_LIMIT: O(1) bitset lookup via mmap cache
    - If n >  MAX_SIEVE_LIMIT: Miller–Rabin (fast, no sieve)
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if (n & 1) == 0:
        return False

    target = max(n, limit or 0, DEFAULT_LIMIT if limit is None else 0)

    if target <= MAX_SIEVE_LIMIT:
        mv = _ensure_mask(target)
        return bool(mv[n >> 1])

    return _isprime_mr(n)


def isprime_many(nums: Iterable[int], *, limit: Optional[int] = None) -> List[bool]:
    xs = list(nums)
    if not xs:
        return []
    mx = max(xs)

    target = max(mx, limit or 0, DEFAULT_LIMIT if limit is None else 0)

    # all in sieve range -> fast path
    if target <= MAX_SIEVE_LIMIT:
        mv = _ensure_mask(target)
        out: List[bool] = []
        for n in xs:
            if n < 2:
                out.append(False)
            elif n == 2:
                out.append(True)
            elif (n & 1) == 0:
                out.append(False)
            else:
                out.append(bool(mv[n >> 1]))
        return out

    # fallback per-number (MR for huge)
    return [isprime(n, limit=limit) for n in xs]


def primerange(a: int, b: int, *, limit: Optional[int] = None) -> List[int]:
    """
    Generate primes in the half-open range [a, b).

    Fast path (b-1 <= MAX_SIEVE_LIMIT): iter_set_bits scanning from mmap bitset.
    Fallback (range exceeds MAX_SIEVE_LIMIT): scan odds + Miller–Rabin (slower).
    """
    if b <= 2 or b <= a:
        return []

    hi = b - 1
    target = max(hi, limit or 0, DEFAULT_LIMIT if limit is None else 0)

    out: List[int] = []
    if a <= 2 < b:
        out.append(2)

    if target <= MAX_SIEVE_LIMIT:
        mv = _ensure_mask(target)

        start = max(a, 3)
        end = b

        if (start & 1) == 0:
            start += 1
        if start >= end:
            return out

        start_bit = start >> 1

        last = end - 1
        if (last & 1) == 0:
            last -= 1
        if last < start:
            return out

        end_bit_excl = (last >> 1) + 1

        for bit_idx in mv.iter_set_bits(start_bit, end_bit_excl):
            out.append((bit_idx << 1) + 1)

        return out

    # Beyond sieve cap: MR scan
    n = max(a, 3)
    if (n & 1) == 0:
        n += 1
    while n < b:
        if _isprime_mr(n):
            out.append(n)
        n += 2

    return out


def primes_up_to(n: int, *, limit: Optional[int] = None) -> List[int]:
    """
    Return all primes <= n.

    Note: for n > MAX_SIEVE_LIMIT, returning all primes is not practical
    and would be enormous output. We raise.
    """
    if n < 2:
        return []
    if n > MAX_SIEVE_LIMIT:
        raise ValueError(
            f"primes_up_to({n}) exceeds MAX_SIEVE_LIMIT={MAX_SIEVE_LIMIT}. "
            f"Use primerange(a,b) with smaller bounds or increase MAX_SIEVE_LIMIT."
        )

    mv = _ensure_mask(max(n, limit or 0, DEFAULT_LIMIT if limit is None else 0))

    out: List[int] = [2]
    if n < 3:
        return out

    last_odd = n if (n & 1) else (n - 1)
    end_bit_excl = (last_odd >> 1) + 1

    for bit_idx in mv.iter_set_bits(1, end_bit_excl):
        out.append((bit_idx << 1) + 1)

    return out


def primes_upto(n: int, *, limit: Optional[int] = None) -> List[int]:
    return primes_up_to(n, limit=limit)


def randprime(a: int, b: int, *, limit: Optional[int] = None, tries: int = 64) -> int:
    if b <= a:
        raise ValueError("randprime requires b > a")
    if b <= 2:
        raise ValueError("No primes in the given range")

    lo = max(a, 2)
    hi = b

    # Small range within sieve: sample from list
    if hi <= MAX_SIEVE_LIMIT and (hi - lo) <= 2_000_000:
        ps = primerange(lo, hi, limit=limit)
        if not ps:
            raise ValueError("No primes exist in the given range")
        return random.choice(ps)

    # Random probes (MR used when needed)
    for _ in range(max(1, tries)):
        x = random.randrange(lo, hi)
        if isprime(x, limit=limit):
            return x

    # Fallback: scan
    ps = primerange(lo, hi, limit=limit)
    if not ps:
        raise ValueError("No primes exist in the given range")
    return random.choice(ps)


def primepi(n: int, *, limit: Optional[int] = None) -> int:
    """
    Count primes <= n.

    Requires sieve (fast bit_count). For n > MAX_SIEVE_LIMIT we raise.
    """
    if n < 2:
        return 0
    if n > MAX_SIEVE_LIMIT:
        raise ValueError(
            f"primepi({n}) exceeds MAX_SIEVE_LIMIT={MAX_SIEVE_LIMIT}. "
            f"This function requires a sieve."
        )

    mv = _ensure_mask(max(n, limit or 0, DEFAULT_LIMIT if limit is None else 0))

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
    """
    Return nth prime (1-indexed). Uses sieve scanning; raises if it would exceed MAX_SIEVE_LIMIT.
    """
    if nth < 1:
        raise ValueError("prime(nth) requires nth >= 1")
    if nth == 1:
        return 2

    target = _nth_prime_upper(nth)
    if limit is not None:
        target = max(target, limit)

    if target > MAX_SIEVE_LIMIT:
        raise ValueError(
            f"prime({nth}) needs sieve > MAX_SIEVE_LIMIT={MAX_SIEVE_LIMIT}. "
            f"Increase MAX_SIEVE_LIMIT or implement segmented build."
        )

    mv = _ensure_mask(max(target, DEFAULT_LIMIT))

    count = 1  # prime 2
    for bit_idx in mv.iter_set_bits(1, mv.nbits):
        count += 1
        if count == nth:
            return (bit_idx << 1) + 1

    raise RuntimeError("Unexpected: sieve too small after bound estimate")


def prevprime(n: int, *, limit: Optional[int] = None) -> int:
    if n <= 2:
        raise ValueError("No prime exists below 2")

    x = n - 1
    if x == 2:
        return 2
    if (x & 1) == 0:
        x -= 1

    if x <= MAX_SIEVE_LIMIT:
        mv = _ensure_mask(max(x, limit or 0, DEFAULT_LIMIT if limit is None else 0))
        while x >= 3:
            if mv[x >> 1]:
                return x
            x -= 2
        return 2

    while x >= 3:
        if _isprime_mr(x):
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

    if x <= MAX_SIEVE_LIMIT:
        mv = _ensure_mask(max(x, limit or 0, DEFAULT_LIMIT if limit is None else 0))
        while True:
            if x <= mv.limit:
                if mv[x >> 1]:
                    return x
                x += 2
            else:
                mv = _ensure_mask(min(max(x, mv.limit * 2), MAX_SIEVE_LIMIT))
                if x > mv.limit:
                    break

    while True:
        if _isprime_mr(x):
            return x
        x += 2


def primes(count: int, *, limit: Optional[int] = None) -> List[int]:
    """
    Return first `count` primes. Uses sieve scanning; raises if it would exceed MAX_SIEVE_LIMIT.
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
    if target > MAX_SIEVE_LIMIT:
        raise ValueError(
            f"primes({count}) needs sieve > MAX_SIEVE_LIMIT={MAX_SIEVE_LIMIT}."
        )

    mv = _ensure_mask(max(target, DEFAULT_LIMIT))

    out = [2]
    for bit_idx in mv.iter_set_bits(1, mv.nbits):
        out.append((bit_idx << 1) + 1)
        if len(out) == count:
            return out
    raise RuntimeError("Unexpected: sieve too small after bound estimate")


def factorint(n: int, *, limit: Optional[int] = None) -> Dict[int, int]:
    """
    Factor integer into prime powers. Uses small primes + sieve trial division (if feasible).
    For hard composites beyond sieve range, this will not fully factor without Pollard Rho.
    """
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

    for p in _SMALL_PRIMES[1:]:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            factors[p] = e
    if n == 1:
        return factors

    if _isprime_mr(n):
        factors[n] = factors.get(n, 0) + 1
        return factors

    r = math.isqrt(n)
    if r <= MAX_SIEVE_LIMIT:
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
        if _isprime_mr(n):
            factors[n] = factors.get(n, 0) + 1
        else:
            # Without Pollard Rho, we can't guarantee complete factorization.
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
    return CacheInfo(
        cache_dir=str(cdir),
        masks=masks,
        current_mask_limit=current,
        default_limit=DEFAULT_LIMIT,
        max_sieve_limit=MAX_SIEVE_LIMIT,
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
