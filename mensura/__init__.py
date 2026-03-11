import mensura.units  # noqa: F401  — populates registry + aliases

from mensura._scalar      import UnitFloat
from mensura._array       import UnitArray
from mensura.prob._scalar import ProbUnitFloat
from mensura.prob._array  import ProbUnitArray
from mensura.prob._copula import CorrelatedSource
from mensura._exceptions  import (
    UnknownUnitError, IncompatibleUnitsError, DimensionError, UnitParseError
)
from mensura._compound    import parse_unit, register_alias, register_tagged
from mensura._registry    import register, get_unit, registered_symbols
from mensura._io import save, load, from_dict   # noqa: F401

def Q(value: float, unit) -> UnitFloat:
    """Exact scalar: Q(9.81, 'm/s^2')"""
    return UnitFloat(value, unit)

def QA(values, unit) -> UnitArray:
    """Exact array:  QA([1.0, 2.0, 3.0], 'km')"""
    return UnitArray(values, unit)

def QP(low: float, high: float, unit, n: int = 1000) -> ProbUnitFloat:
    """Probabilistic scalar, uniform: QP(0.92, 0.96, '1')"""
    return ProbUnitFloat.uniform(low, high, unit, n)

def QPA(elements) -> ProbUnitArray:
    """Probabilistic array: QPA([p1, p2, p3])"""
    return ProbUnitArray(elements)

__all__ = [
    # factories
    "Q", "QA", "QP", "QPA",
    # types
    "UnitFloat", "UnitArray", "ProbUnitFloat", "ProbUnitArray",
    "CorrelatedSource",
    # unit utilities
    "parse_unit", "register_alias", "register_tagged",
    "register", "get_unit", "registered_symbols",
    # exceptions
    "UnknownUnitError", "IncompatibleUnitsError", "DimensionError", "UnitParseError",
    # io
    "save", "load", "from_dict"
]