"""
Density and concentration units.

Note: kg/m³ is a coherent SI derived unit (NIST Table 5) and needs no
explicit registration — it is produced naturally by kg / m^3 arithmetic.

Sources
-------
NIST unit conversion tables (Mass Divided by Volume)
"""
from quantia._registry import Unit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Mass density ──────────────────────────────────────────────────────────────
_reg("g/cm3",  "gram per cubic centimetre", "mass_density", "kg/m3", 1e3)
# NIST: 1 g/cm³ = 1.0 E+03 kg/m³ (exact)
# Most common density unit in fluid PVT / laboratory

_reg("kg/L",   "kilogram per litre",        "mass_density", "kg/m3", 1e3)
# 1 kg/L = 1 kg / 1e-3 m³ = 1e3 kg/m³ (exact)
# Numerically equal to g/cm³ — both registered for user convenience

_reg("g/mL",   "gram per millilitre",       "mass_density", "kg/m3", 1e3)
# 1 g/mL = 1 g / 1e-6 m³ × (1 kg / 1000 g) = 1e3 kg/m³ (exact)
# Common in laboratory / chemistry

_reg("lb/ft3", "pound per cubic foot",      "mass_density", "kg/m3", 1.601_846e1)
# NIST: 1.601 846 E+01 kg/m³

_reg("lb/gal", "pound per US gallon",       "mass_density", "kg/m3", 1.198_264e2)
# NIST: 1.198 264 E+02 kg/m³
# Used in drilling fluid (mud weight) characterization

_reg("lb/in3", "pound per cubic inch",      "mass_density", "kg/m3", 2.767_990e4)
# NIST: 2.767 990 E+04 kg/m³

_reg("sg",     "specific gravity",          "mass_density", "kg/m3", 1e3)
# Specific gravity relative to water at 4°C (ρ_water = 1000 kg/m³)
# sg=1.0 → 1000 kg/m³. Dimensionless by convention but treated as density here.

# ── Concentration ─────────────────────────────────────────────────────────────
_reg("mg/L",   "milligram per litre",       "mass_concentration","kg/m3", 1e-3)
# 1 mg/L = 1e-3 g / 1e-3 m³ = 1e-3 kg/m³
# Common in water quality / produced water analysis

_reg("ppm",    "parts per million (mass)",  "mass_concentration","kg/m3", 1e-3)
# 1 ppm ≡ 1 mg/kg ≈ 1 mg/L for dilute aqueous solutions
# Numerically equal to mg/L for water-based systems

_reg("ppb",    "parts per billion (mass)",  "mass_concentration","kg/m3", 1e-6)
# 1 ppb ≡ 1 µg/kg ≈ 1 µg/L for dilute aqueous solutions