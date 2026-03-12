"""Tests for Phase 6b: config() context manager."""
import random
import pytest
import quantia as qu
from quantia._config import get_config


def test_default_n_samples():
    assert get_config().n_samples == 1000

def test_config_overrides_n_samples():
    with qu.config(n_samples=250):
        pf = qu.ProbUnitFloat.normal(0, 1, "m")
        assert pf._n == 250

def test_config_restores_after_exit():
    with qu.config(n_samples=500):
        pass
    assert get_config().n_samples == 1000

def test_config_nesting():
    with qu.config(n_samples=800):
        with qu.config(n_samples=200):
            inner = get_config().n_samples
        outer = get_config().n_samples
    assert inner == 200
    assert outer == 800

def test_config_seed_reproducibility():
    with qu.config(n_samples=100, seed=42):
        a = qu.ProbUnitFloat.uniform(0, 1, "1")
    with qu.config(n_samples=100, seed=42):
        b = qu.ProbUnitFloat.uniform(0, 1, "1")
    assert list(a._samples) == pytest.approx(list(b._samples))

def test_correlated_source_uses_config():
    with qu.config(n_samples=300):
        src = qu.CorrelatedSource(n_vars=2, rho=0.5)
        x   = src.draw(0, "normal", "m", mean=0, std=1)
        assert x._n == 300