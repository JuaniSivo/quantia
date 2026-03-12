# quantia

A pure-Python library for **unit-aware arithmetic** with first-class support for **Monte Carlo uncertainty propagation**.

No numpy required. No dependencies beyond the standard library.

---

## Installation

```bash
pip install quantia
```

---

## The Four Types

| Type | Use when |
|------|----------|
| `UnitFloat` | exact scalar with a unit |
| `UnitArray` | exact vector with a unit |
| `ProbUnitFloat` | uncertain scalar (Monte Carlo samples) |
| `ProbUnitArray` | uncertain vector of the same quantity |

---

## Quick Start

### Exact scalars

```python
import quantia as qu

d = qu.Q(100.0, "m")
t = qu.Q(9.81,  "s")
v = d / t                        # UnitFloat(10.19…, 'm/s')

v.to("km/h")                     # unit conversion
v.to_si()                        # always works

qu.Q(100.0, "°C").to("K")        # UnitFloat(373.15, 'K')
qu.Q(100.0, "°C").to("°F")       # UnitFloat(212.0, '°F')
```

### Exact arrays

```python
heights = qu.QA([1.75, 1.80, 1.65], "m")

heights.mean()                   # UnitFloat(1.733…, 'm')
heights.sum()
heights.to("cm")

# Boolean mask filtering
tall = heights[heights > qu.Q(1.78, "m")]   # UnitArray([1.80], 'm')
```

### Uncertainty propagation

```python
with qu.config(n_samples=2000, seed=42):
    efficiency = qu.ProbUnitFloat.uniform(0.88, 0.95, "1")
    power_in   = qu.ProbUnitFloat.normal(500.0, 10.0, "W")

power_out = efficiency * power_in

power_out.mean()                 # UnitFloat(~457 W)
power_out.std()
power_out.interval(0.95)         # (lo, hi) 95% CI as UnitFloat tuple
power_out.percentile(10)
```

### Correlated inputs

When inputs are not independent, use a Gaussian copula:

```python
src = qu.CorrelatedSource(n_vars=2, rho=0.8)

x = src.draw(0, "normal",  "m",  mean=10,   std=1)
y = src.draw(1, "uniform", "s",  low=1,     high=3)

speed = x / y                    # ProbUnitFloat, correlated samples
```

Or pass a full correlation matrix:

```python
src = qu.CorrelatedSource(corr_matrix=[
    [1.0, 0.7, 0.4],
    [0.7, 1.0, 0.3],
    [0.4, 0.3, 1.0],
])
```

---

## Unit Expressions

quantia parses unit strings with a full tokenizer:

```python
qu.Q(9.81,  "m/s^2")
qu.Q(1.0,   "kg·m/s^2")          # · or * for multiplication
qu.Q(4.0,   "m^(1/2)")           # rational exponents
qu.Q(1.0,   "kg/m^2/s")          # chained division
```

### Built-in unit domains

| Domain | Examples |
|--------|---------|
| SI base | `m`, `kg`, `s`, `K`, `A`, `mol` |
| SI derived | `N`, `J`, `W`, `Pa`, `V`, `Ω`, `Hz` |
| Temperature | `°C`, `°F`, `K` |
| Imperial | `ft`, `lb`, `psi`, `BTU`, `hp`, `mph` |
| Petroleum | `bbl`, `Mbbl`, `psi_g`, `scf`, `Mscf`, `°API` |
| Data | `B`, `KB`, `MB`, `GB`, `TB`, `bit` |

### Semantic / tagged units

Dimensionally equal but semantically distinct units that won't cancel:

```python
from quantia import register_tagged

register_tagged("Sm3_res", "m3", "reservoir")
register_tagged("Sm3_st",  "m3", "stock_tank")

Rs = qu.Q(150.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")
# UnitFloat(150.0, 'Sm3_res/Sm3_st')  — does not reduce to 1
```

---

## Math Functions

`quantia.math` is a drop-in replacement for the stdlib `math` module that dispatches transparently on all four types:

```python
import quantia.math as mmath

mmath.log10(x)    # float, UnitFloat, ProbUnitFloat, UnitArray, ProbUnitArray
mmath.exp(x)
mmath.sqrt(x)     # preserves units: sqrt(m^2) → m
mmath.sin(x)      # requires angle unit on UnitFloat; raises DimensionError otherwise
mmath.cos(x)
mmath.atan2(y, x)
```

---

## Configuration

```python
with qu.config(n_samples=5000, seed=42):
    x = qu.ProbUnitFloat.normal(10.0, 1.0, "m")
    y = qu.ProbUnitFloat.uniform(0.0, 1.0, "s")
# config restored on exit; contexts nest cleanly
```

---

## Serialization

```python
# Save and load any quantia object
qu.save(power_out, "result.json")
result = qu.load("result.json")

# Dict round-trip
d   = power_out.to_dict()
pf2 = qu.from_dict(d)
```

### CSV export

```python
# UnitArray — single column of values
heights.to_csv("heights.csv")

# ProbUnitArray — mean, std, CI bounds per element
layer_thicknesses = qu.QPA([t1, t2, t3])   # must be same unit
layer_thicknesses.to_csv("stats.csv", confidence=0.90)
layer_thicknesses.samples_to_csv("raw.csv")
```

---

## Error Handling

quantia raises named exceptions from `quantia._exceptions`:

```python
from quantia import IncompatibleUnitsError, DimensionError, UnknownUnitError

qu.Q(1.0, "m") + qu.Q(1.0, "s")   # → IncompatibleUnitsError
mmath.sin(qu.Q(1.0, "m"))          # → DimensionError
qu.Q(1.0, "furlongs")              # → UnknownUnitError
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

56 tests covering scalar arithmetic, array operations, probabilistic math,
unit algebra invariants, serialization, and the config system.

---

## Benchmarks

```bash
python -m quantia.profiling.benchmark
python -m quantia.profiling.benchmark --profile   # cProfile detail at n=10k
python -m quantia.profiling.benchmark --n 10000   # single sample size
```

Typical throughput on a modern laptop (stdlib backend, no numpy):

| Operation | n=10k |
|-----------|-------|
| Scalar arithmetic chain | ~1ms |
| `ProbUnitFloat.normal` construction | ~4ms |
| `mean()` | ~0.1ms |
| `interval(0.95)` | ~0ms (cached sort) |
| Gaussian copula k=3 | ~33ms |

---

## License

MIT — see [LICENSE](LICENSE).