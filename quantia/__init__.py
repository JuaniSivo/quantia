import quantia.units  # noqa: F401  — populates registry + aliases

from quantia._scalar      import UnitFloat
from quantia._array       import UnitArray
from quantia.prob._scalar import ProbUnitFloat
from quantia.prob._array  import ProbUnitArray
from quantia.prob._copula import CorrelatedSource
from quantia._exceptions  import (
    UnknownUnitError, IncompatibleUnitsError, DimensionError, UnitParseError
)
from quantia._compound    import parse_unit, register_alias, register_tagged
from quantia._registry    import register, get_unit, registered_symbols
from quantia._io          import save, load, from_dict
from quantia._config      import config
from quantia.petroleum_conversions import api_to_sg, sg_to_api


def Q(value: float, unit) -> UnitFloat:
    """Exact scalar: Q(9.81, 'm/s^2')"""
    return UnitFloat(value, unit)

def QA(values, unit) -> UnitArray:
    """Exact array:  QA([1.0, 2.0, 3.0], 'km')"""
    return UnitArray(values, unit)

def QP(low: float, high: float, unit, n: int = None) -> ProbUnitFloat:
    """Probabilistic scalar, uniform: QP(0.92, 0.96, '1')"""
    return ProbUnitFloat.uniform(low, high, unit, n)

def QPA(elements) -> ProbUnitArray:
    """Probabilistic array: QPA([p1, p2, p3])"""
    return ProbUnitArray(elements)

__all__ = [
    "Q", "QA", "QP", "QPA",
    "UnitFloat", "UnitArray", "ProbUnitFloat", "ProbUnitArray",
    "CorrelatedSource",
    "parse_unit", "register_alias", "register_tagged",
    "register", "get_unit", "registered_symbols",
    "UnknownUnitError", "IncompatibleUnitsError", "DimensionError", "UnitParseError",
    "save", "load", "from_dict",
    "config",
    "api_to_sg", "sg_to_api",
]