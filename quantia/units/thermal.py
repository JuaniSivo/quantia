"""
Thermal engineering units.

All are coherent SI derived units (NIST Table 6) unless otherwise noted.
Registered as plain Units with to_si=1.0 since they are already SI —
their compound dimensions are resolved naturally by the unit algebra.

Sources
-------
NIST SP811 Table 6
NIST unit conversion tables (Heat sections)
"""
from quantia._registry import Unit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Heat flux density ─────────────────────────────────────────────────────────
_reg("W/m2",   "watt per square metre",       "heat_flux_density",    "W/m2",  1.0)
# NIST Table 6: W/m² = kg·s⁻³

# ── Thermal conductivity ──────────────────────────────────────────────────────
_reg("W/m_K",  "watt per metre kelvin",       "thermal_conductivity", "W/m_K", 1.0)
# NIST Table 6: W/(m·K) = kg·m·s⁻³·K⁻¹

# ── Heat capacity / entropy ───────────────────────────────────────────────────
_reg("J/K",    "joule per kelvin",            "heat_capacity",        "J/K",   1.0)
# NIST Table 6: J/K = kg·m²·s⁻²·K⁻¹

# ── Specific heat capacity / specific entropy ─────────────────────────────────
_reg("J/kg_K", "joule per kilogram kelvin",   "specific_heat_capacity","J/kg_K",1.0)
# NIST Table 6: J/(kg·K) = m²·s⁻²·K⁻¹

# ── Molar quantities ──────────────────────────────────────────────────────────
_reg("J/mol",  "joule per mole",              "molar_energy",         "J/mol", 1.0)
# NIST Table 6: J/mol = kg·m²·s⁻²·mol⁻¹

_reg("J/mol_K","joule per mole kelvin",       "molar_heat_capacity",  "J/mol_K",1.0)
# NIST Table 6: J/(mol·K) = kg·m²·s⁻²·mol⁻¹·K⁻¹

# ── Imperial / practical thermal units ───────────────────────────────────────
_reg("BTU_IT/h",   "BTU (IT) per hour",       "power",   "W",  2.930_711e-1)
# NIST: 2.930 711 E-01 W
_reg("BTU_IT/lb",  "BTU (IT) per pound",      "specific_energy","J/kg", 2.326e3)
# NIST: 2.326 E+03 J/kg (exact — used in steam tables)
_reg("BTU_IT/lb_F","BTU (IT) per lb °F",      "specific_heat_capacity","J/kg_K",4.1868e3)
# NIST: 4.1868 E+03 J/(kg·K)