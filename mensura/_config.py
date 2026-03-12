"""
mensura/_config.py
==================
Thread-safe global configuration.

Usage
-----
with mensura.config(n_samples=5000, seed=42):
    x = ProbUnitFloat.normal(10, 1, "m")   # uses n=5000
"""
from __future__ import annotations
import random
import threading
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class _Config:
    n_samples: int = 1000
    seed: int | None = None


_thread_local  = threading.local()
_default_config = _Config()


def get_config() -> _Config:
    """Return the innermost active config (thread-local stack or global default)."""
    stack = getattr(_thread_local, "stack", None)
    return stack[-1] if stack else _default_config


@contextmanager
def config(n_samples: int | None = None, seed: int | None = None):
    """
    Context manager for temporary mensura configuration.

    Parameters
    ----------
    n_samples : int, optional
        Default Monte Carlo sample count for ProbUnitFloat / ProbUnitArray factories.
    seed : int, optional
        Sets random.seed() on entry for reproducible results.

    Example
    -------
    with mensura.config(n_samples=5000, seed=42):
        x = ProbUnitFloat.normal(10, 1, "m")
        y = ProbUnitFloat.uniform(0, 1, "s")
    # back to previous config here
    """
    current = get_config()
    new = _Config(
        n_samples=n_samples if n_samples is not None else current.n_samples,
        seed=seed,
    )
    stack = getattr(_thread_local, "stack", None)
    if stack is None:
        _thread_local.stack = stack = []
    stack.append(new)
    if seed is not None:
        random.seed(seed)
    try:
        yield new
    finally:
        stack.pop()