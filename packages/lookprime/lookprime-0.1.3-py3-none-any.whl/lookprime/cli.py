from __future__ import annotations

import argparse
import math
import os
import statistics
import time
from pathlib import Path

from .core import count_primes_for_duration, autotune_chunk
from .cpu import cpu_summary, detect_cpu_features
from .mask import cache_dir, default_mask_path, open_mask, sieve_to_cache
from .api import cache_info, clear_cache, isprime, factorint, DEFAULT_LIMIT


def cmd_info(args: argparse.Namespace) -> int:
    print("System")
    print("------")
    info = cpu_summary()
    for k, v in info.items():
        print(f"{k:>14}: {v}")
    print()

    ci = cache_info()
    print("Cache")
    print("-----")
    print(f"{'cache_dir':>14}: {ci.cache_dir}")
    print(f"{'default_limit':>14}: {ci.default_limit:,}")
    print(f"{'open_mask':>14}: {ci.current_mask_limit:,}" if ci.current_mask_limit else f"{'open_mask':>14}: (none)")
    print()

    print("Masks")
    print("-----")
    if not ci.masks:
        print("(none)")
        return 0

    for path, lim in ci.masks:
        lim_s = f"{lim:,}" if lim and lim > 0 else "?"
        print(f"- limit={lim_s}  file={path}")
    return 0


def cmd_clear_cache(args: argparse.Namespace) -> int:
    deleted = clear_cache()
    print(f"Deleted {deleted} cached mask file(s).")
    return 0


def cmd_isprime(args: argparse.Namespace) -> int:
    n = int(args.n)
    lim = int(args.limit) if args.limit is not None else None
    print(isprime(n, limit=lim))
    return 0


def cmd_factor(args: argparse.Namespace) -> int:
    n = int(args.n)
    lim = int(args.limit) if args.limit is not None else None
    print(factorint(n, limit=lim))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    limit = int(args.limit)
    out: Path

    if args.output:
        out = Path(args.output)
    else:
        out = default_mask_path(limit)

    if not args.force and out.exists():
        print(f"Mask already exists: {out}")
        return 0

    print(f"Cache dir: {cache_dir()}")
    print(f"Building mask LIMIT={limit:,} ...")
    t0 = time.perf_counter()

    if not args.output:
        path = sieve_to_cache(limit, force=args.force)
        t1 = time.perf_counter()
        print(f"Saved: {path}")
        print(f"Build time: {t1 - t0:.3f}s")
        return 0

    # Build into cache (bitset format) then move to requested output path
    path = sieve_to_cache(limit, force=True)
    Path(path).replace(out)
    t1 = time.perf_counter()
    print(f"Saved: {out.resolve()}")
    print(f"Build time: {t1 - t0:.3f}s")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    limit = int(args.limit)
    duration = float(args.duration)
    iterations = int(args.iterations)

    print("System")
    print("------")
    info = cpu_summary()
    for k, v in info.items():
        print(f"{k:>10}: {v}")
    print()

    # choose mask path
    if args.mask:
        path = Path(args.mask)
        if not path.exists():
            raise SystemExit(f"Mask file not found: {path}")
    else:
        path = sieve_to_cache(limit, force=args.force_build)

    print(f"Using mask: {path}")
    print("Opening mask (mmap)...")
    t0 = time.perf_counter()
    mv = open_mask(path)
    t1 = time.perf_counter()
    print(f"Opened in {t1 - t0:.3f}s. Limit={mv.limit:,}  bytes={len(mv):,}")

    # chunk selection
    env_chunk = os.environ.get("LOOKPRIME_CHUNK")
    env_chunk_val = int(env_chunk) if (env_chunk and env_chunk.isdigit()) else None

    if args.chunk is not None:
        chunk = int(args.chunk)
        chunk_note = ""
    elif env_chunk_val is not None:
        chunk = env_chunk_val
        chunk_note = " (env)"
    else:
        feats = detect_cpu_features()
        chunk = autotune_chunk(mask_bytes=len(mv), cpu_features=feats)
        chunk_note = " (auto)"

    print(f"Chunk: {chunk:,}{chunk_note}")
    print("Tip: set LOOKPRIME_CHUNK=65536 to change defaults globally.\n")

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

    inf = sub.add_parser("info", help="Show CPU + cache + mask info")
    inf.set_defaults(func=cmd_info)

    cc = sub.add_parser("clear-cache", help="Delete cached mask files")
    cc.set_defaults(func=cmd_clear_cache)

    ip = sub.add_parser("isprime", help="Check primality of a number")
    ip.add_argument("n", type=int, help="Number to test")
    ip.add_argument("--limit", type=int, default=None, help="Ensure sieve covers at least this limit")
    ip.set_defaults(func=cmd_isprime)

    fac = sub.add_parser("factor", help="Factor an integer into prime powers")
    fac.add_argument("n", type=int, help="Integer to factor")
    fac.add_argument("--limit", type=int, default=None, help="Ensure sieve covers at least this limit")
    fac.set_defaults(func=cmd_factor)

    bld = sub.add_parser("build", help="Build and cache a prime lookup mask (bitset + mmap)")
    bld.add_argument("--limit", type=int, required=True, help="Max n supported by lookup")
    bld.add_argument("--output", type=str, default=None, help="Write to this path (default: cache)")
    bld.add_argument("--force", action="store_true", help="Rebuild even if output exists")
    bld.set_defaults(func=cmd_build)

    b = sub.add_parser("benchmark", help="Benchmark prime lookup speed (uses mmap cache)")
    b.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Limit (used for cache if --mask not set)",
    )
    b.add_argument("--mask", type=str, default=None, help="Use a specific mask file instead of cache")
    b.add_argument("--duration", type=float, default=1.0, help="Seconds per iteration")
    b.add_argument("--iterations", type=int, default=25, help="Number of iterations")
    b.add_argument("--chunk", type=int, default=None, help="Time-check granularity (auto if omitted)")
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
