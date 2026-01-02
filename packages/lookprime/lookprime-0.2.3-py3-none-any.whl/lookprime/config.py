from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .mask import cache_dir


def _machine_key() -> str:
    # Key intended to be stable per machine + python build.
    # We avoid serial numbers; just enough to not reuse tune across very different systems.
    return "|".join([
        platform.system(),
        platform.machine(),
        platform.processor() or "unknown-cpu",
        f"py{sys.version_info.major}.{sys.version_info.minor}",
    ])


def _config_path() -> Path:
    return cache_dir() / "config.json"


@dataclass(frozen=True)
class Config:
    machine_key: str
    best_chunk: Optional[int] = None
    max_sieve_limit: int = 100_000_000  # cap sieve growth by default


def load_config() -> Config:
    path = _config_path()
    mk = _machine_key()

    if not path.exists():
        return Config(machine_key=mk)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return Config(machine_key=mk)

        if data.get("machine_key") != mk:
            # Different machine/python: ignore old tune
            return Config(machine_key=mk)

        best_chunk = data.get("best_chunk")
        if isinstance(best_chunk, int) and best_chunk > 0:
            bc = best_chunk
        else:
            bc = None

        msl = data.get("max_sieve_limit")
        if isinstance(msl, int) and msl >= 10_000_000:
            max_sieve = msl
        else:
            max_sieve = 100_000_000

        return Config(machine_key=mk, best_chunk=bc, max_sieve_limit=max_sieve)
    except Exception:
        return Config(machine_key=mk)


def save_best_chunk(chunk: int) -> None:
    if chunk <= 0:
        return
    cdir = cache_dir()
    cdir.mkdir(parents=True, exist_ok=True)
    path = _config_path()
    mk = _machine_key()

    cfg = {
        "machine_key": mk,
        "best_chunk": int(chunk),
        # preserve existing max_sieve_limit if present
        "max_sieve_limit": load_config().max_sieve_limit,
    }
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def set_max_sieve_limit(limit: int) -> None:
    # Used if you later want a CLI to set it.
    if limit < 10_000_000:
        limit = 10_000_000
    cdir = cache_dir()
    cdir.mkdir(parents=True, exist_ok=True)
    path = _config_path()
    mk = _machine_key()

    cfg = {
        "machine_key": mk,
        "best_chunk": load_config().best_chunk,
        "max_sieve_limit": int(limit),
    }
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
