from __future__ import annotations

import argparse
import math
import os
import statistics
import time
import sys
from pathlib import Path

from .core import count_primes_for_duration, autotune_chunk
from .cpu import cpu_summary, detect_cpu_features
from .mask import cache_dir, default_mask_path, open_mask, sieve_to_cache
from .api import cache_info, clear_cache, isprime, factorint, DEFAULT_LIMIT
from .config import load_config


# Maximum integer size (in bits) accepted by the CLI 'factor' command.
# Above this size, lookprime may return an unfactored composite cofactor, which is misleading in CLI output.
MAX_FACTOR_BITS = 128


def _check_factor_input_size(n: int) -> None:
    n_abs = abs(int(n))
    bits = n_abs.bit_length()
    if bits > MAX_FACTOR_BITS:
        raise ValueError(
            f"integer too large to factor reliably ({bits} bits); max is {MAX_FACTOR_BITS} bits"
        )


def mean(xs):
    return statistics.mean(xs) if xs else 0.0


def stdev(xs):
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def pse(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    if m == 0:
        return 0.0
    return 100.0 * (stdev(xs) / (len(xs) ** 0.5)) / m


def bytes_fmt(n: int | None) -> str:
    if n is None:
        return "n/a"
    n = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024.0:
            return f"{n:,.2f} {unit}"
        n /= 1024.0
    return f"{n:,.2f} PB"


def _human_seconds(s: float) -> str:
    if s < 1e-6:
        return f"{s*1e9:.1f} ns"
    if s < 1e-3:
        return f"{s*1e6:.1f} µs"
    if s < 1:
        return f"{s*1e3:.1f} ms"
    return f"{s:.3f} s"


def cmd_info(args: argparse.Namespace) -> int:
    cfg = load_config()
    feats = detect_cpu_features()

    print("lookprime")
    print("--------")
    print(f"{'version':>14}: {getattr(cfg, 'version', '(unknown)')}")
    print(f"{'python':>14}: {sys.version.split()[0]}")
    print(f"{'platform':>14}: {sys.platform}")
    print(f"{'cache_dir':>14}: {cache_dir()}")
    print()

    print("CPU")
    print("---")
    print(cpu_summary(feats))
    print()

    print("Config")
    print("------")
    print(f"{'default_limit':>14}: {DEFAULT_LIMIT:,}")
    print(f"{'config_path':>14}: {cfg.path}")
    print()

    return 0


def cmd_cache(args: argparse.Namespace) -> int:
    if args.clear:
        clear_cache()
        print("Cache cleared.")
        return 0

    ci = cache_info()
    print("Cache")
    print("-----")
    print(f"{'cache_dir':>14}: {ci.cache_dir}")
    print(f"{'default_limit':>14}: {ci.default_limit:,}")
    print(f"{'max_sieve':>14}: {ci.max_sieve_limit:,}")
    print(
        f"{'open_mask':>14}: {ci.current_mask_limit:,}"
        if ci.current_mask_limit
        else f"{'open_mask':>14}: (none)"
    )
    print()

    print("Masks")
    print("-----")
    if not ci.masks:
        print("(none)")
        return 0

    for path, lim in ci.masks:
        p = Path(path)
        sz = p.stat().st_size if p.exists() else 0
        print(f"{lim:>12,}  {bytes_fmt(sz):>10}  {path}")

    return 0


def cmd_isprime(args: argparse.Namespace) -> int:
    n = int(args.n)
    lim = int(args.limit) if args.limit is not None else None
    print(isprime(n, limit=lim))
    return 0


def cmd_factor(args: argparse.Namespace) -> int:
    n = int(args.n)
    lim = int(args.limit) if args.limit is not None else None
    try:
        _check_factor_input_size(n)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        print(
            "hint: use sympy.factorint() or a specialized factoring tool for larger integers",
            file=sys.stderr,
        )
        return 2
    print(factorint(n, limit=lim))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    lim = int(args.limit)
    out = args.output
    force = bool(args.force_build)

    if out is None:
        path = sieve_to_cache(lim, force_build=force)
    else:
        path = sieve_to_cache(lim, output_path=Path(out), force_build=force)

    print(str(path))
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    lim = int(args.limit)
    duration = float(args.duration)
    iters = int(args.iterations)
    prefer_large = bool(args.prefer_large)
    micro_tune = bool(args.micro_tune)

    path = sieve_to_cache(lim, force_build=False)
    mv = open_mask(path)
    try:
        feats = detect_cpu_features()
        chunk = autotune_chunk(
            mask_bytes=len(mv),
            cpu_features=feats,
            prefer_large=prefer_large,
            micro_tune=micro_tune,
        )

        # Warm up
        _ = count_primes_for_duration(mv, duration=0.05, start_n=1, chunk=chunk)

        counts = []
        times = []
        for _ in range(iters):
            ct, elapsed = count_primes_for_duration(
                mv, duration=duration, start_n=1, chunk=chunk
            )
            counts.append(ct)
            times.append(elapsed)

        pps = [c / t if t > 0 else 0.0 for c, t in zip(counts, times)]
        print("Benchmark")
        print("---------")
        print(f"{'limit':>14}: {lim:,}")
        print(f"{'mask_path':>14}: {path}")
        print(f"{'chunk':>14}: {chunk:,}")
        print(f"{'duration':>14}: {duration:.3f} s")
        print(f"{'iterations':>14}: {iters}")
        print()
        print("Results")
        print("-------")
        print(
            f"{'primes/s':>14}: {mean(pps):,.0f}  (sd {stdev(pps):,.0f}, PSE {pse(pps):.3f}%)"
        )
        print(f"{'elapsed':>14}: {_human_seconds(mean(times))} avg")

        return 0
    finally:
        mv.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lookprime", description="Prime lookup + sieve cache utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    inf = sub.add_parser("info", help="Show lookprime system/config info")
    inf.set_defaults(func=cmd_info)

    c = sub.add_parser("cache", help="Show cache state (or clear it)")
    c.add_argument("--clear", action="store_true", help="Clear all cached masks")
    c.set_defaults(func=cmd_cache)

    ip = sub.add_parser("isprime", help="Primality test (fast under the sieve limit)")
    ip.add_argument("n", type=int, help="Integer to test")
    ip.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Ensure sieve covers at least this limit (capped)",
    )
    ip.set_defaults(func=cmd_isprime)

    fac = sub.add_parser("factor", help="Factor an integer into prime powers")
    fac.add_argument("n", type=int, help="Integer to factor")
    fac.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Ensure sieve covers at least this limit (capped)",
    )
    fac.set_defaults(func=cmd_factor)

    bld = sub.add_parser("build", help="Build and cache a prime lookup mask (bitset + mmap)")
    bld.add_argument("--limit", type=int, required=True, help="Max n supported by lookup")
    bld.add_argument("--output", type=str, default=None, help="Output path (optional)")
    bld.add_argument("--force-build", action="store_true", help="Rebuild cache mask even if present")
    bld.set_defaults(func=cmd_build)

    b = sub.add_parser("benchmark", help="Benchmark scanning speed on your machine")
    b.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Mask limit to benchmark (cache will be created if missing)",
    )
    b.add_argument("--duration", type=float, default=1.0, help="Target duration per iteration (seconds)")
    b.add_argument("--iterations", type=int, default=25, help="Number of benchmark iterations")
    b.add_argument("--prefer-large", action="store_true", help="Prefer larger chunks")
    b.add_argument("--micro-tune", action="store_true", help="Run micro-tuning for chunk selection")
    b.set_defaults(func=cmd_benchmark)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
