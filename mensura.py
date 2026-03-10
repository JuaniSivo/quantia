"""
unitfloat.py
============
Unit-aware numerics with four types:

  UnitFloat        — exact scalar with a unit
  UnitArray        — typed array of exact scalars, one unit
  ProbUnitFloat    — probabilistic scalar  (Monte Carlo samples)
  ProbUnitArray    — array of independent probabilistic scalars

Distributions available for ProbUnitFloat / ProbUnitArray:
  uniform(low, high)
  normal(mean, std)
  triangular(low, mode, high)
  lognormal(mean, std)          ← mean/std of the underlying normal

Correlation: any two ProbUnitFloat values can be constructed from a shared
  CorrelatedSource so their samples are coupled via a Gaussian copula.
"""

from __future__ import annotations
from fractions import Fraction
import array as _array
import math
import operator
import random
import statistics
from typing import Iterable, Iterator

_N_SAMPLES = 1000


# ===========================================================================
# Unit registry
# ===========================================================================

class Unit:
    __slots__ = ("name", "quantity", "si_unit", "to_si", "symbol")
    def __init__(self, name, quantity, si_unit, to_si, symbol=""):
        self.name=name; self.quantity=quantity; self.si_unit=si_unit
        self.to_si=float(to_si); self.symbol=symbol or name

_REGISTRY: dict[str, Unit] = {}

def register(sym: str, unit: Unit) -> None: _REGISTRY[sym] = unit
def get_unit(sym: str) -> Unit:
    if sym not in _REGISTRY:
        raise ValueError(f"Unknown unit: '{sym}'. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[sym]

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, to_si, sym))

_reg("m",   "metre",         "length",      "m",  1.0)
_reg("km",  "kilometre",     "length",      "m",  1_000.0)
_reg("cm",  "centimetre",    "length",      "m",  0.01)
_reg("mm",  "millimetre",    "length",      "m",  0.001)
_reg("mi",  "mile",          "length",      "m",  1_609.344)
_reg("yd",  "yard",          "length",      "m",  0.9144)
_reg("ft",  "foot",          "length",      "m",  0.3048)
_reg("in",  "inch",          "length",      "m",  0.0254)
_reg("nm",  "nanometre",     "length",      "m",  1e-9)
_reg("kg",  "kilogram",      "mass",        "kg", 1.0)
_reg("g",   "gram",          "mass",        "kg", 0.001)
_reg("mg",  "milligram",     "mass",        "kg", 1e-6)
_reg("lb",  "pound",         "mass",        "kg", 0.45359237)
_reg("oz",  "ounce",         "mass",        "kg", 0.028349523125)
_reg("t",   "tonne",         "mass",        "kg", 1_000.0)
_reg("s",   "second",        "time",        "s",  1.0)
_reg("ms",  "millisecond",   "time",        "s",  0.001)
_reg("us",  "microsecond",   "time",        "s",  1e-6)
_reg("min", "minute",        "time",        "s",  60.0)
_reg("h",   "hour",          "time",        "s",  3_600.0)
_reg("day", "day",           "time",        "s",  86_400.0)
register("K",  Unit("kelvin",     "temperature", "K", 1.0,  "K"))
register("°C", Unit("celsius",    "temperature", "K", 0.0,  "°C"))
register("°F", Unit("fahrenheit", "temperature", "K", 0.0,  "°F"))
_reg("N",   "newton",        "force",       "N",  1.0)
_reg("kN",  "kilonewton",    "force",       "N",  1_000.0)
_reg("lbf", "pound-force",   "force",       "N",  4.4482216152605)
_reg("Pa",  "pascal",        "pressure",    "Pa", 1.0)
_reg("kPa", "kilopascal",    "pressure",    "Pa", 1_000.0)
_reg("MPa", "megapascal",    "pressure",    "Pa", 1_000_000.0)
_reg("bar", "bar",           "pressure",    "Pa", 100_000.0)
_reg("atm", "atmosphere",    "pressure",    "Pa", 101_325.0)
_reg("psi", "psi",           "pressure",    "Pa", 6_894.757)
_reg("J",   "joule",         "energy",      "J",  1.0)
_reg("kJ",  "kilojoule",     "energy",      "J",  1_000.0)
_reg("cal", "calorie",       "energy",      "J",  4.184)
_reg("kcal","kilocalorie",   "energy",      "J",  4_184.0)
_reg("Wh",  "watt-hour",     "energy",      "J",  3_600.0)
_reg("kWh", "kilowatt-hour", "energy",      "J",  3_600_000.0)
_reg("eV",  "electronvolt",  "energy",      "J",  1.602176634e-19)
_reg("W",   "watt",          "power",       "W",  1.0)
_reg("kW",  "kilowatt",      "power",       "W",  1_000.0)
_reg("MW",  "megawatt",      "power",       "W",  1_000_000.0)
_reg("hp",  "horsepower",    "power",       "W",  745.69987)
_reg("V",   "volt",          "voltage",     "V",  1.0)
_reg("mV",  "millivolt",     "voltage",     "V",  0.001)
_reg("kV",  "kilovolt",      "voltage",     "V",  1_000.0)
_reg("A",   "ampere",        "current",     "A",  1.0)
_reg("mA",  "milliampere",   "current",     "A",  0.001)
_reg("Ω",   "ohm",           "resistance",  "Ω",  1.0)
_reg("kΩ",  "kiloohm",       "resistance",  "Ω",  1_000.0)
_reg("F",   "farad",         "capacitance", "F",  1.0)
_reg("H",   "henry",         "inductance",  "H",  1.0)
_reg("B",   "byte",          "data",        "B",  1.0)
_reg("KB",  "kilobyte",      "data",        "B",  1_024.0)
_reg("MB",  "megabyte",      "data",        "B",  1_048_576.0)
_reg("GB",  "gigabyte",      "data",        "B",  1_073_741_824.0)
_reg("TB",  "terabyte",      "data",        "B",  1_099_511_627_776.0)
_reg("rad", "radian",        "angle",       "rad",1.0)
_reg("deg", "degree",        "angle",       "rad",math.pi / 180)
_reg("mol", "mole",          "amount",      "mol",1.0)
_reg("cd",  "candela",       "luminosity",  "cd", 1.0)
_reg("1",   "dimensionless", "dimensionless","1", 1.0)


# ===========================================================================
# Temperature helpers
# ===========================================================================

def _to_kelvin(v, sym):
    if sym == "K":   return v
    if sym == "°C":  return v + 273.15
    if sym == "°F":  return (v + 459.67) * 5 / 9

def _from_kelvin(v, sym):
    if sym == "K":   return v
    if sym == "°C":  return v - 273.15
    if sym == "°F":  return v * 9 / 5 - 459.67


# ===========================================================================
# CompoundUnit
# ===========================================================================

class CompoundUnit:
    def __init__(self, factors=None):
        self._f: dict[str, Fraction] = {
            s: Fraction(e) for s, e in (factors or {}).items() if e != 0
        }

    @classmethod
    def from_symbol(cls, sym):
        get_unit(sym); return cls({sym: Fraction(1)})

    @classmethod
    def dimensionless(cls): return cls({})

    def __mul__(self, o):
        m = dict(self._f)
        for s, e in o._f.items(): m[s] = m.get(s, Fraction(0)) + e
        return CompoundUnit(m)

    def __truediv__(self, o):
        m = dict(self._f)
        for s, e in o._f.items(): m[s] = m.get(s, Fraction(0)) - e
        return CompoundUnit(m)

    def __pow__(self, exp):
        e = Fraction(exp).limit_denominator(100)
        return CompoundUnit({s: f * e for s, f in self._f.items()})

    def invert(self): return CompoundUnit({s: -e for s, e in self._f.items()})

    def si_factor(self):
        r = 1.0
        for s, e in self._f.items():
            u = get_unit(s)
            if u.quantity == "temperature":
                raise TypeError("Temperature units cannot appear in compound units.")
            r *= u.to_si ** float(e)
        return r

    def to_si_compound(self):
        m = {}
        for s, e in self._f.items():
            si = get_unit(s).si_unit
            m[si] = m.get(si, Fraction(0)) + e
        return CompoundUnit(m)

    def is_compatible(self, o): return self.to_si_compound()._f == o.to_si_compound()._f
    def is_dimensionless(self): return not self._f
    def canonical_key(self):    return frozenset(self.to_si_compound()._f.items())

    def __str__(self):
        alias = _ALIASES.get(self.canonical_key())
        if alias: return alias
        if not self._f: return "1"
        num = sorted((s, e) for s, e in self._f.items() if e > 0)
        den = sorted((s, -e) for s, e in self._f.items() if e < 0)
        def fmt(parts):
            out = []
            for s, e in parts:
                if e == 1: out.append(s)
                elif e.denominator == 1: out.append(f"{s}^{e.numerator}")
                else: out.append(f"{s}^({e})")
            return "·".join(out)
        n = fmt(num) or "1"
        return f"{n}/{fmt(den)}" if den else n

    def __repr__(self): return f"CompoundUnit({self._f!r})"
    def __eq__(self, o): return isinstance(o, CompoundUnit) and self._f == o._f
    def __hash__(self): return hash(frozenset(self._f.items()))


# ===========================================================================
# Alias registry
# ===========================================================================

_ALIASES: dict[frozenset, str] = {}

def register_alias(display, expr):
    _ALIASES[parse_unit(expr).canonical_key()] = display

_PENDING_ALIASES = [
    ("J",  "N·m"), ("W",  "J/s"), ("N",  "kg·m/s^2"),
    ("Pa", "N/m^2"), ("V", "W/A"), ("Ω",  "V/A"), ("Hz", "1/s"),
]


# ===========================================================================
# Unit expression parser
# ===========================================================================

def parse_unit(expr: str) -> CompoundUnit:
    expr = expr.strip()
    num_str, den_str = (expr.split("/", 1) if "/" in expr else (expr, ""))
    def parse_part(s):
        if not s or s == "1": return CompoundUnit.dimensionless()
        cu = CompoundUnit.dimensionless()
        for tok in s.replace("*", "·").split("·"):
            tok = tok.strip()
            if not tok or tok == "1": continue
            if "^" in tok:
                sym, es = tok.split("^", 1)
                exp = Fraction(es.strip("()")).limit_denominator(100)
            else:
                sym, exp = tok, Fraction(1)
            get_unit(sym.strip()); cu = cu * CompoundUnit({sym.strip(): exp})
        return cu
    r = parse_part(num_str)
    if den_str: r = r / parse_part(den_str)
    return r

def _bootstrap_aliases():
    for display, expr in _PENDING_ALIASES:
        try: register_alias(display, expr)
        except Exception: pass

_bootstrap_aliases()


# ===========================================================================
# Shared helpers
# ===========================================================================

def _make_unit(unit) -> CompoundUnit:
    if isinstance(unit, CompoundUnit): return unit
    if isinstance(unit, str):
        return CompoundUnit.from_symbol(unit) if unit in _REGISTRY else parse_unit(unit)
    raise TypeError(f"unit must be str or CompoundUnit, got {type(unit)}")


# ===========================================================================
# Gaussian copula + distribution transforms
# ===========================================================================

# --- Normal CDF via Abramowitz & Stegun (error < 7.5e-8) ---

def _norm_cdf(x: float) -> float:
    """Φ(x): standard normal CDF, pure Python."""
    a = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * a)
    poly = t * (0.319381530
          + t * (-0.356563782
          + t * (1.781477937
          + t * (-1.821255978
          + t * 1.330274429))))
    p = 1.0 - (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * a * a) * poly
    return p if x >= 0 else 1.0 - p

# --- Inverse normal CDF (rational approximation, Beasley-Springer-Moro) ---

def _norm_ppf(p: float) -> float:
    """Φ⁻¹(p): inverse standard normal CDF."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError(f"p must be in (0, 1), got {p}")
    # coefficients
    a = (-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00)
    d = (7.784695709041462e-03,  3.224671290700398e-01,
         2.445134137142996e+00,  3.754408661907416e+00)
    p_lo, p_hi = 0.02425, 1 - 0.02425
    if p < p_lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_hi:
        q = p - 0.5; r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


# --- Inverse CDFs for each supported distribution ---
# Each takes p ∈ (0,1) and distribution params, returns a sample value.

def _icdf_uniform(p: float, low: float, high: float) -> float:
    return low + p * (high - low)

def _icdf_normal(p: float, mean: float, std: float) -> float:
    return mean + std * _norm_ppf(p)

def _icdf_triangular(p: float, low: float, mode: float, high: float) -> float:
    # Closed-form inverse CDF of the triangular distribution
    fc = (mode - low) / (high - low)
    if p < fc:
        return low + math.sqrt(p * (high - low) * (mode - low))
    else:
        return high - math.sqrt((1 - p) * (high - low) * (high - mode))

def _icdf_lognormal(p: float, mean: float, std: float) -> float:
    # mean/std are the underlying normal parameters (not of the lognormal itself)
    return math.exp(mean + std * _norm_ppf(p))


# --- Gaussian copula: generate N correlated uniform samples for K variables ---
#
# Inputs:
#   n          — number of samples
#   corr_matrix — K×K correlation matrix (list of lists), must be symmetric, 1s on diagonal
#
# Returns:
#   list of K arrays of floats in (0, 1) — correlated uniforms
#
# Method:
#   1. Cholesky decompose the correlation matrix  R = L·Lᵀ
#   2. Draw K independent standard normals z_i for each sample
#   3. Multiply L·z to get correlated normals u
#   4. Apply Φ to each u to get correlated uniforms p

def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    """Lower Cholesky factor L such that matrix = L·Lᵀ."""
    k = len(matrix)
    L = [[0.0]*k for _ in range(k)]
    for i in range(k):
        for j in range(i+1):
            s = sum(L[i][m] * L[j][m] for m in range(j))
            if i == j:
                val = matrix[i][i] - s
                if val < 0:
                    raise ValueError(
                        "Correlation matrix is not positive definite. "
                        "Check that correlations are valid (|ρ| < 1 and consistent).")
                L[i][j] = math.sqrt(val)
            else:
                L[i][j] = (matrix[i][j] - s) / L[j][j]
    return L

def _gaussian_copula(n: int, corr_matrix: list[list[float]]) -> list[_array.array]:
    """
    Return K arrays of n correlated uniform samples in (0, 1).
    corr_matrix is K×K.
    """
    k   = len(corr_matrix)
    L   = _cholesky(corr_matrix)
    eps = 1e-9          # clamp to keep p strictly inside (0, 1) for ppf

    # result[i] will hold n uniforms for variable i
    result = [_array.array('d', [0.0]*n) for _ in range(k)]

    for s in range(n):
        z = [random.gauss(0, 1) for _ in range(k)]
        for i in range(k):
            u = sum(L[i][j] * z[j] for j in range(i+1))
            result[i][s] = max(eps, min(1-eps, _norm_cdf(u)))

    return result


# ===========================================================================
# CorrelatedSource
# ===========================================================================

class CorrelatedSource:
    """
    Generates correlated uniform percentile arrays for a group of variables
    via a Gaussian copula, then hands them out one by one.

    Usage
    -----
    src = CorrelatedSource(n_vars=2, rho=0.9)          # 2 vars, ρ=0.9
    # or with a full matrix for >2 vars:
    src = CorrelatedSource(corr_matrix=[[1, .8, .3],
                                        [.8, 1, .5],
                                        [.3, .5, 1]])
    work_out = src.normal(85, 5, "J")
    work_in  = src.normal(95, 5, "J")
    """

    def __init__(self,
                 n_vars: int | None     = None,
                 rho:    float | None   = None,
                 corr_matrix: list[list[float]] | None = None,
                 n: int = _N_SAMPLES):
        if corr_matrix is not None:
            self._matrix = corr_matrix
            self._k      = len(corr_matrix)
        elif n_vars is not None and rho is not None:
            if not -1.0 < rho < 1.0:
                raise ValueError("rho must be in (-1, 1)")
            # constant off-diagonal correlation matrix
            self._k = n_vars
            self._matrix = [
                [1.0 if i == j else rho for j in range(n_vars)]
                for i in range(n_vars)
            ]
        else:
            raise ValueError("Provide either (n_vars, rho) or corr_matrix.")

        self._n       = n
        self._uniforms = _gaussian_copula(n, self._matrix)  # pre-generate all
        self._idx      = 0   # next variable slot to hand out

    def _next_percentiles(self) -> _array.array:
        if self._idx >= self._k:
            raise RuntimeError(
                f"CorrelatedSource has only {self._k} variable slots. "
                "Create a larger source or a new one.")
        p = self._uniforms[self._idx]
        self._idx += 1
        return p

    def _make(self, icdf, unit, *params) -> "ProbUnitFloat":
        p = self._next_percentiles()
        samples = _array.array('d', (icdf(pi, *params) for pi in p))
        return ProbUnitFloat._from_raw(samples, unit)

    def uniform(self, low: float, high: float, unit) -> "ProbUnitFloat":
        return self._make(_icdf_uniform, unit, low, high)

    def normal(self, mean: float, std: float, unit) -> "ProbUnitFloat":
        return self._make(_icdf_normal, unit, mean, std)

    def triangular(self, low: float, mode: float, high: float, unit) -> "ProbUnitFloat":
        return self._make(_icdf_triangular, unit, low, mode, high)

    def lognormal(self, mean: float, std: float, unit) -> "ProbUnitFloat":
        """mean and std are the parameters of the underlying normal (ln X ~ N(mean, std))."""
        return self._make(_icdf_lognormal, unit, mean, std)


# ===========================================================================
# UnitFloat
# ===========================================================================

class UnitFloat:
    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit):
        self._value = float(value); self._unit = _make_unit(unit)

    @property
    def value(self) -> float: return self._value
    @property
    def unit(self) -> CompoundUnit: return self._unit

    def to_si(self):
        if len(self._unit._f) == 1:
            s, e = next(iter(self._unit._f.items()))
            if get_unit(s).quantity == "temperature" and e == 1:
                return UnitFloat(_to_kelvin(self._value, s), "K")
        return UnitFloat(self._value * self._unit.si_factor(), self._unit.to_si_compound())

    def si_value(self): return self.to_si()._value

    def to(self, target):
        tcu = _make_unit(target)
        if isinstance(target, str) and get_unit(target).quantity == "temperature":
            s, _ = next(iter(self._unit._f.items()))
            return UnitFloat(_from_kelvin(_to_kelvin(self._value, s), target), target)
        if not self._unit.is_compatible(tcu):
            raise TypeError(f"Incompatible units: {self._unit} and {tcu}")
        return UnitFloat(self._value * self._unit.si_factor() / tcu.si_factor(), tcu)

    def _coerce(self, o):
        if not self._unit.is_compatible(o._unit):
            raise TypeError(f"Incompatible units: {self._unit} and {o._unit}")
        return o._value * o._unit.si_factor() / self._unit.si_factor()

    def __add__(self, o):
        if isinstance(o, UnitFloat): return UnitFloat(self._value + self._coerce(o), self._unit)
        if isinstance(o, (int,float)): return UnitFloat(self._value + o, self._unit)
        return NotImplemented
    def __radd__(self, o): return self.__add__(o)
    def __sub__(self, o):
        if isinstance(o, UnitFloat): return UnitFloat(self._value - self._coerce(o), self._unit)
        if isinstance(o, (int,float)): return UnitFloat(self._value - o, self._unit)
        return NotImplemented
    def __rsub__(self, o):
        if isinstance(o, (int,float)): return UnitFloat(o - self._value, self._unit)
        return NotImplemented
    def __mul__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit * o._unit
            return UnitFloat(self._value * o._value, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __rmul__(self, o):
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __truediv__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit / o._unit
            return UnitFloat(self._value / o._value, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)): return UnitFloat(self._value / o, self._unit)
        return NotImplemented
    def __rtruediv__(self, o):
        if isinstance(o, (int,float)): return UnitFloat(o / self._value, self._unit.invert())
        return NotImplemented
    def __pow__(self, e): return UnitFloat(self._value**e, self._unit**e)
    def __neg__(self):  return UnitFloat(-self._value, self._unit)
    def __abs__(self):  return UnitFloat(abs(self._value), self._unit)
    def __float__(self): return self._value
    def __int__(self):   return int(self._value)
    def __round__(self, n=None): return UnitFloat(round(self._value, n), self._unit)
    def __floor__(self): return UnitFloat(math.floor(self._value), self._unit)
    def __ceil__(self):  return UnitFloat(math.ceil(self._value),  self._unit)
    def _cmp(self, o):
        if isinstance(o, UnitFloat): return self.si_value(), o.si_value()
        if isinstance(o, (int,float)): return self.si_value(), float(o)
        return NotImplemented
    def __eq__(self, o):
        r = self._cmp(o); return r is not NotImplemented and math.isclose(r[0], r[1])
    def __lt__(self, o): r=self._cmp(o); return r[0]<r[1]
    def __le__(self, o): r=self._cmp(o); return r[0]<=r[1]
    def __gt__(self, o): r=self._cmp(o); return r[0]>r[1]
    def __ge__(self, o): r=self._cmp(o); return r[0]>=r[1]
    def __repr__(self): return f"UnitFloat({self._value!r}, '{self._unit}')"
    def __str__(self):  return f"{self._value} {self._unit}"
    def __format__(self, spec): return f"{self._value:{spec}} {self._unit}"


# ===========================================================================
# UnitArray
# ===========================================================================

class UnitArray:
    def __init__(self, values: Iterable[float], unit):
        self._data = _array.array('d', (float(v) for v in values))
        self._unit = _make_unit(unit)

    @property
    def unit(self) -> CompoundUnit: return self._unit
    @property
    def values(self) -> _array.array: return self._data

    def to_si(self):
        f = self._unit.si_factor()
        return UnitArray((v*f for v in self._data), self._unit.to_si_compound())

    def to(self, target):
        tcu = _make_unit(target)
        if not self._unit.is_compatible(tcu):
            raise TypeError(f"Incompatible units: {self._unit} and {tcu}")
        f = self._unit.si_factor() / tcu.si_factor()
        return UnitArray((v*f for v in self._data), tcu)

    def _elem(self, o, op):
        if isinstance(o, UnitArray):
            if len(self) != len(o): raise ValueError("Length mismatch")
            if not self._unit.is_compatible(o._unit):
                raise TypeError(f"Incompatible units: {self._unit} and {o._unit}")
            f = o._unit.si_factor() / self._unit.si_factor()
            return UnitArray((op(a, b*f) for a,b in zip(self._data, o._data)), self._unit)
        if isinstance(o, UnitFloat):
            if not self._unit.is_compatible(o.unit):
                raise TypeError(f"Incompatible units: {self._unit} and {o.unit}")
            s = o.value * o.unit.si_factor() / self._unit.si_factor()
            return UnitArray((op(v, s) for v in self._data), self._unit)
        if isinstance(o, (int,float)):
            return UnitArray((op(v, float(o)) for v in self._data), self._unit)
        return NotImplemented

    def _mul_div(self, o, op):
        if isinstance(o, (UnitArray, UnitFloat)):
            ou = o._unit
            ov = o._data if isinstance(o, UnitArray) else [o._value]*len(self._data)
            cu = op(self._unit, ou)
            vals = (op(a, b) for a,b in zip(self._data, ov))
            return UnitArray(vals, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)):
            return UnitArray((op(v, float(o)) for v in self._data), self._unit)
        return NotImplemented

    def __add__(self, o): return self._elem(o, operator.add)
    def __radd__(self, o): return self.__add__(o)
    def __sub__(self, o): return self._elem(o, operator.sub)
    def __rsub__(self, o):
        if isinstance(o, (int,float)): return UnitArray((o-v for v in self._data), self._unit)
        return NotImplemented
    def __mul__(self, o):  return self._mul_div(o, operator.mul)
    def __rmul__(self, o):
        if isinstance(o, (int,float)): return UnitArray((v*o for v in self._data), self._unit)
        return NotImplemented
    def __truediv__(self, o): return self._mul_div(o, operator.truediv)
    def __rtruediv__(self, o):
        if isinstance(o, (int,float)): return UnitArray((o/v for v in self._data), self._unit.invert())
        return NotImplemented
    def __pow__(self, e): return UnitArray((v**e for v in self._data), self._unit**e)
    def __neg__(self): return UnitArray((-v for v in self._data), self._unit)
    def __abs__(self): return UnitArray((abs(v) for v in self._data), self._unit)

    def _cmp(self, o, op):
        if isinstance(o, (UnitArray, UnitFloat)):
            ou = o._unit; ov = o._data if isinstance(o, UnitArray) else [o._value]*len(self._data)
            f = ou.si_factor() / self._unit.si_factor()
            return [op(a, b*f) for a,b in zip(self._data, ov)]
        if isinstance(o, (int,float)): return [op(v, float(o)) for v in self._data]
        return NotImplemented
    def __eq__(self, o): return self._cmp(o, lambda a,b: math.isclose(a,b))
    def __lt__(self, o): return self._cmp(o, operator.lt)
    def __le__(self, o): return self._cmp(o, operator.le)
    def __gt__(self, o): return self._cmp(o, operator.gt)
    def __ge__(self, o): return self._cmp(o, operator.ge)

    def sum(self):  return UnitFloat(sum(self._data), self._unit)
    def mean(self): return UnitFloat(sum(self._data)/len(self._data), self._unit)
    def min(self):  return UnitFloat(min(self._data), self._unit)
    def max(self):  return UnitFloat(max(self._data), self._unit)
    def dot(self, o):
        val = sum(a*b for a,b in zip(self._data, o._data))
        cu = self._unit * o._unit
        return UnitFloat(val, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)

    def __len__(self): return len(self._data)
    def __iter__(self): return (UnitFloat(v, self._unit) for v in self._data)
    def __getitem__(self, i):
        if isinstance(i, slice): return UnitArray(self._data[i], self._unit)
        return UnitFloat(self._data[i], self._unit)
    def __setitem__(self, i, val):
        if isinstance(val, UnitFloat):
            self._data[i] = val.value * val.unit.si_factor() / self._unit.si_factor()
        else: self._data[i] = float(val)
    def append(self, val):
        if isinstance(val, UnitFloat):
            self._data.append(val.value * val.unit.si_factor() / self._unit.si_factor())
        else: self._data.append(float(val))

    def __repr__(self):
        p = list(self._data[:6]); dots = ", ..." if len(self._data) > 6 else ""
        return f"UnitArray([{', '.join(str(v) for v in p)}{dots}], '{self._unit}')"
    def __str__(self): return self.__repr__()


# ===========================================================================
# ProbUnitFloat
# ===========================================================================

class ProbUnitFloat:
    """
    Probabilistic unit-aware scalar backed by N Monte Carlo samples.

    Independent construction (no correlation):
        ProbUnitFloat.uniform(low, high, unit)
        ProbUnitFloat.normal(mean, std, unit)
        ProbUnitFloat.triangular(low, mode, high, unit)
        ProbUnitFloat.lognormal(mean, std, unit)

    Correlated construction — use CorrelatedSource:
        src = CorrelatedSource(n_vars=2, rho=0.9)
        a = src.normal(10, 1, "m")
        b = src.normal(10, 1, "m")   # correlated with a
    """

    def __init__(self, samples: Iterable[float], unit, n: int = _N_SAMPLES):
        self._samples = _array.array('d', samples)
        self._unit    = _make_unit(unit)
        self._n       = len(self._samples)

    # ── Factories (independent) ───────────────────────────────────────────────

    @classmethod
    def _independent(cls, icdf, unit, n, *params) -> "ProbUnitFloat":
        eps = 1e-9
        samples = _array.array('d',
            (icdf(max(eps, min(1-eps, random.random())), *params) for _ in range(n)))
        return cls._from_raw(samples, unit)

    @classmethod
    def uniform(cls, low: float, high: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(_icdf_uniform, unit, n, low, high)

    @classmethod
    def normal(cls, mean: float, std: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(_icdf_normal, unit, n, mean, std)

    @classmethod
    def triangular(cls, low: float, mode: float, high: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        return cls._independent(_icdf_triangular, unit, n, low, mode, high)

    @classmethod
    def lognormal(cls, mean: float, std: float, unit, n=_N_SAMPLES) -> "ProbUnitFloat":
        """mean, std are parameters of the underlying normal distribution."""
        return cls._independent(_icdf_lognormal, unit, n, mean, std)

    @classmethod
    def from_unitfloat(cls, uf: UnitFloat, n=_N_SAMPLES) -> "ProbUnitFloat":
        """Degenerate point distribution — no uncertainty."""
        return cls._from_raw(_array.array('d', [uf.value]*n), uf.unit)

    @classmethod
    def _from_raw(cls, samples: _array.array, unit) -> "ProbUnitFloat":
        obj = object.__new__(cls)
        obj._samples = samples
        obj._unit    = _make_unit(unit)
        obj._n       = len(samples)
        return obj

    # ── Statistics ────────────────────────────────────────────────────────────

    def mean(self)     -> UnitFloat: return UnitFloat(sum(self._samples)/self._n, self._unit)
    def std(self)      -> UnitFloat: return UnitFloat(statistics.stdev(self._samples), self._unit)
    def variance(self) -> UnitFloat: return UnitFloat(statistics.variance(self._samples), self._unit)
    def median(self)   -> UnitFloat: return UnitFloat(statistics.median(self._samples), self._unit)
    def min(self)      -> UnitFloat: return UnitFloat(min(self._samples), self._unit)
    def max(self)      -> UnitFloat: return UnitFloat(max(self._samples), self._unit)

    def interval(self, confidence: float = 0.95) -> tuple[UnitFloat, UnitFloat]:
        tail = (1 - confidence) / 2
        s = sorted(self._samples)
        lo = s[int(math.floor(tail * self._n))]
        hi = s[int(math.ceil((1-tail) * self._n)) - 1]
        return UnitFloat(lo, self._unit), UnitFloat(hi, self._unit)

    def percentile(self, p: float) -> UnitFloat:
        s = sorted(self._samples)
        return UnitFloat(s[max(0, min(int(round(p/100*(self._n-1))), self._n-1))], self._unit)

    def histogram(self, bins=10):
        lo, hi = min(self._samples), max(self._samples)
        w = (hi - lo) / bins
        edges = [lo + i*w for i in range(bins+1)]
        counts = [0]*bins
        for v in self._samples:
            counts[min(int((v-lo)/w), bins-1)] += 1
        return edges, counts

    # ── Conversion ────────────────────────────────────────────────────────────

    def to_si(self) -> "ProbUnitFloat":
        if len(self._unit._f) == 1:
            s, e = next(iter(self._unit._f.items()))
            if get_unit(s).quantity == "temperature" and e == 1:
                return ProbUnitFloat._from_raw(
                    _array.array('d', (_to_kelvin(v, s) for v in self._samples)), "K")
        f = self._unit.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v*f for v in self._samples)), self._unit.to_si_compound())

    def to(self, target) -> "ProbUnitFloat":
        tcu = _make_unit(target)
        if not self._unit.is_compatible(tcu):
            raise TypeError(f"Incompatible units: {self._unit} and {tcu}")
        f = self._unit.si_factor() / tcu.si_factor()
        return ProbUnitFloat._from_raw(
            _array.array('d', (v*f for v in self._samples)), tcu)

    # ── Arithmetic ────────────────────────────────────────────────────────────

    def _aligned(self, o: "ProbUnitFloat"):
        if not self._unit.is_compatible(o._unit):
            raise TypeError(f"Incompatible units: {self._unit} and {o._unit}")
        f = o._unit.si_factor() / self._unit.si_factor()
        return self._samples, _array.array('d', (v*f for v in o._samples))

    def _elem(self, o, op, cu=None) -> "ProbUnitFloat":
        a, b = self._aligned(o)
        return ProbUnitFloat._from_raw(
            _array.array('d', (op(x,y) for x,y in zip(a,b))), cu or self._unit)

    def _scalar(self, s, op, cu=None) -> "ProbUnitFloat":
        return ProbUnitFloat._from_raw(
            _array.array('d', (op(v, s) for v in self._samples)), cu or self._unit)

    def __add__(self, o):
        if isinstance(o, ProbUnitFloat): return self._elem(o, operator.add)
        if isinstance(o, UnitFloat):     return self.__add__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):   return self._scalar(float(o), operator.add)
        return NotImplemented
    def __radd__(self, o): return self.__add__(o)

    def __sub__(self, o):
        if isinstance(o, ProbUnitFloat): return self._elem(o, operator.sub)
        if isinstance(o, UnitFloat):     return self.__sub__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):   return self._scalar(float(o), operator.sub)
        return NotImplemented
    def __rsub__(self, o):
        if isinstance(o, (int,float)):
            return ProbUnitFloat._from_raw(
                _array.array('d', (float(o)-v for v in self._samples)), self._unit)
        return NotImplemented

    def __mul__(self, o):
        if isinstance(o, ProbUnitFloat):
            cu = self._unit * o._unit
            cu = CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(
                _array.array('d', (a*b for a,b in zip(self._samples, o._samples))), cu)
        if isinstance(o, UnitFloat):   return self.__mul__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)): return self._scalar(float(o), operator.mul)
        return NotImplemented
    def __rmul__(self, o):
        if isinstance(o, (int,float)): return self._scalar(float(o), operator.mul)
        return NotImplemented

    def __truediv__(self, o):
        if isinstance(o, ProbUnitFloat):
            cu = self._unit / o._unit
            cu = CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return ProbUnitFloat._from_raw(
                _array.array('d', (a/b for a,b in zip(self._samples, o._samples))), cu)
        if isinstance(o, UnitFloat):   return self.__truediv__(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)): return self._scalar(float(o), operator.truediv)
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
        return ProbUnitFloat._from_raw(_array.array('d', (-v for v in self._samples)), self._unit)
    def __abs__(self):
        return ProbUnitFloat._from_raw(_array.array('d', (abs(v) for v in self._samples)), self._unit)

    # ── Probabilistic comparisons ─────────────────────────────────────────────

    def prob_lt(self, o) -> float:
        if isinstance(o, ProbUnitFloat):
            a, b = self._aligned(o); return sum(x<y for x,y in zip(a,b)) / self._n
        if isinstance(o, UnitFloat):     return self.prob_lt(ProbUnitFloat.from_unitfloat(o, self._n))
        if isinstance(o, (int,float)):   return sum(v<float(o) for v in self._samples) / self._n
        return NotImplemented

    def prob_gt(self, o) -> float:
        return 1.0 - self.prob_lt(o) - self.prob_eq(o)

    def prob_eq(self, o, tol=1e-9) -> float:
        if isinstance(o, ProbUnitFloat):
            a, b = self._aligned(o); return sum(abs(x-y)<tol for x,y in zip(a,b)) / self._n
        return 0.0

    def __repr__(self):
        m = sum(self._samples)/self._n; s = statistics.stdev(self._samples)
        return f"ProbUnitFloat(mean={m:.4g}, std={s:.4g}, unit='{self._unit}', n={self._n})"
    def __str__(self): return self.__repr__()


# ===========================================================================
# ProbUnitArray
# ===========================================================================

class ProbUnitArray:
    """Array of independent ProbUnitFloat — flat array.array storage, row-major."""

    def __init__(self, elements: Iterable[ProbUnitFloat]):
        elems = list(elements)
        if not elems: raise ValueError("ProbUnitArray requires at least one element")
        self._unit = elems[0]._unit
        self._n    = elems[0]._n
        self._len  = len(elems)
        flat = []
        for i, el in enumerate(elems):
            if not el._unit.is_compatible(self._unit):
                raise TypeError(f"Element {i}: incompatible unit {el._unit}")
            if el._n != self._n:
                raise ValueError(f"Element {i}: sample count mismatch")
            f = el._unit.si_factor() / self._unit.si_factor()
            flat.extend(v*f for v in el._samples)
        self._data = _array.array('d', flat)

    @classmethod
    def _from_flat(cls, data, unit, length, n):
        obj = object.__new__(cls)
        obj._data = data; obj._unit = _make_unit(unit)
        obj._len  = length; obj._n = n
        return obj

    def _row(self, i): return self._data[i*self._n:(i+1)*self._n]

    def __len__(self): return self._len
    def __iter__(self):
        for i in range(self._len): yield ProbUnitFloat._from_raw(self._row(i), self._unit)
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            indices = range(*idx.indices(self._len))
            flat = _array.array('d')
            for i in indices: flat.extend(self._row(i))
            return ProbUnitArray._from_flat(flat, self._unit, len(indices), self._n)
        i = idx if idx >= 0 else self._len + idx
        return ProbUnitFloat._from_raw(self._row(i), self._unit)

    def to_si(self):
        f = self._unit.si_factor()
        return ProbUnitArray._from_flat(
            _array.array('d', (v*f for v in self._data)),
            self._unit.to_si_compound(), self._len, self._n)

    def to(self, target):
        tcu = _make_unit(target)
        if not self._unit.is_compatible(tcu): raise TypeError(f"Incompatible units: {self._unit} and {tcu}")
        f = self._unit.si_factor() / tcu.si_factor()
        return ProbUnitArray._from_flat(
            _array.array('d', (v*f for v in self._data)), tcu, self._len, self._n)

    def _apply(self, o, op, result_unit):
        if isinstance(o, ProbUnitArray):
            if len(o) != self._len: raise ValueError("Length mismatch")
            f = o._unit.si_factor() / self._unit.si_factor()
            out = _array.array('d', (op(a, b*f) for a,b in zip(self._data, o._data)))
        elif isinstance(o, ProbUnitFloat):
            f = o._unit.si_factor() / self._unit.si_factor()
            b = _array.array('d', (v*f for v in o._samples))
            out = _array.array('d')
            for i in range(self._len): out.extend(op(a, b[j]) for j,a in enumerate(self._row(i)))
        elif isinstance(o, (int,float)):
            out = _array.array('d', (op(v, float(o)) for v in self._data))
        else: return NotImplemented
        return ProbUnitArray._from_flat(out, result_unit, self._len, self._n)

    def _apply_mul(self, o, op):
        if isinstance(o, (ProbUnitArray, ProbUnitFloat)):
            cu = op(self._unit, o._unit)
            cu = CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return self._apply(o, op, cu)
        if isinstance(o, (int,float)):
            out = _array.array('d', (op(v, float(o)) for v in self._data))
            return ProbUnitArray._from_flat(out, self._unit, self._len, self._n)
        return NotImplemented

    def __add__(self, o): return self._apply(o, operator.add, self._unit)
    def __radd__(self, o): return self.__add__(o)
    def __sub__(self, o): return self._apply(o, operator.sub, self._unit)
    def __mul__(self, o): return self._apply_mul(o, operator.mul)
    def __rmul__(self, o):
        if isinstance(o, (int,float)):
            out = _array.array('d', (v*float(o) for v in self._data))
            return ProbUnitArray._from_flat(out, self._unit, self._len, self._n)
        return NotImplemented
    def __truediv__(self, o): return self._apply_mul(o, operator.truediv)
    def __pow__(self, e):
        out = _array.array('d', (v**e for v in self._data))
        return ProbUnitArray._from_flat(out, self._unit**e, self._len, self._n)
    def __neg__(self):
        out = _array.array('d', (-v for v in self._data))
        return ProbUnitArray._from_flat(out, self._unit, self._len, self._n)

    def means(self)   -> UnitArray: return UnitArray([sum(self._row(i))/self._n for i in range(self._len)], self._unit)
    def stds(self)    -> UnitArray: return UnitArray([statistics.stdev(self._row(i)) for i in range(self._len)], self._unit)
    def medians(self) -> UnitArray: return UnitArray([statistics.median(self._row(i)) for i in range(self._len)], self._unit)

    def intervals(self, confidence=0.95):
        tail = (1-confidence)/2
        result = []
        for i in range(self._len):
            s = sorted(self._row(i))
            lo = s[int(math.floor(tail*self._n))]
            hi = s[int(math.ceil((1-tail)*self._n))-1]
            result.append((UnitFloat(lo, self._unit), UnitFloat(hi, self._unit)))
        return result

    def __repr__(self):
        ms = [f"{sum(self._row(i))/self._n:.4g}" for i in range(min(4, self._len))]
        dots = ", ..." if self._len > 4 else ""
        return f"ProbUnitArray(means=[{', '.join(ms)}{dots}], unit='{self._unit}', len={self._len}, n={self._n})"
    def __str__(self): return self.__repr__()


# ===========================================================================
# Math Helpers
# ===========================================================================

def log10(x) -> "ProbUnitFloat":
    """Sample-wise log10 for ProbUnitFloat; falls back to math.log10 otherwise."""
    if isinstance(x, ProbUnitFloat):
        return ProbUnitFloat._from_raw(
            _array.array('d', (math.log10(v) for v in x._samples)),
            CompoundUnit.dimensionless())
    if isinstance(x, UnitFloat):
        return math.log10(x.value)
    return math.log10(x)

def log(x) -> "ProbUnitFloat":
    if isinstance(x, ProbUnitFloat):
        return ProbUnitFloat._from_raw(
            _array.array('d', (math.log(v) for v in x._samples)),
            CompoundUnit.dimensionless())
    if isinstance(x, UnitFloat):
        return math.log(x.value)
    return math.log(x)

def exp(x) -> "ProbUnitFloat":
    if isinstance(x, ProbUnitFloat):
        return ProbUnitFloat._from_raw(
            _array.array('d', (math.exp(v) for v in x._samples)),
            CompoundUnit.dimensionless())
    if isinstance(x, UnitFloat):
        return math.exp(x.value)
    return math.exp(x)

def sqrt(x) -> "ProbUnitFloat":
    if isinstance(x, ProbUnitFloat):
        return ProbUnitFloat._from_raw(
            _array.array('d', (math.sqrt(v) for v in x._samples)),
            x._unit ** Fraction(1, 2))
    if isinstance(x, UnitFloat):
        return UnitFloat(math.sqrt(x.value), x.unit ** Fraction(1, 2))
    return math.sqrt(x)


# ===========================================================================
# Convenience factories
# ===========================================================================

def Q(value: float, unit) -> UnitFloat:
    return UnitFloat(value, unit)

def QA(values: Iterable[float], unit) -> UnitArray:
    return UnitArray(values, unit)

def QP(low: float, high: float, unit, n=_N_SAMPLES) -> ProbUnitFloat:
    """Shorthand for uniform ProbUnitFloat."""
    return ProbUnitFloat.uniform(low, high, unit, n)

def QPA(elements: Iterable[ProbUnitFloat]) -> ProbUnitArray:
    return ProbUnitArray(elements)


# ===========================================================================
# Demo
# ===========================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("1. Independent distributions")
    print("=" * 60)

    u = ProbUnitFloat.uniform(9, 11, "m")
    n = ProbUnitFloat.normal(10, 0.5, "m")
    t = ProbUnitFloat.triangular(8, 10, 12, "m")
    l = ProbUnitFloat.lognormal(0, 0.1, "m")   # ln X ~ N(0, 0.1) mean=1 because eˆ0=1 and std=0.1 because 0.1*eˆ0=0.1

    for label, p in [("uniform", u), ("normal", n), ("triangular", t), ("lognormal", l)]:
        lo, hi = p.interval(0.95)
        print(f"  {label:12s}  mean={p.mean():.3f}  std={p.std():.3f}  "
              f"95%CI=[{lo:.3f}, {hi:.3f}]")

    print()
    print("=" * 60)
    print("2. Correlated source (ρ=0.9) — engine efficiency")
    print("=" * 60)

    # Same instrument measures both → high correlation
    src = CorrelatedSource(n_vars=2, rho=0.9, n=2000)
    work_out = src.normal(90, 5, "J")
    work_in  = src.normal(100, 5, "J")
    eff_corr  = work_out / work_in      # dimensionless

    # Compare with independent
    work_out_i = ProbUnitFloat.normal(90, 5, "J", n=2000)
    work_in_i  = ProbUnitFloat.normal(100, 5, "J", n=2000)
    eff_indep  = work_out_i / work_in_i

    print(f"  correlated   eff: mean={eff_corr.mean():.4f}  std={eff_corr.std():.4f}")
    print(f"  independent  eff: mean={eff_indep.mean():.4f}  std={eff_indep.std():.4f}")
    print(f"  → correlation shrinks std by ~{1 - eff_corr.std().value/eff_indep.std().value:.0%}")

    print()
    print("=" * 60)
    print("3. Full 3-variable corr matrix + mixed distributions")
    print("=" * 60)

    corr = [[1.0,  0.8,  0.3],
            [0.8,  1.0,  0.5],
            [0.3,  0.5,  1.0]]

    src3 = CorrelatedSource(corr_matrix=corr, n=2000)
    F    = src3.normal(10, 1, "N")
    d    = src3.triangular(4, 5, 6, "m")
    t_   = src3.lognormal(0, 0.05, "s")   # ln t ~ N(0, 0.05)

    energy = F * d          # → J
    power  = energy / t_    # → W

    print(f"  F      : {F}")
    print(f"  d      : {d}")
    print(f"  t      : {t_}")
    print(f"  F*d    : {energy}")
    print(f"  F*d/t  : {power}")
    lo, hi = power.interval(0.95)
    print(f"  power 95% CI: [{lo:.3f}, {hi:.3f}]")

    print()
    print("=" * 60)
    print("4. Probabilistic comparison")
    print("=" * 60)

    src2 = CorrelatedSource(n_vars=2, rho=0.3, n=2000)
    a = src2.normal(10, 2, "m")
    b = src2.normal(11, 2, "m")
    print(f"  P(a < b) = {a.prob_lt(b):.3f}")
    print(f"  P(a > b) = {a.prob_gt(b):.3f}")

    print()
    print("=" * 60)
    print("5. GOR example")
    print("=" * 60)

    a1 = 0.3818
    a2 = -5.506
    a3 = 2.902
    a4 = 1.327
    a5 = -0.7355

    SG_o = QP(0.90, 0.96, "1")
    SG_g = QP(0.55, 0.65, "1")
    Tsp = QP(Q(5, "°C").to("°F").value, Q(15, "°C").to("°F").value, "1")
    Psp = QP(15, 30, "1")

    log_Rst = a1 + a2*log10(SG_o) + a3*log10(SG_g) + a4*log10(Psp) + a5*log10(Tsp)
    Rst = exp(log_Rst)

    print(Rst.interval(0.8))


    Rs = Rst + QP(30, 60, "1")
    T = QP(Q(30, "°C").to("°F").value, Q(60, "°C").to("°F").value, "1")
    APIo = QP(15, 30, "1")

    Cpb = (Rs / SG_g) ** 0.83 * 10 ** (0.00091 * T - 0.0125 * APIo)
    Pb = 18.2 * (Cpb - 1.4)