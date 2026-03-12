# Import order matters: si first (base units), then derived domains.
from quantia.units import si          # noqa: F401
from quantia.units import imperial    # noqa: F401
from quantia.units import common      # noqa: F401
from quantia.units import petroleum   # noqa: F401
from quantia.units import data        # noqa: F401

from quantia._compound import _bootstrap_aliases
_bootstrap_aliases()