# quantia — Quick Start

quantia is a pure-Python library for **unit-aware arithmetic** with first-class support
for Monte Carlo uncertainty propagation.

## Installation

pip install quantia

## The Four Types

| Type | Use when |
|------|----------|
| `UnitFloat`    | exact scalar with a unit |
| `UnitArray`    | exact vector with a unit |
| `ProbUnitFloat`| uncertain scalar (Monte Carlo samples) |
| `ProbUnitArray`| uncertain vector |

## Basic Usage
```python
import quantia as qu

# Exact scalars
d = qu.Q(100.0, "m")          # 100 m
t = qu.Q(9.81,  "s")

# Unit-safe arithmetic
v = d / t                     # UnitFloat(10.19…, 'm/s')
v.to("km/h")                  # convert

# Arrays
heights = qu.QA([1.75, 1.80, 1.65], "m")
heights.mean()                # UnitFloat(1.733…, 'm')

# Boolean mask
tall = heights[heights > qu.Q(1.78, "m")]

# Uncertainty (Monte Carlo)
with qu.config(n_samples=2000, seed=42):
    efficiency = qu.ProbUnitFloat.uniform(0.88, 0.95, "1")
    power_in   = qu.ProbUnitFloat.normal(500.0, 10.0, "W")

power_out = efficiency * power_in
power_out.mean()              # UnitFloat(~457 W)
power_out.interval(0.95)      # (lo, hi) 95 % CI
```

## Serialization
```python
qu.save(power_out, "result.json")
power_out2 = qu.load("result.json")

# Or dict round-trip
d = power_out.to_dict()
power_out3 = qu.from_dict(d)
```

## CSV Export
```python
# UnitArray
heights.to_csv("heights.csv")

# ProbUnitArray — means + stds + CIs
results = qu.QPA([power_out, power_in])
results.to_csv("summary.csv", confidence=0.90)
results.samples_to_csv("raw_samples.csv")
```

## Math Functions
```python
import quantia.math as mmath

angle = qu.Q(45.0, "deg")
mmath.sin(angle)              # dimensionless UnitFloat
mmath.sqrt(qu.Q(4.0, "m^2"))  # UnitFloat(2.0, 'm')
mmath.log10(efficiency)       # works on ProbUnitFloat too
```