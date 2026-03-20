from __future__ import annotations
import array as _array
import math
import operator
from typing import Iterable, Iterator, Union
import csv
from pathlib import Path
from quantia._compound import CompoundUnit, _make_unit
from quantia._scalar import UnitFloat
from quantia._exceptions import IncompatibleUnitsError


class UnitArray:
    """An exact array of values sharing a single physical unit.

    All elements carry the same unit. Arithmetic operations between
    two ``UnitArray`` instances check dimensional compatibility and
    handle unit conversion automatically.

    Parameters
    ----------
    values : iterable of float
        Numeric values, all in the given unit.
    unit : str or CompoundUnit
        Physical unit shared by all elements.

    Raises
    ------
    TypeError
        If any element of ``values`` is not numeric.

    Examples
    --------
    >>> import quantia as qu
    >>> heights = qu.QA([1.75, 1.80, 1.65], 'm')
    >>> heights.mean()
    UnitFloat(1.7333..., 'm')

    >>> heights.to('cm')
    UnitArray([175.0, 180.0, 165.0], 'cm')

    Boolean mask filtering:

    >>> tall = heights[heights > qu.Q(1.78, 'm')]
    >>> list(tall.values)
    [1.8]
    """

    def __init__(self, values: Iterable[float],
                 unit: Union[str, "CompoundUnit"]) -> None:
        raw = list(values)
        for i, v in enumerate(raw):
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"UnitArray element {i} must be numeric, got {type(v).__name__!r}")
        self._data = _array.array('d', (float(v) for v in raw))
        self._unit = _make_unit(unit)

    @property
    def unit(self) -> CompoundUnit:
        return self._unit
    
    @property
    def values(self) -> _array.array[float]:
        return self._data

    def to_si(self) -> "UnitArray":
        """Convert all elements to the SI base unit representation.

        Returns
        -------
        UnitArray
            New array with values in SI base units.

        Examples
        --------
        >>> qu.QA([1.0, 2.0], 'km').to_si()
        UnitArray([1000.0, 2000.0], 'm')
        """
        f = self._unit.si_factor()
        return UnitArray((v*f for v in self._data), self._unit.to_si_compound())

    def to(self, target: Union[str, "CompoundUnit"]) -> "UnitArray":
        """Convert all elements to a different unit of the same quantity.

        Parameters
        ----------
        target : str or CompoundUnit
            Target unit. Must be dimensionally compatible.

        Returns
        -------
        UnitArray
            New array with all values expressed in ``target``.

        Raises
        ------
        IncompatibleUnitsError
            If ``target`` has different physical dimensions.

        Examples
        --------
        >>> qu.QA([1.0, 2.0, 3.0], 'km').to('m')
        UnitArray([1000.0, 2000.0, 3000.0], 'm')
        """
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
    def __add__(self, o: Union["UnitArray", "UnitFloat", int, float]) -> "UnitArray":
        return self._elem(o, operator.add)
    def __radd__(self, o: Union["UnitArray", "UnitFloat", int, float]) -> "UnitArray":
        return self.__add__(o)
    def __sub__(self, o: Union["UnitArray", "UnitFloat", int, float]) -> "UnitArray":
        return self._elem(o, operator.sub)
    def __rsub__(self, o: Union[int, float]) -> "UnitArray":
        if isinstance(o, (int,float)):
            return UnitArray((o-v for v in self._data), self._unit)
        return NotImplemented
    def __mul__(self, o: Union["UnitArray", "UnitFloat", int, float]) -> "UnitArray":
        return self._mul_div(o, operator.mul)
    def __rmul__(self, o: Union[int, float]) -> "UnitArray":
        if isinstance(o, (int,float)):
            return UnitArray((v*o for v in self._data), self._unit)
        return NotImplemented
    def __truediv__(self, o: Union["UnitArray", "UnitFloat", int, float]) -> "UnitArray":
        return self._mul_div(o, operator.truediv)
    def __rtruediv__(self, o: Union[int, float]) -> "UnitArray":
        if isinstance(o, (int,float)):
            return UnitArray((o/v for v in self._data), self._unit.invert())
        return NotImplemented
    def __pow__(self, e: Union[int, float]) -> "UnitArray":
        return UnitArray((v**e for v in self._data), self._unit**e)
    def __neg__(self) -> "UnitArray":
        return UnitArray((-v for v in self._data), self._unit)
    def __abs__(self) -> "UnitArray":
        return UnitArray((abs(v) for v in self._data), self._unit)
    def _cmp(self, o, op):
        if isinstance(o, (UnitArray, UnitFloat)):
            ou = o._unit; ov = o._data if isinstance(o, UnitArray) else [o._value]*len(self._data)
            f = ou.si_factor() / self._unit.si_factor()
            return [op(a, b*f) for a,b in zip(self._data, ov)]
        if isinstance(o, (int,float)):
            return [op(v, float(o)) for v in self._data]
        return NotImplemented
    def __eq__(self, o): return self._cmp(o, lambda a,b: math.isclose(a,b))
    def __lt__(self, o): return self._cmp(o, operator.lt)
    def __le__(self, o): return self._cmp(o, operator.le)
    def __gt__(self, o): return self._cmp(o, operator.gt)
    def __ge__(self, o): return self._cmp(o, operator.ge)

    def sum(self)  -> "UnitFloat":
        """Return the sum of all elements.

        Returns
        -------
        UnitFloat
            Sum in the array's unit.

        Examples
        --------
        >>> qu.QA([1.0, 2.0, 3.0], 'm').sum()
        UnitFloat(6.0, 'm')
        """
        return UnitFloat(sum(self._data), self._unit)
    
    def mean(self) -> "UnitFloat":
        """Return the arithmetic mean of all elements.

        Returns
        -------
        UnitFloat
            Mean in the array's unit.

        Examples
        --------
        >>> qu.QA([10.0, 20.0, 30.0], 'm').mean()
        UnitFloat(20.0, 'm')
        """
        return UnitFloat(sum(self._data)/len(self._data), self._unit)
    
    def min(self)  -> "UnitFloat":
        """Return the minimum element.

        Returns
        -------
        UnitFloat
            Minimum value in the array's unit.
        """
        return UnitFloat(min(self._data), self._unit)
    
    def max(self)  -> "UnitFloat":
        """Return the maximum element.

        Returns
        -------
        UnitFloat
            Maximum value in the array's unit.
        """
        return UnitFloat(max(self._data), self._unit)
    
    def dot(self, o: "UnitArray") -> "UnitFloat":
        """Compute the dot product with another array.

        Parameters
        ----------
        o : UnitArray
            Second operand. Must have the same length.

        Returns
        -------
        UnitFloat
            Scalar result with the product unit.

        Raises
        ------
        ValueError
            If arrays have different lengths.

        Examples
        --------
        >>> a = qu.QA([1.0, 2.0, 3.0], 'N')
        >>> b = qu.QA([4.0, 5.0, 6.0], 'm')
        >>> a.dot(b)
        UnitFloat(32.0, 'J')
        """
        if len(self) != len(o):
            raise ValueError("Length mismatch for dot product")
        val = sum(a*b for a,b in zip(self._data, o._data))
        cu  = self._unit * o._unit
        return UnitFloat(val, CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)

    def __len__(self) -> int:
        return len(self._data)
    def __iter__(self) -> Iterator["UnitFloat"]:
        return (UnitFloat(v, self._unit) for v in self._data)
    def __getitem__(self, i: Union[int, slice, list]) -> Union["UnitFloat", "UnitArray"]:
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
    def __setitem__(self, i: int, val: Union["UnitFloat", float]) -> None:
        if isinstance(val, UnitFloat):
            if not self._unit.is_compatible(val.unit): raise IncompatibleUnitsError(self._unit, val.unit)
            self._data[i] = val.value * val.unit.si_factor() / self._unit.si_factor()
        else: self._data[i] = float(val)
    def append(self, val: Union["UnitFloat", float]) -> None:
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
    
    def to_csv(self, path: Union[str, "Path"], header: str | None = None) -> None:
        """
        Write values to a single-column CSV file.

        Parameters
        ----------
        path   : str | Path
        header : str, optional.  Defaults to "value [<unit>]".
        """
        col = header or f"value [{self._unit}]"
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([col])
            for v in self._data:
                w.writerow([v])