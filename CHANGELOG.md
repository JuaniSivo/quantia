# Changelog

All notable changes to quantia are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-03-21

### Added
- Complete type hints on high-value public surface (UnitFloat, UnitArray,
  ProbUnitFloat, CorrelatedSource, petroleum_conversions)
- Numpy-style docstrings on all public classes and methods
- MkDocs documentation site at https://quantia.readthedocs.io
- Unit reference tables auto-generated from live registry
- `py.typed` PEP 561 marker for mypy/Pylance/pyright support

### Changed
- `pyproject.toml`: version 0.2.1, full PyPI classifiers, project URLs

---

## [0.2.0] — 2026-03-19

### Added

**Petroleum units**
- Volume: `Bscf`, `Tscf`, `MMm3`, `acre_ft`
- Flow rate: `MMbbl/day`, `m3/h`, `MMscf/day`, `Bscf/day`, `bbl/h`,
  `L/s`, `gal/min`, `BLPD`
- Energy: `BOE` (5.8 MMBtu), `Mcfe` (1 MMBtu_IT)
- Pressure: `kg/cm2`, `kgf/cm2` (9.806 65 × 10⁴ Pa)
- Tagged units: `STB`, `RB`, `Mscf_res`, `Mscf_st`

**Pressure hierarchy** (gauge / absolute via `AffineUnit`)
- `psia`, `psig` — absolute and gauge psi
- `bara`, `barg` — absolute and gauge bar
- Affine path generalized: `psig → Pa`, `psia → kPa` all work

**SI completions** (NIST Table 4)
- `sr`, `C`, `S`, `Wb`, `T`, `lm`, `lx`, `Bq`, `Gy`, `Sv`, `kat`
- Prefixed variants: `GHz`, `THz`, `GPa`, `GW`, `MΩ`, `GΩ`, `nF`,
  `pF`, `mH`, `µH`, `mmol`, `µmol` and more

**New domain unit files**
- `mechanical.py`: `rpm`, `rad/s`, `D`, `mD`, `µD`, `cP`, `P`,
  `mPa_s`, `cSt`, `St`, torque units
- `thermal.py`: `W/m2`, `W/m_K`, `J/K`, `J/kg_K`, `J/mol`, `J/mol_K`
- `electromagnetic.py`: `A_h`, `G`, `Mx`, `mT`, `µT`, `nT`, `Ω_m`
- `density.py`: `g/cm3`, `kg/L`, `lb/ft3`, `lb/gal`, `sg`, `ppm`, `ppb`

**NIST Table 8 (non-SI accepted)**
- Time: `d` (canonical day), `week`, `yr`
- Angle: `°` (canonical), `′`/`arcmin`, `″`/`arcsec`
- Area: `ha`
- Mass: `Da`
- Log ratio: `Np`, `dB`

**Imperial additions**
- Length: `Å`, `nmi`, `mil`, `ly`
- Area: `ft2`, `in2`, `yd2`, `mi2`, `acre`
- Volume: `ft3`, `in3`, `fl_oz`, `gal_imp`, `pt`
- Mass: `gr`, `slug`, `ton_long`, `ton_short`
- Force: `dyn`, `kgf`, `kip`, `ozf`, `pdl`
- Pressure: `ksi`, `torr`, `inHg`, `inH2O`, `ftH2O`, `cmHg`, `mbar`
- Energy: `ft_lbf`, `therm_EC`, `therm_US`, `MMBtu`, `erg`, `toe`
- Temperature: `°R` (Rankine)
- Velocity: `ft/s`, `ft/min`, `km/h`

**Atomic unit aliases**
- `m2` — alias for `m^2`
- `m3` — alias for `m^3`

**API gravity conversions**
- `api_to_sg(api)` — float, UnitFloat, or ProbUnitFloat dispatch
- `sg_to_api(sg)` — inverse conversion

**Documentation**
- MkDocs + Material theme site at https://quantia.readthedocs.io
- Numpy-style docstrings on high-value public surface
- Complete type hints on all public methods
- Unit reference tables auto-generated from live registry

### Fixed
- `to_si_compound()` now correctly parses compound `si_unit` strings
  (e.g. `m/s`, `m^3/s`) — previously broke compatibility checks for
  `kn`, `mph`, `bbl/day` and any unit with a compound SI string
- `_make_unit()` now calls `get_unit()` — ambiguous unit warnings
  (`psi`, `bar`) now fire correctly in all contexts
- `to()` now handles affine ↔ plain conversions (`psia → Pa`,
  `psig → kPa`) — previously required both sides to be affine
- `CompoundUnit.__truediv__`: same-label division now cancels to
  dimensionless (`Sm3_res / Sm3_res → 1`) — previously always
  produced a labeled ratio
- `ProbUnitFloat.__rtruediv__`: `UnitFloat / ProbUnitFloat` now
  supported — previously raised `TypeError`
- `scf` and `ft3` now share the exact value `0.3048³` m³ — previously
  used independently rounded constants causing identity failures

### Changed
- `BTU` → warns, treated as `BTU_IT`. Use `BTU_IT` or `BTU_th`
- `cal`/`kcal` → warns, treated as `cal_th`. Use `cal_th` or `cal_IT`
- `psi` → warns, treated as `psia`. Use `psia` or `psig`
- `bar` → warns, treated as `bara`. Use `bara` or `barg`
- `psi_g` deprecated → warns, redirects to `psig`
- Opaque GOR ratio units (`Sm3/Sm3`, `scf/STB`, `Mscf/STB`) removed.
  Use tagged units (`Sm3_res`, `Sm3_st`, `STB`, etc.) instead

### Internals
- `register()` now raises `ValueError` on duplicate symbol
  (use `overwrite=True` to replace intentionally)
- `_AMBIGUOUS_UNITS` dict in `_registry.py` is the single place
  to add future ambiguous unit warnings

---

## [0.1.0] — 2026-01-12

### Added
- `UnitFloat` — exact scalar with physical unit
- `UnitArray` — exact vector with physical unit
- `ProbUnitFloat` — uncertain scalar (Monte Carlo samples)
- `ProbUnitArray` — uncertain vector
- `CorrelatedSource` — correlated inputs via Gaussian copula
- Unit domains: SI, Imperial, common, petroleum, data
- `quantia.math` — drop-in replacement for stdlib `math` module
- Serialization: `save()`, `load()`, `to_dict()`, `from_dict()`
- `config()` context manager for sample count and seed control
- CSV export: `UnitArray.to_csv()`, `ProbUnitArray.to_csv()`,
  `ProbUnitArray.samples_to_csv()`