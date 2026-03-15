import math

from quantia._registry import Unit, AffineUnit, register, _REGISTRY


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Volume ────────────────────────────────────────────────────────────────────
_reg("L",  "litre",      "volume", "m^3", 1e-3)
_reg("mL", "millilitre", "volume", "m^3", 1e-6)
_reg("cL", "centilitre", "volume", "m^3", 1e-5)
# NIST Table 8: 1 L = 1 dm3 = 10^-3 m3 (exact)

# ── Pressure — canonical home for non-gauge, non-SI pressure units ────────────
# "atm" and "bar" are absolute. Gauge variants (psig, barg) are in step-1-3.
_reg("atm",  "standard atmosphere",                   "pressure", "Pa", 101_325.0)
# NIST: 1.013 25 E+05 Pa (exact by definition)
_reg("mmHg", "millimetre of mercury (conventional)",  "pressure", "Pa", 133.322387415)
# NIST: 1.333 224 E+02 Pa

# ── Gauge / Absolute bar pressure ────────────────────────────────────────────
# bara: absolute bar — offset=0, numerically identical to plain "bar".
# barg: gauge bar  — P_abs(Pa) = P_g(bar) * 100000 + 101325
# "bar" alone warns and redirects to bara via _AMBIGUOUS_UNITS in _registry.py
register("bara", AffineUnit(
    "bar (absolute)", "pressure", "Pa",
    scale=100_000.0, offset=0.0, symbol="bara"))
# NIST: 1 bar = 1.0 E+05 Pa (exact)

register("barg", AffineUnit(
    "bar (gauge)", "pressure", "Pa",
    scale=100_000.0, offset=101_325.0, symbol="barg"))
# Gauge: P_abs = P_g * 100000 + 101325  (standard atmosphere offset)

# ── NIST Table 8: Non-SI units accepted for use with the SI ──────────────────

# Time
_reg("d",    "day",             "time", "s", 86_400.0)
# NIST Table 8: 1 d = 24 h = 86 400 s (exact). Canonical symbol.
_REGISTRY["day"] = _REGISTRY["d"]    # alias — "day" was the original symbol

_reg("week", "week",             "time",  "s",   604_800.0)
# 7 × 86 400 = 604 800 s

_reg("yr",   "year (365 days)",  "time",  "s",   31_536_000.0)
# NIST: 3.1536 E+07 s  (Julian calendar year = 365 days)

# Angle
# "deg" is already registered in si.py — add "°" as the NIST canonical alias.
# Direction: _REGISTRY["°"] = existing "deg" entry.
_REGISTRY["°"] = _REGISTRY["deg"]    # alias — deg already in si.py

_reg("′",    "arcminute",        "angle", "rad", math.pi / 10_800)
# NIST: 1′ = (1/60)° = π/10 800 rad = 2.908 882 E-04 rad

_reg("″",    "arcsecond",        "angle", "rad", math.pi / 648_000)
# NIST: 1″ = (1/60)′ = π/648 000 rad = 4.848 137 E-06 rad

_reg("arcmin", "arcminute",      "angle", "rad", math.pi / 10_800)
# ASCII alias for ′
_reg("arcsec", "arcsecond",      "angle", "rad", math.pi / 648_000)
# ASCII alias for ″

# Area (NIST Table 8)
_reg("ha",   "hectare",          "area",  "m^2",  1e4)
# NIST Table 8: 1 ha = 1 hm² = 10⁴ m² (exact)

# Mass (NIST Table 8)
_reg("Da",   "dalton",           "mass",  "kg",  1.660_539_040e-27)
# NIST Table 8: 1 Da = 1.660 539 040 E-27 kg

# Logarithmic ratio
_reg("Np",   "neper",            "log_ratio", "1", 1.0)
# NIST Table 8: dimensionless, Np = ln ratio
_reg("dB",   "decibel",          "log_ratio", "1", 0.1151292546)
# 1 dB = (1/20) × ln(10) Np ≈ 0.1151 Np (field quantity convention)