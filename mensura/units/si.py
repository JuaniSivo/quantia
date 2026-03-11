from mensura._registry import Unit, register
from mensura._compound import _register_decomposition

# ── SI base units ─────────────────────────────────────────────────────────────

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

# Length
_reg("m",   "metre",      "length", "m", 1.0)
_reg("km",  "kilometre",  "length", "m", 1_000.0)
_reg("cm",  "centimetre", "length", "m", 0.01)
_reg("mm",  "millimetre", "length", "m", 0.001)
_reg("nm",  "nanometre",  "length", "m", 1e-9)
_reg("um",  "micrometre", "length", "m", 1e-6)

# Mass
_reg("kg",  "kilogram",  "mass", "kg", 1.0)
_reg("g",   "gram",      "mass", "kg", 0.001)
_reg("mg",  "milligram", "mass", "kg", 1e-6)
_reg("t",   "tonne",     "mass", "kg", 1_000.0)

# Time
_reg("s",   "second",      "time", "s", 1.0)
_reg("ms",  "millisecond", "time", "s", 0.001)
_reg("us",  "microsecond", "time", "s", 1e-6)
_reg("min", "minute",      "time", "s", 60.0)
_reg("h",   "hour",        "time", "s", 3_600.0)
_reg("day", "day",         "time", "s", 86_400.0)

# Temperature (offset units — special cased in UnitFloat)
register("K",  Unit("kelvin",     "temperature", "K", 1.0,  "K"))
register("°C", Unit("celsius",    "temperature", "K", 0.0,  "°C"))
register("°F", Unit("fahrenheit", "temperature", "K", 0.0,  "°F"))

# Electric current
_reg("A",  "ampere",      "current", "A", 1.0)
_reg("mA", "milliampere", "current", "A", 0.001)

# Amount
_reg("mol", "mole", "amount", "mol", 1.0)

# Luminosity
_reg("cd", "candela", "luminosity", "cd", 1.0)

# Dimensionless
_reg("1", "dimensionless", "dimensionless", "1", 1.0)

# ── SI derived units ──────────────────────────────────────────────────────────

# Force
_reg("N",  "newton",     "force", "N", 1.0)
_reg("kN", "kilonewton", "force", "N", 1_000.0)

# Energy
_reg("J",    "joule",         "energy", "J", 1.0)
_reg("kJ",   "kilojoule",     "energy", "J", 1_000.0)
_reg("MJ",   "megajoule",     "energy", "J", 1_000_000.0)
_reg("Wh",   "watt-hour",     "energy", "J", 3_600.0)
_reg("kWh",  "kilowatt-hour", "energy", "J", 3_600_000.0)
_reg("eV",   "electronvolt",  "energy", "J", 1.602176634e-19)

# Volume
_reg("m3",  "cubic metre", "volume", "m3", 1.0)

# Power
_reg("W",  "watt",     "power", "W", 1.0)
_reg("kW", "kilowatt", "power", "W", 1_000.0)
_reg("MW", "megawatt", "power", "W", 1_000_000.0)

# Pressure
_reg("Pa",  "pascal",     "pressure", "Pa", 1.0)
_reg("kPa", "kilopascal", "pressure", "Pa", 1_000.0)
_reg("MPa", "megapascal", "pressure", "Pa", 1_000_000.0)

# Voltage / resistance / capacitance / inductance
_reg("V",  "volt",        "voltage",     "V", 1.0)
_reg("mV", "millivolt",   "voltage",     "V", 0.001)
_reg("kV", "kilovolt",    "voltage",     "V", 1_000.0)
_reg("Ω",  "ohm",         "resistance",  "Ω", 1.0)
_reg("kΩ", "kiloohm",     "resistance",  "Ω", 1_000.0)
_reg("F",  "farad",       "capacitance", "F", 1.0)
_reg("H",  "henry",       "inductance",  "H", 1.0)

# Angle
_reg("rad", "radian", "angle", "rad", 1.0)
_reg("deg", "degree", "angle", "rad", 3.141592653589793 / 180)

# Frequency
_reg("Hz",  "hertz",     "frequency", "Hz", 1.0)
_reg("kHz", "kilohertz", "frequency", "Hz", 1_000.0)
_reg("MHz", "megahertz", "frequency", "Hz", 1_000_000.0)

# Decompositions of derived units into base units (for dimensional analysis)
_register_decomposition("m3", {"m" : 3})
_register_decomposition("N",  {"kg": 1,  "m":  1, "s": -2})
_register_decomposition("Pa", {"kg": 1,  "m": -1, "s": -2})
_register_decomposition("J",  {"kg": 1,  "m":  2, "s": -2})
_register_decomposition("W",  {"kg": 1,  "m":  2, "s": -3})
_register_decomposition("V",  {"kg": 1,  "m":  2, "s": -3, "A": -1})
_register_decomposition("Ω",  {"kg": 1,  "m":  2, "s": -3, "A": -2})
_register_decomposition("F",  {"kg": -1, "m": -2, "s":  4, "A":  2})
_register_decomposition("H",  {"kg": 1,  "m":  2, "s": -2, "A": -2})
_register_decomposition("Hz", {"s" : -1})
