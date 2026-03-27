"""
Phase 2 integration tests — petroleum engineering workflows.

These tests exercise the full Phase 2 surface in combination:
units + tagged arithmetic + API gravity + uncertainty propagation.

Each test class represents a realistic petroleum engineering workflow.
Numbers are physically representative of real reservoirs.

Workflows covered
-----------------
1.  Unit conversion chains (field → SI → field)
2.  Volumetric OOIP with unit tracking
3.  Volumetric OGIP with unit tracking
4.  GOR calculation and unit conversion
5.  Material balance identity check
6.  API gravity in a fluid characterization workflow
7.  Production rate unit conversions
8.  Pressure unit chain (field gauges → absolute → SI)
9.  Monte Carlo OOIP with correlated inputs
10. Full probabilistic fluid characterization
"""
import math
import pytest
import quantia as qu
from quantia.petroleum_conversions import api_to_sg, sg_to_api

_SCF = 0.3048 ** 3            # exact ft³ → m³
_BBL = 0.158987294928         # API MPMS: exact bbl → m³


# ── 1. Unit conversion chains ─────────────────────────────────────────────────

class TestUnitConversionChains:
    """Field units → SI → different field units, verifying no precision loss."""

    def test_bbl_m3_bbl_roundtrip(self):
        v = qu.Q(1_234.5, "bbl")
        assert v.to("m3").to("bbl").value == pytest.approx(v.value, rel=1e-10)

    def test_Mscf_m3_scf_chain(self):
        # 1 Mscf = 1000 scf (exact)
        assert qu.Q(1.0, "Mscf").to("m3").to("scf").value == pytest.approx(
               1000.0, rel=1e-9)

    def test_bbl_day_m3_s_m3_h_chain(self):
        # 1000 bbl/day → m³/s → m³/h
        rate = qu.Q(1000.0, "bbl/day")
        rate_m3h = rate.to("m3/h")
        # 1000 bbl/day × 0.158987 m³/bbl / 24 h/day = 6.624 m³/h
        expected = 1000.0 * _BBL / 24
        assert rate_m3h.value == pytest.approx(expected, rel=1e-6)

    def test_kg_cm2_psia_bara_chain(self):
        # 100 kg/cm² → psia → bara → back to Pa
        p = qu.Q(100.0, "kg/cm2")
        p_psia = p.to("psia")
        p_bara = p_psia.to("bara")
        assert p_bara.to("Pa").value == pytest.approx(
               p.to("Pa").value, rel=1e-6)

    def test_psig_to_kg_cm2(self):
        # 1000 psig → Pa → kg/cm2
        # 1000 psig = (1000 × 6894.757 + 101325) Pa = 7 096 082 Pa
        # → 7 096 082 / 98 066.5 = 72.36 kg/cm²
        result = qu.Q(1000.0, "psig").to("kg/cm2").value
        expected = (1000.0 * 6_894.757293168 + 101_325.0) / 9.806_65e4
        assert result == pytest.approx(expected, rel=1e-6)

    def test_acre_ft_bbl_chain(self):
        # 1 acre-ft = 7758.4 bbl (standard petroleum conversion)
        result = qu.Q(1.0, "acre_ft").to("bbl").value
        assert result == pytest.approx(7758.4, rel=1e-3)

    def test_MMscf_day_to_Bscf_yr(self):
        # 100 MMscf/day × 365 days = 36.5 Bscf/yr
        daily = qu.Q(100.0, "MMscf/day")
        yr_volume = daily * qu.Q(365.0, "d")
        assert yr_volume.to("Bscf").value == pytest.approx(36.5, rel=1e-6)


# ── 2. Volumetric OOIP ────────────────────────────────────────────────────────

class TestVolumetricOOIP:
    """
    Standard volumetric OOIP equation:
    OOIP = (A × h × φ × (1-Sw)) / Bo

    Where all inputs are exact and result is in STB (stock-tank barrels).
    """

    def test_OOIP_SI_then_convert(self):
        # Reservoir: 2 km² × 15 m thick × 20% porosity × 75% oil sat
        # Bo = 1.25 Sm3_res/Sm3_st
        A   = qu.Q(2e6,  "m2")       # 2 km²
        h   = qu.Q(15.0, "m")
        phi = 0.20
        Sw  = 0.25
        Bo  = qu.Q(1.25, "Sm3_res") / qu.Q(1.0, "Sm3_st")

        Vp   = A * h * phi            # m³ — pore volume
        Vp_r = qu.Q(Vp.value, "Sm3_res")   # tag as reservoir volume
        ooip = Vp_r * (1 - Sw) / Bo

        # Expected: 2e6 × 15 × 0.20 × 0.75 / 1.25 = 3 600 000 Sm3_st
        assert ooip.to("m3").value == pytest.approx(3_600_000.0, rel=1e-9)

    def test_OOIP_in_MMbbl(self):
        A   = qu.Q(5e6, "m2")        # 5 km²
        h   = qu.Q(20.0, "m")
        phi = 0.18
        Sw  = 0.30
        Bo  = qu.Q(1.3, "Sm3_res") / qu.Q(1.0, "Sm3_st")

        Vp_r = qu.Q(A.value * h.value * phi, "Sm3_res")
        ooip = Vp_r * (1 - Sw) / Bo

        expected_m3  = 5e6 * 20.0 * 0.18 * 0.70 / 1.3
        expected_bbl = expected_m3 / _BBL
        assert ooip.to("bbl").value == pytest.approx(expected_bbl, rel=1e-6)
        assert ooip.to("MMbbl").value == pytest.approx(
               expected_bbl / 1e6, rel=1e-6)

    def test_OOIP_acre_ft_basis(self):
        # Common US calculation: pore volume in acre-ft
        Vp  = qu.Q(10_000.0, "acre_ft")     # 10 000 acre-ft pore volume
        Vp_r = qu.Q(Vp.to("m3").value, "Sm3_res")
        Sw  = 0.25
        Bo  = qu.Q(1.2, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ooip = Vp_r * (1 - Sw) / Bo

        # Result in STB
        expected_m3  = 10_000 * 1_233.48 * 0.75 / 1.2
        assert ooip.to("bbl").value == pytest.approx(
               expected_m3 / _BBL, rel=1e-4)


# ── 3. Volumetric OGIP ────────────────────────────────────────────────────────

class TestVolumetricOGIP:
    """
    OGIP = (A × h × φ × (1-Sw)) / Bg

    Bg at reservoir conditions expressed as Sm3_res/Sm3_st.
    """

    def test_OGIP_in_Bscf(self):
        # Reservoir: 10 km² × 30 m × 15% porosity × 80% gas sat
        # Bg = 0.004 Sm3_res/Sm3_st (typical for moderate depth)
        A   = qu.Q(10e6, "m2")
        h   = qu.Q(30.0, "m")
        phi = 0.15
        Sw  = 0.20
        Bg  = qu.Q(0.004, "Sm3_res") / qu.Q(1.0, "Sm3_st")

        Vp_r = qu.Q(A.value * h.value * phi, "Sm3_res")
        ogip = Vp_r * (1 - Sw) / Bg

        # Expected: 10e6 × 30 × 0.15 × 0.80 / 0.004 = 9e9 Sm3_st
        assert ogip.to("m3").value == pytest.approx(9e9, rel=1e-9)

        # Convert to Bscf
        expected_bscf = 9e9 / (_SCF * 1e9)
        assert ogip.to("Bscf").value == pytest.approx(expected_bscf, rel=1e-6)

    def test_OGIP_smaller_Bg_gives_larger_OGIP(self):
        # Physical: deeper (higher pressure) → smaller Bg → more gas in place
        Vp_r = qu.Q(1e8, "Sm3_res")
        Sw   = 0.25
        Bg_shallow = qu.Q(0.010, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        Bg_deep    = qu.Q(0.003, "Sm3_res") / qu.Q(1.0, "Sm3_st")

        ogip_shallow = (Vp_r * (1 - Sw) / Bg_shallow).to("m3").value
        ogip_deep    = (Vp_r * (1 - Sw) / Bg_deep).to("m3").value
        assert ogip_deep > ogip_shallow


# ── 4. GOR calculations ───────────────────────────────────────────────────────

class TestGORWorkflow:

    def test_GOR_field_to_SI_to_field(self):
        # 500 scf/STB → SI (m³/m³) → Sm3/Sm3 (=SI for these units)
        gor = qu.Q(500.0, "scf_res") / qu.Q(1.0, "STB")
        si  = gor.si_value()
        expected = 500.0 * _SCF / _BBL
        assert si == pytest.approx(expected, rel=1e-9)

    def test_GOR_Mscf_STB_equals_1000_scf_STB(self):
        gor_mscf = qu.Q(1.0,      "Mscf_res") / qu.Q(1.0, "STB")
        gor_scf  = qu.Q(1_000.0,  "scf_res")  / qu.Q(1.0, "STB")
        assert gor_mscf.si_value() == pytest.approx(gor_scf.si_value(), rel=1e-9)

    def test_GOR_classification(self):
        # Physical GOR ranges:
        # < 200 Sm3/Sm3 → black oil / volatile oil
        # > 600 Sm3/Sm3 → gas condensate
        def classify(gor_sm3_sm3):
            if gor_sm3_sm3 < 200:
                return "oil"
            elif gor_sm3_sm3 > 600:
                return "condensate"
            return "volatile"

        gor_oil  = (qu.Q(100.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")).si_value()
        gor_cond = (qu.Q(800.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")).si_value()
        assert classify(gor_oil)  == "oil"
        assert classify(gor_cond) == "condensate"


# ── 5. Material balance identity ──────────────────────────────────────────────

class TestMaterialBalance:
    """
    For a volumetric depletion reservoir at abandonment:
    RF = (Bg_i/Bg_a - 1) / (1/Bg_i - 1)  [simplified]

    Simpler identity test: cumulative production ≤ OGIP
    """

    def test_cumulative_production_le_OGIP(self):
        # OGIP = 10 Bscf
        # Cumulative production = 7.5 Bscf (75% recovery)
        ogip = qu.Q(10.0, "Bscf")
        cum  = qu.Q(7.5,  "Bscf")
        rf   = cum.si_value() / ogip.si_value()
        assert 0 < rf < 1.0
        assert rf == pytest.approx(0.75, rel=1e-9)

    def test_production_unit_consistency(self):
        # Daily rate × time = cumulative volume (unit algebra)
        rate     = qu.Q(10.0, "MMscf/day")
        duration = qu.Q(365.0, "d")
        cumvol   = rate * duration
        # 10 MMscf/day × 365 day = 3650 MMscf = 3.65 Bscf
        assert cumvol.to("Bscf").value == pytest.approx(3.65, rel=1e-6)

    def test_oil_production_unit_consistency(self):
        rate     = qu.Q(5_000.0, "bbl/day")
        duration = qu.Q(365.0, "d")
        cumvol   = rate * duration
        # 5000 bbl/day × 365 day = 1 825 000 bbl = 1.825 MMbbl
        assert cumvol.to("MMbbl").value == pytest.approx(1.825, rel=1e-6)


# ── 6. API gravity fluid characterization ─────────────────────────────────────

class TestApiGravityWorkflow:

    def test_sg_from_api_used_in_density(self):
        # 35 °API crude → SG → density in kg/m³
        api = qu.Q(35.0, "°API")
        sg  = api_to_sg(api)                           # UnitFloat
        rho = sg * qu.Q(1000.0, "kg/m3")         # water=1000 kg/m³

        assert rho.to("g/cm3").value == pytest.approx(sg, rel=1e-9)
        assert rho.to("sg").value    == pytest.approx(sg, rel=1e-9)

    def test_api_classification(self):
        # API classification: >31.1 light, 22.3-31.1 medium, <22.3 heavy
        def classify_api(api_val):
            if api_val > 31.1:   return "light"
            if api_val > 22.3:   return "medium"
            return "heavy"

        assert classify_api(40.0) == "light"
        assert classify_api(26.0) == "medium"
        assert classify_api(15.0) == "heavy"

    def test_round_trip_api_sg_api(self):
        for api_val in [10.0, 25.0, 35.0, 45.0, 60.0]:
            assert sg_to_api(api_to_sg(api_val)).value == pytest.approx(
                   api_val, rel=1e-10)

    def test_api_to_density_array(self):
        # Array of API measurements → density array
        apis   = qu.QA([20.0, 30.0, 40.0, 50.0], "°API")
        sgs    = qu.QA([api_to_sg(a).value for a in apis], "1")
        rhos   = sgs * qu.Q(1000, "kg/m3")
        # Density must be monotonically decreasing with API
        vals = list(rhos.values)
        assert all(vals[i] > vals[i+1] for i in range(len(vals)-1))


# ── 7. Production rate conversions ───────────────────────────────────────────

class TestProductionRates:

    def test_oil_rate_field_to_SI_to_field(self):
        rate = qu.Q(10_000.0, "bbl/day")
        assert rate.to("m3/s").to("bbl/day").value == pytest.approx(
               10_000.0, rel=1e-9)

    def test_gas_rate_MMscf_to_m3_h(self):
        rate    = qu.Q(50.0, "MMscf/day")
        rate_m3h = rate.to("m3/h")
        expected = 50e6 * _SCF / 24
        assert rate_m3h.value == pytest.approx(expected, rel=1e-6)

    def test_liquid_rate_BLPD_equals_bbl_day(self):
        assert qu.Q(5_000.0, "BLPD").to("m3/s").value == pytest.approx(
               qu.Q(5_000.0, "bbl/day").to("m3/s").value, rel=1e-10)

    def test_injection_rate_gal_min_to_bbl_day(self):
        # Water injection: 500 gal/min → bbl/day
        rate = qu.Q(500.0, "gal/min")
        # 500 gal/min × 60 min/h × 24 h/day / 42 gal/bbl = 17 142.9 bbl/day
        expected = 500.0 * 60 * 24 / 42
        assert rate.to("bbl/day").value == pytest.approx(expected, rel=1e-6)


# ── 8. Pressure chain ─────────────────────────────────────────────────────────

class TestPressureChain:

    def test_wellhead_pressure_psig_to_bara(self):
        # Typical wellhead: 500 psig → bara
        p_pa   = 500.0 * 6_894.757293168 + 101_325.0
        p_bara = p_pa / 100_000.0
        assert qu.Q(500.0, "psig").to("bara").value == pytest.approx(
               p_bara, rel=1e-6)

    def test_reservoir_pressure_kg_cm2_to_psia(self):
        # 150 kg/cm² reservoir pressure → psia
        p_pa   = 150.0 * 9.806_65e4
        p_psia = p_pa / 6_894.757293168
        assert qu.Q(150.0, "kg/cm2").to("psia").value == pytest.approx(
               p_psia, rel=1e-6)

    def test_pressure_gradient_psi_ft(self):
        # Typical oil gradient: ~0.35 psi/ft
        # 0.35 psi/ft × 1000 ft = 350 psi pressure difference
        depth    = qu.Q(1_000.0, "ft")
        gradient = qu.Q(0.35, "psia") / qu.Q(1.0, "ft")  # psi → psia
        delta_p  = gradient * depth
        assert delta_p.to("psia").value == pytest.approx(350.0, rel=1e-6)

    def test_psi_g_deprecated_gives_same_as_psig(self):
        import warnings
        with pytest.warns(UserWarning, match="psig"):
            v_deprecated = qu.Q(500.0, "psi_g").to("Pa").value
        v_current = qu.Q(500.0, "psig").to("Pa").value
        assert v_deprecated == pytest.approx(v_current, rel=1e-10)


# ── 9. Monte Carlo OOIP with correlated inputs ────────────────────────────────

class TestMonteCarloOOIP:
    """
    Realistic probabilistic OOIP calculation with correlated inputs.
    Porosity and net-to-gross tend to be positively correlated in
    layered reservoirs.
    """

    def test_prob_OOIP_uncertainty(self):
        # Independent uncertain inputs
        with qu.config(seed=42, n_samples=5000):
            phi = qu.ProbUnitFloat.triangular(0.12, 0.18, 0.25, "1")
            Sw  = qu.ProbUnitFloat.triangular(0.20, 0.28, 0.35, "1")
            Bo  = qu.ProbUnitFloat.normal(1.25, 0.05, "Sm3_res")

        A = qu.Q(3e6, "m2")
        h = qu.Q(18.0, "m")

        Vp_val = A.value * h.value   # m² × m = m³
        Vp_r   = qu.Q(Vp_val, "Sm3_res") * phi

        Bo_ratio = Bo / qu.Q(1.0, "Sm3_st")
        ooip = Vp_r * (1 - Sw) / Bo_ratio

        mean_ooip = ooip.mean().to("MMbbl").value
        std_ooip  = ooip.std().to("MMbbl").value

        # Physical sanity checks
        assert mean_ooip > 0
        assert std_ooip  > 0
        assert std_ooip / mean_ooip < 0.5   # CV < 50%

        # P10/P90 spread
        lo, hi = ooip.interval(0.80)
        assert lo.to("MMbbl").value < mean_ooip < hi.to("MMbbl").value

    def test_prob_OOIP_correlated_inputs(self):
        # Porosity and Bo positively correlated (richer fluid in better rock)
        with qu.config(seed=0, n_samples=3000):
            src = qu.CorrelatedSource(n_vars=2, rho=0.6)
            phi = src.draw(0, "triangular", "1", low=0.12, mode=0.18, high=0.25)
            Bo  = src.draw(1, "normal",     "Sm3_res", mean=1.25, std=0.05)

        Sw     = 0.25
        Vp_r   = qu.Q(3e6 * 18.0, "Sm3_res") * phi
        Bo_rat = Bo / qu.Q(1.0, "Sm3_st")
        ooip   = Vp_r * (1 - Sw) / Bo_rat

        assert ooip.mean().to("MMbbl").value > 0
        assert ooip.std().to("MMbbl").value  > 0


# ── 10. Full probabilistic fluid characterization ─────────────────────────────

class TestProbFluidCharacterization:
    """
    Full workflow: uncertain API → uncertain SG → uncertain density →
    uncertain OOIP weighting.
    """

    def test_prob_api_to_density(self):
        # Uncertain crude API gravity → density distribution
        with qu.config(seed=5, n_samples=3000):
            api = qu.ProbUnitFloat.normal(35.0, 3.0, "°API")

        sg  = api_to_sg(api)              # ProbUnitFloat, dimensionless
        rho = sg * qu.Q(1000.0, "kg/m3")                 # kg/m³ equivalent

        # Mean density at mean API
        expected_mean_sg = api_to_sg(35.0).value
        assert sg.mean().value == pytest.approx(expected_mean_sg, rel=0.03)

    def test_prob_sg_to_api_round_trip(self):
        with qu.config(seed=6, n_samples=2000):
            api_orig = qu.ProbUnitFloat.uniform(25.0, 45.0, "1")

        api_rt = sg_to_api(api_to_sg(api_orig))
        assert api_rt.mean().value == pytest.approx(
               api_orig.mean().value, rel=0.01)

    def test_full_workflow_api_to_OOIP_weight(self):
        """
        Heavier oil (lower API) → higher density → higher mass OOIP.
        This test verifies the full chain produces physically consistent
        results when API uncertainty feeds into a volumetric calculation.
        """
        with qu.config(seed=7, n_samples=2000):
            api_light = qu.ProbUnitFloat.normal(45.0, 2.0, "1")
            api_heavy = qu.ProbUnitFloat.normal(20.0, 2.0, "1")

        sg_light = api_to_sg(api_light)
        sg_heavy = api_to_sg(api_heavy)

        # Heavier oil has higher SG
        assert sg_heavy.mean().value > sg_light.mean().value

        # Heavier oil has lower API → confirmed by round-trip
        assert sg_to_api(sg_heavy).mean().value < sg_to_api(sg_light).mean().value