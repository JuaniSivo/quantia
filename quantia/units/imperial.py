from quantia._registry import Unit, AffineUnit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Length ────────────────────────────────────────────────────────────────────
_reg("mi",  "mile",               "length",   "m",   1_609.344)
# NIST: 1.609 344 E+03 m (exact)
_reg("yd",  "yard",               "length",   "m",   0.9144)
# NIST: 9.144 E-01 m (exact)
_reg("ft",  "foot",               "length",   "m",   0.3048)
# NIST: 3.048 E-01 m (exact)
_reg("in",  "inch",               "length",   "m",   0.0254)
# NIST: 2.54 E-02 m (exact)
_reg("Å",    "ångström",          "length",   "m",   1e-10)
# NIST: 1 Å = 1.0 E-10 m (exact)
_reg("nmi",  "nautical mile",     "length",   "m",   1852.0)
# NIST: 1 nmi = 1852 m (exact, international)
_reg("mil",  "mil (0.001 inch)",  "length",   "m",   2.54e-5)
# NIST: 1 mil = 2.54 E-05 m
_reg("ly",   "light year",        "length",   "m",   9.460_73e15)
# NIST: 9.460 73 E+15 m

# ── Mass ──────────────────────────────────────────────────────────────────────
_reg("lb",       "pound",          "mass",    "kg",  0.45359237)
# NIST: 4.535 924 E-01 kg (exact)
_reg("oz",       "ounce",          "mass",    "kg",  0.028349523125)
# NIST: 2.834 952 E-02 kg
_reg("gr",       "grain",          "mass",    "kg",  6.479_891e-5)
# NIST: 6.479 891 E-05 kg
_reg("slug",     "slug",           "mass",    "kg",  1.459_390e1)
# NIST: 1.459 390 E+01 kg
_reg("ton_long", "long ton (2240 lb)",   "mass",     "kg", 0.45359237 * 2240)
# Exact: 1 long ton = 2240 lb (by definition)
_reg("ton_short","short ton (2000 lb)",  "mass",     "kg", 0.45359237 * 2000)
# Exact: 1 short ton = 2000 lb (by definition)

# ── Force ─────────────────────────────────────────────────────────────────────
_reg("lbf",  "pound-force",       "force",    "N",   4.4482216152605)
# NIST: 4.448 222 E+00 N
_reg("dyn",  "dyne",              "force",    "N",   1e-5)
# NIST: 1 dyn = 1.0 E-05 N (exact)
_reg("kgf",  "kilogram-force",    "force",    "N",   9.806_65)
# NIST: 9.806 65 E+00 N (exact — gn by definition)
_reg("kip",      "kip (1000 lbf)",       "force",    "N",  4.4482216152605 * 1000)
# Exact: 1 kip = 1000 lbf (by definition)
_reg("ozf",      "ounce-force",          "force",    "N",  4.4482216152605 / 16)
# Exact: 1 ozf = 1/16 lbf (by definition)
_reg("pdl",  "poundal",           "force",    "N",   1.382_550e-1)
# NIST: 1.382 550 E-01 N

# ── Pressure ──────────────────────────────────────────────────────────────────
# "psi" is the generic symbol — it will become ambiguous in step-1-3 when
# psia/psig are added. It is kept here for backward compatibility until then.
# "atm", "bar", "mmHg" are intentionally absent — defined in common.py.
_reg("psi",   "pound per square inch",          "pressure", "Pa", 6_894.757293168)
# NIST: 6.894 757 E+03 Pa
_reg("ksi",      "kip per square inch",  "pressure", "Pa", 6_894.757293168 * 1000)
# Exact: 1 ksi = 1000 psi — use same base factor as psia for consistency
_reg("torr",  "torr",                           "pressure", "Pa", 1.333_224e2)
# NIST: 1.333 224 E+02 Pa
_reg("inHg",  "inch of mercury (conventional)", "pressure", "Pa", 3.386_389e3)
# NIST: 3.386 389 E+03 Pa
_reg("inH2O", "inch of water (conventional)",   "pressure", "Pa", 2.490_889e2)
# NIST: 2.490 889 E+02 Pa
_reg("ftH2O", "foot of water (conventional)",   "pressure", "Pa", 2.989_067e3)
# NIST: 2.989 067 E+03 Pa
_reg("cmHg",  "centimetre of mercury (conventional)","pressure","Pa",1.333_224e3)
# NIST: 1.333 224 E+03 Pa
_reg("mbar",  "millibar",                       "pressure", "Pa", 1e2)
# NIST: 1.0 E+02 Pa (exact — 0.001 bar)

# ── Gauge / Absolute pressure ─────────────────────────────────────────────────
# psia: absolute — offset=0, scale = psi factor. Same numeric result as plain
#       multiplicative unit but uses AffineUnit for interface consistency with psig.
# psig: gauge — P_abs(Pa) = P_gauge(psi) * scale + 1 atm
#       1 atm = 101 325 Pa (exact, NIST)
# "psi" alone warns and redirects to psia via _AMBIGUOUS_UNITS in _registry.py

register("psia", AffineUnit(
    "pound per square inch (absolute)", "pressure", "Pa",
    scale=6_894.757293168, offset=0.0, symbol="psia"))
# NIST: 1 psi = 6.894 757 E+03 Pa

register("psig", AffineUnit(
    "pound per square inch (gauge)", "pressure", "Pa",
    scale=6_894.757293168, offset=101_325.0, symbol="psig"))
# Gauge: P_abs = P_g * 6894.757 + 101325  (standard atmosphere offset)

# ── Temperature ──────────────────────────────────────────────────────────────
register("°R", AffineUnit(
    "rankine", "temperature", "K",
    scale=5/9, offset=0.0, symbol="°R"))
# NIST: T(K) = T(°R) × 5/9  — absolute scale, no offset

# ── Energy ───────────────────────────────────────────────────────────────────
# BTU has two common thermodynamic definitions.
# "BTU" alone triggers a UserWarning and redirects to BTU_IT via _AMBIGUOUS_UNITS.
_reg("BTU_IT", "British thermal unit (International Table)",     "energy", "J", 1_055.056)
_reg("BTU_th", "British thermal unit (thermochemical)",          "energy", "J", 1_054.350)
# NIST SP811: BTU_IT = 1.055 056 E+03 J; BTU_th = 1.054 350 E+03 J

# calorie has two common thermodynamic definitions.
# "cal" / "kcal" alone trigger a UserWarning and redirect via _AMBIGUOUS_UNITS.
_reg("cal_th",  "calorie (thermochemical)",          "energy", "J", 4.184)
_reg("cal_IT",  "calorie (International Table)",     "energy", "J", 4.1868)
_reg("kcal_th", "kilocalorie (thermochemical)",      "energy", "J", 4_184.0)
_reg("kcal_IT", "kilocalorie (International Table)", "energy", "J", 4_186.8)
# NIST SP811: cal_th = 4.184 J (exact); cal_IT = 4.1868 J

_reg("ft_lbf",  "foot pound-force",            "energy","J", 1.355_818)
# NIST: 1.355 818 E+00 J
_reg("therm_EC","therm (EC)",                  "energy","J", 1.055_06e8)
# NIST: 1.055 06 E+08 J
_reg("therm_US","therm (US)",                  "energy","J", 1.054_804e8)
# NIST: 1.054 804 E+08 J
_reg("MMBtu",   "million BTU (IT)",            "energy","J", 1.055_056e9)
# Derived: 1e6 × BTU_IT — common in gas contracts
_reg("erg",     "erg",                         "energy","J", 1e-7)
# NIST: 1.0 E-07 J (exact)
_reg("toe",     "tonne of oil equivalent",     "energy","J", 4.1868e10)
# IEA definition: 1 toe = 41.868 GJ = 4.1868 E+10 J

# ── Power ─────────────────────────────────────────────────────────────────────
_reg("hp",  "horsepower (550 ft·lbf/s)", "power", "W", 745.6999)
# NIST: 7.456 999 E+02 W

# ── Speed ─────────────────────────────────────────────────────────────────────
_reg("mph", "mile per hour", "speed", "m/s", 0.44704)
# NIST: 4.4704 E-01 m/s (exact — derived from mile and hour definitions)

_reg("kn",  "knot", "speed", "m/s", 1852 / 3600)
# NIST: 5.144 444 E-01 m/s — 1 kn = 1852 m / 3600 s (exact, international nautical mile)
# Previous value 0.514444 was truncated; 1852/3600 = 0.51444... recurring

# ── Volume ────────────────────────────────────────────────────────────────────
_reg("gal",   "US gallon",         "volume",  "m^3",  3.785_411_784e-3)
# NIST: 3.785 412 E-03 m3
_reg("qt",    "US quart",          "volume",  "m^3",  9.463_529_5e-4)
# NIST: 9.463 529 E-04 m3
_reg("ft3",   "cubic foot",        "volume",  "m^3",  2.831_685e-2)
# NIST: 2.831 685 E-02 m³
_reg("in3",   "cubic inch",        "volume",  "m^3",  1.638_706e-5)
# NIST: 1.638 706 E-05 m³
_reg("yd3",   "cubic yard",        "volume",  "m^3",  7.645_549e-1)
# NIST: 7.645 549 E-01 m³
_reg("fl_oz", "fluid ounce (US)",  "volume",  "m^3",  2.957_353e-5)
# NIST: 2.957 353 E-05 m³
_reg("gal_imp","Imperial gallon",  "volume",  "m^3",  4.546_09e-3)
# NIST: 4.546 09 E-03 m³ (Canadian and UK)
_reg("pt",    "pint (US liquid)",  "volume",  "m^3",  4.731_765e-4)
# NIST: 4.731 765 E-04 m³

# ── Area ─────────────────────────────────────────────────────────────────────
_reg("ft2",  "square foot",       "area",     "m^2",  9.290_304e-2)
# NIST: 9.290 304 E-02 m² (exact — derived from ft definition)
_reg("in2",  "square inch",       "area",     "m^2",  6.4516e-4)
# NIST: 6.4516 E-04 m² (exact)
_reg("yd2",  "square yard",       "area",     "m^2",  8.361_274e-1)
# NIST: 8.361 274 E-01 m²
_reg("mi2",  "square mile",       "area",     "m^2",  2.589_988e6)
# NIST: 2.589 988 E+06 m²
_reg("acre", "acre",              "area",     "m^2",  4.046_873e3)
# NIST: 4.046 873 E+03 m²

# ── Velocity additions ────────────────────────────────────────────────────────
_reg("ft/s",   "foot per second",    "speed",  "m/s", 0.3048)
# NIST: 3.048 E-01 m/s (exact — same as ft definition)
_reg("ft/min", "foot per minute",    "speed",  "m/s", 5.08e-3)
# NIST: 5.08 E-03 m/s (exact)
_reg("km/h",   "kilometre per hour", "speed",  "m/s", 1/3.6)
# NIST: 2.777 778 E-01 m/s (exact — 1000/3600)