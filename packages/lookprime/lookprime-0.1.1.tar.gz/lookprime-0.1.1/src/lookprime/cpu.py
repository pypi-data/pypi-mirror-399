from __future__ import annotations

import os
import platform
import subprocess
from typing import Dict, Set


def _parse_cpuinfo_flags_linux() -> Set[str]:
    flags: Set[str] = set()
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.lower().startswith("flags"):
                    # "flags : a b c"
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        flags.update(parts[1].strip().split())
                    break
    except Exception:
        pass
    return flags


def _parse_sysctl_flags_macos() -> Set[str]:
    flags: Set[str] = set()
    try:
        out = subprocess.check_output(
            ["sysctl", "-a"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1.5,
        )
        # common keys:
        # machdep.cpu.features
        # machdep.cpu.leaf7_features
        for line in out.splitlines():
            low = line.lower()
            if low.startswith("machdep.cpu.features") or low.startswith("machdep.cpu.leaf7_features"):
                _, v = line.split(":", 1)
                flags.update(v.strip().lower().split())
    except Exception:
        pass
    return flags


def _parse_wmic_windows() -> Set[str]:
    # Windows doesn't expose AVX flags cleanly via stdlib.
    # We do best-effort: check architecture + vendor/model; leave flags mostly empty.
    return set()


def detect_cpu_features() -> Set[str]:
    """
    Returns a set of lowercased feature tokens (best-effort).
    On Linux: parses /proc/cpuinfo flags.
    On macOS: uses sysctl machdep.cpu.*.
    On Windows: limited in stdlib; returns minimal info.
    """
    sysname = platform.system().lower()
    if sysname == "linux":
        return {f.lower() for f in _parse_cpuinfo_flags_linux()}
    if sysname == "darwin":
        return {f.lower() for f in _parse_sysctl_flags_macos()}
    if sysname == "windows":
        return _parse_wmic_windows()
    return set()


def cpu_summary() -> Dict[str, str]:
    """
    Human-readable summary useful for benchmarks.
    """
    feats = detect_cpu_features()
    arch = platform.machine()
    impl = platform.python_implementation()
    pyver = platform.python_version()
    osname = f"{platform.system()} {platform.release()}"
    bits = "64-bit" if (platform.architecture()[0] == "64bit") else "32-bit"

    # Common SIMD features to highlight if present
    highlight = []
    for k in ("avx512f", "avx2", "avx", "sse4_2", "sse4_1", "ssse3", "sse2"):
        if k in feats:
            highlight.append(k)

    return {
        "os": osname,
        "arch": f"{arch} ({bits})",
        "python": f"{impl} {pyver}",
        "simd": ", ".join(highlight) if highlight else "(unknown/none detected)",
        "cache_dir": _cache_dir_string(),
    }


def _cache_dir_string() -> str:
    # avoid circular import: compute cache similarly
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        return str((base and (os.path.join(base, "lookprime", "Cache"))) or os.path.join(os.path.expanduser("~"), "AppData", "Local", "lookprime", "Cache"))
    if platform.system().lower() == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Caches", "lookprime")
    xdg = os.environ.get("XDG_CACHE_HOME")
    return os.path.join(xdg, "lookprime") if xdg else os.path.join(os.path.expanduser("~"), ".cache", "lookprime")
