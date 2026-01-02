import time
from typing import Protocol, Tuple


class MaskLike(Protocol):
    """Any mask that supports byte indexing (0/1) for odd numbers."""
    limit: int

    def __getitem__(self, idx: int) -> int: ...
    def __len__(self) -> int: ...


def sieve_odd_mask(limit: int) -> bytearray:
    """
    Odd-only sieve mask:
      mask[i] == 1  <=>  (2*i + 1) is prime
    So:
      i = n >> 1, for odd n
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


def count_primes_for_duration(
    mask: MaskLike,
    duration: float,
    start_n: int = 1,
    chunk: int = 32768,
) -> Tuple[int, int]:
    """
    Counts prime 'hits' by lookup for `duration` seconds starting at n=start_n.
    Uses odd-only mask, and checks the clock in chunks to reduce overhead.
    Returns (count, next_n).
    """
    end_time = time.perf_counter() + duration
    max_n = mask.limit

    n = start_n
    count = 0

    # count prime 2 if we start below it
    if n <= 2 and max_n >= 2:
        count += 1
        n = 3

    if n % 2 == 0:
        n += 1

    while True:
        stop = n + 2 * chunk
        while n < stop:
            if n > max_n:
                return count, n
            count += mask[n >> 1]  # 0 or 1
            n += 2
        if time.perf_counter() >= end_time:
            return count, n
