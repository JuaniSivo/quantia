"""
Electromagnetic units.

Covers
------
- Electric charge          C, A·h
- Electric conductance     S
- Magnetic flux            Wb, Mx (maxwell)
- Magnetic flux density    T, G (gauss)
- Magnetic field strength  A/m, Oe (oersted)

Note: V, Ω, F, H, A are defined in si.py as named SI derived units
(NIST Table 4). This file adds the remaining electromagnetic units
from Table 4 (C, S, Wb, T) plus practical/legacy variants.

Sources
-------
NIST SP811 Table 4, NIST unit conversion tables (Electricity and Magnetism).
"""
from quantia._registry import Unit, register  # noqa: F401 — used in Step 1.4


# Units added in Step 1.4