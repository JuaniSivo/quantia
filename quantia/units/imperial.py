from quantia._registry import Unit, AffineUnit, register


def _reg(sym, name, quantity, si_unit, to_si):
    register(sym, Unit(name, quantity, si_unit, float(to_si), sym))


# ── Length ────────────────────────────────────────────────────────────────────
_reg("mi",  "mile",  "length", "m", 1_609.344)
# NIST: 1.609 344 E+03 m (exact)
_reg("yd",  "yard",  "length", "m", 0.9144)
# NIST: 9.144 E-01 m (exact)
_reg("ft",  "foot",  "length", "m", 0.3048)
# NIST: 3.048 E-01 m (exact)
_reg("in",  "inch",  "length", "m", 0.0254)
# NIST: 2.54 E-02 m (exact)

# ── Mass ──────────────────────────────────────────────────────────────────────
_reg("lb",  "pound", "mass", "kg", 0.45359237)
# NIST: 4.535 924 E-01 kg (exact)
_reg("oz",  "ounce", "mass", "kg", 0.028349523125)
# NIST: 2.834 952 E-02 kg

# ── Force ─────────────────────────────────────────────────────────────────────
_reg("lbf", "pound-force", "force", "N", 4.4482216152605)
# NIST: 4.448 222 E+00 N

# ── Pressure ──────────────────────────────────────────────────────────────────
# "psi" is the generic symbol — it will become ambiguous in step-1-3 when
# psia/psig are added. It is kept here for backward compatibility until then.
# "atm", "bar", "mmHg" are intentionally absent — defined in common.py.
_reg("psi", "pound per square inch", "pressure", "Pa", 6_894.757293168)
# NIST: 6.894 757 E+03 Pa

# ── Energy ───────────────────────────────────────────────────────────────────
# BTU has two common thermodynamic definitions.
# "BTU" alone triggers a UserWarning and redirects to BTU_IT via _AMBIGUOUS_UNITS.
_reg("BTU_IT", "British thermal unit (International Table)",    "energy", "J", 1_055.056)
_reg("BTU_th", "British thermal unit (thermochemical)",          "energy", "J", 1_054.350)
# NIST SP811: BTU_IT = 1.055 056 E+03 J; BTU_th = 1.054 350 E+03 J

# calorie has two common thermodynamic definitions.
# "cal" / "kcal" alone trigger a UserWarning and redirect via _AMBIGUOUS_UNITS.
_reg("cal_th",  "calorie (thermochemical)",          "energy", "J", 4.184)
_reg("cal_IT",  "calorie (International Table)",     "energy", "J", 4.1868)
_reg("kcal_th", "kilocalorie (thermochemical)",      "energy", "J", 4_184.0)
_reg("kcal_IT", "kilocalorie (International Table)", "energy", "J", 4_186.8)
# NIST SP811: cal_th = 4.184 J (exact); cal_IT = 4.1868 J

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
_reg("gal", "US gallon", "volume", "m3", 3.785_411_784e-3)
# NIST: 3.785 412 E-03 m3
_reg("qt",  "US quart",  "volume", "m3", 9.463_529_5e-4)
# NIST: 9.463 529 E-04 m3