from __future__ import annotations
from fractions import Fraction
from mensura._registry import _REGISTRY, get_unit, register
from mensura._exceptions import UnknownUnitError, IncompatibleUnitsError


_SI_BASES = frozenset({"m", "kg", "s", "A", "K", "mol", "cd", "1"})

_DERIVED_DECOMPOSITION: dict[str, dict] = {}

def _register_decomposition(symbol: str, factors: dict) -> None:
    from fractions import Fraction
    _DERIVED_DECOMPOSITION[symbol] = {s: Fraction(e) for s, e in factors.items()}


class CompoundUnit:
    """
    A product of base units raised to rational exponents.

    Internally stored as {symbol: Fraction(exponent)}.
    Zero-exponent entries are always dropped.

    Examples
    --------
    kg·m/s²  →  {"kg": Fraction(1), "m": Fraction(1), "s": Fraction(-2)}
    """

    def __init__(self, factors: dict[str, Fraction | int] | None = None):
        self._f: dict[str, Fraction] = {
            s: Fraction(e)
            for s, e in (factors or {}).items()
            if e != 0
        }

    # ── Factories ────────────────────────────────────────────────────────────

    @classmethod
    def from_symbol(cls, symbol: str) -> "CompoundUnit":
        get_unit(symbol)          # validates; raises UnknownUnitError if missing
        return cls({symbol: Fraction(1)})

    @classmethod
    def dimensionless(cls) -> "CompoundUnit":
        return cls({})

    # ── Algebra ──────────────────────────────────────────────────────────────

    def __mul__(self, other: "CompoundUnit") -> "CompoundUnit":
        m = dict(self._f)
        for s, e in other._f.items():
            m[s] = m.get(s, Fraction(0)) + e
        return CompoundUnit(m)

    def __truediv__(self, other: "CompoundUnit") -> "CompoundUnit":
        m = dict(self._f)
        for s, e in other._f.items():
            m[s] = m.get(s, Fraction(0)) - e
        return CompoundUnit(m)

    def __pow__(self, exp: int | float | Fraction) -> "CompoundUnit":
        e = Fraction(exp).limit_denominator(100)
        return CompoundUnit({s: f * e for s, f in self._f.items()})

    def invert(self) -> "CompoundUnit":
        return CompoundUnit({s: -e for s, e in self._f.items()})

    # ── SI ───────────────────────────────────────────────────────────────────

    def si_factor(self) -> float:
        """Total multiplicative factor to convert to SI."""
        r = 1.0
        for s, e in self._f.items():
            u = get_unit(s)
            if u.quantity == "temperature":
                raise DimensionError(
                    "Temperature units cannot appear in compound units. "
                    "Use UnitFloat.to() for temperature conversion.")
            r *= u.to_si ** float(e)
        return r
    
    def to_si_compound(self) -> "CompoundUnit":
        result: dict[str, Fraction] = {}

        def resolve(sym: str, exp: Fraction) -> None:
            if sym in _SI_BASES:
                result[sym] = result.get(sym, Fraction(0)) + exp
                return
            if sym in _DERIVED_DECOMPOSITION:
                for base_sym, base_exp in _DERIVED_DECOMPOSITION[sym].items():
                    result[base_sym] = result.get(base_sym, Fraction(0)) + exp * base_exp
                return
            si_sym = get_unit(sym).si_unit
            if si_sym == sym or si_sym in _SI_BASES:
                result[si_sym] = result.get(si_sym, Fraction(0)) + exp
            else:
                resolve(si_sym, exp)

        for s, e in self._f.items():
            resolve(s, e)

        return CompoundUnit(result)

    # ── Compatibility ─────────────────────────────────────────────────────────

    def is_compatible(self, other: "CompoundUnit") -> bool:
        return self.to_si_compound()._f == other.to_si_compound()._f

    def is_dimensionless(self) -> bool:
        return not self._f

    def canonical_key(self) -> frozenset:
        """Physical fingerprint — used for alias lookup."""
        return frozenset(self.to_si_compound()._f.items())

    # ── Display ──────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        # If the unit is a single factor with exponent 1 and that symbol is
        # directly registered, display it as-is — never let the alias table
        # override an explicit named unit like "kPa", "bar", "psi".
        if len(self._f) == 1:
            sym, exp = next(iter(self._f.items()))
            if exp == Fraction(1) and sym in _REGISTRY:
                return sym

        # For compound results (from arithmetic), check alias table so that
        # e.g. kg·m/s² displays as "N" and N·m displays as "J".
        alias = _ALIASES.get(self.canonical_key())
        if alias:
            return alias

        # Fallback: build the expression string
        if not self._f:
            return "1"
        num = sorted((s, e)  for s, e in self._f.items() if e > 0)
        den = sorted((s, -e) for s, e in self._f.items() if e < 0)

        def fmt(parts: list) -> str:
            tokens = []
            for s, e in parts:
                if e == 1:
                    tokens.append(s)
                elif e.denominator == 1:
                    tokens.append(f"{s}^{e.numerator}")
                else:
                    tokens.append(f"{s}^({e})")
            return "·".join(tokens)

        n = fmt(num) or "1"
        return f"{n}/{fmt(den)}" if den else n

    def __repr__(self): return f"CompoundUnit({self._f!r})"
    def __eq__(self, o): return isinstance(o, CompoundUnit) and self._f == o._f
    def __hash__(self): return hash(frozenset(self._f.items()))


# ── Alias registry ────────────────────────────────────────────────────────────

_ALIASES: dict[frozenset, str] = {}


def register_alias(display: str, compound_expr: str) -> None:
    """
    Register a display name for a compound unit fingerprint.
    E.g. register_alias("J", "N·m")
    """
    _ALIASES[parse_unit(compound_expr).canonical_key()] = display


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_unit(expr: str) -> CompoundUnit:
    """
    Parse a unit expression string into a CompoundUnit.

    Supports:
      · or * for multiplication
      /  splits numerator and denominator (first occurrence)
      ^  for integer or fractional exponents, e.g. m^2, kg^(1/2)

    Examples
    --------
    parse_unit("kg·m/s^2")   →  CompoundUnit({"kg":1, "m":1, "s":-2})
    parse_unit("m^(1/2)")    →  CompoundUnit({"m": Fraction(1,2)})
    """
    expr = expr.strip()
    num_str, den_str = expr.split("/", 1) if "/" in expr else (expr, "")

    def parse_part(s: str) -> CompoundUnit:
        if not s or s == "1":
            return CompoundUnit.dimensionless()
        cu = CompoundUnit.dimensionless()
        for tok in s.replace("*", "·").split("·"):
            tok = tok.strip()
            if not tok or tok == "1":
                continue
            if "^" in tok:
                sym, es = tok.split("^", 1)
                exp = Fraction(es.strip("()")).limit_denominator(100)
            else:
                sym, exp = tok, Fraction(1)
            sym = sym.strip()
            get_unit(sym)   # validate
            cu = cu * CompoundUnit({sym: exp})
        return cu

    result = parse_part(num_str)
    if den_str:
        result = result / parse_part(den_str)
    return result


def _make_unit(unit) -> CompoundUnit:
    """Coerce a str or CompoundUnit to CompoundUnit."""
    if isinstance(unit, CompoundUnit):
        return unit
    if isinstance(unit, str):
        return CompoundUnit.from_symbol(unit) if unit in _REGISTRY else parse_unit(unit)
    raise TypeError(f"unit must be str or CompoundUnit, got {type(unit).__name__!r}")


# ── Bootstrapped aliases (populated by units/__init__.py) ─────────────────────

_PENDING_ALIASES: list[tuple[str, str]] = [
    ("J",  "N·m"),
    ("W",  "J/s"),
    ("N",  "kg·m/s^2"),
    ("Pa", "N/m^2"),
    ("Pa", "kg/m·s^2"),
    ("V",  "W/A"),
    ("Ω",  "V/A"),
    ("Hz", "1/s"),
]


def _bootstrap_aliases() -> None:
    for display, expr in _PENDING_ALIASES:
        try:
            register_alias(display, expr)
        except Exception:
            pass