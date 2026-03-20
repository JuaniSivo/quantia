from __future__ import annotations
from typing import Union
import math
import operator
from quantia._compound import CompoundUnit, _make_unit
from quantia._registry import get_unit, AffineUnit
from quantia._exceptions import IncompatibleUnitsError, DimensionError


class UnitFloat:
    """An exact scalar value with a physical unit.

    Supports unit-safe arithmetic, conversion, and comparison.
    Dimensional compatibility is checked automatically on every
    operation that combines two ``UnitFloat`` instances.

    Parameters
    ----------
    value : float
        Numeric value in the given unit. Must not be NaN.
    unit : str or CompoundUnit
        Unit expression string (e.g. ``'kg·m/s^2'``, ``'psia'``) or
        a :class:`~quantia._compound.CompoundUnit` instance.

    Raises
    ------
    UnknownUnitError
        If ``unit`` contains an unregistered symbol.
    UnitParseError
        If ``unit`` is a malformed expression string.
    ValueError
        If ``value`` is NaN.

    Examples
    --------
    Basic arithmetic and conversion:

    >>> import quantia as qu
    >>> d = qu.Q(100.0, 'm')
    >>> t = qu.Q(10.0, 's')
    >>> v = d / t
    >>> v.to('km/h')
    UnitFloat(36.0, 'km/h')

    Temperature conversion (affine):

    >>> qu.Q(100.0, '°C').to('K')
    UnitFloat(373.15, 'K')

    Gauge to absolute pressure:

    >>> qu.Q(0.0, 'psig').to('psia')
    UnitFloat(14.695..., 'psia')
    """

    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit: Union[str, "CompoundUnit"]) -> None:
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
        """Convert to the SI base unit representation.

        For affine units (temperature, gauge pressure) applies the full
        affine transformation including offset. For multiplicative units
        applies the scale factor only.

        Returns
        -------
        UnitFloat
            Value expressed in SI base units (e.g. ``K``, ``Pa``,
            ``m/s``, ``m^3``).

        Examples
        --------
        >>> qu.Q(1.0, 'km').to_si()
        UnitFloat(1000.0, 'm')

        >>> qu.Q(100.0, '°C').to_si()
        UnitFloat(373.15, 'K')

        >>> qu.Q(0.0, 'psig').to_si()
        UnitFloat(101325.0, 'Pa')
        """
        affine = self._is_single_affine(self._unit)
        if affine:
            return UnitFloat(affine.to_si_value(self._value), affine.si_unit)
        return UnitFloat(self._value * self._unit.si_factor(),
                        self._unit.to_si_compound())

    def si_value(self) -> float:
        """Return the numeric SI value as a plain float.

        Equivalent to ``self.to_si().value``. Use this when you need a
        dimensionless number for further computation or comparison.

        Returns
        -------
        float
            Numeric value in SI base units.

        Examples
        --------
        >>> qu.Q(1.0, 'km').si_value()
        1000.0

        >>> qu.Q(1.0, 'bbl').si_value()
        0.158987294928

        >>> qu.Q(0.0, 'psig').si_value()
        101325.0
        """
        return self.to_si()._value
    
    def to(self, target: Union[str, "CompoundUnit"]) -> "UnitFloat":
        """Convert to a different unit of the same physical quantity.

        Handles multiplicative units (``m`` → ``km``) and affine units
        (``°C`` → ``K``, ``psig`` → ``psia``, ``psig`` → ``Pa``).

        Parameters
        ----------
        target : str or CompoundUnit
            Target unit. Must be dimensionally compatible with the
            current unit.

        Returns
        -------
        UnitFloat
            New instance with the value expressed in ``target``.

        Raises
        ------
        IncompatibleUnitsError
            If ``target`` has different physical dimensions
            (e.g. pressure → length).
        DimensionError
            If mixing affine and non-affine units of incompatible
            quantities (e.g. ``psig`` → ``m``).

        Examples
        --------
        >>> qu.Q(1.0, 'km').to('m')
        UnitFloat(1000.0, 'm')

        >>> qu.Q(100.0, '°C').to('°F')
        UnitFloat(212.0, '°F')

        >>> qu.Q(100.0, 'psig').to('bara')
        UnitFloat(7.895..., 'bara')

        >>> qu.Q(1.0, 'bbl').to('L')
        UnitFloat(158.987..., 'L')
        """
        tcu = _make_unit(target)
        src_affine = self._is_single_affine(self._unit)
        tgt_affine = self._is_single_affine(tcu)

        if src_affine and tgt_affine:
            # Both affine: °C→K, psig→psia, barg→bara, etc.
            si_val = src_affine.to_si_value(self._value)
            return UnitFloat(tgt_affine.from_si_value(si_val), target)

        if src_affine:
            # Affine → plain: psia→Pa, psig→kPa, °C→[invalid if Pa]
            # Go through SI absolute value, then scale to target.
            # Dimensional compatibility is checked via si_unit of the affine unit,
            # so °C→Pa raises IncompatibleUnitsError because K ≠ Pa.
            si_val    = src_affine.to_si_value(self._value)
            si_unit_cu = _make_unit(src_affine.si_unit)
            if not si_unit_cu.is_compatible(tcu):
                raise IncompatibleUnitsError(self._unit, tcu)
            return UnitFloat(si_val / tcu.si_factor(), tcu)

        if tgt_affine:
            # Plain → affine: Pa→psig, Pa→°C[invalid if m], etc.
            si_unit_cu = _make_unit(tgt_affine.si_unit)
            if not self._unit.is_compatible(si_unit_cu):
                raise IncompatibleUnitsError(self._unit, tcu)
            si_val = self._value * self._unit.si_factor()
            return UnitFloat(tgt_affine.from_si_value(si_val), target)

        # Both plain: standard multiplicative path
        if not self._unit.is_compatible(tcu):
            raise IncompatibleUnitsError(self._unit, tcu)
        return UnitFloat(
            self._value * self._unit.si_factor() / tcu.si_factor(), tcu)

    # ── Arithmetic ───────────────────────────────────────────────────────────

    def _coerce(self, o: "UnitFloat") -> float:
        if not self._unit.is_compatible(o._unit):
            raise IncompatibleUnitsError(self._unit, o._unit)
        return o._value * o._unit.si_factor() / self._unit.si_factor()
    def __add__(self, o: Union["UnitFloat", int, float]) -> "UnitFloat":
        if isinstance(o, UnitFloat):  return UnitFloat(self._value + self._coerce(o), self._unit)
        if isinstance(o, (int,float)):return UnitFloat(self._value + o,               self._unit)
        return NotImplemented
    def __radd__(self, o: Union["UnitFloat", int, float]) -> "UnitFloat":
        return self.__add__(o)
    def __sub__(self, o: Union["UnitFloat", int, float]) -> "UnitFloat":
        if isinstance(o, UnitFloat):  return UnitFloat(self._value - self._coerce(o), self._unit)
        if isinstance(o, (int,float)):return UnitFloat(self._value - o,               self._unit)
        return NotImplemented
    def __rsub__(self, o: Union[int, float]) -> "UnitFloat":
        if isinstance(o, (int,float)): return UnitFloat(o - self._value, self._unit)
        return NotImplemented
    def __mul__(self, o: Union["UnitFloat", int, float]) -> "UnitFloat":
        if isinstance(o, UnitFloat):
            cu = self._unit * o._unit
            return UnitFloat(self._value * o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __rmul__(self, o: Union[int, float]) -> "UnitFloat":
        if isinstance(o, (int,float)): return UnitFloat(self._value * o, self._unit)
        return NotImplemented
    def __truediv__(self, o: Union["UnitFloat", int, float]) -> "UnitFloat":
        if isinstance(o, UnitFloat):
            cu = self._unit / o._unit
            return UnitFloat(self._value / o._value,
                             CompoundUnit.dimensionless() if cu.is_dimensionless() else cu)
        if isinstance(o, (int,float)): return UnitFloat(self._value / o, self._unit)
        return NotImplemented
    def __rtruediv__(self, o: Union[int, float]) -> "UnitFloat":
        if isinstance(o, (int,float)): return UnitFloat(o / self._value, self._unit.invert())
        return NotImplemented
    def __pow__(self, e: Union[int, float]) -> "UnitFloat":
        return UnitFloat(self._value**e, self._unit**e)
    def __neg__(self) -> "UnitFloat":
        return UnitFloat(-self._value, self._unit)
    def __abs__(self) -> "UnitFloat":
        return UnitFloat(abs(self._value), self._unit)
    def __float__(self) -> float:
        return self._value
    def __int__(self) -> int:
        return int(self._value)
    def __round__(self, n: int | None = None) -> "UnitFloat":
        return UnitFloat(round(self._value, n), self._unit)
    def __floor__(self) -> "UnitFloat":
        return UnitFloat(math.floor(self._value), self._unit)
    def __ceil__(self) -> "UnitFloat":
        return UnitFloat(math.ceil(self._value),  self._unit)
    def _cmp(self, o):
        if isinstance(o, UnitFloat): return self.si_value(), o.si_value()
        if isinstance(o, (int,float)): return self.si_value(), float(o)
        return NotImplemented
    def __eq__(self, o: object) -> bool:
        r = self._cmp(o);
        return r is not NotImplemented and math.isclose(r[0], r[1])
    def __lt__(self, o: Union["UnitFloat", int, float]) -> bool:
        r=self._cmp(o)
        return r[0]<r[1]
    def __le__(self, o: Union["UnitFloat", int, float]) -> bool:
        r=self._cmp(o)
        return r[0]<=r[1]
    def __gt__(self, o: Union["UnitFloat", int, float]) -> bool:
        r=self._cmp(o)
        return r[0]>r[1]
    def __ge__(self, o: Union["UnitFloat", int, float]) -> bool:
        r=self._cmp(o)
        return r[0]>=r[1]

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