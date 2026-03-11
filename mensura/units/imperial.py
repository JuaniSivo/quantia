from mensura._registry import Unit, register

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

# Length
_reg("mi",  "mile",       "length", "m", 1_609.344)
_reg("yd",  "yard",       "length", "m", 0.9144)
_reg("ft",  "foot",       "length", "m", 0.3048)
_reg("in",  "inch",       "length", "m", 0.0254)

# Mass
_reg("lb",  "pound", "mass", "kg", 0.45359237)
_reg("oz",  "ounce", "mass", "kg", 0.028349523125)

# Force
_reg("lbf", "pound-force", "force", "N", 4.4482216152605)

# Pressure
_reg("psi", "pound per square inch", "pressure", "Pa", 6_894.757293168)

# Energy
_reg("BTU",  "british thermal unit", "energy", "J", 1_055.05585262)
_reg("cal",  "calorie",              "energy", "J", 4.184)
_reg("kcal", "kilocalorie",          "energy", "J", 4_184.0)

# Power
_reg("hp", "horsepower", "power", "W", 745.69987158227)

# Speed
_reg("mph", "mile per hour",       "speed", "m/s", 0.44704)
_reg("kn",  "knot",                "speed", "m/s", 0.514444)

# Volume
_reg("gal",    "US gallon",  "volume", "m3", 0.003785411784)
_reg("qt",     "US quart",   "volume", "m3", 0.000946352946)
_reg("fl_oz",  "fluid ounce","volume", "m3", 2.95735296875e-5)