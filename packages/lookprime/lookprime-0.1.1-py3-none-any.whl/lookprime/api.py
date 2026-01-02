from __future__ import annotations

from typing import Optional

from .mask import open_mask, sieve_to_cache

DEFAULT_LIMIT = 100_000_000

_mask = None  # global singleton mmap mask view


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
    Fast primality test via odd-only lookup in an mmap-backed cached sieve.

    - If no cache exists, builds to DEFAULT_LIMIT (or the provided limit).
    - If n exceeds the current sieve limit, raises ValueError.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if (n & 1) == 0:
        return False

    use_limit = limit or DEFAULT_LIMIT
    mask = _ensure_mask(use_limit)

    if n > mask.limit:
        raise ValueError(
            f"isprime({n}) exceeds sieve limit {mask.limit}. "
            f"Rebuild with a higher limit (e.g. lookprime build --limit {n})."
        )

    return bool(mask[n >> 1])
