"""Shared helpers: hashing, retry, file IO."""
from __future__ import annotations

import functools
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

from src import config

log = logging.getLogger(__name__)

T = TypeVar("T")


def puzzle_hash(text: str) -> str:
    """SHA256 prefix used to dedupe puzzles."""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()[: config.PUZZLE_HASH_LEN]


def retry(
    attempts: int,
    base_delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Exponential-backoff retry decorator."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> T:
            last_exc: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    log.warning("[%s] attempt %d/%d failed: %s", fn.__name__, attempt, attempts, exc)
                    if attempt < attempts:
                        time.sleep(base_delay * (2 ** (attempt - 1)))
            assert last_exc is not None
            raise last_exc

        return wrapped

    return decorator


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def ensure_tmp() -> Path:
    config.TMP_DIR.mkdir(parents=True, exist_ok=True)
    return config.TMP_DIR


def log_error(message: str) -> None:
    """Append a line to data/errors.log so failures are visible in repo."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with config.ERRORS_LOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
