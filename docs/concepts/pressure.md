# Gauge vs Absolute Pressure

Pressure is the most common source of unit errors in petroleum
engineering. quantia handles gauge and absolute pressure the same way
it handles temperature — via an **affine unit** that carries both a
scale factor and an offset.

## The problem

A gauge pressure reading of 0 psig does not mean "no pressure" —
it means atmospheric pressure. The relationship is:

$$P_{absolute} = P_{gauge} \times scale + P_{atm}$$

where $P_{atm}$ = 101 325 Pa (standard atmosphere, exact).

This is mathematically identical to the Celsius → Kelvin conversion:

$$T_K = T_{°C} \times 1 + 273.15$$

quantia uses the same `AffineUnit` mechanism for both.

## The four pressure units

| Symbol | Type | Offset | Use when |
|--------|------|--------|----------|
| `psia` | absolute | 0 Pa | reservoir pressure, PVT calculations |
| `psig` | gauge | 101 325 Pa | wellhead, separator, surface readings |
| `bara` | absolute | 0 Pa | SI-adjacent absolute |
| `barg` | gauge | 101 325 Pa | European gauge readings |

## Converting between them
```python
import quantia as qu

# 0 psig is always 1 atm absolute
qu.Q(0.0, 'psig').to('psia')    # UnitFloat(14.695..., 'psia')
qu.Q(0.0, 'psig').to('Pa')      # UnitFloat(101325.0, 'Pa')

# Typical wellhead pressure
qu.Q(500.0, 'psig').to('psia')  # UnitFloat(514.695..., 'psia')
qu.Q(500.0, 'psig').to('bara')  # UnitFloat(35.47...,   'bara')

# Reservoir pressure in various units
qu.Q(3500.0, 'psia').to('MPa')  # UnitFloat(24.13..., 'MPa')
qu.Q(3500.0, 'psia').to('barg') # UnitFloat(240.6..., 'barg')
```

## Ambiguous `psi` and `bar`

Using plain `psi` or `bar` emits a `UserWarning` and is treated
as absolute. Always use `psia`/`psig` or `bara`/`barg` explicitly:
```python
qu.Q(100.0, 'psi')   # ⚠ UserWarning: treated as psia
qu.Q(100.0, 'psia')  # ✓ no warning
qu.Q(100.0, 'psig')  # ✓ no warning
```

## Legacy field unit: `kg/cm²`

Common in Latin America and older literature. quantia registers
both spellings:
```python
qu.Q(100.0, 'kg/cm2').to('psia')   # UnitFloat(1422.3..., 'psia')
qu.Q(100.0, 'kgf/cm2').to('bara')  # UnitFloat(98.07...,  'bara')
```

## Gauge pressure in compound expressions

Gauge pressure cannot be used in compound expressions because
the offset is non-linear when multiplied. quantia raises a
`DimensionError` to prevent silent errors:
```python
# This raises DimensionError — offset pressure × length is undefined
qu.Q(100.0, 'psig') * qu.Q(1.0, 'm')   # → DimensionError on .si_value()

# Correct approach: convert to absolute first
p_abs = qu.Q(100.0, 'psig').to('psia')
p_abs * qu.Q(1.0, 'm')                  # ✓ works
```

## Uncertain pressure

`ProbUnitFloat` handles gauge pressure the same way:
```python
with qu.config(seed=42, n_samples=3000):
    p_wh = qu.ProbUnitFloat.normal(500.0, 20.0, 'psig')

p_wh.to('psia').mean()   # ≈ UnitFloat(514.7, 'psia')
p_wh.to('bara').interval(0.90)
```