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
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from quantia._scalar import UnitFloat
    from quantia.prob._scalar import ProbUnitFloat

def api_to_sg(
    api: Union[float, "UnitFloat", "ProbUnitFloat"]
) -> Union[float, "ProbUnitFloat"]:
    """Convert API gravity to specific gravity relative to water at 60°F.

    Parameters
    ----------
    api : float, UnitFloat, or ProbUnitFloat
        API gravity value. When a :class:`~quantia._scalar.UnitFloat`
        is passed, the ``.value`` attribute is extracted. When a
        :class:`~quantia.prob._scalar.ProbUnitFloat` is passed, the
        conversion is applied sample-wise and a new ``ProbUnitFloat``
        is returned.

    Returns
    -------
    float or ProbUnitFloat
        Specific gravity (dimensionless). Returns the same type as
        the input when input is ``ProbUnitFloat``.

    Raises
    ------
    ValueError
        If ``api <= −131.5`` (produces zero or negative specific gravity).

    See Also
    --------
    sg_to_api : Inverse conversion.

    Examples
    --------
    >>> from quantia.petroleum_conversions import api_to_sg
    >>> api_to_sg(10.0)    # water by definition
    1.0
    >>> api_to_sg(35.0)    # medium crude
    0.8498...
    >>> api_to_sg(60.0)    # light condensate
    0.7389...

    Uncertain API gravity:

    >>> with qu.config(seed=42, n_samples=2000):
    ...     api = qu.ProbUnitFloat.normal(35.0, 3.0, '1')
    >>> sg = api_to_sg(api)   # ProbUnitFloat
    >>> sg.mean().value
    0.849...
    """

    from quantia.prob._scalar import ProbUnitFloat as _PUF
    import array as _array

    if isinstance(api, _PUF):
        samples = _array.array('d', (
            _api_to_sg_scalar(v) for v in api._samples))
        return _PUF._from_raw(samples, "1")

    v = _extract_value(api)
    return _api_to_sg_scalar(v)


def sg_to_api(
    sg: Union[float, "UnitFloat", "ProbUnitFloat"]
) -> Union[float, "ProbUnitFloat"]:
    """Convert specific gravity to API gravity.

    Parameters
    ----------
    sg : float, UnitFloat, or ProbUnitFloat
        Specific gravity relative to water at 60°F. Must be > 0.

    Returns
    -------
    float or ProbUnitFloat
        API gravity in degrees.

    Raises
    ------
    ValueError
        If ``sg <= 0``.

    See Also
    --------
    api_to_sg : Inverse conversion.

    Examples
    --------
    >>> from quantia.petroleum_conversions import sg_to_api
    >>> sg_to_api(1.0)     # water
    10.0
    >>> sg_to_api(0.85)    # medium crude
    35.03...
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