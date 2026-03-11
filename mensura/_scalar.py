from __future__ import annotations
import math
import operator
from mensura._compound import CompoundUnit, _make_unit
from mensura._registry import get_unit
from mensura._exceptions import IncompatibleUnitsError, DimensionError


def _to_kelvin(v: float, sym: str) -> float:
    if sym == "K":   return v
    if sym == "°C":  return v + 273.15
    if sym == "°F":  return (v + 459.67) * 5 / 9
    raise DimensionError(f"Not a temperature unit: '{sym}'")

def _from_kelvin(v: float, sym: str) -> float:
    if sym == "K":   return v
    if sym == "°C":  return v - 273.15
    if sym == "°F":  return v * 9 / 5 - 459.67
    raise DimensionError(f"Not a temperature unit: '{sym}'")


class UnitFloat:
    """An exact scalar value with a CompoundUnit."""

    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit):
        self._value = float(value)
        self._unit  = _make_unit(unit)

    @property
    def value(self) -> float:        return self._value
    @property
    def unit(self) -> CompoundUnit:  return self._unit

    # ── Conversion ───────────────────────────────────────────────────────────

    def to_si(self) -> "UnitFloat":
        if len(self._unit._f) == 1:
            s, e = next(iter(self._unit._f.items()))
            if get_unit(s).quantity == "temperature" and e == 1:
                return UnitFloat(_to_kelvin(self._value, s), "K")
        return UnitFloat(self._value * self._unit.si_factor(),
                         self._unit.to_si_compound())

    def si_value(self) -> float:
        return self.to_si()._value

    def to(self, target) -> "UnitFloat":
        tcu = _make_unit(target)
        if isinstance(target, str):
            u = get_unit(target)
            if u.quantity == "temperature":
                s, _ = next(iter(self._unit._f.items()))
                k = _to_kelvin(self._value, s)
                return UnitFloat(_from_kelvin(k, target), target)
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
        if isinstance(o, UnitFloat):
            return UnitFloat(self._value + self._coerce(o), self._unit)
        if isinstance(o, (int, float)):
            return UnitFloat(self._value + o, self._unit)
        return NotImplemented
    def __radd__(self, o): return self.__add__(o)

    def __sub__(self, o):
        if isinstance(o, UnitFloat):
            return UnitFloat(self._value - self._coerce(o), self._unit)
        if isinstance(o, (int, float)):
            return UnitFloat(self._value - o, self._unit)
        return NotImplemented
    def __rsub__(self, o):
        if isinstance(o, (int, float)):
            return UnitFloat(o - self._value, self._unit)
        return NotImplemented

    def __mul__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit * o._unit
            return UnitFloat(self._value * o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int, float)):
            return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __rmul__(self, o):
        if isinstance(o, (int, float)):
            return UnitFloat(self._value * o, self._unit)
        return NotImplemented

    def __truediv__(self, o):
        if isinstance(o, UnitFloat):
            cu = self._unit / o._unit
            return UnitFloat(self._value / o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int, float)):
            return UnitFloat(self._value / o, self._unit)
        return NotImplemented
    def __rtruediv__(self, o):
        if isinstance(o, (int, float)):
            return UnitFloat(o / self._value, self._unit.invert())
        return NotImplemented

    def __pow__(self, e):
        return UnitFloat(self._value ** e, self._unit ** e)
    def __neg__(self):  return UnitFloat(-self._value, self._unit)
    def __abs__(self):  return UnitFloat(abs(self._value), self._unit)
    def __float__(self): return self._value
    def __int__(self):   return int(self._value)
    def __round__(self, n=None): return UnitFloat(round(self._value, n), self._unit)
    def __floor__(self): return UnitFloat(math.floor(self._value), self._unit)
    def __ceil__(self):  return UnitFloat(math.ceil(self._value),  self._unit)

    # ── Comparison ───────────────────────────────────────────────────────────

    def _cmp(self, o):
        if isinstance(o, UnitFloat):  return self.si_value(), o.si_value()
        if isinstance(o, (int,float)):return self.si_value(), float(o)
        return NotImplemented

    def __eq__(self, o):
        r = self._cmp(o)
        return r is not NotImplemented and math.isclose(r[0], r[1])
    def __lt__(self, o): r = self._cmp(o); return r[0] <  r[1]
    def __le__(self, o): r = self._cmp(o); return r[0] <= r[1]
    def __gt__(self, o): r = self._cmp(o); return r[0] >  r[1]
    def __ge__(self, o): r = self._cmp(o); return r[0] >= r[1]

    def __repr__(self): return f"UnitFloat({self._value!r}, '{self._unit}')"
    def __str__(self):  return f"{self._value} {self._unit}"
    def __format__(self, spec): return f"{self._value:{spec}} {self._unit}"