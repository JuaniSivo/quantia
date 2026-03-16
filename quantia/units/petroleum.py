"""
Petroleum engineering units.

Sources
-------
API Manual of Petroleum Measurement Standards (MPMS)
NIST SP811 (base conversion factors)
SPE nomenclature conventions

Notes
-----
- m3 is registered in si.py as an atomic alias for m^3.
- psi_g is a deprecated alias — redirects to psig with a warning.
- Opaque named ratio units (Sm3/Sm3, scf/STB, Mscf/STB) removed.
  Use register_tagged() units for GOR and FVF calculations.
"""
from quantia._registry import Unit, register, _AMBIGUOUS_UNITS
from quantia._compound import register_tagged


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Volume ────────────────────────────────────────────────────────────────────
_reg("bbl",    "barrel",           "volume", "m^3", 0.158987294928)
# API MPMS Ch.11: 1 bbl = 42 US gal = 0.158 987 294 928 m³ (exact)

_reg("Mbbl",   "thousand barrels", "volume", "m^3", 158.987294928)
_reg("MMbbl",  "million barrels",  "volume", "m^3", 158_987.294928)

# Gas volume at standard conditions
_reg("scf",    "standard cubic foot",        "gas_volume", "m^3", 0.0283168466)
# 1 scf = 1 ft³ at standard conditions
_reg("Mscf",   "thousand standard cu ft",    "gas_volume", "m^3", 28.3168466)
_reg("MMscf",  "million standard cu ft",     "gas_volume", "m^3", 28_316.8466)
_reg("Bscf",   "billion standard cu ft",     "gas_volume", "m^3", 28_316_846.6)
# 1 Bscf = 1e9 scf (exact)
_reg("Tscf",   "trillion standard cu ft",    "gas_volume", "m^3", 2.83168466e10)
# 1 Tscf = 1e12 scf (exact)

# Metric gas volume
_reg("MMm3",   "million cubic metres",       "volume",     "m^3", 1e6)
# 1 MMm3 = 1e6 m³ (exact)

# Reservoir volume
_reg("acre_ft", "acre-foot",                 "volume",     "m^3", 1_233.48)
# 1 acre-ft = 43 560 ft³ = 1 233.48 m³ (NIST: 1.233 489 E+03 m³)

# ── Pressure ──────────────────────────────────────────────────────────────────
# psia, psig, bara, barg — registered in imperial.py / common.py (Phase 1)

# psi_g: deprecated alias → warns and redirects to psig
_AMBIGUOUS_UNITS["psi_g"] = (
    "psig",
    "Deprecated: 'psi_g' has been replaced by 'psig'. "
    "Please update your code to use 'psig' explicitly."
)

# kg/cm² — common field unit in Latin America and legacy literature
# NIST: 1 kgf/cm² = 9.806 65 E+04 Pa (exact — standard gravity × 10⁴)
_reg("kg/cm2",  "kilogram-force per square centimetre", "pressure", "Pa", 9.806_65e4)
_reg("kgf/cm2", "kilogram-force per square centimetre", "pressure", "Pa", 9.806_65e4)

# ── Flow rate ─────────────────────────────────────────────────────────────────
_reg("bbl/day",    "barrels per day",              "flow_rate", "m^3/s",
     0.158987294928 / 86_400)
_reg("Mbbl/day",   "thousand barrels per day",     "flow_rate", "m^3/s",
     158.987294928  / 86_400)
_reg("MMbbl/day",  "million barrels per day",      "flow_rate", "m^3/s",
     158_987.294928 / 86_400)
# 1 MMbbl/day = 1e6 bbl/day

_reg("m3/day",     "cubic metres per day",         "flow_rate", "m^3/s",
     1.0            / 86_400)
_reg("m3/h",       "cubic metres per hour",        "flow_rate", "m^3/s",
     1.0            / 3_600)
# 1 m³/h = 1/3600 m³/s

_reg("Mscf/day",   "thousand scf per day",         "flow_rate", "m^3/s",
     28.3168466     / 86_400)
_reg("MMscf/day",  "million scf per day",           "flow_rate", "m^3/s",
     28_316.8466    / 86_400)
_reg("Bscf/day",   "billion scf per day",           "flow_rate", "m^3/s",
     28_316_846.6   / 86_400)

_reg("bbl/h",      "barrels per hour",             "flow_rate", "m^3/s",
     0.158987294928 / 3_600)
# 1 bbl/h = 1 bbl / 3600 s

_reg("L/s",        "litres per second",            "flow_rate", "m^3/s", 1e-3)
# 1 L/s = 1e-3 m³/s (exact)

_reg("gal/min",    "US gallons per minute",        "flow_rate", "m^3/s",
     3.785_411_784e-3 / 60)
# 1 gal/min = 1 US gal / 60 s
# Also known as GPM — common in surface facility design

# BLPD: barrels of liquid per day — alias for bbl/day
# Same SI factor, different name used in production reporting
_reg("BLPD",       "barrels of liquid per day",   "flow_rate", "m^3/s",
     0.158987294928 / 86_400)

# ── Energy ────────────────────────────────────────────────────────────────────
# MMBtu, toe already registered in imperial.py
# BOE: barrel of oil equivalent
_reg("BOE",  "barrel of oil equivalent", "energy", "J", 6.117e9)
# 1 BOE = 5.8 MMBtu = 5.8 × 1.055056e9 J ≈ 6.117e9 J
# SPE convention: 1 BOE = 5.8 MMBtu_IT

_reg("Mcfe", "thousand cubic feet equivalent", "energy", "J", 1.055056e9)
# 1 Mcfe = 1 MMBtu_IT = 1.055 056 E+09 J
# Used for gas energy equivalent reporting

# ── API gravity ───────────────────────────────────────────────────────────────
register("°API", Unit("API gravity", "api_gravity", "1", 1.0, "°API"))
# Non-linear unit — use api_to_sg() / sg_to_api() in
# quantia/petroleum_conversions.py (Step 2.4)

# ── Semantic tagged units ─────────────────────────────────────────────────────
# Reservoir and stock-tank cubic metres
register_tagged("Sm3_res", "m3",   "reservoir")
register_tagged("Sm3_st",  "m3",   "stock_tank")

# Reservoir and stock-tank standard cubic feet
# Base is "scf" so SI factors are correct for scf/STB GOR conversions
register_tagged("scf_res",  "scf",  "reservoir")
register_tagged("scf_st",   "scf",  "stock_tank")

# Stock-tank and reservoir barrels — for FVF calculations
register_tagged("STB",      "bbl",  "stock_tank")
register_tagged("RB",       "bbl",  "reservoir")

# Mscf tagged variants — for Mscf/STB GOR
register_tagged("Mscf_res", "Mscf", "reservoir")
register_tagged("Mscf_st",  "Mscf", "stock_tank")