"""
Mechanical engineering units.

Covers
------
- Angular velocity and acceleration
- Torque  (semantically tagged — prevents cancellation with energy J)
- Permeability  (darcy, millidarcy — critical for petroleum/reservoir)
- Dynamic viscosity   (Pa·s, cP, P)
- Kinematic viscosity (m²/s, cSt, St)

Sources
-------
NIST SP811 Table 6 (angular velocity, viscosity)
NIST unit conversion tables (Permeability, Viscosity, Moment of Force)
API MPMS / SPE: darcy definition
"""
from quantia._registry import Unit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Angular velocity ──────────────────────────────────────────────────────────
_reg("rpm",    "revolution per minute", "angular_velocity", "rad/s", 3.141_592_653_589_793/30)
# NIST: 1 rpm = 2π/60 rad/s = 1.047 198 E-01 rad/s
_reg("rad/s",  "radian per second",     "angular_velocity", "rad/s", 1.0)
# SI coherent derived unit (NIST Table 6)

# ── Angular acceleration ──────────────────────────────────────────────────────
_reg("rad/s2", "radian per second squared", "angular_acceleration", "rad/s2", 1.0)
# SI coherent derived unit (NIST Table 6)

# ── Torque ────────────────────────────────────────────────────────────────────
# Torque and energy share the same SI dimensions (kg·m²·s⁻²) but are
# physically distinct vector vs scalar quantities.
# register_tagged() creates a labeled CompoundUnit that does not cancel
# when divided by another torque unit or multiplied by angle.
#
# Use "N_m_torque" in code where the distinction matters.
# For display, str() returns "N·m" (the standard engineering notation).
from quantia._compound import register_tagged
register_tagged("N_m_torque", "m",  "torque")
# Semantic wrapper — same SI dimensions as J but will not reduce to J

# Imperial torque — plain Units (convert to N·m numerically)
_reg("lbf_ft", "pound-force foot",  "torque", "N_m_torque", 1.355_818)
# NIST: 1 lbf·ft = 1.355 818 E+00 N·m
_reg("lbf_in", "pound-force inch", "torque", "N_m_torque", 1.355_818 / 12)
# Exact: 1 lbf·in = 1/12 lbf·ft (by definition)
_reg("kgf_m",  "kilogram-force metre","torque","N_m_torque", 9.806_65)
# NIST: 1 kgf·m = 9.806 65 E+00 N·m
_reg("ozf_in", "ounce-force inch",  "torque", "N_m_torque", 7.061_552e-3)
# NIST: 1 ozf·in = 7.061 552 E-03 N·m

# ── Permeability ──────────────────────────────────────────────────────────────
_reg("D",   "darcy",      "permeability", "m2", 9.869_233e-13)
# NIST conversion tables (Permeability): 1 darcy = 9.869 233 E-13 m²
# Definition: 1 D = flow of 1 cP fluid through 1 cm² cross-section
#             with 1 atm/cm pressure gradient at 1 cm³/s
_reg("mD",  "millidarcy", "permeability", "m2", 9.869_233e-16)
# 1 mD = 1e-3 D = 9.869 233 E-16 m²
_reg("µD",  "microdarcy", "permeability", "m2", 9.869_233e-19)
# 1 µD = 1e-6 D — tight/unconventional reservoirs
_reg("uD",  "microdarcy", "permeability", "m2", 9.869_233e-19)
# ASCII fallback for µD

# ── Dynamic viscosity ─────────────────────────────────────────────────────────
_reg("Pa_s", "pascal second",  "dynamic_viscosity", "Pa_s", 1.0)
# NIST Table 6: Pa·s = kg·m⁻¹·s⁻¹ (SI coherent)
_reg("cP",   "centipoise",     "dynamic_viscosity", "Pa_s", 1e-3)
# NIST: 1 cP = 1.0 E-03 Pa·s (exact — 0.01 × poise)
# Most common viscosity unit in petroleum engineering
_reg("P",    "poise",          "dynamic_viscosity", "Pa_s", 1e-1)
# NIST: 1 P = 1.0 E-01 Pa·s (exact — CGS unit)
_reg("mPa_s","millipascal second","dynamic_viscosity","Pa_s",1e-3)
# 1 mPa·s = 1 cP exactly — SI-preferred form

# ── Kinematic viscosity ───────────────────────────────────────────────────────
_reg("m2/s", "square metre per second", "kinematic_viscosity", "m2/s", 1.0)
# SI coherent derived unit
_reg("cSt",  "centistokes",    "kinematic_viscosity", "m2/s", 1e-6)
# NIST: 1 cSt = 1.0 E-06 m²/s (exact)
_reg("St",   "stokes",         "kinematic_viscosity", "m2/s", 1e-4)
# NIST: 1 St = 1.0 E-04 m²/s (exact — CGS unit)
_reg("ft2/s","square foot per second","kinematic_viscosity","m2/s", 9.290_304e-2)
# NIST: 9.290 304 E-02 m²/s