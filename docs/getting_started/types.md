# Choosing a Type

quantia has four types. The choice depends on whether your value is
scalar or vector, and whether it is exact or uncertain.

|  | Scalar | Vector |
|--|--------|--------|
| **Exact** | `UnitFloat` | `UnitArray` |
| **Uncertain** | `ProbUnitFloat` | `ProbUnitArray` |

## UnitFloat — exact scalar

Use when you have one value that is known precisely:
```python
reservoir_pressure = qu.Q(3500.0, 'psia')
depth              = qu.Q(2450.0, 'm')
temperature        = qu.Q(95.0,   '°C')
```

## UnitArray — exact vector

Use when you have a list of measurements all in the same unit:
```python
layer_depths      = qu.QA([1200.0, 1450.0, 1700.0], 'm')
permeabilities    = qu.QA([12.5, 8.3, 45.2], 'mD')
```

## ProbUnitFloat — uncertain scalar

Use when a value has uncertainty that should propagate through
calculations. Internally stores Monte Carlo samples.
```python
with qu.config(n_samples=3000):
    porosity = qu.ProbUnitFloat.triangular(0.12, 0.18, 0.25, '1')
    Bo       = qu.ProbUnitFloat.normal(1.25, 0.05, 'Sm3_res')
```

## ProbUnitArray — uncertain vector

Use when you have multiple uncertain values of the same quantity,
for example a set of layer thicknesses each with their own uncertainty:
```python
with qu.config(n_samples=2000):
    layers = qu.QPA([
        qu.ProbUnitFloat.triangular(8.0,  12.0, 18.0, 'm'),
        qu.ProbUnitFloat.triangular(5.0,   8.0, 14.0, 'm'),
        qu.ProbUnitFloat.triangular(15.0, 20.0, 28.0, 'm'),
    ])

layers.means()       # UnitArray of mean thicknesses
layers.intervals()   # list of (P2.5, P97.5) tuples
```

## Mixing types

Exact values can be combined with uncertain values freely.
The result is always uncertain:
```python
Vp       = qu.Q(1_000_000.0, 'Sm3_res')    # exact
porosity = qu.ProbUnitFloat.uniform(...)   # uncertain
Vp_pore  = Vp * porosity                   # → ProbUnitFloat
```