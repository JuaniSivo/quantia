# scripts/gen_unit_tables.py
"""
Generate unit reference markdown tables from the live quantia registry.

Usage
-----
    python scripts/gen_unit_tables.py

Output is printed to stdout. Redirect to a file or copy-paste into
the relevant docs/reference/ page.

The script groups units by quantity and sorts alphabetically within
each group. AffineUnit entries are marked with a † symbol.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import quantia  # noqa — populates registry
from quantia._registry import _REGISTRY, AffineUnit

# ── Group by quantity ─────────────────────────────────────────────────────────
by_quantity: dict[str, list] = {}
for sym, unit in sorted(_REGISTRY.items()):
    q = unit.quantity
    by_quantity.setdefault(q, []).append((sym, unit))

# ── Print full table ──────────────────────────────────────────────────────────
print("# All Unit Symbols\n")
print("Complete list of every symbol registered in quantia, grouped by")
print("physical quantity. Use these exact strings in `qu.Q()`, `.to()`,")
print("and distribution factories.\n")
print("† Affine unit (has offset — temperature or gauge pressure).\n")

for quantity in sorted(by_quantity.keys()):
    units = by_quantity[quantity]
    title = quantity.replace("_", " ").title()
    print(f"## {title}\n")
    print("| Symbol | Name | SI unit | Factor to SI |")
    print("|--------|------|---------|-------------|")
    for sym, unit in sorted(units, key=lambda x: x[0].lower()):
        affine = "†" if isinstance(unit, AffineUnit) else ""
        factor = f"{unit.to_si:.6g}"
        print(f"| `{sym}` {affine} | {unit.name} | `{unit.si_unit}` | {factor} |")
    print()