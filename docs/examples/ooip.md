# OOIP Calculation

Probabilistic oil originally in place using the volumetric equation
with uncertain porosity, water saturation, and formation volume factor.

## Deterministic baseline
```python
import quantia as qu

Vp  = qu.Q(1_000_000.0, 'Sm3_res')  # pore volume
Sw  = 0.25                            # water saturation
Bo  = qu.Q(1.2, 'Sm3_res') / qu.Q(1.0, 'Sm3_st')

ooip = Vp * (1 - Sw) / Bo
print(f"OOIP: {ooip.to('MMbbl'):.2f}")   # 3.93 MMbbl
```

## Probabilistic — independent inputs
```python
with qu.config(n_samples=5000, seed=42):
    phi = qu.ProbUnitFloat.triangular(0.12, 0.18, 0.25, '1')
    Sw  = qu.ProbUnitFloat.triangular(0.20, 0.28, 0.35, '1')
    Bo  = qu.ProbUnitFloat.normal(1.25, 0.05, 'Sm3_res')

A  = qu.Q(3_000_000.0, 'm2')     # 3 km²
h  = qu.Q(18.0, 'm')

Vp_r = qu.Q(A.value * h.value, 'Sm3_res') * phi
ooip = Vp_r * (1 - Sw) / (Bo / qu.Q(1.0, 'Sm3_st'))

lo, mid, hi = (ooip.percentile(p).to('MMbbl') for p in [10, 50, 90])
print(f"P10: {lo:.2f}  P50: {mid:.2f}  P90: {hi:.2f}")
```

## Probabilistic — correlated inputs

Porosity and Bo are positively correlated (better rock holds
lighter, more expandable oil):
```python
with qu.config(n_samples=5000, seed=0):
    src = qu.CorrelatedSource(n_vars=2, rho=0.6)
    phi = src.draw(0, 'triangular', '1',      low=0.12, mode=0.18, high=0.25)
    Bo  = src.draw(1, 'normal',     'Sm3_res', mean=1.25, std=0.05)

Sw   = 0.25
Vp_r = qu.Q(3_000_000.0 * 18.0, 'Sm3_res') * phi
ooip = Vp_r * (1 - Sw) / (Bo / qu.Q(1.0, 'Sm3_st'))

lo, hi = ooip.interval(0.80)
print(f"P10–P90: {lo.to('MMbbl'):.2f} – {hi.to('MMbbl'):.2f}")
```