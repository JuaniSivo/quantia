# Solution GOR

Calculating gas-oil ratio and converting between unit systems.

## Building GOR from tagged units
```python
import quantia as qu

# scf/STB
gas = qu.Q(1000.0, 'scf_res')
oil = qu.Q(1.0,    'STB')
gor = gas / oil

print(gor.si_value())   # 178.107...  m³/m³
```

## Converting GOR between unit systems

The SI value is the universal exchange rate:
```python
# 1000 scf/STB expressed as Sm3/Sm3
gor_si = gor.si_value()       # 178.107 m³/m³

# To express as Sm3/Sm3: SI value is already in m³/m³
# So 1000 scf/STB = 178.1 Sm3/Sm3

# Verify: build same GOR in Sm3 units
gas_sm3 = qu.Q(1000.0 * 0.3048**3, 'Sm3_res')   # convert scf → m3
oil_sm3 = qu.Q(0.158987294928,      'Sm3_st')    # 1 STB in m3
gor_sm3 = gas_sm3 / oil_sm3
print(gor_sm3.si_value())   # 178.107... ✓
```

## Probabilistic GOR
```python
with qu.config(seed=1, n_samples=3000):
    gas = qu.ProbUnitFloat.triangular(800.0, 1000.0, 1300.0, 'scf_res')

oil = qu.Q(1.0, 'STB')
gor = gas / oil

print(f"GOR P50: {gor.percentile(50).si_value():.1f} Sm3/Sm3")
lo, hi = gor.interval(0.80)
print(f"GOR P10–P90: {lo.si_value():.1f} – {hi.si_value():.1f} Sm3/Sm3")
```