# quantia

**Unit-aware arithmetic with Monte Carlo uncertainty propagation.**

Pure Python. No dependencies beyond the standard library.

---

quantia lets you write calculations the way engineers think —
with units attached to every value, and uncertainty tracked automatically.
```python
import quantia as qu

# Exact calculations
d = qu.Q(100.0, 'm')
t = qu.Q(9.81,  's')
v = d / t
v.to('km/h')   # UnitFloat(36.69..., 'km/h')

# Temperature — affine conversion handled automatically
qu.Q(100.0, '°C').to('K')   # UnitFloat(373.15, 'K')

# Gauge to absolute pressure
qu.Q(500.0, 'psig').to('psia')  # UnitFloat(514.69..., 'psia')

# Uncertainty propagation
with qu.config(n_samples=5000, seed=42):
    Bo  = qu.ProbUnitFloat.normal(1.25, 0.05, 'Sm3_res')
    phi = qu.ProbUnitFloat.triangular(0.12, 0.18, 0.25, '1')

Vp   = qu.Q(1_000_000.0, 'Sm3_res')
ooip = Vp * phi * 0.75 / (Bo / qu.Q(1.0, 'Sm3_st'))
lo, hi = ooip.interval(0.80)   # P10–P90
```
`
See [Getting Started](getting_started/installation.md) to install,
or jump to the [Five-Minute Tutorial](getting_started/tutorial.md).