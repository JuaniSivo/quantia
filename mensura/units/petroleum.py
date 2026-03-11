from mensura._registry import Unit, register

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

# Volume
_reg("bbl",   "barrel",               "volume", "m3", 0.158987294928)
_reg("Mbbl",  "thousand barrels",     "volume", "m3", 158.987294928)
_reg("MMbbl", "million barrels",      "volume", "m3", 158_987.294928)
_reg("gal",   "US gallon",            "volume", "m3", 0.003785411784)  # also in imperial
_reg("m3",    "cubic metre",          "volume", "m3", 1.0)
_reg("Sm3",   "standard cubic metre", "volume", "m3", 1.0)  # same SI factor; semantic tag TBD

# Gas volume (surface conditions)
_reg("scf",   "standard cubic foot",      "gas_volume", "m3", 0.0283168466)
_reg("Mscf",  "thousand standard cu ft",  "gas_volume", "m3", 28.3168466)
_reg("MMscf", "million standard cu ft",   "gas_volume", "m3", 28_316.8466)
_reg("Bscf",  "billion standard cu ft",   "gas_volume", "m3", 28_316_846.6)

# Pressure (common in petroleum — Pa already in si.py)
_reg("kPa_g", "kilopascal gauge",  "pressure", "Pa", 1_000.0)  # gauge = abs - 101325; factor only

# API gravity (dimensionless derived)
register("°API", Unit("API gravity", "api_gravity", "1", 1.0, "°API"))

# GOR / solution gas (dimensionless ratios — semantic tags TBD in Phase 2)
register("Sm3/Sm3", Unit("sm3 per sm3",  "GOR", "1", 1.0, "Sm3/Sm3"))
register("scf/STB", Unit("scf per STB",  "GOR", "1", 1.0, "scf/STB"))
register("Mscf/STB",Unit("Mscf per STB", "GOR", "1", 1.0, "Mscf/STB"))

# Flow rate
_reg("bbl/day",  "barrels per day",          "flow_rate", "m3/s", 0.158987294928 / 86_400)
_reg("Mbbl/day", "thousand barrels per day", "flow_rate", "m3/s", 158.987294928  / 86_400)
_reg("m3/day",   "cubic metres per day",     "flow_rate", "m3/s", 1.0            / 86_400)
_reg("Mscf/day", "thousand scf per day",     "flow_rate", "m3/s", 28.3168466     / 86_400)