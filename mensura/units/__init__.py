# Import order matters: si first (base units), then derived domains.
from mensura.units import si          # noqa: F401
from mensura.units import imperial    # noqa: F401
from mensura.units import common      # noqa: F401
from mensura.units import petroleum   # noqa: F401
from mensura.units import data        # noqa: F401

from mensura._compound import _bootstrap_aliases
_bootstrap_aliases()