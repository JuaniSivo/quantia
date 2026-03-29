# Five-Minute Tutorial

This tutorial covers the four types in quantia with real examples.
All code runs as-is after `pip install quantia`.
```python
import quantia as qu
```

## Exact scalars — UnitFloat

Every value carries its unit. Arithmetic checks dimensional
compatibility automatically.
```python
distance = qu.Q(100.0, 'm')
time     = qu.Q(10.0,  's')
velocity = distance / time     # UnitFloat(10.0, 'm/s')

velocity.to('km/h')            # UnitFloat(36.0, 'km/h')
velocity.si_value()            # 10.0  (plain float, in m/s)
```

Adding incompatible units raises immediately:
```python
qu.Q(1.0, 'm') + qu.Q(1.0, 's')   # → IncompatibleUnitsError
# IncompatibleUnitsError: Incompatible units: 'm' and 's'
```

Temperature uses the full affine conversion automatically:
```python
qu.Q(100.0, '°C').to('K')     # UnitFloat(373.15, 'K')
qu.Q(100.0, '°C').to('°F')    # UnitFloat(212.0, '°F')
```

Gauge and absolute pressure:
```python
qu.Q(0.0,   'psig').to('psia')   # UnitFloat(14.695..., 'psia')
qu.Q(100.0, 'psig').to('bara')   # UnitFloat(7.908...,  'bara')
```

## Exact arrays — UnitArray
```python
depths = qu.QA([1000.0, 1500.0, 2000.0], 'm')

depths.mean()            # UnitFloat(1500.0, 'm')
depths.to('ft')          # UnitArray([3280.8..., 4921.2..., 6561.7...], 'ft')

# Boolean mask filtering
deep = depths[depths > qu.Q(1200.0, 'm')]
# UnitArray([1500.0, 2000.0], 'm')
```

## Uncertain scalars — ProbUnitFloat

Use `qu.config()` to set the sample count and seed:
```python
with qu.config(n_samples=2000, seed=42):
    efficiency = qu.ProbUnitFloat.uniform(0.88, 0.95, "1")  # ProbUnitFloat(mean=0.9154, std=0.01999, unit='1', n=2000)
    power_in   = qu.ProbUnitFloat.normal(500.0, 10.0, "W")  # ProbUnitFloat(mean=500.1,  std=10.02,   unit='W', n=2000)

power_out = efficiency * power_in # ProbUnitFloat(mean=457.8, std=13.54, unit='W', n=2000

power_out.mean()                  # UnitFloat(457.76..., 'W')
power_out.std()                   # UnitFloat(13.54...,  'W')

# (lo, hi) 95% CI as UnitFloat tuple
power_out.interval(0.95)          # (UnitFloat(432.72...,'W'), UnitFloat(484.46..., 'W'))
power_out.percentile(10)          # UnitFloat(439.82..., 'W')
```

## Petroleum OOIP in 10 lines
```python
with qu.config(n_samples=5000, seed=0):
    phi = qu.ProbUnitFloat.triangular(0.12, 0.18, 0.25, '1')
    Sw  = qu.ProbUnitFloat.uniform(0.20, 0.35, '1')
    Bo  = qu.ProbUnitFloat.normal(1.25, 0.05, 'Sm3_res/Sm3_st')

Vp   = qu.Q(1_000_000.0, 'Sm3_res')   # 1 MMm3 pore volume
ooip = Vp * phi * (1 - Sw) / Bo

lo, hi = ooip.interval(0.80)           # P10–P90
print(f"OOIP P10: {lo.to('MMbbl'):.2f}")
print(f"OOIP P50: {ooip.percentile(50).to('MMbbl'):.2f}")
print(f"OOIP P90: {hi.to('MMbbl'):.2f}")
```

## Next steps

- [Choosing a Type](types.md) — when to use each of the four types
- [Gauge vs Absolute Pressure](../concepts/pressure.md) — the psig/psia design
- [Petroleum Units](../concepts/petroleum.md) — GOR and FVF with tagged units