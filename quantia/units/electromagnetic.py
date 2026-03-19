# quantia/units/electromagnetic.py
"""
Electromagnetic units not already covered by si.py.

Note: V, Ω, F, H, A, mA are defined in si.py as NIST Table 4 named
SI derived units. This file adds:
  - C, S, Wb, T (Table 4 units added to si.py in step 1.4)
  - Practical variants: A·h, G, Mx, Oe
  - Ω·m (resistivity)

Sources
-------
NIST SP811 Table 4
NIST unit conversion tables (Electricity and Magnetism)
"""
from quantia._registry import Unit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Electric charge ───────────────────────────────────────────────────────────
_reg("A_h",  "ampere-hour",           "electric_charge",       "C",    3_600.0)
# NIST: 1 A·h = 3.6 E+03 C (exact — used in battery capacity)

# ── Magnetic flux density ─────────────────────────────────────────────────────
_reg("G",    "gauss",                 "magnetic_flux_density", "T",    1e-4)
# NIST: 1 G = 1.0 E-04 T (exact — CGS unit)
_reg("mT",   "millitesla",            "magnetic_flux_density", "T",    1e-3)
_reg("µT",   "microtesla",            "magnetic_flux_density", "T",    1e-6)
_reg("uT",   "microtesla",            "magnetic_flux_density", "T",    1e-6)
_reg("nT",   "nanotesla",             "magnetic_flux_density", "T",    1e-9)
# nT commonly used in geophysics / MRI

# ── Magnetic flux ─────────────────────────────────────────────────────────────
_reg("Mx",   "maxwell",               "magnetic_flux",         "Wb",   1e-8)
# NIST: 1 Mx = 1.0 E-08 Wb (exact — CGS unit)
_reg("mWb",  "milliweber",            "magnetic_flux",         "Wb",   1e-3)
_reg("µWb",  "microweber",            "magnetic_flux",         "Wb",   1e-6)
_reg("uWb",  "microweber",            "magnetic_flux",         "Wb",   1e-6)

# ── Resistivity ───────────────────────────────────────────────────────────────
_reg("Ω_m",  "ohm metre",             "resistivity",           "Ω_m",  1.0)
# SI coherent: ρ = R × A / L  [Ω·m]
_reg("µΩ_m", "microohm metre",        "resistivity",           "Ω_m",  1e-6)
_reg("uΩ_m", "microohm metre",        "resistivity",           "Ω_m",  1e-6)
# Used in conductor / material characterization