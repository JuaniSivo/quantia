"""
Mechanical engineering units.

Covers
------
- Angular velocity and acceleration
- Torque  (semantically tagged — does not cancel with energy J)
- Permeability  (darcy, millidarcy — critical for petroleum/reservoir)
- Dynamic and kinematic viscosity

Sources
-------
NIST SP811, NIST unit conversion tables (https://www.nist.gov/pml/owm/metric-si/unit-conversion)
"""
from quantia._registry import Unit, register  # noqa: F401 — used in Step 1.4


# Units added in Step 1.4