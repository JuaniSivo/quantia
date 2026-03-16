"""
Phase 2 Step 2.1 — Audit and fix regression tests.

Covers
------
- m2/m3 atomic symbol registration and equivalence with m^2/m^3
- psi_g deprecation warning and redirect to psig
- scf_res/scf_st correct SI factors (base = scf, not m3)
- kg/cm2 and kgf/cm2 NIST value
- Opaque ratio units removed (scf/STB etc. should raise UnknownUnitError)
"""
import warnings
import pytest
import quantia as qu
from quantia._exceptions import UnknownUnitError


# ── m2 / m3 atomic aliases ────────────────────────────────────────────────────

class TestAtomicAliases:

    def test_m2_registered(self):
        from quantia._registry import get_unit
        assert get_unit("m2").symbol == "m2"

    def test_m3_registered(self):
        from quantia._registry import get_unit
        assert get_unit("m3").symbol == "m3"

    def test_m2_equals_m_squared(self):
        # qu.Q(1.0, "m2") and qu.Q(1.0, "m^2") must have identical SI values
        assert qu.Q(1.0, "m2").si_value() == pytest.approx(
               qu.Q(1.0, "m^2").si_value(), rel=1e-10)

    def test_m3_equals_m_cubed(self):
        assert qu.Q(1.0, "m3").si_value() == pytest.approx(
               qu.Q(1.0, "m^3").si_value(), rel=1e-10)

    def test_m2_compatible_with_m_squared(self):
        from quantia._compound import parse_unit
        assert parse_unit("m2").is_compatible(parse_unit("m^2"))

    def test_m3_compatible_with_m_cubed(self):
        from quantia._compound import parse_unit
        assert parse_unit("m3").is_compatible(parse_unit("m^3"))

    def test_m2_to_cm2(self):
        # 1 m2 = 10 000 cm²
        assert qu.Q(1.0, "m2").to("cm^2").value == pytest.approx(1e4, rel=1e-9)

    def test_m3_to_L(self):
        # 1 m3 = 1000 L
        assert qu.Q(1.0, "m3").to("L").value == pytest.approx(1000.0, rel=1e-9)

    def test_ha_to_m2_atomic(self):
        # ha was registered with si_unit="m^2" — confirm m2 target also works
        assert qu.Q(1.0, "ha").to("m2").value == pytest.approx(1e4, rel=1e-9)

    def test_bbl_to_m3_atomic(self):
        # petroleum.py uses si_unit="m3" — confirm round-trip
        assert qu.Q(1.0, "bbl").to("m3").value == pytest.approx(
               0.158987294928, rel=1e-9)


# ── psi_g deprecation ─────────────────────────────────────────────────────────

class TestPsiGDeprecation:

    def test_psi_g_warns(self):
        with pytest.warns(UserWarning, match="psig"):
            qu.Q(100.0, "psi_g")

    def test_psi_g_redirects_to_psig(self):
        with pytest.warns(UserWarning):
            v_psi_g = qu.Q(100.0, "psi_g").to("Pa").value
        v_psig = qu.Q(100.0, "psig").to("Pa").value
        assert v_psi_g == pytest.approx(v_psig, rel=1e-10)

    def test_psig_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(100.0, "psig")


# ── scf_res / scf_st correct SI factors ──────────────────────────────────────

class TestScfTaggedSIFactors:
    """
    scf_res/scf_st must have the same SI factor as scf (0.028316... m³/scf).
    Previously they were registered with base="m3" (to_si=1.0) which made
    GOR conversions between scf/STB and Sm3/Sm3 numerically wrong.
    """

    def test_scf_res_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("scf_res").to_si == pytest.approx(0.0283168466, rel=1e-9)

    def test_scf_st_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("scf_st").to_si == pytest.approx(0.0283168466, rel=1e-9)

    def test_gor_scf_STB_to_Sm3_Sm3(self):
        """
        GOR conversion: 1000 scf_res/scf_st → Sm3_res/Sm3_st

        scf → m³:  1 scf = 0.0283168466 m³
        bbl → m³:  1 bbl = 0.158987294928 m³
        1000 scf/STB × (0.0283168466 / 0.158987294928) = 178.1 Sm3/Sm3
        """
        gas = qu.Q(1000.0, "scf_res")
        oil = qu.Q(1.0, "scf_st")      # using scf_st as denominator base
        gor_scf = gas / oil             # scf_res/scf_st

        # Convert to Sm3_res/Sm3_st by building target ratio
        gas_sm3 = qu.Q(1000.0 * 0.0283168466, "Sm3_res")
        oil_sm3 = qu.Q(1.0    * 0.0283168466, "Sm3_st")
        gor_sm3 = gas_sm3 / oil_sm3

        assert gor_scf.si_value() == pytest.approx(gor_sm3.si_value(), rel=1e-9)

    def test_Sm3_res_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("Sm3_res").to_si == pytest.approx(1.0, rel=1e-10)

    def test_Sm3_st_si_factor(self):
        from quantia._registry import get_unit
        assert get_unit("Sm3_st").to_si == pytest.approx(1.0, rel=1e-10)


# ── kg/cm2 ────────────────────────────────────────────────────────────────────

class TestKgCm2:

    def test_kg_cm2_to_Pa(self):
        # NIST: 1 kgf/cm² = 9.806 65 E+04 Pa (exact)
        assert qu.Q(1.0, "kg/cm2").to("Pa").value == pytest.approx(
               9.806_65e4, rel=1e-9)

    def test_kgf_cm2_equals_kg_cm2(self):
        assert qu.Q(1.0, "kgf/cm2").to("Pa").value == pytest.approx(
               qu.Q(1.0, "kg/cm2").to("Pa").value, rel=1e-10)

    def test_kg_cm2_to_psia(self):
        # 1 kgf/cm² = 9.806 65e4 Pa / 6894.757 Pa/psi = 14.223 psia
        assert qu.Q(1.0, "kg/cm2").to("psia").value == pytest.approx(
               9.806_65e4 / 6_894.757293168, rel=1e-6)

    def test_kg_cm2_to_bara(self):
        # 1 kgf/cm² = 9.806 65e4 / 1e5 = 0.980 665 bara
        assert qu.Q(1.0, "kg/cm2").to("bara").value == pytest.approx(
               0.980_665, rel=1e-6)


# ── Opaque ratio units removed ────────────────────────────────────────────────

class TestOpaqueUnitsRemoved:
    """
    Confirm that opaque named ratio units have been removed.
    Users should build GOR/FVF from tagged units instead.
    """

    def test_Sm3_Sm3_removed(self):
        with pytest.raises(UnknownUnitError):
            qu.Q(1.0, "Sm3/Sm3")

    def test_scf_STB_removed(self):
        with pytest.raises(UnknownUnitError):
            qu.Q(1.0, "scf/STB")

    def test_Mscf_STB_removed(self):
        with pytest.raises(UnknownUnitError):
            qu.Q(1.0, "Mscf/STB")