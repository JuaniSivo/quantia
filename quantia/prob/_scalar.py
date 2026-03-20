from __future__ import annotations
import array as _array, math, operator, random
from typing import Iterable, Union
from quantia._compound import CompoundUnit, _make_unit
from quantia._scalar import UnitFloat
from quantia._registry import get_unit, AffineUnit
from quantia._exceptions import IncompatibleUnitsError, DimensionError
from quantia.prob._distributions import icdf_uniform, icdf_normal, icdf_triangular, icdf_lognormal
from quantia.prob._copula import _N_SAMPLES


class ProbUnitFloat:
    """An uncertain scalar quantity represented by Monte Carlo samples.

    Stores ``n`` samples drawn from a probability distribution, all
    carrying the same physical unit. Arithmetic between two
    ``ProbUnitFloat`` instances is performed sample-wise, naturally
    propagating correlations introduced by shared inputs.

    Do not construct directly — use the class factories:
    :meth:`uniform`, :meth:`normal`, :meth:`triangular`, :meth:`lognormal`.

    Parameters passed to factories
    --------------------------------
    unit : str or CompoundUnit
        Physical unit shared by all samples.
    n : int, optional
        Monte Carlo sample count. Defaults to the value set by
        :func:`quantia.config` (1 000 if not overridden).

    Examples
    --------
    Basic uncertainty propagation:

    >>> import quantia as qu
    >>> with qu.config(n_samples=5000, seed=42):
    ...     eff      = qu.ProbUnitFloat.uniform(0.88, 0.95, '1')
    ...     power_in = qu.ProbUnitFloat.normal(500.0, 10.0, 'W')
    >>> power_out = eff * power_in
    >>> power_out.mean()
    UnitFloat(457..., 'W')
    >>> lo, hi = power_out.interval(0.90)

    Petroleum OOIP with uncertain Bo:

    >>> with qu.config(seed=0, n_samples=3000):
    ...     Bo = qu.ProbUnitFloat.normal(1.25, 0.05, 'Sm3_res')
    >>> Vp   = qu.Q(1_000_000.0, 'Sm3_res')
    >>> ooip = Vp * 0.75 / (Bo / qu.Q(1.0, 'Sm3_st'))
    >>> ooip.percentile(10)   # P10
    UnitFloat(..., ...)
    """

    def __init__(self, samples: Iterable[float],
                 unit: Union[str, "CompoundUnit"]) -> None:
        self._samples = _array.array('d', (float(v) for v in samples))
        self._unit    = _make_unit(unit)
        self._n       = len(self._samples)
        if self._n == 0:
            raise ValueError("ProbUnitFloat requires at least one sample")

    @classmethod
    def _from_raw(cls, samples, unit):
        obj = object.__new__(cls)
        obj._samples = samples
        obj._unit    = _make_unit(unit)
        obj._n       = len(samples)
        # no _sorted_cache — will be built lazily on first access
        return obj

    # ── 2d: validated factories ───────────────────────────────────────────────

    @classmethod
    def _independent(cls, icdf, unit, n, *params):
        eps=1e-9
        return cls._from_raw(
            _array.array('d',(icdf(max(eps,min(1-eps,random.random())),*params) for _ in range(n))),
            unit)

    @classmethod
    def uniform(cls, low: float, high: float,
                unit: Union[str, "CompoundUnit"],
                n: int | None = None) -> "ProbUnitFloat":
        """Create samples from a uniform distribution U(low, high).

        Parameters
        ----------
        low : float
            Lower bound (inclusive).
        high : float
            Upper bound. Must be strictly greater than ``low``.
        unit : str or CompoundUnit
            Physical unit for all samples.
        n : int, optional
            Sample count. Defaults to active :func:`~quantia.config` value.

        Returns
        -------
        ProbUnitFloat

        Raises
        ------
        ValueError
            If ``low >= high``.

        Examples
        --------
        >>> with qu.config(seed=0):
        ...     eff = qu.ProbUnitFloat.uniform(0.88, 0.95, '1')
        >>> eff.mean().value
        0.915...
        """

        if low >= high:
            raise ValueError(f"uniform requires low < high, got low={low}, high={high}")
        return cls._independent(icdf_uniform, unit, _default_n(n), low, high)

    @classmethod
    def normal(cls, mean: float, std: float,
               unit: Union[str, "CompoundUnit"],
               n: int | None = None) -> "ProbUnitFloat":
        """Create samples from a normal distribution N(mean, std).

        Parameters
        ----------
        mean : float
            Distribution mean.
        std : float
            Standard deviation. Must be strictly positive.
        unit : str or CompoundUnit
            Physical unit for all samples.
        n : int, optional
            Sample count.

        Returns
        -------
        ProbUnitFloat

        Raises
        ------
        ValueError
            If ``std <= 0``.

        Examples
        --------
        >>> with qu.config(seed=42):
        ...     p = qu.ProbUnitFloat.normal(3000.0, 200.0, 'psia')
        >>> p.std().value
        200...
        """

        if std <= 0:
            raise ValueError(f"normal requires std > 0, got std={std}")
        return cls._independent(icdf_normal, unit, _default_n(n), mean, std)

    @classmethod
    def triangular(cls, low: float, mode: float, high: float,
                   unit: Union[str, "CompoundUnit"],
                   n: int | None = None) -> "ProbUnitFloat":
        """Create samples from a triangular distribution.

        Parameters
        ----------
        low : float
            Minimum value.
        mode : float
            Most likely value. Must satisfy ``low <= mode <= high``.
        high : float
            Maximum value. Must be strictly greater than ``low``.
        unit : str or CompoundUnit
            Physical unit for all samples.
        n : int, optional
            Sample count.

        Returns
        -------
        ProbUnitFloat

        Raises
        ------
        ValueError
            If ``low > mode``, ``mode > high``, or ``low == high``.

        Examples
        --------
        >>> with qu.config(seed=1):
        ...     h = qu.ProbUnitFloat.triangular(10.0, 15.0, 22.0, 'm')
        """

        if not (low <= mode <= high):
            raise ValueError(f"triangular requires low <= mode <= high, got ({low}, {mode}, {high})")
        if low == high:
            raise ValueError("triangular requires low < high")
        return cls._independent(icdf_triangular, unit, _default_n(n), low, mode, high)

    @classmethod
    def lognormal(cls, mean: float, std: float,
                  unit: Union[str, "CompoundUnit"],
                  n: int | None = None) -> "ProbUnitFloat":
        """Create samples from a log-normal distribution.

        Parameters
        ----------
        mean : float
            Mean of the underlying normal distribution (i.e. ln X ~ N(mean, std)).
        std : float
            Standard deviation of the underlying normal. Must be > 0.
        unit : str or CompoundUnit
            Physical unit for all samples.
        n : int, optional
            Sample count.

        Returns
        -------
        ProbUnitFloat

        Raises
        ------
        ValueError
            If ``std <= 0``.
        """

        if std <= 0:
            raise ValueError(f"lognormal requires std > 0, got std={std}")
        return cls._independent(icdf_lognormal, unit, _default_n(n), mean, std)

    @classmethod
    def from_unitfloat(cls, uf: "UnitFloat", n: int) -> "ProbUnitFloat":
        return cls._from_raw(_array.array('d',[uf.value]*n), uf.unit)

    # ── Statistics ────────────────────────────────────────────────────────────

    def _welford(self) -> tuple[float, float]:
        """
        Single-pass mean and variance using Welford's online algorithm.
        Returns (mean, variance) without importing statistics.
        """
        n = 0
        mean = 0.0
        M2   = 0.0
        for x in self._samples:
            n    += 1
            delta = x - mean
            mean += delta / n
            M2   += delta * (x - mean)
        if n < 2:
            return mean, 0.0
        return mean, M2 / (n - 1)   # sample variance
    
    @property
    def _sorted(self):
        if not hasattr(self, '_sorted_cache'):
            self._sorted_cache = sorted(self._samples)
        return self._sorted_cache
    
    def mean(self)     -> "UnitFloat":
        """Return the sample mean.

        Returns
        -------
        UnitFloat
            Mean value in the distribution's unit.

        Examples
        --------
        >>> with qu.config(seed=0, n_samples=10000):
        ...     x = qu.ProbUnitFloat.uniform(0.0, 10.0, 'm')
        >>> x.mean().value   # ≈ 5.0
        5.0...
        """
        return UnitFloat(sum(self._samples)/self._n, self._unit)
    
    def std(self)      -> "UnitFloat":
        """Return the sample standard deviation.

        Uses Welford's online algorithm (single pass, numerically stable).

        Returns
        -------
        UnitFloat
            Standard deviation in the distribution's unit.
        """
        _, v = self._welford()
        return UnitFloat(v ** 0.5, self._unit)
    
    def variance(self) -> "UnitFloat":
        _, v = self._welford()
        return UnitFloat(v, self._unit)
    
    def min(self)      -> "UnitFloat":
        return UnitFloat(min(self._samples), self._unit)
    
    def max(self)      -> "UnitFloat":
        return UnitFloat(max(self._samples), self._unit)
    
    def median(self)   -> "UnitFloat":
        """Return the sample median (P50).

        Returns
        -------
        UnitFloat
            Median value in the distribution's unit.
        """

        s   = self._sorted
        mid = self._n // 2
        m   = s[mid] if self._n % 2 else (s[mid - 1] + s[mid]) / 2
        return UnitFloat(m, self._unit)

    def interval(self, confidence: float = 0.95
                 ) -> tuple["UnitFloat", "UnitFloat"]:
        """Return a central confidence interval from the sample distribution.

        Parameters
        ----------
        confidence : float
            Confidence level in (0, 1). Default 0.95 returns the
            P2.5–P97.5 range. Use 0.80 for P10–P90 (common in petroleum).

        Returns
        -------
        tuple of (UnitFloat, UnitFloat)
            ``(lower_bound, upper_bound)`` at the requested confidence level.

        Raises
        ------
        ValueError
            If ``confidence`` is not in (0, 1).

        Examples
        --------
        >>> lo, hi = power_out.interval(0.90)   # P10–P90
        >>> lo, hi = power_out.interval(0.80)   # P10–P90 (petroleum convention)
        """

        if not 0 < confidence < 1:
            raise ValueError(f"confidence must be in (0, 1), got {confidence}")
        tail = (1 - confidence) / 2
        s    = self._sorted
        return (UnitFloat(s[int(math.floor(tail * self._n))], self._unit),
                UnitFloat(s[int(math.ceil((1 - tail) * self._n)) - 1], self._unit))

    def percentile(self, p: float) -> "UnitFloat":
        """Return the p-th percentile of the sample distribution.

        Parameters
        ----------
        p : float
            Percentile value in [0, 100].
            P10 = pessimistic, P50 = median, P90 = optimistic
            (petroleum convention: P10 is the low case).

        Returns
        -------
        UnitFloat
            The p-th percentile in the distribution's unit.

        Raises
        ------
        ValueError
            If ``p`` is not in [0, 100].

        Examples
        --------
        >>> ooip.percentile(10)    # P10 — low case
        UnitFloat(..., 'bbl')
        >>> ooip.percentile(50)    # P50 — base case
        UnitFloat(..., 'bbl')
        >>> ooip.percentile(90)    # P90 — high case
        UnitFloat(..., 'bbl')
        """
        
        if not 0 <= p <= 100:
            raise ValueError(f"percentile p must be in [0, 100], got {p}")
        s = self._sorted
        return UnitFloat(s[max(0, min(int(round(p / 100 * (self._n - 1))), self._n - 1))], self._unit)

    def histogram(self, bins: int = 10
                  ) -> tuple[list[float], list[int]]:
        if bins < 1: raise ValueError(f"bins must be >= 1, got {bins}")
        lo,hi=min(self._samples),max(self._samples); w=(hi-lo)/bins
        edges=[lo+i*w for i in range(bins+1)]; counts=[0]*bins
        for v in self._samples: counts[min(int((v-lo)/w),bins-1)]+=1
        return edges,counts

    # ── Conversion ────────────────────────────────────────────────────────────

    def to_si(self) -> "ProbUnitFloat":
        if len(self._unit._f) == 1:
            s, e = next(iter(self._unit._f.items()))
            u = get_unit(s)
            if isinstance(u, AffineUnit) and e == 1:
                # Covers all AffineUnit: temperature (°C→K) and pressure (psig→Pa)
                return ProbUnitFloat._from_raw(
                    _array.array('d', (u.to_si_value(v) for v in self._samples)),
                    u.si_unit)
        f = self._unit.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v * f for v in self._samples)),
            self._unit.to_si_compound())

    def to(self, target: Union[str, "CompoundUnit"]) -> "ProbUnitFloat":
        tcu = _make_unit(target)
        src_affine = UnitFloat._is_single_affine(self._unit)
        tgt_affine = UnitFloat._is_single_affine(tcu)

        if src_affine and tgt_affine:
            # Both affine: psig→psia, °C→K, etc. — sample-wise
            return ProbUnitFloat._from_raw(
                _array.array('d', (tgt_affine.from_si_value(
                                    src_affine.to_si_value(v))
                                for v in self._samples)),
                tcu)

        if src_affine:
            # Affine → plain: psia→Pa, psig→kPa, etc.
            si_unit_cu = _make_unit(src_affine.si_unit)
            if not si_unit_cu.is_compatible(tcu):
                raise IncompatibleUnitsError(self._unit, tcu)
            factor = 1.0 / tcu.si_factor()
            return ProbUnitFloat._from_raw(
                _array.array('d', (src_affine.to_si_value(v) * factor
                                for v in self._samples)),
                tcu)

        if tgt_affine:
            # Plain → affine: Pa→psig, etc.
            si_unit_cu = _make_unit(tgt_affine.si_unit)
            if not self._unit.is_compatible(si_unit_cu):
                raise IncompatibleUnitsError(self._unit, tcu)
            factor = self._unit.si_factor()
            return ProbUnitFloat._from_raw(
                _array.array('d', (tgt_affine.from_si_value(v * factor)
                                for v in self._samples)),
                tcu)

        # Both plain
        if not self._unit.is_compatible(tcu):
            raise IncompatibleUnitsError(self._unit, tcu)
        f = self._unit.si_factor() / tcu.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v * f for v in self._samples)), tcu)

    # ── Arithmetic ────────────────────────────────────────────────────────────

    def _aligned(self, o):
        if not self._unit.is_compatible(o._unit): raise IncompatibleUnitsError(self._unit,o._unit)
        f=o._unit.si_factor()/self._unit.si_factor()
        return self._samples,_array.array('d',(v*f for v in o._samples))

    def _elem(self,o,op,cu=None):
        a,b=self._aligned(o)
        return ProbUnitFloat._from_raw(_array.array('d',(op(x,y) for x,y in zip(a,b))),cu or self._unit)

    def _scalar_op(self,s,op,cu=None):
        return ProbUnitFloat._from_raw(_array.array('d',(op(v,s) for v in self._samples)),cu or self._unit)

    def __add__(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                ) -> "ProbUnitFloat":
        if isinstance(o,ProbUnitFloat): return self._elem(o,operator.add)
        if isinstance(o,UnitFloat):     return self.__add__(ProbUnitFloat.from_unitfloat(o,self._n))
        if isinstance(o,(int,float)):   return self._scalar_op(float(o),operator.add)
        return NotImplemented
    def __radd__(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                 ) -> "ProbUnitFloat":
        if isinstance(o, UnitFloat):
            return self.__add__(o)
        return self.__add__(o)
    def __sub__(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                ) -> "ProbUnitFloat":
        if isinstance(o,ProbUnitFloat): return self._elem(o,operator.sub)
        if isinstance(o,UnitFloat):     return self.__sub__(ProbUnitFloat.from_unitfloat(o,self._n))
        if isinstance(o,(int,float)):   return self._scalar_op(float(o),operator.sub)
        return NotImplemented
    def __rsub__(self, o: Union["UnitFloat", int, float]) -> "ProbUnitFloat":
        if isinstance(o, UnitFloat):
            return ProbUnitFloat.from_unitfloat(o, self._n).__sub__(self)
        if isinstance(o, (int, float)):
            return ProbUnitFloat._from_raw(
                _array.array('d', (float(o) - v for v in self._samples)), self._unit)
        return NotImplemented
    def __mul__(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                ) -> "ProbUnitFloat":
        if isinstance(o,ProbUnitFloat):
            cu=self._unit*o._unit; cu=CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(_array.array('d',(a*b for a,b in zip(self._samples,o._samples))),cu)
        if isinstance(o,UnitFloat):   return self.__mul__(ProbUnitFloat.from_unitfloat(o,self._n))
        if isinstance(o,(int,float)): return self._scalar_op(float(o),operator.mul)
        return NotImplemented
    def __rmul__(self, o: Union["UnitFloat", int, float]) -> "ProbUnitFloat":
        if isinstance(o, (int, float, UnitFloat)):
            return self.__mul__(o)
        return NotImplemented
    def __truediv__(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                    ) -> "ProbUnitFloat":
        if isinstance(o,ProbUnitFloat):
            cu=self._unit/o._unit; cu=CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(_array.array('d',(a/b for a,b in zip(self._samples,o._samples))),cu)
        if isinstance(o,UnitFloat):   return self.__truediv__(ProbUnitFloat.from_unitfloat(o,self._n))
        if isinstance(o,(int,float)): return self._scalar_op(float(o),operator.truediv)
        return NotImplemented
    def __rtruediv__(self, o: Union["UnitFloat", int, float]) -> "ProbUnitFloat":
        if isinstance(o, UnitFloat):
            # UnitFloat / ProbUnitFloat — convert UnitFloat to ProbUnitFloat first
            return ProbUnitFloat.from_unitfloat(o, self._n).__truediv__(self)
        if isinstance(o, (int, float)):
            return ProbUnitFloat._from_raw(
                _array.array('d', (float(o) / v for v in self._samples)),
                self._unit.invert())
        return NotImplemented
    def __pow__(self, e: Union[int, float]) -> "ProbUnitFloat":
        return ProbUnitFloat._from_raw(_array.array('d',(v**e for v in self._samples)),self._unit**e)
    def __neg__(self) -> "ProbUnitFloat":
        return ProbUnitFloat._from_raw(_array.array('d',(-v for v in self._samples)),self._unit)
    def __abs__(self) -> "ProbUnitFloat":
        return ProbUnitFloat._from_raw(_array.array('d',(abs(v) for v in self._samples)),self._unit)

    def prob_lt(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                ) -> float:
        if isinstance(o,ProbUnitFloat):
            a,b=self._aligned(o)
            return sum(x<y for x,y in zip(a,b))/self._n
        if isinstance(o,UnitFloat):
            return self.prob_lt(ProbUnitFloat.from_unitfloat(o,self._n))
        if isinstance(o,(int,float)):
            return sum(v<float(o) for v in self._samples)/self._n
        return NotImplemented
    def prob_gt(self, o: Union["ProbUnitFloat", "UnitFloat", int, float]
                ) -> float:
        return 1.0-self.prob_lt(o)-self.prob_eq(o)
    def prob_eq(self,o,tol=1e-9):
        if isinstance(o,ProbUnitFloat):
            a,b=self._aligned(o)
            return sum(abs(x-y)<tol for x,y in zip(a,b))/self._n
        return 0.0

    def __repr__(self):
        m, v = self._welford()
        return f"ProbUnitFloat(mean={m:.4g}, std={v**0.5:.4g}, unit='{self._unit}', n={self._n})"
    def __str__(self): return self.__repr__()

    # ── Serialization ─────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "type":    "ProbUnitFloat",
            "samples": list(self._samples),
            "unit":    str(self._unit),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProbUnitFloat":
        if d.get("type") != "ProbUnitFloat":
            raise ValueError(f"Expected type 'ProbUnitFloat', got {d.get('type')!r}")
        import array as _array
        return cls._from_raw(_array.array('d', d["samples"]), d["unit"])
    

def _default_n(n: int | None) -> int:
    if n is not None:
        return n
    from quantia._config import get_config
    return get_config().n_samples