"""
quantia/_io.py
==============
Top-level serialization helpers.

    quantia.from_dict(d)        → dispatch on "type" field
    quantia.save(obj, path)     → write JSON file
    quantia.load(path)          → read JSON file → object
"""
from __future__ import annotations
import json
from pathlib import Path


def from_dict(d: dict):
    """
    Reconstruct any quantia object from its dict representation.

    Parameters
    ----------
    d : dict   A dict produced by obj.to_dict().

    Returns
    -------
    UnitFloat | UnitArray | ProbUnitFloat | ProbUnitArray
    """
    t = d.get("type")
    if t == "UnitFloat":
        from quantia._scalar import UnitFloat
        return UnitFloat.from_dict(d)
    if t == "UnitArray":
        from quantia._array import UnitArray
        return UnitArray.from_dict(d)
    if t == "ProbUnitFloat":
        from quantia.prob._scalar import ProbUnitFloat
        return ProbUnitFloat.from_dict(d)
    if t == "ProbUnitArray":
        from quantia.prob._array import ProbUnitArray
        return ProbUnitArray.from_dict(d)
    raise ValueError(
        f"Unknown quantia type {t!r}. "
        "Expected 'UnitFloat', 'UnitArray', 'ProbUnitFloat', or 'ProbUnitArray'."
    )


def save(obj, path) -> None:
    """Serialize a quantia object to a JSON file."""
    Path(path).write_text(json.dumps(obj.to_dict(), indent=2), encoding="utf-8")


def load(path):
    """Load a quantia object from a JSON file."""
    return from_dict(json.loads(Path(path).read_text(encoding="utf-8")))