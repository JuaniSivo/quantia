"""
Thermal engineering units.

Covers
------
- Heat flux density        W/m²
- Thermal conductivity     W/(m·K)
- Heat capacity            J/K
- Specific heat capacity   J/(kg·K)
- Molar energy             J/mol
- Molar heat capacity      J/(mol·K)

Sources
-------
NIST SP811, NIST unit conversion tables.
All coherent SI derived units per Table 6.
"""
from quantia._registry import Unit, register  # noqa: F401 — used in Step 1.4


# Units added in Step 1.4