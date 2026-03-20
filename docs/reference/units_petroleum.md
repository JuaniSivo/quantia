# Petroleum Units

Sources: API Manual of Petroleum Measurement Standards (MPMS) Chapter 11,
SPE nomenclature conventions.

## Tagged Units

The following units are *semantically tagged* — they share SI dimensions
with their base unit but will **not cancel** when divided by a differently
tagged unit. Use them to build GOR and FVF ratios that preserve
petroleum meaning through calculations.

| Symbol | Base | Tag | Use for |
|--------|------|-----|---------|
| `Sm3_res` | `m3` | reservoir | Reservoir pore/fluid volumes |
| `Sm3_st` | `m3` | stock_tank | Stock-tank oil volumes |
| `scf_res` | `scf` | reservoir | Reservoir gas volumes |
| `scf_st` | `scf` | stock_tank | Stock-tank gas volumes |
| `STB` | `bbl` | stock_tank | Stock-tank barrels |
| `RB` | `bbl` | reservoir | Reservoir barrels |
| `Mscf_res` | `Mscf` | reservoir | Reservoir Mscf volumes |
| `Mscf_st` | `Mscf` | stock_tank | Stock-tank Mscf volumes |

## Api Gravity

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `°API`  | API gravity | `1` | 1 |

## Flow Rate

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `bbl/day`  | barrels per day | `m^3/s` | 1.84013e-06 |
| `bbl/h`  | barrels per hour | `m^3/s` | 4.41631e-05 |
| `BLPD`  | barrels of liquid per day | `m^3/s` | 1.84013e-06 |
| `Bscf/day`  | billion scf per day | `m^3/s` | 327.741 |
| `gal/min`  | US gallons per minute | `m^3/s` | 6.30902e-05 |
| `L/s`  | litres per second | `m^3/s` | 0.001 |
| `m3/day`  | cubic metres per day | `m^3/s` | 1.15741e-05 |
| `m3/h`  | cubic metres per hour | `m^3/s` | 0.000277778 |
| `Mbbl/day`  | thousand barrels per day | `m^3/s` | 0.00184013 |
| `MMbbl/day`  | million barrels per day | `m^3/s` | 1.84013 |
| `MMscf/day`  | million scf per day | `m^3/s` | 0.327741 |
| `Mscf/day`  | thousand scf per day | `m^3/s` | 0.000327741 |

## Gas Volume

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `Bscf`  | billion standard cu ft | `m^3` | 2.83168e+07 |
| `MMscf`  | million standard cu ft | `m^3` | 28316.8 |
| `Mscf`  | thousand standard cu ft | `m^3` | 28.3168 |
| `scf`  | standard cubic foot | `m^3` | 0.0283168 |
| `Tscf`  | trillion standard cu ft | `m^3` | 2.83168e+10 |

## Volume

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `acre_ft`  | acre-foot | `m^3` | 1233.48 |
| `bbl`  | barrel | `m^3` | 0.158987 |
| `ft3`  | cubic foot | `m^3` | 0.0283168 |
| `gal`  | US gallon | `m^3` | 0.00378541 |
| `m3`  | cubic metre | `m^3` | 1 |
| `Mbbl`  | thousand barrels | `m^3` | 158.987 |
| `MMbbl`  | million barrels | `m^3` | 158987 |
| `MMm3`  | million cubic metres | `m^3` | 1e+06 |

## Volume Reservoir

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `RB`  | barrel [reservoir] | `m^3` | 0.158987 |
| `Sm3_res`  | cubic metre [reservoir] | `m^3` | 1 |

## Volume Stock Tank

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `Sm3_st`  | cubic metre [stock_tank] | `m^3` | 1 |
| `STB`  | barrel [stock_tank] | `m^3` | 0.158987 |