from mensura._exceptions import UnknownUnitError


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

    Used for temperature units (°C, °F) where a simple multiplicative
    factor is not enough.  K is also represented as AffineUnit for
    uniformity (scale=1, offset=0).
    """
    __slots__ = ("name", "quantity", "si_unit", "to_si", "symbol", "offset")

    def __init__(self, name: str, quantity: str, si_unit: str,
                 scale: float, offset: float, symbol: str = ""):
        super().__init__(name, quantity, si_unit, scale, symbol)
        self.offset = float(offset)   # to_si is reused as scale

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


def register(symbol: str, unit: Unit) -> None:
    """Add a unit to the global registry."""
    _REGISTRY[symbol] = unit


def get_unit(symbol: str) -> Unit:
    """Retrieve a unit by symbol; raises UnknownUnitError if missing."""
    try:
        return _REGISTRY[symbol]
    except KeyError:
        raise UnknownUnitError(symbol)


def registered_symbols() -> list[str]:
    return sorted(_REGISTRY)