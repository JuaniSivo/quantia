from __future__ import annotations
import array as _array
import math
import operator
import statistics
from typing import Iterable
from mensura._compound import CompoundUnit, _make_unit
from mensura._scalar import UnitFloat, _to_kelvin, _from_kelvin
from mensura._registry import get_unit
from mensura._exceptions import IncompatibleUnitsError
from mensura.prob._distributions import (
    icdf_uniform, icdf_normal, icdf_triangular, icdf_lognormal
)
from mensura.prob._config import _N_SAMPLES

import random


class ProbUnitFloat:
    """
    A probabilistic unit-aware scalar backed by N Monte Carlo samples.

    Independent construction
    ------------------------
    ProbUnitFloat.uniform(low, high, unit)
    ProbUnitFloat.normal(mean, std, unit)
    ProbUnitFloat.triangular(low, mode, high, unit)
    ProbUnitFloat.lognormal(mean, std, unit)

    Correlated construction
    -----------------------
    Use CorrelatedSource (see mensura/prob/_copula.py).
    """

    def __init__(self, samples: Iterable[float], unit):
        self._samples = _array.array('d', (float(v) for v in samples))
        self._unit    = _make_unit(unit)
        self._n       = len(self._samples)

    # ── Internal factory ─────────────────────────────────────────────────────

    @classmethod
    def _from_raw(cls, samples: _array.array, unit) -> "ProbUnitFloat":
        obj          = object.__new__(cls)
        obj._samples = samples
        obj._unit    = _make_unit(unit)
        obj._n       = len(samples)
        return obj

    # ── Public distribution factories ────────────────────────────────────────

    @classmethod
    def _independent(cls, icdf, unit, n, *params) -> "ProbUnitFloat":
        eps = 1e-9
        s   = _array.array('d',
              (icdf(max(eps, min(1-eps, random.random())), *params) for _ in range(n)))
        return cls._from_raw(s, unit)

    @classmethod
    def uniform(cls, low: float, high: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(icdf_uniform, unit, n, low, high)

    @classmethod
    def normal(cls, mean: float, std: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(icdf_normal, unit, n, mean, std)

    @classmethod
    def triangular(cls, low: float, mode: float, high: float,
                   unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(icdf_triangular, unit, n, low, mode, high)

    @classmethod
    def lognormal(cls, mean: float, std: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(icdf_lognormal, unit, n, mean, std)

    @classmethod
    def from_unitfloat(cls, uf: UnitFloat, n=_N_SAMPLES) -> "ProbUnitFloat":
        """Degenerate point distribution — no uncertainty."""
        return cls._from_raw(_array.array('d', [uf.value] * n), uf.unit)

    # ── Statistics ───────────────────────────────────────────────────────────

    def mean(self)     -> UnitFloat: return UnitFloat(sum(self._samples)/self._n,       self._unit)
    def std(self)      -> UnitFloat: return UnitFloat(statistics.stdev(self._samples),   self._unit)
    def variance(self) -> UnitFloat: return UnitFloat(statistics.variance(self._samples),self._unit)
    def median(self)   -> UnitFloat: return UnitFloat(statistics.median(self._samples),  self._unit)
    def min(self)      -> UnitFloat: return UnitFloat(min(self._samples),                self._unit)
    def max(self)      -> UnitFloat: return UnitFloat(max(self._samples),                self._unit)

    def interval(self, confidence: float = 0.95) -> tuple[UnitFloat, UnitFloat]:
        if not 0 < confidence < 1:
            raise ValueError(f"confidence must be in (0, 1), got {confidence}")
        tail = (1 - confidence) / 2
        s    = sorted(self._samples)
        lo   = s[int(math.floor(tail * self._n))]
        hi   = s[int(math.ceil((1-tail) * self._n)) - 1]
        return UnitFloat(lo, self._unit), UnitFloat(hi, self._unit)

    def percentile(self, p: float) -> UnitFloat:
        s   = sorted(self._samples)
        idx = max(0, min(int(round(p / 100 * (self._n - 1))), self._n - 1))
        return UnitFloat(s[idx], self._unit)

    def histogram(self, bins: int = 10) -> tuple[list[float], list[float]]:
        lo, hi = min(self._samples), max(self._samples)
        w      = (hi - lo) / bins
        edges  = [lo + i * w for i in range(bins + 1)]
        counts = [0] * bins
        for v in self._samples:
            counts[min(int((v - lo) / w), bins - 1)] += 1
        return edges, counts

    # ── Conversion ───────────────────────────────────────────────────────────

    def to_si(self) -> "ProbUnitFloat":
        if len(self._unit._f) == 1:
            s, e = next(iter(self._unit._f.items()))
            if get_unit(s).quantity == "temperature" and e == 1:
                return ProbUnitFloat._from_raw(
                    _array.array('d', (_to_kelvin(v, s) for v in self._samples)), "K")
        f = self._unit.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v * f for v in self._samples)),
            self._unit.to_si_compound())

    def to(self, target) -> "ProbUnitFloat":
        tcu = _make_unit(target)
        if not self._unit.is_compatible(tcu):
            raise IncompatibleUnitsError(self._unit, tcu)
        f = self._unit.si_factor() / tcu.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v * f for v in self._samples)), tcu)

    # ── Arithmetic helpers ───────────────────────────────────────────────────

    def _aligned(self, o: "ProbUnitFloat") -> tuple[_array.array, _array.array]:
        if not self._unit.is_compatible(o._unit):
            raise IncompatibleUnitsError(self._unit, o._unit)
        f = o._unit.si_factor() / self._unit.si_factor()
        return self._samples, _array.array('d', (v * f for v in o._samples))

    def _elem(self, o, op, cu=None) -> "ProbUnitFloat":
        a, b = self._aligned(o)
        return ProbUnitFloat._from_raw(
            _array.array('d', (op(x, y) for x, y in zip(a, b))), cu or self._unit)

    def _scalar_op(self, s, op, cu=None) -> "ProbUnitFloat":
        return ProbUnitFloat._from_raw(
            _array.array('d', (op(v, s) for v in self._samples)), cu or self._unit)

    # ── Arithmetic ───────────────────────────────────────────────────────────

    def __add__(self, o):
        if isinstance(o, ProbUnitFloat): return self._elem(o, operator.add)
        if isinstance(o, UnitFloat):     return self.__add__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):   return self._scalar_op(float(o), operator.add)
        return NotImplemented
    def __radd__(self, o): return self.__add__(o)

    def __sub__(self, o):
        if isinstance(o, ProbUnitFloat): return self._elem(o, operator.sub)
        if isinstance(o, UnitFloat):     return self.__sub__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):   return self._scalar_op(float(o), operator.sub)
        return NotImplemented
    def __rsub__(self, o):
        if isinstance(o, (int,float)):
            return ProbUnitFloat._from_raw(
                _array.array('d', (float(o) - v for v in self._samples)), self._unit)
        return NotImplemented

    def __mul__(self, o):
        if isinstance(o, ProbUnitFloat):
            cu = self._unit * o._unit
            cu = CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(
                _array.array('d', (a*b for a,b in zip(self._samples, o._samples))), cu)
        if isinstance(o, UnitFloat):   return self.__mul__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)): return self._scalar_op(float(o), operator.mul)
        return NotImplemented
    def __rmul__(self, o):
        if isinstance(o, (int,float)): return self._scalar_op(float(o), operator.mul)
        return NotImplemented

    def __truediv__(self, o):
        if isinstance(o, ProbUnitFloat):
            cu = self._unit / o._unit
            cu = CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(
                _array.array('d', (a/b for a,b in zip(self._samples, o._samples))), cu)
        if isinstance(o, UnitFloat):   return self.__truediv__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)): return self._scalar_op(float(o), operator.truediv)
        return NotImplemented
    def __rtruediv__(self, o):
        if isinstance(o, (int,float)):
            return ProbUnitFloat._from_raw(
                _array.array('d', (float(o)/v for v in self._samples)), self._unit.invert())
        return NotImplemented

    def __pow__(self, e):
        return ProbUnitFloat._from_raw(
            _array.array('d', (v**e for v in self._samples)), self._unit**e)
    def __neg__(self):
        return ProbUnitFloat._from_raw(
            _array.array('d', (-v for v in self._samples)), self._unit)
    def __abs__(self):
        return ProbUnitFloat._from_raw(
            _array.array('d', (abs(v) for v in self._samples)), self._unit)

    # ── Probabilistic comparisons ─────────────────────────────────────────────

    def prob_lt(self, o) -> float:
        if isinstance(o, ProbUnitFloat):
            a, b = self._aligned(o)
            return sum(x < y for x,y in zip(a,b)) / self._n
        if isinstance(o, UnitFloat):
            return self.prob_lt(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):
            return sum(v < float(o) for v in self._samples) / self._n
        return NotImplemented

    def prob_gt(self, o) -> float: return 1.0 - self.prob_lt(o) - self.prob_eq(o)

    def prob_eq(self, o, tol=1e-9) -> float:
        if isinstance(o, ProbUnitFloat):
            a, b = self._aligned(o)
            return sum(abs(x-y) < tol for x,y in zip(a,b)) / self._n
        return 0.0

    def __repr__(self):
        m = sum(self._samples) / self._n
        s = statistics.stdev(self._samples)
        return (f"ProbUnitFloat(mean={m:.4g}, std={s:.4g}, "
                f"unit='{self._unit}', n={self._n})")
    def __str__(self): return self.__repr__()