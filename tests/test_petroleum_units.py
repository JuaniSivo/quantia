"""
Petroleum unit regression tests — Step 2.2.

Sources
-------
API MPMS Ch.11 (barrel, scf conversions)
SPE nomenclature (BOE, GOR units)
NIST SP811 (base conversion factors)
"""
import pytest
import quantia as qu


# ── Volume ────────────────────────────────────────────────────────────────────

class TestVolume:

    def test_bbl_to_m3(self):
        # API MPMS: 1 bbl = 0.158 987 294 928 m³ (exact)
        assert qu.Q(1.0, "bbl").to("m3").value == pytest.approx(
               0.158987294928, rel=1e-9)

    def test_bbl_to_gal(self):
        # 1 bbl = 42 US gal (exact by API definition)
        assert qu.Q(1.0, "bbl").to("gal").value == pytest.approx(42.0, rel=1e-9)

    def test_Mbbl_to_bbl(self):
        assert qu.Q(1.0, "Mbbl").to("bbl").value == pytest.approx(1000.0, rel=1e-9)

    def test_MMbbl_to_Mbbl(self):
        assert qu.Q(1.0, "MMbbl").to("Mbbl").value == pytest.approx(1000.0, rel=1e-9)

    def test_scf_to_m3(self):
        # 1 scf = 1 ft³ = 2.831 685 E-02 m³ (NIST)
        assert qu.Q(1.0, "scf").to("m3").value == pytest.approx(
            2.831_685e-2, rel=1e-6)

    def test_scf_to_ft3(self):
        # 1 scf = 1 ft³ — exact identity, same registration value
        assert qu.Q(1.0, "scf").to("ft3").value == pytest.approx(1.0, rel=1e-9)

    def test_Mscf_to_scf(self):
        assert qu.Q(1.0, "Mscf").to("scf").value == pytest.approx(1000.0, rel=1e-9)

    def test_MMscf_to_Mscf(self):
        assert qu.Q(1.0, "MMscf").to("Mscf").value == pytest.approx(1000.0, rel=1e-9)

    def test_Bscf_to_MMscf(self):
        assert qu.Q(1.0, "Bscf").to("MMscf").value == pytest.approx(1000.0, rel=1e-9)

    def test_Tscf_to_Bscf(self):
        assert qu.Q(1.0, "Tscf").to("Bscf").value == pytest.approx(1000.0, rel=1e-9)

    def test_MMm3_to_m3(self):
        assert qu.Q(1.0, "MMm3").to("m3").value == pytest.approx(1e6, rel=1e-9)

    def test_acre_ft_to_m3(self):
        # NIST: 1 acre-ft = 1.233 489 E+03 m³
        assert qu.Q(1.0, "acre_ft").to("m3").value == pytest.approx(
               1_233.48, rel=1e-4)

    def test_acre_ft_to_bbl(self):
        # 1 acre-ft = 1233.48 / 0.158987... bbl ≈ 7758.4 bbl
        # Standard petroleum reservoir calculation
        result = qu.Q(1.0, "acre_ft").to("bbl").value
        assert result == pytest.approx(7758.4, rel=1e-3)


# ── Pressure ──────────────────────────────────────────────────────────────────

class TestPressure:

    def test_kg_cm2_to_Pa(self):
        # NIST: 1 kgf/cm² = 9.806 65 E+04 Pa (exact)
        assert qu.Q(1.0, "kg/cm2").to("Pa").value == pytest.approx(
               9.806_65e4, rel=1e-9)

    def test_kgf_cm2_equals_kg_cm2(self):
        assert qu.Q(1.0, "kgf/cm2").to("Pa").value == pytest.approx(
               qu.Q(1.0, "kg/cm2").to("Pa").value, rel=1e-10)

    def test_kg_cm2_to_psia(self):
        # 1 kgf/cm² = 14.223 psia
        assert qu.Q(1.0, "kg/cm2").to("psia").value == pytest.approx(
               14.223, rel=1e-3)

    def test_kg_cm2_to_bara(self):
        # 1 kgf/cm² = 0.980 665 bara
        assert qu.Q(1.0, "kg/cm2").to("bara").value == pytest.approx(
               0.980_665, rel=1e-6)

    def test_psi_g_warns_and_redirects(self):
        import warnings
        with pytest.warns(UserWarning, match="psig"):
            v = qu.Q(100.0, "psi_g").to("Pa").value
        assert v == pytest.approx(qu.Q(100.0, "psig").to("Pa").value, rel=1e-10)


# ── Flow rate ─────────────────────────────────────────────────────────────────

class TestFlowRate:

    def test_bbl_day_to_m3_s(self):
        # 1 bbl/day = 0.158987... / 86400 m³/s
        assert qu.Q(1.0, "bbl/day").to("m3/s").value == pytest.approx(
               0.158987294928 / 86_400, rel=1e-9)

    def test_Mbbl_day_to_bbl_day(self):
        assert qu.Q(1.0, "Mbbl/day").to("bbl/day").value == pytest.approx(
               1000.0, rel=1e-9)

    def test_MMbbl_day_to_Mbbl_day(self):
        assert qu.Q(1.0, "MMbbl/day").to("Mbbl/day").value == pytest.approx(
               1000.0, rel=1e-9)

    def test_m3_h_to_m3_s(self):
        # 1 m³/h = 1/3600 m³/s (exact)
        assert qu.Q(1.0, "m3/h").to("m3/s").value == pytest.approx(
               1/3600, rel=1e-9)

    def test_m3_h_to_bbl_day(self):
        # 1 m³/h = 24 m³/day = 24/0.158987... bbl/day ≈ 150.96 bbl/day
        result = qu.Q(1.0, "m3/h").to("bbl/day").value
        assert result == pytest.approx(24 / 0.158987294928, rel=1e-6)

    def test_Mscf_day_to_m3_s(self):
        assert qu.Q(1.0, "Mscf/day").to("m3/s").value == pytest.approx(
               28.3168466 / 86_400, rel=1e-9)

    def test_MMscf_day_to_Mscf_day(self):
        assert qu.Q(1.0, "MMscf/day").to("Mscf/day").value == pytest.approx(
               1000.0, rel=1e-9)

    def test_Bscf_day_to_MMscf_day(self):
        assert qu.Q(1.0, "Bscf/day").to("MMscf/day").value == pytest.approx(
               1000.0, rel=1e-9)

    def test_bbl_h_to_bbl_day(self):
        # 1 bbl/h = 24 bbl/day (exact)
        assert qu.Q(1.0, "bbl/h").to("bbl/day").value == pytest.approx(
               24.0, rel=1e-9)

    def test_L_s_to_m3_s(self):
        # 1 L/s = 1e-3 m³/s (exact)
        assert qu.Q(1.0, "L/s").to("m3/s").value == pytest.approx(
               1e-3, rel=1e-10)

    def test_gal_min_to_L_s(self):
        # 1 gal/min = 3.785411784e-3 / 60 m³/s = 0.06309 L/s
        result = qu.Q(1.0, "gal/min").to("L/s").value
        assert result == pytest.approx(3.785_411_784e-3 / 60 * 1e3, rel=1e-6)

    def test_BLPD_equals_bbl_day(self):
        # BLPD is an alias for bbl/day — identical SI factor
        assert qu.Q(1.0, "BLPD").to("m3/s").value == pytest.approx(
               qu.Q(1.0, "bbl/day").to("m3/s").value, rel=1e-10)


# ── Energy ────────────────────────────────────────────────────────────────────

class TestEnergy:

    def test_BOE_to_J(self):
        # SPE: 1 BOE = 5.8 MMBtu_IT = 5.8 × 1.055056e9 J
        assert qu.Q(1.0, "BOE").to("J").value == pytest.approx(6.117e9, rel=1e-3)

    def test_Mcfe_to_J(self):
        # 1 Mcfe = 1 MMBtu_IT = 1.055 056 E+09 J
        assert qu.Q(1.0, "Mcfe").to("J").value == pytest.approx(1.055056e9, rel=1e-6)

    def test_BOE_to_MMBtu(self):
        # 1 BOE = 5.8 MMBtu (SPE convention)
        assert qu.Q(1.0, "BOE").to("MMBtu").value == pytest.approx(5.8, rel=1e-3)


# ── Tagged units ──────────────────────────────────────────────────────────────

class TestTaggedUnits:

    def test_STB_si_factor(self):
        # STB is tagged bbl — same SI factor as bbl
        from quantia._registry import get_unit
        assert get_unit("STB").to_si == pytest.approx(0.158987294928, rel=1e-9)

    def test_RB_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("RB").to_si == pytest.approx(0.158987294928, rel=1e-9)

    def test_Mscf_res_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("Mscf_res").to_si == pytest.approx(28.3168466, rel=1e-9)

    def test_Mscf_st_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("Mscf_st").to_si == pytest.approx(28.3168466, rel=1e-9)

    def test_STB_does_not_cancel_with_RB(self):
        # RB/STB is FVF — must not collapse to dimensionless
        rb  = qu.Q(1.2, "RB")
        stb = qu.Q(1.0, "STB")
        fvf = rb / stb
        assert not fvf.unit.is_dimensionless()

    def test_Sm3_res_does_not_cancel_with_Sm3_st(self):
        gor = qu.Q(150.0, "Sm3_res") / qu.Q(1.0, "Sm3_st")
        assert not gor.unit.is_dimensionless()

    def test_scf_res_does_not_cancel_with_scf_st(self):
        gor = qu.Q(1000.0, "scf_res") / qu.Q(1.0, "scf_st")
        assert not gor.unit.is_dimensionless()

    def test_Mscf_res_does_not_cancel_with_Mscf_st(self):
        gor = qu.Q(1.0, "Mscf_res") / qu.Q(1.0, "Mscf_st")
        assert not gor.unit.is_dimensionless()

    def test_GOR_scf_per_STB_to_Sm3_per_Sm3(self):
        """
        1000 scf_res / STB → Sm3_res/Sm3_st

        SI factor of scf_res/STB:
          to_si(scf_res) / to_si(STB) = 0.0283168466 / 0.158987294928
                                      = 0.17811 m³/m³ per scf/STB

        1000 scf/STB × 0.17811 = 178.11 Sm3/Sm3
        """
        gas = qu.Q(1000.0, "scf_res")
        oil = qu.Q(1.0,    "STB")
        gor = gas / oil

        expected = 1000.0 * 0.0283168466 / 0.158987294928
        assert gor.si_value() == pytest.approx(expected, rel=1e-6)

    def test_FVF_RB_per_STB(self):
        """Bo = 1.2 RB/STB is dimensionless in SI (both m³) but labeled."""
        bo  = qu.Q(1.2, "RB") / qu.Q(1.0, "STB")
        assert bo.si_value() == pytest.approx(1.2, rel=1e-9)
        assert not bo.unit.is_dimensionless()

    def test_OOIP_calculation(self):
        """
        OOIP = Vp [Sm3_res] × (1 - Sw) / Bo [RB/STB → Sm3_res/Sm3_st]

        Vp    = 1 000 000 Sm3_res
        Sw    = 0.25
        Bo    = 1.2 RB/STB  (≈ Sm3_res/Sm3_st, same SI factor)

        OOIP  = 1e6 × 0.75 / 1.2 = 625 000 Sm3_st
              = 625 000 / 0.158987... bbl ≈ 3 931 595 bbl
        """
        Vp  = qu.Q(1_000_000.0, "Sm3_res")
        Sw  = 0.25
        Bo  = qu.Q(1.2, "RB") / qu.Q(1.0, "STB")
        ooip = Vp * (1 - Sw) / Bo
        result = ooip.to("bbl").value
        expected = 1_000_000 * 0.75 / 1.2 / 0.158987294928
        assert result == pytest.approx(expected, rel=1e-6)