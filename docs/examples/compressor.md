# Compressor Power

Estimating compressor power with uncertain efficiency and flow rate.
```python
import quantia as qu
import quantia.math as qmath

# Isentropic compressor power:
# W = Q × ΔP / η
# where Q = volumetric flow, ΔP = pressure rise, η = efficiency

with qu.config(n_samples=5000, seed=42):
    Q   = qu.ProbUnitFloat.normal(50.0, 3.0, 'm3/h')    # inlet flow
    eta = qu.ProbUnitFloat.uniform(0.72, 0.82, '1')     # isentropic efficiency

P_in  = qu.Q(1.0,  'bara')
P_out = qu.Q(10.0, 'bara')

# Pressure ratio (dimensionless)
# Note: absolute pressures for thermodynamic ratio
dP = P_out - P_in

# Power: Q [m3/s] × dP [Pa] = W [W]
power   = Q * dP / eta

print(f"Power P50: {power.mean().to_si():.1f}")
lo, hi = power.interval(0.80)
print(f"Power P10–P90: {lo.to_si():.1f} – {hi.to_si():.1f}")
```