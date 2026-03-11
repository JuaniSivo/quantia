# 1. Load all unit domains (populates _REGISTRY and _ALIASES)
import mensura.units  # noqa: F401

# 2. Public types
from mensura._scalar       import UnitFloat
from mensura._array        import UnitArray
from mensura.prob._scalar  import ProbUnitFloat
from mensura.prob._array   import ProbUnitArray
from mensura.prob._copula  import CorrelatedSource
from mensura._exceptions   import (
    UnknownUnitError, IncompatibleUnitsError, DimensionError
)
from mensura._compound     import parse_unit, register_alias
from mensura._registry     import register, get_unit, registered_symbols

# 3. Convenience factories
def Q(value: float, unit) -> UnitFloat:
    """Exact scalar: Q(9.81, 'm/s^2')"""
    return UnitFloat(value, unit)

def QA(values, unit) -> UnitArray:
    """Exact array: QA([1, 2, 3], 'km')"""
    return UnitArray(values, unit)

def QP(low: float, high: float, unit, n: int = 1000) -> ProbUnitFloat:
    """Probabilistic scalar, uniform: QP(0.92, 0.96, '1')"""
    return ProbUnitFloat.uniform(low, high, unit, n)

def QPA(elements) -> ProbUnitArray:
    """Probabilistic array: QPA([p1, p2, p3])"""
    return ProbUnitArray(elements)

__all__ = [
    "Q", "QA", "QP", "QPA",
    "UnitFloat", "UnitArray", "ProbUnitFloat", "ProbUnitArray",
    "CorrelatedSource",
    "parse_unit", "register_alias", "register", "get_unit", "registered_symbols",
    "UnknownUnitError", "IncompatibleUnitsError", "DimensionError",
]