"""
quantia/_dispatch.py
====================
Unified arithmetic dispatch for UnitFloat, UnitArray, ProbUnitFloat,
and ProbUnitArray.

Design
------
All four classes delegate their arithmetic dunder methods here.
The dispatcher:
  1. Coerces plain int/float to UnitFloat("1")
  2. Validates operands (unit compatibility, n, len)
  3. Determines output type via the 2x2 rule (array/scalar x prob/det)
  4. Computes result values via unified _get_val indexing
  5. Constructs and returns the output object

Lazy imports are used throughout to avoid circular imports, since
the four type modules import this module at their top level.

Output type rule (2x2)
----------------------
Two independent axes:
  array axis:         UnitFloat / ProbUnitFloat  <  UnitArray / ProbUnitArray
  probabilistic axis: UnitFloat / UnitArray      <  ProbUnitFloat / ProbUnitArray

Output = combination of the maximum on each axis:
  (scalar, deterministic) -> UnitFloat
  (array,  deterministic) -> UnitArray
  (scalar, probabilistic) -> ProbUnitFloat
  (array,  probabilistic) -> ProbUnitArray

Broadcast semantics (i = element index, j = sample index)
----------------------------------------------------------
  UnitFloat      -> _get_val(x, i, j) = x._value          (ignores i, j)
  UnitArray      -> _get_val(x, i, j) = x._data[i]        (ignores j)
  ProbUnitFloat  -> _get_val(x, i, j) = x._samples[j]     (ignores i)
  ProbUnitArray  -> _get_val(x, i, j) = x._data[i*_n + j]

The output flat array is built as:
  for i in range(out_len):
      for j in range(out_n):
          result[i*out_n + j] = op(_get_val(a, i, j), _get_val(b, i, j))
"""
from __future__ import annotations
import array as _array
import operator as _operator
from typing import Any


# ── Coercion ──────────────────────────────────────────────────────────────────

def _coerce(x: Any) -> Any:
    """Normalize plain int/float to UnitFloat("1")."""
    if isinstance(x, (int, float)):
        from quantia._scalar import UnitFloat
        return UnitFloat(float(x), "1")
    return x


# ── Type classification ───────────────────────────────────────────────────────

def _is_array(x: Any) -> bool:
    from quantia._array import UnitArray
    from quantia.prob._array import ProbUnitArray
    return isinstance(x, (UnitArray, ProbUnitArray))


def _is_probabilistic(x: Any) -> bool:
    from quantia.prob._scalar import ProbUnitFloat
    from quantia.prob._array import ProbUnitArray
    return isinstance(x, (ProbUnitFloat, ProbUnitArray))


def _output_type(a: Any, b: Any) -> type:
    """Determine output type using the 2x2 rule."""
    from quantia._scalar import UnitFloat
    from quantia._array import UnitArray
    from quantia.prob._scalar import ProbUnitFloat
    from quantia.prob._array import ProbUnitArray

    arr  = _is_array(a)         or _is_array(b)
    prob = _is_probabilistic(a) or _is_probabilistic(b)

    if arr and prob:  return ProbUnitArray
    if arr:           return UnitArray
    if prob:          return ProbUnitFloat
    return UnitFloat


# ── Shape helpers ─────────────────────────────────────────────────────────────

def _get_len(x: Any) -> int | None:
    """Return number of elements, or None if x is scalar."""
    return getattr(x, '_len', None)


def _get_n(x: Any) -> int | None:
    """Return number of Monte Carlo samples, or None if x is deterministic."""
    return getattr(x, '_n', None)


# ── Validation ────────────────────────────────────────────────────────────────

def _validate(op: str, a: Any, b: Any) -> None:
    """
    Raise an appropriate error if the operation is invalid.

    add / sub  : units must be compatible
    pow        : exponent must be dimensionless; base must also be
                 dimensionless when exponent has multiple values
    n          : must match if both operands are probabilistic
    len        : must match if both operands are array-typed
    """
    from quantia._exceptions import IncompatibleUnitsError, DimensionError

    if op in ("add", "sub"):
        if not a._unit.is_compatible(b._unit):
            raise IncompatibleUnitsError(a._unit, b._unit)

    if op == "pow":
        if not b._unit.is_dimensionless():
            raise DimensionError(
                f"Exponent must be dimensionless, got '{b._unit}'"
            )
        if _is_array(b) or _is_probabilistic(b):
            if not a._unit.is_dimensionless():
                raise DimensionError(
                    f"Base must be dimensionless when exponent has multiple "
                    f"values, got '{a._unit}'"
                )

    n_a, n_b = _get_n(a), _get_n(b)
    if n_a is not None and n_b is not None and n_a != n_b:
        raise ValueError(f"Sample count mismatch: {n_a} != {n_b}")

    l_a, l_b = _get_len(a), _get_len(b)
    if l_a is not None and l_b is not None and l_a != l_b:
        raise ValueError(f"Length mismatch: {l_a} != {l_b}")


# ── Output unit ───────────────────────────────────────────────────────────────

def _output_unit(op: str, a: Any, b: Any):
    """Compute the CompoundUnit for the result of op(a, b)."""
    from quantia._compound import CompoundUnit

    if op in ("add", "sub"):
        return a._unit

    if op == "mul":
        cu = a._unit * b._unit
        return CompoundUnit.dimensionless() if cu.is_dimensionless() else cu

    if op == "truediv":
        cu = a._unit / b._unit
        return CompoundUnit.dimensionless() if cu.is_dimensionless() else cu

    if op == "pow":
        from quantia._scalar import UnitFloat
        if isinstance(b, UnitFloat):
            # single known exponent — result unit is a._unit ** b._value
            return a._unit ** b._value
        # multiple exponent values — base is guaranteed dimensionless (validated)
        return CompoundUnit.dimensionless()

    raise ValueError(f"Unknown operator: '{op}'")


# ── Value extraction ──────────────────────────────────────────────────────────

def _get_val(x: Any, i: int, j: int) -> float:
    """
    Extract a single float from x at logical position (i, j).

    i : element index  (used by UnitArray and ProbUnitArray)
    j : sample index   (used by ProbUnitFloat and ProbUnitArray)
    """
    from quantia._scalar import UnitFloat
    from quantia._array import UnitArray
    from quantia.prob._scalar import ProbUnitFloat
    from quantia.prob._array import ProbUnitArray

    if isinstance(x, UnitFloat):     return x._value
    if isinstance(x, UnitArray):     return x._data[i]
    if isinstance(x, ProbUnitFloat): return x._samples[j]
    if isinstance(x, ProbUnitArray): return x._data[i * x._n + j]
    raise TypeError(f"Unsupported type in _get_val: {type(x).__name__!r}")


# ── Operator map ──────────────────────────────────────────────────────────────

_OPS = {
    "add":     _operator.add,
    "sub":     _operator.sub,
    "mul":     _operator.mul,
    "truediv": _operator.truediv,
    "pow":     _operator.pow,
}


# ── Main dispatcher ───────────────────────────────────────────────────────────

def _dispatch(op: str, a: Any, b: Any) -> Any:
    """
    Unified arithmetic dispatcher.

    Parameters
    ----------
    op : str
        One of 'add', 'sub', 'mul', 'truediv', 'pow'.
    a  : left operand
    b  : right operand

    Both operands may be int, float, UnitFloat, UnitArray,
    ProbUnitFloat, or ProbUnitArray.

    Returns
    -------
    UnitFloat, UnitArray, ProbUnitFloat, or ProbUnitArray.

    Raises
    ------
    TypeError               if operand types are not supported
    IncompatibleUnitsError  for incompatible units in add/sub
    DimensionError          for invalid pow operands
    ValueError              for n or len mismatch
    """
    from quantia._scalar import UnitFloat
    from quantia._array import UnitArray
    from quantia.prob._scalar import ProbUnitFloat
    from quantia.prob._array import ProbUnitArray

    # 1. Coerce plain numbers to UnitFloat("1")
    a = _coerce(a)
    b = _coerce(b)

    # 2. Type check
    _supported = (UnitFloat, UnitArray, ProbUnitFloat, ProbUnitArray)
    if not isinstance(a, _supported) or not isinstance(b, _supported):
        raise TypeError(
            f"Unsupported operand types for '{op}': "
            f"{type(a).__name__!r} and {type(b).__name__!r}"
        )

    # 3. Validate
    _validate(op, a, b)

    # 4. Output metadata
    OutType  = _output_type(a, b)
    out_unit = _output_unit(op, a, b)
    out_n    = _get_n(a)   or _get_n(b)   or 1
    out_len  = _get_len(a) or _get_len(b) or 1

    # 5. Conversion factor — for add/sub, scale b to a's unit
    #    for mul/truediv/pow, no conversion (units combine algebraically)
    factor_b = (b._unit.si_factor() / a._unit.si_factor()
                if op in ("add", "sub") else 1.0)

    # 6. Python operator
    py_op = _OPS[op]

    # 7. Compute and construct
    if OutType is UnitFloat:
        val = py_op(_get_val(a, 0, 0), _get_val(b, 0, 0) * factor_b)
        return UnitFloat(val, out_unit)

    if OutType is UnitArray:
        data = _array.array('d', (
            py_op(_get_val(a, i, 0), _get_val(b, i, 0) * factor_b)
            for i in range(out_len)
        ))
        return UnitArray(data, out_unit)

    if OutType is ProbUnitFloat:
        samples = _array.array('d', (
            py_op(_get_val(a, 0, j), _get_val(b, 0, j) * factor_b)
            for j in range(out_n)
        ))
        return ProbUnitFloat._from_raw(samples, out_unit)

    if OutType is ProbUnitArray:
        flat = _array.array('d', (
            py_op(_get_val(a, i, j), _get_val(b, i, j) * factor_b)
            for i in range(out_len)
            for j in range(out_n)
        ))
        return ProbUnitArray._from_flat(flat, out_unit, out_len, out_n)

    raise TypeError(  # unreachable — guards above are exhaustive
        f"Cannot dispatch '{op}' for "
        f"{type(a).__name__!r} and {type(b).__name__!r}"
    )