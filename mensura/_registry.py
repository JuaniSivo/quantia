from mensura._exceptions import UnknownUnitError


class Unit:
    """
    A named unit of measurement.

    Attributes
    ----------
    name     : human-readable name, e.g. "kilometre"
    quantity : physical quantity, e.g. "length"
    si_unit  : symbol of the SI base unit, e.g. "m"
    to_si    : multiply by this to convert a value to SI
    symbol   : short symbol used in expressions, e.g. "km"
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


_REGISTRY: dict[str, Unit] = {}


def register(symbol: str, unit: Unit) -> None:
    """Add a unit to the global registry."""
    _REGISTRY[symbol] = unit


def get_unit(symbol: str) -> Unit:
    """Retrieve a unit by symbol, raising UnknownUnitError if missing."""
    try:
        return _REGISTRY[symbol]
    except KeyError:
        raise UnknownUnitError(symbol)


def registered_symbols() -> list[str]:
    """Return a sorted list of all registered unit symbols."""
    return sorted(_REGISTRY)