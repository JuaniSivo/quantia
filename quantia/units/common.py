from quantia._registry import Unit, AffineUnit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Volume ────────────────────────────────────────────────────────────────────
_reg("L",  "litre",      "volume", "m3", 1e-3)
_reg("mL", "millilitre", "volume", "m3", 1e-6)
_reg("cL", "centilitre", "volume", "m3", 1e-5)
# NIST Table 8: 1 L = 1 dm3 = 10^-3 m3 (exact)

# ── Pressure — canonical home for non-gauge, non-SI pressure units ────────────
# "atm" and "bar" are absolute. Gauge variants (psig, barg) are in step-1-3.
_reg("atm",  "standard atmosphere",      "pressure", "Pa", 101_325.0)
# NIST: 1.013 25 E+05 Pa (exact by definition)
_reg("bar",  "bar",                      "pressure", "Pa", 100_000.0)
# NIST: 1.0 E+05 Pa (exact)
_reg("mmHg", "millimetre of mercury (conventional)", "pressure", "Pa", 133.322387415)
# NIST: 1.333 224 E+02 Pa

# ── Gauge / Absolute pressure ─────────────────────────────────────────────────
# bara: absolute bar — offset=0, numerically identical to "bar".
# barg: gauge bar  — P_abs(Pa) = P_g(bar) * 100000 + 101325
# "bar" alone warns and redirects to bara via _AMBIGUOUS_UNITS in _registry.py

from quantia._registry import AffineUnit
register("bara", AffineUnit(
    "bar (absolute)", "pressure", "Pa",
    scale=100_000.0, offset=0.0, symbol="bara"))
# NIST: 1 bar = 1.0 E+05 Pa (exact)

register("barg", AffineUnit(
    "bar (gauge)", "pressure", "Pa",
    scale=100_000.0, offset=101_325.0, symbol="barg"))
# Gauge: P_abs = P_g * 100000 + 101325  (standard atmosphere offset)