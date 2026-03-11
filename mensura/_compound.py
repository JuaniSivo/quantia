from __future__ import annotations
import functools
from fractions import Fraction
from mensura._registry import _REGISTRY, get_unit, register, AffineUnit
from mensura._exceptions import UnknownUnitError, IncompatibleUnitsError, UnitParseError, DimensionError


# ── CompoundUnit ──────────────────────────────────────────────────────────────

class CompoundUnit:
    """
    A product of base units raised to rational exponents, with an optional
    semantic label that prevents dimensional cancellation.

    Internal storage: {symbol: Fraction(exponent)}

    The `label` field is used for semantic / tagged units (Phase 2e).
    When label is set, str() shows the label instead of the expanded form,
    and division between compatible-but-differently-labeled units does NOT
    cancel to dimensionless.

    Examples
    --------
    kg·m/s²          → {"kg":1, "m":1, "s":-2},  label=None
    Sm3_res/Sm3_st   → {"m3":1, "m3":-1} normally cancels,
                        but label="Sm3_res/Sm3_st" prevents that.
    """

    def __init__(self,
                 factors: dict[str, Fraction | int] | None = None,
                 label: str | None = None):
        self._f: dict[str, Fraction] = {
            s: Fraction(e)
            for s, e in (factors or {}).items()
            if e != 0
        }
        self._label = label

    # ── Factories ────────────────────────────────────────────────────────────

    @classmethod
    def from_symbol(cls, symbol: str) -> "CompoundUnit":
        get_unit(symbol)
        return cls({symbol: Fraction(1)})

    @classmethod
    def dimensionless(cls) -> "CompoundUnit":
        return cls({})

    @classmethod
    def labeled(cls, label: str, factors: dict[str, Fraction | int]) -> "CompoundUnit":
        """Create a semantically labeled compound unit that won't auto-cancel."""
        return cls(factors, label=label)

    # ── Algebra ──────────────────────────────────────────────────────────────

    def __mul__(self, other: "CompoundUnit") -> "CompoundUnit":
        m = dict(self._f)
        for s, e in other._f.items():
            m[s] = m.get(s, Fraction(0)) + e
        # Labels only survive if both operands share the same label
        label = self._label if self._label == other._label else None
        return CompoundUnit(m, label=label)

    def __truediv__(self, other: "CompoundUnit") -> "CompoundUnit":
        # 2e: if both have labels, produce a new labeled ratio instead of cancelling
        if self._label is not None and other._label is not None:
            new_label = f"{self._label}/{other._label}"
            m = dict(self._f)
            for s, e in other._f.items():
                m[s] = m.get(s, Fraction(0)) - e
            return CompoundUnit(m, label=new_label)
        m = dict(self._f)
        for s, e in other._f.items():
            m[s] = m.get(s, Fraction(0)) - e
        return CompoundUnit(m)

    def __pow__(self, exp) -> "CompoundUnit":
        e = Fraction(exp).limit_denominator(100)
        return CompoundUnit({s: f * e for s, f in self._f.items()}, label=self._label)

    def invert(self) -> "CompoundUnit":
        return CompoundUnit({s: -e for s, e in self._f.items()})

    # ── SI ───────────────────────────────────────────────────────────────────

    def si_factor(self) -> float:
        """Total multiplicative factor to convert to SI (offset units excluded)."""
        r = 1.0
        for s, e in self._f.items():
            u = get_unit(s)
            if isinstance(u, AffineUnit) and u.offset != 0.0:
                raise DimensionError(
                    f"Unit '{s}' has a non-zero offset and cannot be used "
                    "in compound unit expressions. Use UnitFloat.to() instead.")
            r *= u.to_si ** float(e)
        return r

    def to_si_compound(self) -> "CompoundUnit":
        m: dict[str, Fraction] = {}
        for s, e in self._f.items():
            si = get_unit(s).si_unit
            m[si] = m.get(si, Fraction(0)) + e
        return CompoundUnit(m)

    # ── Compatibility ─────────────────────────────────────────────────────────

    def is_compatible(self, other: "CompoundUnit") -> bool:
        return self.to_si_compound()._f == other.to_si_compound()._f

    def is_dimensionless(self) -> bool:
        # Labeled units are never considered dimensionless even if factors cancel
        if self._label:
            return False
        return not self._f

    def canonical_key(self) -> frozenset:
        return frozenset(self.to_si_compound()._f.items())

    # ── Display ──────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        if self._label:
            return self._label
        alias = _ALIASES.get(self.canonical_key())
        if alias:
            return alias
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

    def __repr__(self): return f"CompoundUnit({self._f!r}, label={self._label!r})"
    def __eq__(self, o): return isinstance(o, CompoundUnit) and self._f == o._f and self._label == o._label
    def __hash__(self): return hash((frozenset(self._f.items()), self._label))


# ── Alias registry ────────────────────────────────────────────────────────────

_ALIASES: dict[frozenset, str] = {}


def register_alias(display: str, compound_expr: str) -> None:
    _ALIASES[parse_unit(compound_expr).canonical_key()] = display


# ── 2e: Semantic / tagged unit registration ───────────────────────────────────

def register_tagged(symbol: str, base_symbol: str, tag: str) -> None:
    """
    Register a semantically tagged unit that shares the same SI dimensions
    as base_symbol but will not cancel when divided by another tagged unit.

    Example
    -------
    register_tagged("Sm3_res", "m3", "reservoir")
    register_tagged("Sm3_st",  "m3", "stock_tank")

    Q(100, "Sm3_res") / Q(1, "Sm3_st")
    → UnitFloat(100.0, 'Sm3_res/Sm3_st')   # does not cancel to 1
    """
    from mensura._registry import Unit
    base = get_unit(base_symbol)
    # Register a plain Unit with the same SI properties
    register(symbol, Unit(
        name     = f"{base.name} [{tag}]",
        quantity = f"{base.quantity}_{tag}",
        si_unit  = base.si_unit,
        to_si    = base.to_si,
        symbol   = symbol,
    ))
    # Mark its CompoundUnit as labeled so division won't cancel
    _TAGGED_LABELS[symbol] = tag


_TAGGED_LABELS: dict[str, str] = {}   # symbol → tag

_UNIT_CACHE: dict[str, CompoundUnit] = {}

def _make_unit(unit) -> CompoundUnit:
    """Coerce a str or CompoundUnit to CompoundUnit. Registry lookups are cached."""
    if isinstance(unit, CompoundUnit):
        return unit
    if isinstance(unit, str):
        cached = _UNIT_CACHE.get(unit)
        if cached is not None:
            return cached
        if unit in _REGISTRY:
            cu = CompoundUnit({unit: Fraction(1)},
                              label=unit if unit in _TAGGED_LABELS else None)
        else:
            cu = parse_unit(unit)
        _UNIT_CACHE[unit] = cu
        return cu
    raise TypeError(f"unit must be str or CompoundUnit, got {type(unit).__name__!r}")


# ── 2a: Proper tokenizer / parser ────────────────────────────────────────────

def _tokenize(expr: str) -> list[tuple[str, str]]:
    """
    Tokenize a unit expression into a list of (token_type, value) pairs.

    Token types
    -----------
    SYM    — a unit symbol, e.g. "kg", "m", "s"
    OP     — one of  ·  *  /  ^
    LPAREN — (
    RPAREN — )
    INT    — integer literal
    FRAC   — fraction literal "1/2" inside exponent parens
    """
    tokens = []
    i, n = 0, len(expr)

    while i < n:
        c = expr[i]

        if c in (' ', '\t'):
            i += 1
            continue

        if c in ('·', '*'):
            tokens.append(('OP', '*')); i += 1; continue

        if c == '/':
            tokens.append(('OP', '/')); i += 1; continue

        if c == '^':
            tokens.append(('OP', '^')); i += 1; continue

        if c == '(':
            tokens.append(('LPAREN', '(')); i += 1; continue

        if c == ')':
            tokens.append(('RPAREN', ')')); i += 1; continue

        # Number (integer or sign)
        if c.isdigit() or (c == '-' and i + 1 < n and expr[i+1].isdigit()):
            j = i + 1
            while j < n and expr[j].isdigit(): j += 1
            tokens.append(('INT', expr[i:j])); i = j; continue

        # Symbol: everything else up to a delimiter
        j = i
        while j < n and expr[j] not in ('·', '*', '/', '^', '(', ')', ' ', '\t'):
            j += 1
        if j == i:
            raise UnitParseError(expr, f"unexpected character '{c}' at position {i}")
        tokens.append(('SYM', expr[i:j])); i = j

    return tokens


@functools.lru_cache(maxsize=512)
def parse_unit(expr: str) -> CompoundUnit:
    """
    Parse a unit expression string into a CompoundUnit.

    Supports
    --------
    · or * — multiplication
    /       — division (chainable: kg/m/s = kg·m⁻¹·s⁻¹)
    ^       — exponentiation with integer, negative integer, or p/q fraction
    ()      — parentheses around exponents only

    Examples
    --------
    "kg·m/s^2"         → kg¹ m¹ s⁻²
    "kg/m^2/s"         → kg¹ m⁻² s⁻¹
    "m^(1/2)"          → m^½
    "m^-1"             → m⁻¹
    "kg·m^(2/3)/s^2·K" → kg¹ m^(2/3) s⁻² K⁻¹   (K in denominator because
                          the last · after s^2 is in the denominator context)
    """
    expr = expr.strip()
    if not expr:
        raise UnitParseError(expr, "empty expression")

    tokens = _tokenize(expr)
    pos    = [0]   # mutable pointer

    def peek() -> tuple[str, str] | None:
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume(expected_type: str | None = None) -> tuple[str, str]:
        tok = tokens[pos[0]]
        if expected_type and tok[0] != expected_type:
            raise UnitParseError(expr,
                f"expected {expected_type} but got {tok[0]}='{tok[1]}'")
        pos[0] += 1
        return tok

    def parse_exponent() -> Fraction:
        """
        Parse the exponent after ^.
        Handles:  2  -1  (2/3)  (-1/2)
        Bare integers (no parens) consume ONLY one INT token — never a '/'.
        Fractions require parens: ^(1/2), ^(-1/2).
        """
        nxt = peek()
        if nxt and nxt[0] == 'LPAREN':
            consume('LPAREN')
            parts = []
            while peek() and peek()[0] != 'RPAREN':
                parts.append(consume())
            consume('RPAREN')
            inner = "".join(v for _, v in parts)
            try:
                return Fraction(inner).limit_denominator(1000)
            except (ValueError, ZeroDivisionError):
                raise UnitParseError(expr, f"invalid exponent '({inner})'")
        elif nxt and nxt[0] == 'INT':
            # bare integer only — do NOT consume a following '/'
            _, val = consume('INT')
            return Fraction(int(val))
        else:
            raise UnitParseError(expr, "expected exponent after '^'")

    def parse_factor() -> CompoundUnit:
        """Parse a single symbol with optional exponent."""
        tok = peek()
        if tok is None:
            raise UnitParseError(expr, "unexpected end of expression")

        if tok[0] == 'SYM':
            _, sym = consume('SYM')
            get_unit(sym)   # validate — raises UnknownUnitError if missing
            label = sym if sym in _TAGGED_LABELS else None
            cu = CompoundUnit({sym: Fraction(1)}, label=label)
            if peek() == ('OP', '^'):
                consume('OP')
                exp = parse_exponent()
                cu  = CompoundUnit({sym: exp}, label=label)
            return cu

        if tok[0] == 'INT':
            _, val = consume('INT')
            if int(val) == 1:
                return CompoundUnit.dimensionless()
            raise UnitParseError(expr,
                f"bare integer '{val}' not allowed; use '1' for dimensionless")

        raise UnitParseError(expr, f"unexpected token {tok}")

    def parse_expr() -> CompoundUnit:
        """
        Parse a full expression respecting left-to-right * and / with
        equal precedence (standard unit expression convention).
        """
        result = parse_factor()

        while True:
            op = peek()
            if op is None or op[0] not in ('OP',):
                break
            if op[1] == '*':
                consume('OP')
                result = result * parse_factor()
            elif op[1] == '/':
                consume('OP')
                result = result / parse_factor()
            elif op[1] in ('^',):
                # ^ binds tighter and was already consumed in parse_factor
                break
            else:
                break

        return result

    result = parse_expr()
    if pos[0] != len(tokens):
        leftover = "".join(v for _, v in tokens[pos[0]:])
        raise UnitParseError(expr, f"unexpected trailing tokens: '{leftover}'")
    return result


# ── Bootstrapped aliases ──────────────────────────────────────────────────────

_PENDING_ALIASES: list[tuple[str, str]] = [
    ("J",  "N·m"),
    ("W",  "J/s"),
    ("N",  "kg·m/s^2"),
    ("Pa", "N/m^2"),
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