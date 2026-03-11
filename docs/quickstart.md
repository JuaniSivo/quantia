# mensura — Quick Start

mensura is a pure-Python library for **unit-aware arithmetic** with first-class support
for Monte Carlo uncertainty propagation.

## Installation

pip install mensura

## The Four Types

| Type | Use when |
|------|----------|
| `UnitFloat`    | exact scalar with a unit |
| `UnitArray`    | exact vector with a unit |
| `ProbUnitFloat`| uncertain scalar (Monte Carlo samples) |
| `ProbUnitArray`| uncertain vector |

## Basic Usage
```python
import mensura as ms

# Exact scalars
d = ms.Q(100.0, "m")          # 100 m
t = ms.Q(9.81,  "s")

# Unit-safe arithmetic
v = d / t                     # UnitFloat(10.19…, 'm/s')
v.to("km/h")                  # convert

# Arrays
heights = ms.QA([1.75, 1.80, 1.65], "m")
heights.mean()                # UnitFloat(1.733…, 'm')

# Boolean mask
tall = heights[heights > ms.Q(1.78, "m")]

# Uncertainty (Monte Carlo)
with ms.config(n_samples=2000, seed=42):
    efficiency = ms.ProbUnitFloat.uniform(0.88, 0.95, "1")
    power_in   = ms.ProbUnitFloat.normal(500.0, 10.0, "W")

power_out = efficiency * power_in
power_out.mean()              # UnitFloat(~457 W)
power_out.interval(0.95)      # (lo, hi) 95 % CI
```

## Serialization
```python
ms.save(power_out, "result.json")
power_out2 = ms.load("result.json")

# Or dict round-trip
d = power_out.to_dict()
power_out3 = ms.from_dict(d)
```

## CSV Export
```python
# UnitArray
heights.to_csv("heights.csv")

# ProbUnitArray — means + stds + CIs
results = ms.QPA([power_out, efficiency])
results.to_csv("summary.csv", confidence=0.90)
results.samples_to_csv("raw_samples.csv")
```

## Math Functions
```python
import mensura.math as mmath

angle = ms.Q(45.0, "deg")
mmath.sin(angle)              # dimensionless UnitFloat
mmath.sqrt(ms.Q(4.0, "m^2")) # UnitFloat(2.0, 'm')
mmath.log10(efficiency)       # works on ProbUnitFloat too
```