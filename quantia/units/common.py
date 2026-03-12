from quantia._registry import Unit, register

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))
    
# Volume
_reg("L",  "litre",      "volume", "m3", 0.001)
_reg("mL", "millilitre", "volume", "m3", 1e-6)
_reg("cL", "centilitre", "volume", "m3", 1e-5)

# Pressure
_reg("atm", "atmosphere",            "pressure", "Pa", 101_325.0)
_reg("bar", "bar",                   "pressure", "Pa", 100_000.0)
_reg("mmHg","millimetre of mercury", "pressure", "Pa", 133.322387415)