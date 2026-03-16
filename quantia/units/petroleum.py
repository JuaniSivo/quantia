# quantia/units/petroleum.py
"""
Petroleum engineering units.

Sources
-------
API Manual of Petroleum Measurement Standards (MPMS)
NIST SP811 (base conversion factors)

Notes
-----
- m3 is registered in si.py as an atomic alias for m^3.
  Do not re-register it here.
- psi_g is a deprecated alias — redirects to psig with a warning.
  psig is the correct symbol (registered in imperial.py, Phase 1).
- Opaque named ratio units (Sm3/Sm3, scf/STB, Mscf/STB) have been
  removed. Use register_tagged() units for GOR and FVF calculations —
  the conversion math is identical and the physics is preserved.
"""
from quantia._registry import Unit, register
from quantia._compound import register_tagged


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Volume ────────────────────────────────────────────────────────────────────
_reg("bbl",   "barrel",           "volume", "m^3", 0.158987294928)
# API MPMS Ch.11: 1 bbl = 42 US gal = 0.158 987 294 928 m³ (exact)

_reg("Mbbl",  "thousand barrels", "volume", "m^3", 158.987294928)
# 1 Mbbl = 1000 bbl (exact)

_reg("MMbbl", "million barrels",  "volume", "m^3", 158_987.294928)
# 1 MMbbl = 1e6 bbl (exact)

# Gas volume at standard conditions
_reg("scf",   "standard cubic foot",     "gas_volume", "m^3", 0.0283168466)
# 1 scf = 1 ft³ at standard conditions = 0.028 316 846 6 m³

_reg("Mscf",  "thousand standard cu ft", "gas_volume", "m^3", 28.3168466)
# 1 Mscf = 1000 scf (exact)

_reg("MMscf", "million standard cu ft",  "gas_volume", "m^3", 28_316.8466)
# 1 MMscf = 1e6 scf (exact)

# ── Pressure ──────────────────────────────────────────────────────────────────
# psia, psig, bara, barg — registered in imperial.py / common.py (Phase 1)
#
# psi_g: deprecated alias → warns and redirects to psig
# Added to _AMBIGUOUS_UNITS so get_unit() handles the redirect automatically.
from quantia._registry import _AMBIGUOUS_UNITS
_AMBIGUOUS_UNITS["psi_g"] = (
    "psig",
    "Deprecated: 'psi_g' has been replaced by 'psig'. "
    "Please update your code to use 'psig' explicitly."
)

# kg/cm² — common field pressure unit in Latin America and legacy literature
# NIST: 1 kgf/cm² = 9.806 65 E+04 Pa (exact — standard gravity × 10⁴)
_reg("kg/cm2",  "kilogram-force per square centimetre", "pressure", "Pa", 9.806_65e4)
_reg("kgf/cm2", "kilogram-force per square centimetre", "pressure", "Pa", 9.806_65e4)

# ── Flow rate ─────────────────────────────────────────────────────────────────
_reg("bbl/day",   "barrels per day",          "flow_rate", "m^3/s",
     0.158987294928 / 86_400)
_reg("Mbbl/day",  "thousand barrels per day", "flow_rate", "m^3/s",
     158.987294928  / 86_400)
_reg("m3/day",    "cubic metres per day",     "flow_rate", "m^3/s",
     1.0            / 86_400)
_reg("Mscf/day",  "thousand scf per day",     "flow_rate", "m^3/s",
     28.3168466     / 86_400)

# ── API gravity ───────────────────────────────────────────────────────────────
register("°API", Unit("API gravity", "api_gravity", "1", 1.0, "°API"))
# Non-linear unit — direct conversion to/from SG via api_to_sg() / sg_to_api()
# in quantia/petroleum_conversions.py (added in Step 2.4)

# ── Semantic tagged units ─────────────────────────────────────────────────────
# These share SI dimensions with their base units but will NOT cancel when
# divided by another tagged unit of the same quantity.
# Use these to build GOR (gas-oil ratio) and FVF (formation volume factor)
# quantities that preserve petroleum meaning through calculations.

# Reservoir and stock-tank cubic metres
register_tagged("Sm3_res", "m3",  "reservoir")
register_tagged("Sm3_st",  "m3",  "stock_tank")

# Reservoir and stock-tank standard cubic feet
# Base is "scf" (not "m3") so SI factors are correct for scf/STB GOR
register_tagged("scf_res", "scf", "reservoir")
register_tagged("scf_st",  "scf", "stock_tank")