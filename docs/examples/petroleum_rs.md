# Worked Example: Solution GOR (Rs) Correlation

The Standing correlation estimates solution gas-oil ratio from separator
conditions.  mensura propagates the uncertainty in stock-tank oil
specific gravity through the full expression in one pass.
```python
import mensura as ms
import mensura.math as mmath

# ── Correlation constants (Standing 1947) ───────────────────────────────────
a1, a2, a3, a4, a5 = 0.3818, -5.506, 2.902, 1.327, -0.7355

# ── Known exact inputs ───────────────────────────────────────────────────────
SG_g = 0.65                           # gas specific gravity (exact)
Tsp  = ms.Q(10.0, "°C").to("°F")    # separator temperature
Psp  = ms.Q(1.0, "atm").to("psi")   # separator pressure

# ── Uncertain input ──────────────────────────────────────────────────────────
with ms.config(n_samples=5000, seed=42):
    SG_o = ms.ProbUnitFloat.uniform(0.92, 0.96, "1")

# ── Correlation ──────────────────────────────────────────────────────────────
import math
log_Rst = (a1
         + a2 * mmath.log10(SG_o)
         + a3 * math.log10(SG_g)
         + a4 * math.log10(Psp.value)
         + a5 * math.log10(Tsp.value))

Rst = mmath.exp(log_Rst)   # ProbUnitFloat, dimensionless

# ── Results ──────────────────────────────────────────────────────────────────
print(f"Rs  mean : {Rst.mean():.4g}")
lo, hi = Rst.interval(0.95)
print(f"95% CI   : [{lo:.4g}, {hi:.4g}]")

# ── Save ─────────────────────────────────────────────────────────────────────
ms.save(Rst, "Rs_result.json")
```