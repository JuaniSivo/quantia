"""
quantia/math.py
===============
Drop-in replacement for the stdlib math module that auto-dispatches
on UnitFloat, UnitArray, ProbUnitFloat, and ProbUnitArray.

Usage
-----
import quantia.math as mmath

mmath.log10(x)   # works for float, UnitFloat, ProbUnitFloat, UnitArray, ProbUnitArray
mmath.exp(x)
mmath.sqrt(x)
mmath.log(x)
mmath.sin(x)     # expects angle unit on UnitFloat; plain float treated as radians
mmath.cos(x)
mmath.tan(x)

Falls through to stdlib math for plain int / float so existing code
that does `import quantia.math as math` keeps working.

Design rules
------------
1. Every function handles: int/float, UnitFloat, UnitArray,
   ProbUnitFloat, ProbUnitArray.
2. Trig functions validate that UnitFloat / UnitArray carry an angle unit.
3. log / log10 / exp produce dimensionless results.
4. sqrt preserves unit exponents (e.g. sqrt(m^2) → m).
5. Unknown types raise TypeError with a clear message.
"""

from __future__ import annotations
import math as _math
import array as _array
from fractions import Fraction


# ── lazy imports to avoid circular deps ──────────────────────────────────────

def _uf():
    from quantia._scalar import UnitFloat
    return UnitFloat

def _ua():
    from quantia._array import UnitArray
    return UnitArray

def _puf():
    from quantia.prob._scalar import ProbUnitFloat
    return ProbUnitFloat

def _pua():
    from quantia.prob._array import ProbUnitArray
    return ProbUnitArray

def _cu():
    from quantia._compound import CompoundUnit
    return CompoundUnit

def _make_unit(u):
    from quantia._compound import _make_unit as _mu
    return _mu(u)


# ── angle validation ──────────────────────────────────────────────────────────

_ANGLE_SI = "rad"   # SI unit for angle

def _to_radians_value(uf) -> float:
    """
    Extract a plain-float radian value from a UnitFloat.
    Raises DimensionError if the unit is not an angle.
    """
    from quantia._exceptions import DimensionError
    from quantia._registry import get_unit

    cu = uf.unit
    # Accept dimensionless (plain radians passed as float-like UnitFloat)
    if cu.is_dimensionless():
        return uf.value
    # Must be a single angle unit
    if len(cu._f) != 1:
        raise DimensionError(
            f"Trig functions require an angle unit, got '{cu}'")
    sym, exp = next(iter(cu._f.items()))
    u = get_unit(sym)
    if u.quantity != "angle":
        raise DimensionError(
            f"Trig functions require an angle unit, got '{cu}'")
    # Convert to radians
    return uf.value * u.to_si ** float(exp)


# ── core dispatcher factory ───────────────────────────────────────────────────

def _make_func(
    scalar_fn,          # float → float
    result_unit,        # str | CompoundUnit | None | callable(input_unit) → CompoundUnit
    *,
    angle_check=False,  # if True, validate angle unit before applying
    name="<unknown>",
):
    """
    Build a dispatching math function.

    result_unit can be:
      None                  → dimensionless CompoundUnit
      str                   → fixed unit symbol, e.g. "rad"
      CompoundUnit          → fixed compound unit
      callable(cu) → cu     → derive result unit from input unit (used by sqrt)
    """

    def _get_result_unit(input_cu):
        if result_unit is None:
            return _cu().dimensionless()
        if callable(result_unit):
            return result_unit(input_cu)
        return _make_unit(result_unit)

    def dispatch(x):
        UnitFloat   = _uf()
        UnitArray   = _ua()
        ProbUnitFloat = _puf()
        ProbUnitArray = _pua()

        # ── plain numeric ─────────────────────────────────────────────────────
        if isinstance(x, (int, float)):
            return scalar_fn(float(x))

        # ── UnitFloat ─────────────────────────────────────────────────────────
        if isinstance(x, UnitFloat):
            v = _to_radians_value(x) if angle_check else x.value
            ru = _get_result_unit(x.unit)
            return UnitFloat(scalar_fn(v), ru)

        # ── UnitArray ─────────────────────────────────────────────────────────
        if isinstance(x, UnitArray):
            if angle_check:
                # convert every element to radians first
                from quantia._registry import get_unit as _gu
                cu = x.unit
                if len(cu._f) == 1:
                    sym, exp = next(iter(cu._f.items()))
                    factor = _gu(sym).to_si ** float(exp)
                else:
                    factor = 1.0
                data = _array.array('d', (scalar_fn(v * factor) for v in x.values))
            else:
                data = _array.array('d', (scalar_fn(v) for v in x.values))
            ru = _get_result_unit(x.unit)
            return UnitArray(data, ru)

        # ── ProbUnitFloat ─────────────────────────────────────────────────────
        if isinstance(x, ProbUnitFloat):
            if angle_check:
                from quantia._registry import get_unit as _gu
                cu = x._unit
                if len(cu._f) == 1:
                    sym, exp = next(iter(cu._f.items()))
                    factor = _gu(sym).to_si ** float(exp)
                else:
                    factor = 1.0
                samples = _array.array('d', (scalar_fn(v * factor) for v in x._samples))
            else:
                samples = _array.array('d', (scalar_fn(v) for v in x._samples))
            ru = _get_result_unit(x._unit)
            return ProbUnitFloat._from_raw(samples, ru)

        # ── ProbUnitArray ─────────────────────────────────────────────────────
        if isinstance(x, ProbUnitArray):
            if angle_check:
                from quantia._registry import get_unit as _gu
                cu = x._unit
                if len(cu._f) == 1:
                    sym, exp = next(iter(cu._f.items()))
                    factor = _gu(sym).to_si ** float(exp)
                else:
                    factor = 1.0
                data = _array.array('d', (scalar_fn(v * factor) for v in x._data))
            else:
                data = _array.array('d', (scalar_fn(v) for v in x._data))
            ru = _get_result_unit(x._unit)
            return ProbUnitArray._from_flat(data, ru, x._len, x._n)

        raise TypeError(
            f"quantia.math.{name}() does not support type "
            f"{type(x).__name__!r}. Expected float, UnitFloat, UnitArray, "
            f"ProbUnitFloat, or ProbUnitArray.")

    dispatch.__name__ = name
    dispatch.__doc__  = (
        f"quantia-aware {name}(). Dispatches on float, UnitFloat, UnitArray, "
        f"ProbUnitFloat, ProbUnitArray. Falls through to math.{name} for plain numbers."
    )
    return dispatch


# ── sqrt: result unit is input_unit ^ (1/2) ──────────────────────────────────

def _sqrt_unit(cu):
    return cu ** Fraction(1, 2)


# ── public functions ──────────────────────────────────────────────────────────

# Logarithms & exponentials — always dimensionless result
log    = _make_func(_math.log,    None,        name="log")
log10  = _make_func(_math.log10,  None,        name="log10")
log2   = _make_func(_math.log2,   None,        name="log2")
exp    = _make_func(_math.exp,    None,        name="exp")
exp2   = _make_func(lambda x: 2**x, None,     name="exp2")

# Powers & roots
sqrt   = _make_func(_math.sqrt,   _sqrt_unit,  name="sqrt")

def cbrt(x):
    """Cube root — preserves unit^(1/3)."""
    def _cbrt(v): return _math.copysign(abs(v)**(1/3), v)
    return _make_func(_cbrt, lambda cu: cu ** Fraction(1, 3), name="cbrt")(x)

def pow(base, exp_val):
    """
    quantia-aware pow(base, exp).
    """
    UnitFloat     = _uf()
    UnitArray     = _ua()
    ProbUnitFloat = _puf()
    ProbUnitArray = _pua()

    if isinstance(exp_val, (UnitFloat, UnitArray, ProbUnitFloat, ProbUnitArray)):
        if not exp_val._unit.is_dimensionless():
            raise TypeError(f"exponent must be dimensionless, got unit {exp_val._unit}")

    if isinstance(exp_val, (int, float)):
        if isinstance(base, (UnitFloat, UnitArray, ProbUnitFloat, ProbUnitArray)):
            return base ** exp_val
        return _math.pow(float(base), exp_val)

    if isinstance(exp_val, UnitFloat):
        if isinstance(base, (UnitFloat, UnitArray, ProbUnitFloat, ProbUnitArray)):
            return base ** exp_val._value
        return _math.pow(float(base), exp_val._value)
    
    if isinstance(exp_val, ProbUnitFloat):
        if not base._unit.is_dimensionless(): # base must be dimensionless to apply probabilistic exponentiation
            raise TypeError(f"base must be dimensionless when exponent is ProbUnitFloat, got unit {base._unit}")
        if isinstance(base, UnitFloat):
            a = base._value
            samples = _array.array('d',(a**b for b in exp_val._samples))
            return ProbUnitFloat._from_raw(samples=samples, unit="1")
        if isinstance(base, ProbUnitFloat):
            if base._n != exp_val._n:
                raise ValueError("Length of base and exponent samples must match for ProbUnitFloat exponentiation")
            samples = _array.array('d',(a**b for a,b in zip(base._samples, exp_val._samples)))
            return ProbUnitFloat._from_raw(samples=samples, unit="1")
        if isinstance(base, UnitArray):
            data = _array.array('d',(a**b for a in base._data for b in exp_val._samples))
            return ProbUnitArray._from_flat(data, "1", len(base._data), exp_val._n)
        if isinstance(base, ProbUnitArray):
            if base._n != exp_val._n:
                raise ValueError("Length of base and exponent samples must match for ProbUnitArray exponentiation")
            flat = []
            for r in range(base._len):
                samples = _array.array('d',(a**b for a,b in zip(base._row(r), exp_val._samples)))
                flat.extend(samples)
            return ProbUnitArray._from_flat(flat, "1", base._len, exp_val._n)
        return ProbUnitFloat._from_raw([_math.pow(float(base), e) for e in exp_val._samples], "1")

    raise TypeError(f"exponent must be a plain number, UnitFloat or ProbUnitFloat, got {type(exp_val).__name__!r}")

# Absolute value
def fabs(x):
    """quantia-aware fabs() — preserves unit."""
    return abs(x) if not isinstance(x, (int, float)) else _math.fabs(x)

# Trig — validate angle unit on UnitFloat/UnitArray/Prob*
sin    = _make_func(_math.sin,    None,  angle_check=True,  name="sin")
cos    = _make_func(_math.cos,    None,  angle_check=True,  name="cos")
tan    = _make_func(_math.tan,    None,  angle_check=True,  name="tan")

# Inverse trig — return radians (UnitFloat with 'rad')
asin   = _make_func(_math.asin,   "rad", name="asin")
acos   = _make_func(_math.acos,   "rad", name="acos")
atan   = _make_func(_math.atan,   "rad", name="atan")

def atan2(y, x):
    """quantia-aware atan2. Both args must be compatible units or plain floats."""
    UnitFloat = _uf()
    if isinstance(y, UnitFloat) and isinstance(x, UnitFloat):
        # units must be compatible; ratio is dimensionless
        yv = y.si_value()
        xv = x.si_value()
        from quantia._scalar import UnitFloat as UF
        return UF(_math.atan2(yv, xv), "rad")
    if isinstance(y, (int, float)) and isinstance(x, (int, float)):
        return _math.atan2(float(y), float(x))
    raise TypeError("atan2 requires both arguments to be the same type")

# Hyperbolic
sinh   = _make_func(_math.sinh,   None,  name="sinh")
cosh   = _make_func(_math.cosh,   None,  name="cosh")
tanh   = _make_func(_math.tanh,   None,  name="tanh")
asinh  = _make_func(_math.asinh,  None,  name="asinh")
acosh  = _make_func(_math.acosh,  None,  name="acosh")
atanh  = _make_func(_math.atanh,  None,  name="atanh")

# Rounding — preserve unit
def ceil(x):
    """quantia-aware ceil — preserves unit."""
    return _math.ceil(x)   # __ceil__ is defined on UnitFloat already

def floor(x):
    """quantia-aware floor — preserves unit."""
    return _math.floor(x)  # __floor__ is defined on UnitFloat already

def round_(x, n=None):
    """quantia-aware round — preserves unit. Named round_ to avoid shadowing builtin."""
    return builtins_round(x, n)

import builtins as _builtins
builtins_round = _builtins.round

# Pass-through constants from stdlib math
pi    = _math.pi
e     = _math.e
tau   = _math.tau
inf   = _math.inf
nan   = _math.nan

# Pass-through pure-numeric functions from stdlib
# (these never take unit arguments)
factorial = _math.factorial
gcd       = _math.gcd
comb      = _math.comb
perm      = _math.perm
isclose   = _math.isclose
isfinite  = _math.isfinite
isinf     = _math.isinf
isnan     = _math.isnan
degrees   = _math.degrees   # float → float only; use .to('deg') for UnitFloat
radians   = _math.radians   # float → float only; use .to('rad') for UnitFloat
hypot     = _math.hypot
ldexp     = _math.ldexp
frexp     = _math.frexp
modf      = _math.modf
trunc     = _math.trunc
copysign  = _math.copysign
fmod      = _math.fmod
remainder = _math.remainder


# ── summary of what's available ───────────────────────────────────────────────

__all__ = [
    # quantia-aware (dispatch on all four types)
    "log", "log10", "log2",
    "exp", "exp2",
    "sqrt", "cbrt", "pow", "fabs",
    "sin", "cos", "tan",
    "asin", "acos", "atan", "atan2",
    "sinh", "cosh", "tanh",
    "asinh", "acosh", "atanh",
    "ceil", "floor", "round_",
    # constants
    "pi", "e", "tau", "inf", "nan",
    # pass-through numerics
    "factorial", "gcd", "comb", "perm",
    "isclose", "isfinite", "isinf", "isnan",
    "degrees", "radians",
    "hypot", "ldexp", "frexp", "modf",
    "trunc", "copysign", "fmod", "remainder",
]
