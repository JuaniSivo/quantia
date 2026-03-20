# Monte Carlo Uncertainty Propagation

When an input to a calculation is uncertain, the output is also
uncertain. quantia propagates uncertainty by running the same
calculation thousands of times — once per sample — and collecting
the distribution of outputs.

## How it works
```python
import quantia as qu

with qu.config(n_samples=5000, seed=42):
    efficiency = qu.ProbUnitFloat.uniform(0.88, 0.95, '1')
    power_in   = qu.ProbUnitFloat.normal(500.0, 10.0, 'W')

# Every arithmetic operation is applied sample-wise
power_out = efficiency * power_in   # 5000 output samples
```

Each sample of `power_out[i] = efficiency[i] × power_in[i]`.
The output distribution captures how uncertainty in both inputs
combines.

## Reading results
```python
power_out.mean()           # central estimate
power_out.std()            # spread
power_out.median()         # P50
power_out.interval(0.90)   # P5–P95 range
power_out.percentile(10)   # P10

# Full histogram
edges, counts = power_out.histogram(bins=20)
```

## Controlling sample count and reproducibility
```python
# More samples → more accurate statistics, slower calculation
with qu.config(n_samples=10_000, seed=0):
    x = qu.ProbUnitFloat.normal(100.0, 5.0, 'm')

# Contexts nest cleanly
with qu.config(n_samples=5000):
    with qu.config(n_samples=200):   # inner overrides outer
        y = qu.ProbUnitFloat.uniform(0.0, 1.0, '1')
    z = qu.ProbUnitFloat.normal(0.0, 1.0, '1')   # back to 5000
```

## Available distributions

| Factory | Parameters | Use when |
|---------|-----------|----------|
| `uniform(low, high)` | bounds | equal probability across range |
| `normal(mean, std)` | mean, std deviation | symmetric, bell-shaped |
| `triangular(low, mode, high)` | min, most-likely, max | expert judgment |
| `lognormal(mean, std)` | log-space mean, std | skewed, always positive |

## Units survive through uncertainty

Every `ProbUnitFloat` carries a unit. Arithmetic preserves and
combines units exactly as `UnitFloat` does:
```python
with qu.config(seed=1):
    force  = qu.ProbUnitFloat.normal(100.0, 5.0, 'N')
    length = qu.ProbUnitFloat.uniform(2.0, 4.0, 'm')

work = force * length    # ProbUnitFloat in 'J'
work.mean()              # UnitFloat(..., 'J')
```