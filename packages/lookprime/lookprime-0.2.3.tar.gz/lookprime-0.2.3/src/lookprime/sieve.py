# src/lookprime/sieve.py
from __future__ import annotations


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
