"""
Semantic tagged unit tests for petroleum GOR and FVF calculations.

Covers
------
- Non-cancellation of tagged units (physics preserved)
- GOR calculations and unit conversions
- FVF (formation volume factor) calculations
- OOIP and OGIP end-to-end calculations
- ProbUnitFloat uncertainty propagation through tagged units

All conversion factors derived from exact definitions where possible.
SPE nomenclature conventions followed throughout.
"""
import pytest
import quantia as qu
from quantia._registry import get_unit

_SCF = 0.3048 ** 3          # exact ft³ → m³
_BBL = 0.158987294928        # API MPMS: exact bbl → m³


# ── Tagged unit registration sanity ──────────────────────────────────────────

class TestTaggedRegistration:
    """All tagged symbols must be in the registry with correct SI factors."""

    def test_Sm3_res_registered(self):
        assert get_unit("Sm3_res").to_si == pytest.approx(1.0, rel=1e-10)

    def test_Sm3_st_registered(self):
        assert get_unit("Sm3_st").to_si == pytest.approx(1.0, rel=1e-10)

    def test_scf_res_registered(self):
        assert get_unit("scf_res").to_si == pytest.approx(_SCF, rel=1e-10)

    def test_scf_st_registered(self):
        assert get_unit("scf_st").to_si == pytest.approx(_SCF, rel=1e-10)

    def test_STB_registered(self):
        assert get_unit("STB").to_si == pytest.approx(_BBL, rel=1e-10)

    def test_RB_registered(self):
        assert get_unit("RB").to_si == pytest.approx(_BBL, rel=1e-10)

    def test_Mscf_res_registered(self):
        assert get_unit("Mscf_res").to_si == pytest.approx(_SCF * 1_000, rel=1e-10)

    def test_Mscf_st_registered(self):
        assert get_unit("Mscf_st").to_si == pytest.approx(_SCF * 1_000, rel=1e-10)


# ── Non-cancellation (physics preservation) ───────────────────────────────────

class TestNonCancellation:
    """
    Dividing tagged units of the same base must NOT produce dimensionless.
    This is the core correctness guarantee of the tagged unit mechanism.
    """

    def test_Sm3_res_div_Sm3_st_not_dimensionless(self):
        gor = qu.Q(200.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert not gor.unit.is_dimensionless()

    def test_scf_res_div_scf_st_not_dimensionless(self):
        gor = qu.Q(1000.0, "scf_res") / qu.Q(1.0, "scf_st")
        assert not gor.unit.is_dimensionless()

    def test_RB_div_STB_not_dimensionless(self):
        bo = qu.Q(1.2, "RB") / qu.Q(1.0, "STB")
        assert not bo.unit.is_dimensionless()

    def test_Mscf_res_div_Mscf_st_not_dimensionless(self):
        gor = qu.Q(2.0, "Mscf_res") / qu.Q(1.0, "Mscf_st")
        assert not gor.unit.is_dimensionless()

    def test_Sm3_res_div_Sm3_res_IS_dimensionless(self):
        # Dividing SAME tag cancels normally — only different tags preserve
        ratio = qu.Q(2.0, "Sm3_res") / qu.Q(1.0, "Sm3_res")
        assert ratio.unit.is_dimensionless()

    def test_plain_m3_div_m3_is_dimensionless(self):
        # Plain (untagged) volume always cancels
        ratio = qu.Q(200.0, "m3") / qu.Q(1.0, "m3")
        assert ratio.unit.is_dimensionless()


# ── GOR (Gas-Oil Ratio) ───────────────────────────────────────────────────────

class TestGOR:
    """
    GOR unit conversion: scf/STB ↔ Sm3/Sm3 ↔ Mscf/STB

    Key identity:
      1 Sm3/Sm3 = 1 m³ gas / 1 m³ oil at surface
               = (1/0.3048³) scf / (1/0.158987...) STB
               = 5.614 scf/STB
    """

    _SM3_PER_SCF_STB = _SCF / _BBL   # ≈ 0.178107 Sm3/Sm3 per scf/STB

    def test_GOR_Sm3_Sm3_si_value(self):
        # 200 Sm3_res / 1 Sm3_st — SI value = 200 (both m³, ratio = 200)
        gor = qu.Q(200.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert gor.si_value() == pytest.approx(200.0, rel=1e-9)

    def test_GOR_scf_STB_si_value(self):
        # 1000 scf_res / 1 STB
        # SI = 1000 × 0.3048³ / 0.158987... = 178.107 m³/m³
        gor = qu.Q(1000.0, "scf_res") / qu.Q(1.0, "STB")
        expected = 1000.0 * _SCF / _BBL
        assert gor.si_value() == pytest.approx(expected, rel=1e-9)

    def test_GOR_1000_scf_STB_to_Sm3_Sm3(self):
        # 1000 scf/STB × (0.3048³ m³/scf) / (0.158987... m³/STB)
        #              = 178.107 Sm3/Sm3
        gor_scf = qu.Q(1000.0, "scf_res") / qu.Q(1.0, "STB")
        gor_sm3 = qu.Q(200.0,  "Sm3_res") / qu.Q(1.0, "Sm3_st")
        # 1000 scf/STB in Sm3/Sm3:
        expected_sm3 = 1000.0 * _SCF / _BBL
        assert gor_scf.si_value() == pytest.approx(expected_sm3, rel=1e-9)
        # Cross-check: 1000 scf/STB ≠ 200 Sm3/Sm3
        assert gor_scf.si_value() != pytest.approx(gor_sm3.si_value(), rel=1e-2)

    def test_GOR_Mscf_STB_to_Sm3_Sm3(self):
        # 1 Mscf/STB = 1000 scf/STB = 178.107 Sm3/Sm3
        gor_mscf = qu.Q(1.0, "Mscf_res") / qu.Q(1.0, "STB")
        gor_scf  = qu.Q(1000.0, "scf_res") / qu.Q(1.0, "STB")
        assert gor_mscf.si_value() == pytest.approx(gor_scf.si_value(), rel=1e-9)

    def test_GOR_conversion_scf_STB_to_Sm3_Sm3_numeric(self):
        # Explicit: 5 000 scf/STB → Sm3/Sm3
        # = 5000 × 0.3048³ / 0.158987... = 890.53 Sm3/Sm3
        gor = qu.Q(5_000.0, "scf_res") / qu.Q(1.0, "STB")
        expected = 5_000.0 * _SCF / _BBL
        assert gor.si_value() == pytest.approx(expected, rel=1e-9)

    def test_GOR_typical_oil_reservoir(self):
        # Typical solution GOR for medium-gravity oil: ~100 Sm3/Sm3
        gor = qu.Q(100.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert gor.si_value() == pytest.approx(100.0, rel=1e-9)
        assert 50 < gor.si_value() < 500   # physically reasonable range

    def test_GOR_dry_gas_condensate(self):
        # Dry gas condensate: ~50 000 scf/STB (very high GOR)
        gor = qu.Q(50_000.0, "scf_res") / qu.Q(1.0, "STB")
        expected = 50_000.0 * _SCF / _BBL
        assert gor.si_value() == pytest.approx(expected, rel=1e-9)


# ── FVF (Formation Volume Factor) ─────────────────────────────────────────────

class TestFVF:
    """
    Oil FVF (Bo): RB/STB or Sm3_res/Sm3_st
    Gas FVF (Bg): RB/scf or m³_res/m³_st (rarely tagged, usually small number)

    Bo > 1 always (reservoir oil expands from dissolved gas)
    Typical range: 1.05 to 2.5 RB/STB
    """

    def test_Bo_RB_STB_si_value(self):
        # Bo = 1.2 RB/STB — SI value = 1.2 (both m³, exact ratio)
        bo = qu.Q(1.2, "RB") / qu.Q(1.0, "STB")
        assert bo.si_value() == pytest.approx(1.2, rel=1e-9)

    def test_Bo_Sm3_res_Sm3_st_si_value(self):
        # Bo = 1.35 Sm3_res/Sm3_st
        bo = qu.Q(1.35, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert bo.si_value() == pytest.approx(1.35, rel=1e-9)

    def test_Bo_RB_STB_equals_Sm3_res_Sm3_st(self):
        # Both FVF representations have identical SI value
        # (all four units have same SI base m³)
        bo_rb  = qu.Q(1.2, "RB")  / qu.Q(1.0, "STB")
        bo_sm3 = qu.Q(1.2, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert bo_rb.si_value() == pytest.approx(bo_sm3.si_value(), rel=1e-9)

    def test_Bo_not_dimensionless(self):
        bo = qu.Q(1.2, "RB") / qu.Q(1.0, "STB")
        assert not bo.unit.is_dimensionless()

    def test_Bo_physically_reasonable(self):
        # All typical Bo values > 1
        for bo_val in [1.05, 1.2, 1.5, 2.0, 2.5]:
            bo = qu.Q(bo_val, "RB") / qu.Q(1.0, "STB")
            assert bo.si_value() > 1.0


# ── OOIP (Oil Originally In Place) ────────────────────────────────────────────

class TestOOIP:
    """
    OOIP = Vp × (1 - Sw) / Bo

    Where:
      Vp  = pore volume [Sm3_res]
      Sw  = water saturation [dimensionless]
      Bo  = oil FVF [Sm3_res/Sm3_st]

    Result is in Sm3_st → convert to bbl
    """

    def test_OOIP_basic(self):
        # Vp=1e6 Sm3_res, Sw=0.25, Bo=1.2
        # OOIP = 1e6 × 0.75 / 1.2 = 625 000 Sm3_st
        Vp   = qu.Q(1_000_000.0, "Sm3_res")
        Sw   = 0.25
        Bo   = qu.Q(1.2, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ooip = Vp * (1 - Sw) / Bo
        assert ooip.to("m3").value == pytest.approx(625_000.0, rel=1e-9)

    def test_OOIP_in_bbl(self):
        # Same as above, result in bbl
        Vp   = qu.Q(1_000_000.0, "Sm3_res")
        Sw   = 0.25
        Bo   = qu.Q(1.2, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ooip = Vp * (1 - Sw) / Bo
        expected_bbl = 625_000.0 / _BBL
        assert ooip.to("bbl").value == pytest.approx(expected_bbl, rel=1e-9)

    def test_OOIP_RB_STB_tags(self):
        # Same calculation using RB/STB tags
        Vp   = qu.Q(1_000_000.0, "Sm3_res")
        Sw   = 0.20
        Bo   = qu.Q(1.35, "RB") / qu.Q(1.0, "STB")
        ooip = Vp * (1 - Sw) / Bo
        expected = 1_000_000.0 * 0.80 / 1.35
        assert ooip.to("m3").value == pytest.approx(expected, rel=1e-9)

    def test_OOIP_higher_Bo_gives_lower_OOIP(self):
        # Physical sanity: higher Bo → more shrinkage → less OOIP
        Vp = qu.Q(1_000_000.0, "Sm3_res")
        Sw = 0.25
        Bo_low  = qu.Q(1.1, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        Bo_high = qu.Q(1.5, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ooip_low  = (Vp * (1 - Sw) / Bo_low).to("m3").value
        ooip_high = (Vp * (1 - Sw) / Bo_high).to("m3").value
        assert ooip_low > ooip_high


# ── OGIP (Original Gas In Place) ─────────────────────────────────────────────

class TestOGIP:
    """
    OGIP = Vp × (1 - Sw) / Bg

    Where Bg = gas FVF [m³_res/scf_std] — typically very small number.
    For dry gas reservoirs, often expressed as Sm3_res/Sm3_st.

    Simplified: OGIP = Vp × (1 - Sw)  [in scf, using scf_res volumes]
    """

    def test_OGIP_Sm3_basis(self):
        # Vp=1e8 Sm3_res, Sw=0.30, Bg=0.005 (tight gas)
        # OGIP = 1e8 × 0.70 / 0.005 = 1.4e10 Sm3_st
        Vp   = qu.Q(1e8, "Sm3_res")
        Sw   = 0.30
        Bg   = qu.Q(0.005, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ogip = Vp * (1 - Sw) / Bg
        assert ogip.to("m3").value == pytest.approx(1.4e10, rel=1e-9)

    def test_OGIP_in_scf(self):
        # Same result expressed in scf
        Vp   = qu.Q(1e8, "Sm3_res")
        Sw   = 0.30
        Bg   = qu.Q(0.005, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        ogip = Vp * (1 - Sw) / Bg
        expected_scf = 1.4e10 / _SCF
        assert ogip.to("scf").value == pytest.approx(expected_scf, rel=1e-6)


# ── ProbUnitFloat uncertainty propagation ─────────────────────────────────────

class TestProbTagged:
    """
    Verify that uncertainty propagation works correctly through
    tagged unit arithmetic. The semantic labels must survive through
    ProbUnitFloat operations.
    """

    def test_prob_OOIP_mean_matches_deterministic(self):
        """
        When Bo is uncertain, mean OOIP should match deterministic
        calculation at mean Bo.
        """
        Vp = qu.Q(1_000_000.0, "Sm3_res")
        Sw = 0.25

        with qu.config(seed=42, n_samples=5000):
            Bo_prob = qu.ProbUnitFloat.normal(1.2, 0.05, "Sm3_res")

        Bo_st = qu.Q(1.0, "Sm3_st")

        # Build probabilistic Bo ratio
        Bo = Bo_prob / Bo_st
        ooip = Vp * (1 - Sw) / Bo

        # Mean should be close to deterministic value at mean Bo
        det_ooip = 1_000_000.0 * 0.75 / 1.2  # Sm3_st
        assert ooip.mean().to("m3").value == pytest.approx(
               det_ooip, rel=0.05)   # 5% tolerance for MC at n=5000

    def test_prob_OOIP_std_positive(self):
        """Uncertain Bo must produce uncertain OOIP (std > 0)."""
        Vp = qu.Q(1_000_000.0, "Sm3_res")
        Sw = 0.25

        with qu.config(seed=0, n_samples=2000):
            Bo_prob = qu.ProbUnitFloat.uniform(1.1, 1.5, "Sm3_res")

        Bo = Bo_prob / qu.Q(1.0, "Sm3_st")
        ooip = Vp * (1 - Sw) / Bo
        assert ooip.std().to("m3").value > 0

    def test_prob_GOR_mean(self):
        """Uncertain GOR mean should match expected value."""
        with qu.config(seed=1, n_samples=3000):
            gas = qu.ProbUnitFloat.normal(100.0, 5.0, "Sm3_res")

        oil = qu.Q(1.0, "Sm3_st")
        gor = gas / oil
        assert gor.mean().si_value() == pytest.approx(100.0, rel=0.05)