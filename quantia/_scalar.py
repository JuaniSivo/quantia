from __future__ import annotations
import math
import operator
from quantia._compound import CompoundUnit, _make_unit
from quantia._registry import get_unit, AffineUnit
from quantia._exceptions import IncompatibleUnitsError, DimensionError


class UnitFloat:
    """An exact scalar value with a CompoundUnit."""

    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit):
        # 2d: validate value
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"UnitFloat value must be numeric, got {type(value).__name__!r}")
        if math.isnan(value):
            raise ValueError("UnitFloat value must not be NaN")
        self._value = float(value)
        self._unit  = _make_unit(unit)   # raises UnknownUnitError / UnitParseError

    @property
    def value(self) -> float:           return self._value
    @property
    def unit(self) -> CompoundUnit:     return self._unit

    # ── 2c: Unified temperature conversion via AffineUnit ────────────────────

    @staticmethod
    def _is_single_affine(cu: CompoundUnit) -> "AffineUnit | None":
        if len(cu._f) == 1:
            sym, exp = next(iter(cu._f.items()))
            u = get_unit(sym)
            if isinstance(u, AffineUnit) and exp == 1:   # ← remove `u.offset != 0.0`
                return u
        return None
    
    def to_si(self) -> "UnitFloat":
        affine = self._is_single_affine(self._unit)
        if affine:
            # Use affine.si_unit (e.g. "K" for temperature, "Pa" for pressure)
            # rather than hardcoding "K" — works for any AffineUnit
            return UnitFloat(affine.to_si_value(self._value), affine.si_unit)
        return UnitFloat(self._value * self._unit.si_factor(),
                        self._unit.to_si_compound())

    def si_value(self) -> float:
        return self.to_si()._value
    
    def to(self, target) -> "UnitFloat":
        tcu = _make_unit(target)
        src_affine = self._is_single_affine(self._unit)
        tgt_affine = self._is_single_affine(tcu)
        if src_affine or tgt_affine:
            if not (src_affine and tgt_affine):
                raise DimensionError(
                    f"Cannot mix affine unit '{self._unit}' with "
                    f"non-affine unit '{tcu}' in .to(). "
                    "Both sides must be affine (e.g. both temperature or "
                    "both pressure absolute/gauge).")
            si_val = src_affine.to_si_value(self._value)
            return UnitFloat(tgt_affine.from_si_value(si_val), target)
        # General multiplicative path
        if not self._unit.is_compatible(tcu):
            raise IncompatibleUnitsError(self._unit, tcu)
        return UnitFloat(
            self._value * self._unit.si_factor() / tcu.si_factor(), tcu)

    # ── Arithmetic ───────────────────────────────────────────────────────────

    def _coerce(self, o: "UnitFloat") -> float:
        if not self._unit.is_compatible(o._unit):
            raise IncompatibleUnitsError(self._unit, o._unit)
        return o._value * o._unit.si_factor() / self._unit.si_factor()

    def __add__(self, o):
        if isinstance(o, UnitFloat):  return UnitFloat(self._value + self._coerce(o), self._unit)
        if isinstance(o, (int,float)):return UnitFloat(self._value + o,               self._unit)
        return NotImplemented
    def __radd__(self, o): return self.__add__(o)

    def __sub__(self, o):
        if isinstance(o, UnitFloat):  return UnitFloat(self._value - self._coerce(o), self._unit)
        if isinstance(o, (int,float)):return UnitFloat(self._value - o,               self._unit)
        return NotImplemented
    def __rsub__(self, o):
        if isinstance(o, (int,float)): return UnitFloat(o - self._value, self._unit)
        return NotImplemented

    def __mul__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit * o._unit
            return UnitFloat(self._value * o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __rmul__(self, o):
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented

    def __truediv__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit / o._unit
            return UnitFloat(self._value / o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
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
        if isinstance(o, UnitFloat):   return self.si_value(), o.si_value()
        if isinstance(o, (int,float)): return self.si_value(), float(o)
        return NotImplemented
    def __eq__(self, o):
        r = self._cmp(o); return r is not NotImplemented and math.isclose(r[0], r[1])
    def __lt__(self, o): r=self._cmp(o); return r[0]<r[1]
    def __le__(self, o): r=self._cmp(o); return r[0]<=r[1]
    def __gt__(self, o): r=self._cmp(o); return r[0]>r[1]
    def __ge__(self, o): r=self._cmp(o); return r[0]>=r[1]

    def __repr__(self): return f"UnitFloat({self._value!r}, {str(self._unit)!r})"
    def __str__(self): return f"{self._value} {self._unit}"
    def __format__(self, spec): return f"{self._value:{spec}} {self._unit}"

    # ── Serialization ─────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a plain dict that round-trips through UnitFloat.from_dict()."""
        return {"type": "UnitFloat", "value": self._value, "unit": str(self._unit)}

    @classmethod
    def from_dict(cls, d: dict) -> "UnitFloat":
        """Reconstruct from a dict produced by to_dict()."""
        if d.get("type") != "UnitFloat":
            raise ValueError(f"Expected type 'UnitFloat', got {d.get('type')!r}")
        return cls(d["value"], d["unit"])