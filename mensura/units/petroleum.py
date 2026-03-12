from mensura._registry import Unit, register
from mensura._compound import register_tagged

def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))

# Volume
_reg("bbl",   "barrel",               "volume", "m3", 0.158987294928)
_reg("Mbbl",  "thousand barrels",     "volume", "m3", 158.987294928)
_reg("MMbbl", "million barrels",      "volume", "m3", 158_987.294928)
_reg("m3",    "cubic metre",          "volume", "m3", 1.0)

# Gas volume (surface conditions)
_reg("scf",   "standard cubic foot",     "gas_volume", "m3", 0.0283168466)
_reg("Mscf",  "thousand standard cu ft", "gas_volume", "m3", 28.3168466)
_reg("MMscf", "million standard cu ft",  "gas_volume", "m3", 28_316.8466)

# Pressure
_reg("psi_g", "psi gauge",  "pressure", "Pa", 6_894.757293168)

# API gravity
register("°API", Unit("API gravity", "api_gravity", "1", 1.0, "°API"))

# Flow rate
_reg("bbl/day",  "barrels per day",          "flow_rate", "m3/s", 0.158987294928 / 86_400)
_reg("Mbbl/day", "thousand barrels per day", "flow_rate", "m3/s", 158.987294928  / 86_400)
_reg("m3/day",   "cubic metres per day",     "flow_rate", "m3/s", 1.0            / 86_400)
_reg("Mscf/day", "thousand scf per day",     "flow_rate", "m3/s", 28.3168466     / 86_400)

# 2e: Semantic tagged units — these share SI dimensions but won't cancel
register_tagged("Sm3_res", "m3", "reservoir")   # reservoir cubic metres
register_tagged("Sm3_st",  "m3", "stock_tank")  # stock-tank cubic metres
register_tagged("scf_res", "m3", "reservoir")   # reservoir cubic feet (via scf base? use m3)
register_tagged("scf_st",  "m3", "stock_tank")

# Named GOR ratios (pre-labeled, registered as opaque units)
register("Sm3/Sm3", Unit("sm3 per sm3",  "GOR", "1", 1.0, "Sm3/Sm3"))
register("scf/STB", Unit("scf per STB",  "GOR", "1", 1.0, "scf/STB"))
register("Mscf/STB",Unit("Mscf per STB", "GOR", "1", 1.0, "Mscf/STB"))