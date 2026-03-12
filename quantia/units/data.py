from quantia._registry import Unit, register

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

_reg("B",   "byte",     "data", "B", 1.0)
_reg("KB",  "kilobyte", "data", "B", 1_024.0)
_reg("MB",  "megabyte", "data", "B", 1_048_576.0)
_reg("GB",  "gigabyte", "data", "B", 1_073_741_824.0)
_reg("TB",  "terabyte", "data", "B", 1_099_511_627_776.0)
_reg("bit", "bit",      "data", "B", 0.125)