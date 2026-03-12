from __future__ import annotations
import array as _array
import math
import operator
from typing import Iterable, Iterator
from quantia._compound import CompoundUnit, _make_unit
from quantia._scalar import UnitFloat
from quantia._exceptions import IncompatibleUnitsError


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
        # Boolean mask: UnitArray[bool_list]
        if isinstance(i, (list, tuple)) and i and isinstance(i[0], (bool,)):
            if len(i) != len(self._data):
                raise IndexError(
                    f"Boolean mask length {len(i)} != array length {len(self._data)}")
            return UnitArray(
                _array.array('d', (v for v, keep in zip(self._data, i) if keep)),
                self._unit)
        # Integer index list: UnitArray[[0, 2, 4]]
        if isinstance(i, (list, tuple)):
            return UnitArray(
                _array.array('d', (self._data[j] for j in i)),
                self._unit)
        # Slice
        if isinstance(i, slice):
            return UnitArray(self._data[i], self._unit)
        # Single integer
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
        unit = str(self._unit)
        n    = len(self._data)
        if n <= 100:
            return f"UnitArray({list(self._data)!r}, {unit!r})"
        head = list(self._data[:3])
        tail = list(self._data[-3:])
        return (f"UnitArray(<{n} values>, {unit!r}, "
                f"first={head}, last={tail})")
    def __str__(self): return self.__repr__()

    # ── Serialization ─────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"type": "UnitArray", "values": list(self._data), "unit": str(self._unit)}

    @classmethod
    def from_dict(cls, d: dict) -> "UnitArray":
        if d.get("type") != "UnitArray":
            raise ValueError(f"Expected type 'UnitArray', got {d.get('type')!r}")
        return cls(d["values"], d["unit"])
    
    def to_csv(self, path, header: str | None = None) -> None:
        """
        Write values to a single-column CSV file.

        Parameters
        ----------
        path   : str | Path
        header : str, optional.  Defaults to "value [<unit>]".
        """
        import csv
        from pathlib import Path
        col = header or f"value [{self._unit}]"
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([col])
            for v in self._data:
                w.writerow([v])