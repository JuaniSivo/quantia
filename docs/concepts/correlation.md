# Correlated Inputs

By default, separate `ProbUnitFloat` instances are statistically
independent — high samples in one do not tend to coincide with
high samples in another. When inputs are correlated in reality,
independent sampling underestimates the spread of the output.

## When correlation matters

In a reservoir, porosity and net-to-gross tend to move together —
thick, high-quality intervals tend to have higher porosity. If you
sample them independently, you miss scenarios where both are
simultaneously high (optimistic) or simultaneously low (pessimistic).

## Using CorrelatedSource
```python
import quantia as qu

with qu.config(n_samples=3000, seed=0):
    src = qu.CorrelatedSource(n_vars=2, rho=0.7)

    phi = src.draw(0, 'triangular', '1',  low=0.12, mode=0.18, high=0.25)
    ntg = src.draw(1, 'uniform',    '1',  low=0.60, high=0.90)
```

`rho=0.7` means a Pearson correlation of 0.7 between `phi` and `ntg`.
High porosity samples are more likely to coincide with high NTG samples.

## Full correlation matrix

For three or more variables with different pairwise correlations:
```python
with qu.config(n_samples=3000, seed=0):
    src = qu.CorrelatedSource(corr_matrix=[
        [1.0, 0.7, 0.4],
        [0.7, 1.0, 0.3],
        [0.4, 0.3, 1.0],
    ])
    thickness = src.draw(0, 'triangular', 'm',  low=10, mode=15, high=22)
    porosity  = src.draw(1, 'normal',     '1',  mean=0.18, std=0.02)
    Sw        = src.draw(2, 'uniform',    '1',  low=0.15,  high=0.35)
```

The matrix must be:

- Square and symmetric
- Ones on the diagonal
- Positive definite (all eigenvalues > 0)

## Each slot is drawn once

`CorrelatedSource` generates all samples upfront. Each slot (variable)
can only be drawn once — drawing the same slot twice raises `RuntimeError`:
```python
x = src.draw(0, 'normal', 'm', mean=10, std=1)
x = src.draw(0, 'normal', 'm', mean=10, std=1)   # → RuntimeError
```