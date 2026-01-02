from __future__ import annotations

import argparse
import math
import statistics
import time
from pathlib import Path

from .core import count_primes_for_duration
from .mask import cache_dir, default_mask_path, open_mask, sieve_to_cache, write_mask_file
from .cpu import cpu_summary


def cmd_build(args: argparse.Namespace) -> int:
    limit = args.limit
    out: Path

    if args.output:
        out = Path(args.output)
    else:
        out = default_mask_path(limit)

    # build (or rebuild) into destination
    if not args.force and out.exists():
        print(f"Mask already exists: {out}")
        return 0

    print(f"Cache dir: {cache_dir()}")
    print(f"Building mask LIMIT={limit:,} ...")
    t0 = time.perf_counter()

    # Build via sieve_to_cache if we're targeting default cache path,
    # otherwise build and write to the chosen output.
    if not args.output:
        path = sieve_to_cache(limit, force=args.force)
        t1 = time.perf_counter()
        print(f"Saved: {path}")
        print(f"Build time: {t1 - t0:.3f}s")
        return 0

    # custom path:
    from .core import sieve_odd_mask
    mask = sieve_odd_mask(limit)
    write_mask_file(out, limit=limit, mask_bytes=bytes(mask))
    t1 = time.perf_counter()
    print(f"Saved: {out.resolve()}")
    print(f"Build time: {t1 - t0:.3f}s")
    print(f"Mask size: {len(mask):,} bytes")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    limit = args.limit
    duration = args.duration
    iterations = args.iterations
    chunk = args.chunk

    print("System")
    print("------")
    info = cpu_summary()
    for k, v in info.items():
        print(f"{k:>10}: {v}")
    print()

    # Choose mask path:
    if args.mask:
        path = Path(args.mask)
        if not path.exists():
            raise SystemExit(f"Mask file not found: {path}")
    else:
        # auto-cache: reuse if present, else build
        path = sieve_to_cache(limit, force=args.force_build)

    print(f"Using mask: {path}")
    print("Opening mask (mmap)...")
    t0 = time.perf_counter()
    mv = open_mask(path)
    t1 = time.perf_counter()
    print(f"Opened in {t1 - t0:.3f}s. Limit={mv.limit:,}  bytes={len(mv):,}\n")

    results = []
    max_ns = []

    try:
        for i in range(iterations):
            c, maxn = count_primes_for_duration(mv, duration=duration, start_n=1, chunk=chunk)
            results.append(c)
            max_ns.append(maxn)

            if not args.quiet:
                rate = c / duration if duration > 0 else float("inf")
                print(f"Iter {i+1:>3}/{iterations}: hits={c:,}  hits/s={rate:,.0f}  max_n={maxn:,}")

        avg = statistics.mean(results)
        stdev = statistics.stdev(results) if len(results) > 1 else 0.0
        pse = 100 * ((stdev / math.sqrt(len(results))) / avg) if (len(results) > 1 and avg != 0) else 0.0
        avg_rate = avg / duration if duration > 0 else float("inf")

        print("\nSummary")
        print("-------")
        print(f"Mask file:          {path}")
        print(f"LIMIT:              {mv.limit:,}")
        print(f"DURATION:           {duration:.6f}s")
        print(f"ITERATIONS:         {iterations}")
        print(f"CHUNK:              {chunk}")
        print(f"Average hits:       {avg:,.2f}")
        print(f"Average hits/sec:   {avg_rate:,.2f}")
        print(f"Std dev:            {stdev:,.2f}")
        print(f"Percent Std Error:  {pse:.3f}%")
        print(f"Avg max n reached:  {int(statistics.mean(max_ns)):,}")
        return 0
    finally:
        mv.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lookprime", description="lookprime CLI")
    sub = p.add_subparsers(dest="command", required=True)

    bld = sub.add_parser("build", help="Build and cache a prime lookup mask (mmap-friendly)")
    bld.add_argument("--limit", type=int, required=True, help="Max n supported by lookup")
    bld.add_argument("--output", type=str, default=None, help="Write to this path (default: cache)")
    bld.add_argument("--force", action="store_true", help="Rebuild even if output exists")
    bld.set_defaults(func=cmd_build)

    b = sub.add_parser("benchmark", help="Benchmark prime lookup speed (uses mmap cache)")
    b.add_argument("--limit", type=int, default=100_000_000, help="Limit (used for cache path if --mask not set)")
    b.add_argument("--mask", type=str, default=None, help="Use a specific mask file instead of cache")
    b.add_argument("--duration", type=float, default=1.0, help="Seconds per iteration")
    b.add_argument("--iterations", type=int, default=25, help="Number of iterations")
    b.add_argument("--chunk", type=int, default=32768, help="Time-check granularity")
    b.add_argument("--quiet", action="store_true", help="Only print summary")
    b.add_argument("--force-build", action="store_true", help="Rebuild cache mask even if present")
    b.set_defaults(func=cmd_benchmark)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
