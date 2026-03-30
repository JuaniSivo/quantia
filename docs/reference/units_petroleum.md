# Petroleum Units

Sources: API Manual of Petroleum Measurement Standards (MPMS) Chapter 11,
SPE nomenclature conventions.

## Tagged Units

The following units are *semantically tagged* — they share SI dimensions
with their base unit but will **not cancel** when divided by a differently
tagged unit. Use them to build GOR and FVF ratios that preserve
petroleum meaning through calculations.

| Symbol       | Base | Tag               | Typical use                  |
|--------------|------|-------------------|------------------------------|
| `m3_res` (1) | m3   | reservoir         | Reservoir pore/fluid volumes |
| `m3_sep` (1) | m3   | separator         | Separator fluid volumes      |
| `m3_sc`  (1) | m3   | standar condition | Stock-tank fluid volumes     |
| `cf_res` (2) | ft3  | reservoir         | Reservoir gas volumes        |
| `cf_sep` (2) | ft3  | separator         | Separator gas volumes        |
| `RB`         | bbl  | reservoir         | Reservoir liquid barrels     |
| `STB`        | bbl  | stock_tank        | Stock-tank liquid barrels    |
| `bbl_sep`    | bbl  | separator         | separator liquid barrels     |
| `Mcf_res`    | ft3  | reservoir         | Reservoir gas volumes        |
| `Mcf_sep`    | ft3  | separator         | Separator gas volumes        |

> (1) It is also available in fluid-specific versions. Example: m3_o_res,
m3_g_res or m3_w_res.
>
> (2) cf_sc does not exist because it is covered by scf (standard cubic
foot).

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

| Symbol  | Name | SI unit | Factor to SI |
|---------|------|---------|-------------|
| `scf`   | standard cubic foot     | `m^3` | 0.0283168   |
| `Mscf`  | thousand standard cu ft | `m^3` | 28.3168     |
| `MMscf` | million standard cu ft  | `m^3` | 28316.8     |
| `Bscf`  | billion standard cu ft  | `m^3` | 2.83168e+07 |
| `Tscf`  | trillion standard cu ft | `m^3` | 2.83168e+10 |

## Gas Volume Reservoir

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `Mcf_res`  | thousand standard cu ft [reservoir] | `m^3` | 28.3168 |

## Gas Volume Separator

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `Mcf_sep`  | thousand standard cu ft [separator] | `m^3` | 28.3168 |

## Volume

| Symbol     | Name | SI unit | Factor to SI |
|------------|------|---------|-------------|
| `acre_ft`  | acre-foot | `m^3` | 1233.48 |
| `bbl`      | barrel | `m^3` | 0.158987 |
| `Mbbl`     | thousand barrels | `m^3` | 158.987 |
| `MMbbl`    | million barrels | `m^3` | 158987 |
| `ft3`      | cubic foot | `m^3` | 0.0283168 |
| `gal`      | US gallon | `m^3` | 0.00378541 |
| `m3`       | cubic metre | `m^3` | 1 |
| `k(m3)`    | thousand cubic metres | `m^3` | 1000 |
| `MMm3`     | million cubic metres | `m^3` | 1e+06 |

## Volume Reservoir

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `cf_res`  | cubic foot [reservoir] | `m^3` | 0.0283168 |
| `m3_g_res`  | cubic metre [reservoir] | `m^3` | 1 |
| `m3_o_res`  | cubic metre [reservoir] | `m^3` | 1 |
| `m3_res`  | cubic metre [reservoir] | `m^3` | 1 |
| `m3_w_res`  | cubic metre [reservoir] | `m^3` | 1 |
| `RB`  | barrel [reservoir] | `m^3` | 0.158987 |

## Volume Separator

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `bbl_sep`  | barrel [separator] | `m^3` | 0.158987 |
| `cf_sep`  | cubic foot [separator] | `m^3` | 0.0283168 |
| `m3_g_sep`  | cubic metre [separator] | `m^3` | 1 |
| `m3_o_sep`  | cubic metre [separator] | `m^3` | 1 |
| `m3_sep`  | cubic metre [separator] | `m^3` | 1 |
| `m3_w_sep`  | cubic metre [separator] | `m^3` | 1 |

## Volume Standar Conditions

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `m3_g_sc`  | cubic metre [standar_conditions] | `m^3` | 1 |
| `m3_o_sc`  | cubic metre [standar_conditions] | `m^3` | 1 |
| `m3_sc`  | cubic metre [standar_conditions] | `m^3` | 1 |
| `m3_w_sc`  | cubic metre [standar_conditions] | `m^3` | 1 |

## Volume Stock Tank

| Symbol | Name | SI unit | Factor to SI |
|--------|------|---------|-------------|
| `STB`  | barrel [stock_tank] | `m^3` | 0.158987 |