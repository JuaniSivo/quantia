"""
Density and concentration units.

Covers
------
- Mass density     g/cm³, kg/L, lb/ft³, lb/gal (US), lb/in³
- Concentration    mg/L, ppm, ppb  (Step 1.4)

Note: kg/m³ is a coherent SI derived unit (NIST Table 5) and needs
no explicit registration — it is produced naturally by kg / m^3
arithmetic in the compound unit system.

Sources
-------
NIST SP811, NIST unit conversion tables (Mass Divided by Volume).
"""
from quantia._registry import Unit, register  # noqa: F401 — used in Step 1.4


# Units added in Step 1.4