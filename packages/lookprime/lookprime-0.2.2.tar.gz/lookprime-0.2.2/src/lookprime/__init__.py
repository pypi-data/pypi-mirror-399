# src/lookprime/__init__.py
from __future__ import annotations

from .core import (
    count_primes_for_duration,
    autotune_chunk,
)

from .sieve import (
    sieve_odd_mask,
)

from .mask import (
    MaskView,
    cache_dir,
    default_mask_path,
    open_mask,
    sieve_to_cache,
)

from .cpu import (
    detect_cpu_features,
    cpu_summary,
)

from .api import (
    DEFAULT_LIMIT,
    MAX_SIEVE_LIMIT,
    isprime,
    isprime_many,
    primerange,
    randprime,
    primepi,
    prime,
    prevprime,
    nextprime,
    primes_up_to,
    primes_upto,
    primes,
    factorint,
    cache_info,
    clear_cache,
    CacheInfo,
)

__all__ = [
    # core
    "count_primes_for_duration",
    "autotune_chunk",

    # sieve
    "sieve_odd_mask",

    # mask / cache
    "MaskView",
    "cache_dir",
    "default_mask_path",
    "open_mask",
    "sieve_to_cache",

    # cpu
    "detect_cpu_features",
    "cpu_summary",

    # api
    "DEFAULT_LIMIT",
    "MAX_SIEVE_LIMIT",
    "isprime",
    "isprime_many",
    "primerange",
    "randprime",
    "primepi",
    "prime",
    "prevprime",
    "nextprime",
    "primes_up_to",
    "primes_upto",
    "primes",
    "factorint",
    "cache_info",
    "clear_cache",
    "CacheInfo",
]
