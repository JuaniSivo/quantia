from __future__ import annotations
import array as _array
import math
import operator
from typing import Iterable, Iterator
from mensura._compound import CompoundUnit, _make_unit
from mensura._scalar import UnitFloat
from mensura._exceptions import IncompatibleUnitsError


class UnitArray:
    def __init__(self, values: Iterable[float], unit):
        # 2d: validate
        raw = list(values)
        for i, v in enumerate(raw):
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"UnitArray element {i} must be numeric, got {type(v).__name__!r}")
        self._data = _array.array('d', (float(v) for v in raw))
        self._unit = _make_unit(unit)

    @property
    def unit(self) -> CompoundUnit:   return self._unit
    @property
    def values(self) -> _array.array: return self._data

    def to_si(self):
        f = self._unit.si_factor()
        return UnitArray((v*f for v in self._data), self._unit.to_si_compound())

    def to(self, target):
        tcu = _make_unit(target)
        if not self._unit.is_compatible(tcu):
            raise IncompatibleUnitsError(self._unit, tcu)
        f = self._unit.si_factor() / tcu.si_factor()
        return UnitArray((v*f for v in self._data), tcu)

    def _elem(self, o, op):
        if isinstance(o, UnitArray):
            if len(self) != len(o): raise ValueError("Length mismatch")
            if not self._unit.is_compatible(o._unit): raise IncompatibleUnitsError(self._unit, o._unit)
            f = o._unit.si_factor() / self._unit.si_factor()
            return UnitArray((op(a, b*f) for a,b in zip(self._data, o._data)), self._unit)
        if isinstance(o, UnitFloat):
            if not self._unit.is_compatible(o.unit): raise IncompatibleUnitsError(self._unit, o.unit)
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
            return UnitArray((op(a,b) for a,b in zip(self._data, ov)),
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
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
        if len(self) != len(o): raise ValueError("Length mismatch for dot product")
        val = sum(a*b for a,b in zip(self._data, o._data))
        cu  = self._unit * o._unit
        return UnitFloat(val, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)

    def __len__(self): return len(self._data)
    def __iter__(self) -> Iterator[UnitFloat]: return (UnitFloat(v, self._unit) for v in self._data)
    def __getitem__(self, i):
        if isinstance(i, slice): return UnitArray(self._data[i], self._unit)
        return UnitFloat(self._data[i], self._unit)
    def __setitem__(self, i, val):
        if isinstance(val, UnitFloat):
            if not self._unit.is_compatible(val.unit): raise IncompatibleUnitsError(self._unit, val.unit)
            self._data[i] = val.value * val.unit.si_factor() / self._unit.si_factor()
        else: self._data[i] = float(val)
    def append(self, val):
        if isinstance(val, UnitFloat):
            if not self._unit.is_compatible(val.unit): raise IncompatibleUnitsError(self._unit, val.unit)
            self._data.append(val.value * val.unit.si_factor() / self._unit.si_factor())
        else: self._data.append(float(val))

    def __repr__(self):
        p = list(self._data[:6]); dots = ", ..." if len(self._data) > 6 else ""
        return f"UnitArray([{', '.join(str(v) for v in p)}{dots}], '{self._unit}')"
    def __str__(self): return self.__repr__()