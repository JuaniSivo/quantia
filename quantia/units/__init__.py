# Import order matters:
#   1. si       — base units and named SI derived (other files depend on these)
#   2. common   — NIST Table 8 non-SI accepted units
#   3. imperial — US customary / Imperial
#   4. mechanical, thermal, electromagnetic, density — domain units
#   5. petroleum — domain units (may depend on mechanical/density)
#   6. data     — digital storage units
# Aliases are bootstrapped last, after all units are registered.

from quantia.units import si               # noqa: F401
from quantia.units import common           # noqa: F401
from quantia.units import imperial         # noqa: F401
from quantia.units import mechanical       # noqa: F401
from quantia.units import thermal          # noqa: F401
from quantia.units import electromagnetic  # noqa: F401
from quantia.units import density          # noqa: F401
from quantia.units import petroleum        # noqa: F401
from quantia.units import data             # noqa: F401

from quantia._compound import _bootstrap_aliases
_bootstrap_aliases()