# Worked Example: Correlated Inputs with a Gaussian Copula

When input variables are correlated (e.g. formation thickness and
porosity tend to move together), independent sampling underestimates
the spread of the output.  `CorrelatedSource` handles this.
```python
import quantia as qu

# Correlation matrix: 3 variables, moderate positive correlation
corr = [
    [1.0, 0.7, 0.4],
    [0.7, 1.0, 0.3],
    [0.4, 0.3, 1.0],
]

with qu.config(n_samples=3000, seed=0):
    src       = qu.CorrelatedSource(corr_matrix=corr)
    thickness = src.draw(0, "triangular", "m",  low=10, mode=15, high=22)
    porosity  = src.draw(1, "normal",     "1",  mean=0.18, std=0.02)
    Sw        = src.draw(2, "uniform",    "1",  low=0.15, high=0.35)

# Hydrocarbon pore volume (simplified)
area   = qu.Q(1_000_000.0, "m^2")
Vp     = area * thickness * porosity
Vhc    = Vp * (1 - Sw)

print(f"Vhc mean : {Vhc.mean().to('m^3'):.4g}")
lo, hi = Vhc.interval(0.90)
print(f"90% CI   : [{lo.to('m^3'):.4g}, {hi.to('m^3'):.4g}]")

# Export results
qu.save(Vhc, "Vhc_result.json")
```

The key difference from independent sampling is that `thickness` and
`porosity` are drawn from a joint distribution that respects ρ = 0.7 —
high-thickness samples are more likely to be paired with high-porosity
samples, widening the tail of `Vhc`.