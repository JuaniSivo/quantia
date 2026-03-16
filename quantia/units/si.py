from quantia._registry import Unit, AffineUnit, register

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

# Length
_reg("m",   "metre",      "length", "m", 1.0)
_reg("km",  "kilometre",  "length", "m", 1_000.0)
_reg("cm",  "centimetre", "length", "m", 0.01)
_reg("mm",  "millimetre", "length", "m", 0.001)
_reg("nm",  "nanometre",  "length", "m", 1e-9)
_reg("um",  "micrometre", "length", "m", 1e-6)

# ── Area / Volume atomic shorthands ──────────────────────────────────────────
# Both m^2 and m2 are valid expressions. m^2 is the canonical compound form.
# m2 / m3 are registered atomic aliases so engineers can write them as bare
# unit strings (e.g. qu.Q(1.0, "m3")) without the exponent syntax.
_reg("m2", "square metre",  "area",   "m^2", 1.0)
_reg("m3", "cubic metre",   "volume", "m^3", 1.0)

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

# 2c: Temperature — now all AffineUnit
#   to_kelvin  = value * scale + offset
#   from_kelvin = (kelvin - offset) / scale
register("K",  AffineUnit("kelvin",     "temperature", "K", scale=1.0,       offset=0.0,     symbol="K"))
register("°C", AffineUnit("celsius",    "temperature", "K", scale=1.0,       offset=273.15,  symbol="°C"))
register("°F", AffineUnit("fahrenheit", "temperature", "K", scale=5/9,       offset=459.67*(5/9), symbol="°F"))

# Current
_reg("A",  "ampere",      "current", "A", 1.0)
_reg("mA", "milliampere", "current", "A", 0.001)

# Amount / Luminosity / Dimensionless
_reg("mol", "mole",    "amount",      "mol", 1.0)
_reg("cd",  "candela", "luminosity",  "cd",  1.0)
_reg("1",   "dimensionless", "dimensionless", "1", 1.0)

# SI derived
_reg("N",   "newton",         "force",       "N",  1.0)
_reg("kN",  "kilonewton",     "force",       "N",  1_000.0)
_reg("J",   "joule",          "energy",      "J",  1.0)
_reg("kJ",  "kilojoule",      "energy",      "J",  1_000.0)
_reg("MJ",  "megajoule",      "energy",      "J",  1_000_000.0)
_reg("Wh",  "watt-hour",      "energy",      "J",  3_600.0)
_reg("kWh", "kilowatt-hour",  "energy",      "J",  3_600_000.0)
_reg("eV",  "electronvolt",   "energy",      "J",  1.602176634e-19)
_reg("W",   "watt",           "power",       "W",  1.0)
_reg("kW",  "kilowatt",       "power",       "W",  1_000.0)
_reg("MW",  "megawatt",       "power",       "W",  1_000_000.0)
_reg("Pa",  "pascal",         "pressure",    "Pa", 1.0)
_reg("kPa", "kilopascal",     "pressure",    "Pa", 1_000.0)
_reg("MPa", "megapascal",     "pressure",    "Pa", 1_000_000.0)
_reg("V",   "volt",           "voltage",     "V",  1.0)
_reg("mV",  "millivolt",      "voltage",     "V",  0.001)
_reg("kV",  "kilovolt",       "voltage",     "V",  1_000.0)
_reg("Ω",   "ohm",            "resistance",  "Ω",  1.0)
_reg("kΩ",  "kiloohm",        "resistance",  "Ω",  1_000.0)
_reg("F",   "farad",          "capacitance", "F",  1.0)
_reg("H",   "henry",          "inductance",  "H",  1.0)
_reg("rad", "radian",         "angle",       "rad",1.0)
_reg("deg", "degree",         "angle",       "rad",3.141592653589793/180)
_reg("Hz",  "hertz",          "frequency",   "Hz", 1.0)
_reg("kHz", "kilohertz",      "frequency",   "Hz", 1_000.0)
_reg("MHz", "megahertz",      "frequency",   "Hz", 1_000_000.0)

_reg("sr",  "steradian",   "solid_angle",          "sr",   1.0)
# NIST Table 4: sr = m²/m² = 1 (dimensionless but named)

_reg("C",   "coulomb",     "electric_charge",      "C",    1.0)
# NIST Table 4: C = A·s

_reg("S",   "siemens",     "electric_conductance", "S",    1.0)
# NIST Table 4: S = A/V = kg⁻¹·m⁻²·s³·A²

_reg("Wb",  "weber",       "magnetic_flux",        "Wb",   1.0)
# NIST Table 4: Wb = V·s = kg·m²·s⁻²·A⁻¹

_reg("T",   "tesla",       "magnetic_flux_density","T",    1.0)
# NIST Table 4: T = Wb/m² = kg·s⁻²·A⁻¹

_reg("lm",  "lumen",       "luminous_flux",        "lm",   1.0)
# NIST Table 4: lm = cd·sr

_reg("lx",  "lux",         "illuminance",          "lx",   1.0)
# NIST Table 4: lx = lm/m² = cd·sr·m⁻²

_reg("Bq",  "becquerel",   "radioactivity",        "Hz",   1.0)
# NIST Table 4: Bq = s⁻¹ (same SI dimension as Hz but distinct quantity)

_reg("Gy",  "gray",        "absorbed_dose",        "Gy",   1.0)
# NIST Table 4: Gy = J/kg = m²·s⁻²

_reg("Sv",  "sievert",     "dose_equivalent",      "Sv",   1.0)
# NIST Table 4: Sv = J/kg = m²·s⁻² (same dimension as Gy, distinct quantity)

_reg("kat", "katal",       "catalytic_activity",   "kat",  1.0)
# NIST Table 4: kat = mol·s⁻¹

# ── Additional prefixed SI variants (engineering-common) ─────────────────────

# Frequency
_reg("GHz", "gigahertz",   "frequency",  "Hz", 1e9)
_reg("THz", "terahertz",   "frequency",  "Hz", 1e12)

# Force
_reg("MN",  "meganewton",  "force",      "N",  1e6)
_reg("mN",  "millinewton", "force",      "N",  1e-3)
_reg("µN",  "micronewton", "force",      "N",  1e-6)
_reg("uN",  "micronewton", "force",      "N",  1e-6)   # ASCII fallback

# Energy
_reg("GJ",  "gigajoule",   "energy",     "J",  1e9)

# Power
_reg("GW",  "gigawatt",    "power",      "W",  1e9)
_reg("mW",  "milliwatt",   "power",      "W",  1e-3)
_reg("µW",  "microwatt",   "power",      "W",  1e-6)
_reg("uW",  "microwatt",   "power",      "W",  1e-6)   # ASCII fallback

# Pressure / Stress
_reg("GPa", "gigapascal",  "pressure",   "Pa", 1e9)
_reg("µPa", "micropascal", "pressure",   "Pa", 1e-6)   # acoustics
_reg("uPa", "micropascal", "pressure",   "Pa", 1e-6)   # ASCII fallback

# Current
_reg("µA",  "microampere", "current",    "A",  1e-6)
_reg("uA",  "microampere", "current",    "A",  1e-6)   # ASCII fallback
_reg("nA",  "nanoampere",  "current",    "A",  1e-9)

# Voltage
_reg("µV",  "microvolt",   "voltage",    "V",  1e-6)
_reg("uV",  "microvolt",   "voltage",    "V",  1e-6)   # ASCII fallback
_reg("nV",  "nanovolt",    "voltage",    "V",  1e-9)

# Resistance
_reg("MΩ",  "megaohm",     "resistance", "Ω",  1e6)
_reg("GΩ",  "gigaohm",     "resistance", "Ω",  1e9)

# Capacitance
_reg("mF",  "millifarad",  "capacitance","F",  1e-3)
_reg("µF",  "microfarad",  "capacitance","F",  1e-6)
_reg("uF",  "microfarad",  "capacitance","F",  1e-6)   # ASCII fallback
_reg("nF",  "nanofarad",   "capacitance","F",  1e-9)
_reg("pF",  "picofarad",   "capacitance","F",  1e-12)

# Inductance
_reg("mH",  "millihenry",  "inductance", "H",  1e-3)
_reg("µH",  "microhenry",  "inductance", "H",  1e-6)
_reg("uH",  "microhenry",  "inductance", "H",  1e-6)   # ASCII fallback
_reg("nH",  "nanohenry",   "inductance", "H",  1e-9)

# Amount
_reg("mmol","millimole",   "amount",     "mol",1e-3)
_reg("µmol","micromole",   "amount",     "mol",1e-6)
_reg("umol","micromole",   "amount",     "mol",1e-6)   # ASCII fallback
_reg("nmol","nanomole",    "amount",     "mol",1e-9)