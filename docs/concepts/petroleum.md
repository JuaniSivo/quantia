# Petroleum Units

quantia includes a comprehensive petroleum unit set designed for
reservoir and production engineering calculations.

## Volume units
```python
import quantia as qu

# Liquid volumes
qu.Q(1.0, 'bbl').to('L')          # 158.987... L
qu.Q(1.0, 'bbl').to('gal')        # 42.0 gal (exact)

# Gas volumes at standard conditions
qu.Q(1.0, 'Mscf').to('scf')       # 1000.0 scf (exact)
qu.Q(1.0, 'MMscf').to('m3')       # 28316.8... m3
qu.Q(1.0, 'Bscf').to('MMscf')     # 1000.0 MMscf (exact)

# Reservoir volume
qu.Q(1.0, 'acre_ft').to('bbl')    # 7758.4... bbl
```

## Flow rate units
```python
qu.Q(10_000.0, 'bbl/day').to('m3/s')     # 0.01840... m3/s
qu.Q(50.0,     'MMscf/day').to('m3/h')   # 59099... m3/h
qu.Q(1.0,      'm3/h').to('bbl/day')     # 150.96... bbl/day

# BLPD is an alias for bbl/day
qu.Q(5000.0, 'BLPD').to('bbl/day')       # 5000.0 bbl/day
```

## API gravity

API gravity is a non-linear unit — it cannot be converted with a
simple scale factor. Use the dedicated functions:
```python
from quantia.petroleum_conversions import api_to_sg, sg_to_api

api_to_sg(10.0)    # 1.0  — water by definition
api_to_sg(35.0)    # 0.8498...  — medium crude
sg_to_api(1.0)     # 10.0
sg_to_api(0.85)    # 35.03...

# Works with ProbUnitFloat too
with qu.config(seed=0, n_samples=3000):
    api = qu.ProbUnitFloat.normal(35.0, 3.0, '1')
sg = api_to_sg(api)   # ProbUnitFloat of SG values
```

## Tagged units — GOR and FVF

Gas-oil ratio (GOR) and formation volume factor (FVF) are
volume-over-volume quantities. Without tagging, the units cancel
to dimensionless and the result loses its physical meaning.

quantia uses **tagged units** that share SI dimensions with their
base unit but do not cancel when divided by a differently tagged unit:
```python
# Without tags — units cancel, result is meaningless
gas = qu.Q(150.0, 'm3')
oil = qu.Q(1.0,   'm3')
gor = gas / oil          # UnitFloat(150.0, '1')  ← dimensionless, lost meaning

# With tags — units preserved
gas = qu.Q(150.0, 'Sm3_res')
oil = qu.Q(1.0,   'Sm3_st')
gor = gas / oil          # UnitFloat(150.0, 'Sm3_res/Sm3_st')  ← preserved
gor.si_value()           # 150.0  (both m3, ratio = 150)
```

### Available tagged units

| Symbol | Base | Tag | Typical use |
|--------|------|-----|-------------|
| `Sm3_res` | m3 | reservoir | Reservoir pore/fluid volumes |
| `Sm3_st` | m3 | stock_tank | Stock-tank oil volumes |
| `scf_res` | scf | reservoir | Reservoir gas volumes |
| `scf_st` | scf | stock_tank | Stock-tank gas volumes |
| `STB` | bbl | stock_tank | Stock-tank barrels |
| `RB` | bbl | reservoir | Reservoir barrels |
| `Mscf_res` | Mscf | reservoir | Reservoir Mscf volumes |
| `Mscf_st` | Mscf | stock_tank | Stock-tank Mscf volumes |

### GOR conversion: scf/STB ↔ Sm3/Sm3

Tag-based conversion works automatically through SI factors:
```python
# 1000 scf/STB in SI units (m³/m³)
gor = qu.Q(1000.0, 'scf_res') / qu.Q(1.0, 'STB')
gor.si_value()   # 178.107...  (1000 × 0.3048³ / 0.158987...)
```

### FVF calculation
```python
Bo = qu.Q(1.2, 'RB') / qu.Q(1.0, 'STB')
Bo.si_value()           # 1.2  (both barrels, ratio = 1.2)
Bo.unit.is_dimensionless()  # False  ← tag preserved
```

## OOIP calculation
```python
Vp  = qu.Q(1_000_000.0, 'Sm3_res')   # pore volume
Sw  = 0.25                             # water saturation
Bo  = qu.Q(1.2, 'Sm3_res') / qu.Q(1.0, 'Sm3_st')

ooip = Vp * (1 - Sw) / Bo
ooip.to('bbl')    # UnitFloat(3_931_595..., 'bbl')
ooip.to('MMbbl')  # UnitFloat(3.931..., 'MMbbl')
```

## Pressure

See [Gauge vs Absolute Pressure](pressure.md) for the full guide
on `psia`, `psig`, `bara`, `barg`, and `kg/cm2`.