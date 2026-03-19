"""
Non-linear petroleum conversion functions.

These conversions cannot be expressed as simple unit scale factors
and are therefore not handled by the unit registry. They accept
plain floats, UnitFloat (°API or dimensionless), and ProbUnitFloat.

Functions
---------
api_to_sg : API gravity → specific gravity (relative to water at 60°F)
sg_to_api : specific gravity → API gravity

References
----------
API Manual of Petroleum Measurement Standards (MPMS) Chapter 11
Definition: SG = 141.5 / (°API + 131.5)
"""
from __future__ import annotations


def api_to_sg(api) -> float:
    """Convert API gravity to specific gravity relative to water at 60°F.

    Formula:  SG = 141.5 / (°API + 131.5)

    Defined by API MPMS Ch.11. Specific gravity is relative to water
    at 60°F (15.56°C), where water = 10 °API = SG 1.0 by definition.

    Parameters
    ----------
    api : float | UnitFloat | ProbUnitFloat
        API gravity value. If UnitFloat, must have quantity 'api_gravity'
        or be dimensionless. If ProbUnitFloat, returns ProbUnitFloat.

    Returns
    -------
    float or ProbUnitFloat
        Specific gravity (dimensionless). Returns same type as input
        when input is ProbUnitFloat.

    Examples
    --------
    >>> api_to_sg(10.0)   # water by definition
    1.0
    >>> api_to_sg(35.0)   # medium crude
    0.8498...
    >>> api_to_sg(60.0)   # light condensate
    0.7389...

    Raises
    ------
    ValueError : If API gravity <= -131.5 (division by zero / negative SG)
    """
    from quantia.prob._scalar import ProbUnitFloat as _PUF
    import array as _array

    if isinstance(api, _PUF):
        samples = _array.array('d', (
            _api_to_sg_scalar(v) for v in api._samples))
        return _PUF._from_raw(samples, "1")

    v = _extract_value(api)
    return _api_to_sg_scalar(v)


def sg_to_api(sg) -> float:
    """Convert specific gravity to API gravity.

    Formula:  °API = 141.5 / SG − 131.5

    Parameters
    ----------
    sg : float | UnitFloat | ProbUnitFloat
        Specific gravity (dimensionless, relative to water at 60°F).
        Must be > 0.

    Returns
    -------
    float or ProbUnitFloat
        API gravity in degrees. Returns same type as input
        when input is ProbUnitFloat.

    Examples
    --------
    >>> sg_to_api(1.0)    # water
    10.0
    >>> sg_to_api(0.85)   # medium crude
    35.03...

    Raises
    ------
    ValueError : If SG <= 0
    """
    from quantia.prob._scalar import ProbUnitFloat as _PUF
    import array as _array

    if isinstance(api := sg, _PUF):   # reuse variable name for clarity
        samples = _array.array('d', (
            _sg_to_api_scalar(v) for v in sg._samples))
        return _PUF._from_raw(samples, "1")

    v = _extract_value(sg)
    return _sg_to_api_scalar(v)


# ── Internal scalar implementations ──────────────────────────────────────────

def _api_to_sg_scalar(api: float) -> float:
    if api <= -131.5:
        raise ValueError(
            f"API gravity must be > -131.5, got {api}. "
            "Values ≤ -131.5 produce zero or negative specific gravity.")
    return 141.5 / (api + 131.5)


def _sg_to_api_scalar(sg: float) -> float:
    if sg <= 0:
        raise ValueError(
            f"Specific gravity must be > 0, got {sg}.")
    return 141.5 / sg - 131.5


def _extract_value(x) -> float:
    """Extract float from UnitFloat or return float directly."""
    from quantia._scalar import UnitFloat
    if isinstance(x, UnitFloat):
        return float(x.value)
    return float(x)