class UnknownUnitError(KeyError):
    """Raised when a unit symbol is not found in the registry."""
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Unknown unit: '{symbol}'")

class IncompatibleUnitsError(TypeError):
    """Raised when two units have different physical dimensions."""
    def __init__(self, a, b):
        super().__init__(f"Incompatible units: '{a}' and '{b}'")

class DimensionError(TypeError):
    """Raised when a unit is used in a context that requires a different dimension."""
    def __init__(self, msg: str):
        super().__init__(msg)

class UnitParseError(ValueError):
    """Raised when a unit expression string cannot be parsed."""
    def __init__(self, expr: str, reason: str = ""):
        self.expr = expr
        msg = f"Cannot parse unit expression: '{expr}'"
        if reason:
            msg += f" — {reason}"
        super().__init__(msg)