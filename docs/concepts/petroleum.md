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
qu.Q(1.0, 'acre_ft').to('bbl')    # 7758.3... bbl
```

## Flow rate units
```python
qu.Q(10_000.0, 'bbl/day').to('m3/s')     # 0.01840... m3/s
qu.Q(50.0,     'MMscf/day').to('m3/h')   # 58993... m3/h
qu.Q(1.0,      'm3/h').to('bbl/day')     # 150.95... bbl/day

# BLPD is an alias for bbl/day
qu.Q(5000.0, 'BLPD').to('bbl/day')       # 5000.0 bbl/day
```

## API gravity

API gravity is a non-linear unit — it cannot be converted with a
simple scale factor. Use the dedicated functions:
```python
from quantia.petroleum_conversions import api_to_sg, sg_to_api

api_to_sg(10.0)    # UnitFloat(1.0, '1')       — water by definition
api_to_sg(35.0)    # UnitFloat(0.849..., '1')  — medium crude
sg_to_api(1.0)     # UnitFloat(10.0, '°API')
sg_to_api(0.85)    # UnitFloat(34.97..., '°API')

# Works with ProbUnitFloat too
with qu.config(seed=0, n_samples=3000):
    api = qu.ProbUnitFloat.normal(35.0, 3.0, '1')
sg = api_to_sg(api)   # ProbUnitFloat of SG values
sg
#  ProbUnitFloat(mean=0.8501, std=0.0157, unit='1', n=3000)
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
gor = gas / oil          # UnitFloat(150.0, '1') ← dimensionless, lost meaning

# With tags — units preserved
gas = qu.Q(150.0, 'm3_g_sep')
oil = qu.Q(1.0,   'm3_o_sep')
gor_sep = gas / oil      # UnitFloat(150.0, 'm3_g_sep/m3_o_sep') ← preserved
gor.si_value()           # 150.0  (both m3, ratio = 150

# Conversions
gor_sep.to("scf/bbl")    # UnitFloat(842.1875, 'scf/bbl')
gor_sep.to("scf/STB")    # UnitFloat(842.1875, 'scf/STB')
gor_sep.to("ft^3/STB")   # UnitFloat(842.1875, 'ft^3/STB')

Bo = qu.Q(1.1, "m3_res/m3_sc")
Bo                       # UnitFloat(1.1, 'm3_res/m3_sc')
Bo.to("RB/STB")          # UnitFloat(1.1, 'RB/STB')
```

### Available tagged units

| Symbol       | Base | Tag               | Typical use                  |
|--------------|------|-------------------|------------------------------|
| `m3_res` (1) | m3   | reservoir         | Reservoir pore/fluid volumes |
| `m3_sep` (1) | m3   | separator         | Separator fluid volumes      |
| `m3_sc`  (1) | m3   | standar condition | Stock-tank fluid volumes     |
| `cf_res` (2) | ft^3 | reservoir         | Reservoir gas volumes        |
| `cf_sep` (2) | ft^3 | separator         | Separator gas volumes        |
| `RB`         | bbl  | reservoir         | Reservoir liquid barrels     |
| `STB`        | bbl  | stock_tank        | Stock-tank liquid barrels    |
| `bbl_sep`    | bbl  | separator         | separator liquid barrels     |
| `Mcf_res`    | ft^3 | reservoir         | Reservoir gas volumes        |
| `Mcf_sep`    | ft^3 | separator         | Separator gas volumes        |

> [!NOTE]
> (1) It is also available in fluid-specific versions. Example: m3_o_res,
m3_g_res or m3_w_res.
> (2) cf_sc does not exist because it is covered by scf (standard cubic
foot).

### GOR conversion: scf/STB ↔ m3/m3

Tag-based conversion works automatically through SI factors:
```python
# 1000 scf/STB in SI units (m³/m³)
gor = qu.Q(1000.0, 'cf_res') / qu.Q(1.0, 'STB')
gor.si_value()   # 178.107...  (1000 × 0.3048³ / 0.158987...)
```

### FVF calculation
```python
Bo = qu.Q(1.2, 'RB/STB')
Bo.si_value()               # 1.2  (both barrels, ratio = 1.2)
Bo.unit.is_dimensionless()  # False  ← tag preserved
```

## OOIP calculation
```python
Vp  = qu.Q(1_000_000.0, 'm3_res')      # pore volume
Sw  = 0.25                             # water saturation
Bo  = qu.Q(1.2, 'm3_res/m3_sc')

ooip = Vp * (1 - Sw) / Bo              # UnitFloat(625000.0, 'm3_sc')
ooip.to('bbl')                         # UnitFloat(3931131..., 'bbl')
ooip.to('MMbbl')                       # UnitFloat(3.931..., 'MMbbl')
```

## Pressure

See [Gauge vs Absolute Pressure](pressure.md) for the full guide
on `psia`, `psig`, `bara`, `barg`, and `kg/cm2`.