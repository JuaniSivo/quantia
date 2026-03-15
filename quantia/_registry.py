from __future__ import annotations
import warnings
from quantia._exceptions import UnknownUnitError


class Unit:
    """
    A named unit of measurement.

    Attributes
    ----------
    name     : human-readable name, e.g. "kilometre"
    quantity : physical quantity,   e.g. "length"
    si_unit  : SI base unit symbol, e.g. "m"
    to_si    : multiply by this to reach SI
    symbol   : short symbol,        e.g. "km"
    """
    __slots__ = ("name", "quantity", "si_unit", "to_si", "symbol")

    def __init__(self, name: str, quantity: str, si_unit: str,
                 to_si: float, symbol: str = ""):
        self.name     = name
        self.quantity = quantity
        self.si_unit  = si_unit
        self.to_si    = float(to_si)
        self.symbol   = symbol or name

    def __repr__(self):
        return f"Unit('{self.symbol}', quantity='{self.quantity}')"


class AffineUnit(Unit):
    """
    A unit with a scale AND an offset relative to its SI base.

    Conversion to SI:   si_value = value * scale + offset
    Conversion from SI: value    = (si_value - offset) / scale

    Used for temperature (°C, °F) and gauge pressure (psig, barg).
    K is also AffineUnit for uniformity (scale=1, offset=0).
    """
    __slots__ = ("name", "quantity", "si_unit", "to_si", "symbol", "offset")

    def __init__(self, name: str, quantity: str, si_unit: str,
                 scale: float, offset: float, symbol: str = ""):
        super().__init__(name, quantity, si_unit, scale, symbol)
        self.offset = float(offset)

    @property
    def scale(self) -> float:
        return self.to_si

    def to_kelvin(self, value: float) -> float:
        return value * self.scale + self.offset

    def from_kelvin(self, kelvin: float) -> float:
        return (kelvin - self.offset) / self.scale

    def __repr__(self):
        return (f"AffineUnit('{self.symbol}', scale={self.scale}, "
                f"offset={self.offset})")


_REGISTRY: dict[str, Unit] = {}

# Units that are ambiguous — get_unit() warns and redirects to the canonical form.
# Format: ambiguous_symbol → (canonical_symbol, warning_message)
#
# Add new entries here as more ambiguous units are discovered.
# Step 1.3 will add "psi" and "bar" once psia/psig/bara/barg are registered.
_AMBIGUOUS_UNITS: dict[str, tuple[str, str]] = {
    "BTU":  ("BTU_IT",
             "Ambiguous: 'BTU' treated as 'BTU_IT' (International Table). "
             "Use 'BTU_IT' or 'BTU_th' explicitly."),
    "cal":  ("cal_th",
             "Ambiguous: 'cal' treated as 'cal_th' (thermochemical, 4.184 J). "
             "Use 'cal_th' or 'cal_IT' explicitly."),
    "kcal": ("kcal_th",
             "Ambiguous: 'kcal' treated as 'kcal_th' (thermochemical). "
             "Use 'kcal_th' or 'kcal_IT' explicitly."),
}


def register(symbol: str, unit: Unit, overwrite: bool = False) -> None:
    """Add a unit to the global registry.

    Parameters
    ----------
    symbol    : The unit symbol, e.g. 'km', 'psia'.
    unit      : A Unit or AffineUnit instance.
    overwrite : If False (default), raises ValueError when symbol already
                exists. Pass True only when intentionally replacing a unit.

    Raises
    ------
    ValueError : If symbol is already registered and overwrite=False.
    """
    if symbol in _REGISTRY and not overwrite:
        raise ValueError(
            f"Unit '{symbol}' is already registered. "
            "Use overwrite=True to replace it intentionally."
        )
    _REGISTRY[symbol] = unit


def get_unit(symbol: str) -> Unit:
    """Retrieve a unit by symbol.

    If the symbol is in _AMBIGUOUS_UNITS, emits a UserWarning and
    redirects to the canonical form before lookup.

    Parameters
    ----------
    symbol : The unit symbol to look up.

    Returns
    -------
    Unit or AffineUnit

    Raises
    ------
    UnknownUnitError : If the symbol is not found in the registry.
    """
    if symbol in _AMBIGUOUS_UNITS:
        canonical, msg = _AMBIGUOUS_UNITS[symbol]
        warnings.warn(msg, UserWarning, stacklevel=3)
        symbol = canonical
    try:
        return _REGISTRY[symbol]
    except KeyError:
        raise UnknownUnitError(symbol)


def registered_symbols() -> list[str]:
    """Return a sorted list of all registered unit symbols."""
    return sorted(_REGISTRY)