"""
SI unit regression tests — NIST SP811 Table 4 completions and
prefixed variants added in Step 1.4.

All base SI units (m, kg, s, A, K, mol, cd) are covered implicitly
by existing tests. This file targets the new registrations only.
"""
import pytest
import quantia as qu


class TestTable4Completions:
    """NIST Table 4 — 22 named SI derived units."""

    def test_sr_registered(self):
        from quantia._registry import get_unit
        assert get_unit("sr").symbol == "sr"

    def test_coulomb_registered(self):
        from quantia._registry import get_unit
        assert get_unit("C").quantity == "electric_charge"

    def test_siemens_registered(self):
        from quantia._registry import get_unit
        assert get_unit("S").quantity == "electric_conductance"

    def test_weber_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Wb").quantity == "magnetic_flux"

    def test_tesla_registered(self):
        from quantia._registry import get_unit
        assert get_unit("T").quantity == "magnetic_flux_density"

    def test_lumen_registered(self):
        from quantia._registry import get_unit
        assert get_unit("lm").quantity == "luminous_flux"

    def test_lux_registered(self):
        from quantia._registry import get_unit
        assert get_unit("lx").quantity == "illuminance"

    def test_becquerel_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Bq").quantity == "radioactivity"

    def test_gray_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Gy").quantity == "absorbed_dose"

    def test_sievert_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Sv").quantity == "dose_equivalent"

    def test_katal_registered(self):
        from quantia._registry import get_unit
        assert get_unit("kat").quantity == "catalytic_activity"


class TestPrefixedFrequency:

    def test_GHz_to_Hz(self):
        assert qu.Q(1.0, "GHz").to("Hz").value == pytest.approx(1e9, rel=1e-10)

    def test_THz_to_Hz(self):
        assert qu.Q(1.0, "THz").to("Hz").value == pytest.approx(1e12, rel=1e-10)

    def test_kHz_to_MHz(self):
        assert qu.Q(1000.0, "kHz").to("MHz").value == pytest.approx(1.0, rel=1e-10)


class TestPrefixedForce:

    def test_MN_to_N(self):
        assert qu.Q(1.0, "MN").to("N").value == pytest.approx(1e6, rel=1e-10)

    def test_mN_to_N(self):
        assert qu.Q(1.0, "mN").to("N").value == pytest.approx(1e-3, rel=1e-10)

    def test_uN_to_N(self):
        assert qu.Q(1.0, "uN").to("N").value == pytest.approx(1e-6, rel=1e-10)

    def test_µN_uN_equivalent(self):
        assert qu.Q(1.0, "µN").to("N").value == pytest.approx(
               qu.Q(1.0, "uN").to("N").value, rel=1e-10)


class TestPrefixedPower:

    def test_GW_to_W(self):
        assert qu.Q(1.0, "GW").to("W").value == pytest.approx(1e9, rel=1e-10)

    def test_mW_to_W(self):
        assert qu.Q(1.0, "mW").to("W").value == pytest.approx(1e-3, rel=1e-10)

    def test_uW_to_W(self):
        assert qu.Q(1.0, "uW").to("W").value == pytest.approx(1e-6, rel=1e-10)


class TestPrefixedPressure:

    def test_GPa_to_Pa(self):
        assert qu.Q(1.0, "GPa").to("Pa").value == pytest.approx(1e9, rel=1e-10)

    def test_GPa_to_MPa(self):
        assert qu.Q(1.0, "GPa").to("MPa").value == pytest.approx(1000.0, rel=1e-10)

    def test_uPa_to_Pa(self):
        assert qu.Q(1.0, "uPa").to("Pa").value == pytest.approx(1e-6, rel=1e-10)


class TestPrefixedElectrical:

    def test_uA_to_A(self):
        assert qu.Q(1.0, "uA").to("A").value == pytest.approx(1e-6, rel=1e-10)

    def test_nA_to_A(self):
        assert qu.Q(1.0, "nA").to("A").value == pytest.approx(1e-9, rel=1e-10)

    def test_uV_to_V(self):
        assert qu.Q(1.0, "uV").to("V").value == pytest.approx(1e-6, rel=1e-10)

    def test_MΩ_to_Ω(self):
        assert qu.Q(1.0, "MΩ").to("Ω").value == pytest.approx(1e6, rel=1e-10)

    def test_nF_to_F(self):
        assert qu.Q(1.0, "nF").to("F").value == pytest.approx(1e-9, rel=1e-10)

    def test_pF_to_F(self):
        assert qu.Q(1.0, "pF").to("F").value == pytest.approx(1e-12, rel=1e-10)

    def test_uF_to_mF(self):
        assert qu.Q(1000.0, "uF").to("mF").value == pytest.approx(1.0, rel=1e-10)

    def test_mH_to_H(self):
        assert qu.Q(1.0, "mH").to("H").value == pytest.approx(1e-3, rel=1e-10)

    def test_uH_to_H(self):
        assert qu.Q(1.0, "uH").to("H").value == pytest.approx(1e-6, rel=1e-10)


class TestPrefixedAmount:

    def test_mmol_to_mol(self):
        assert qu.Q(1.0, "mmol").to("mol").value == pytest.approx(1e-3, rel=1e-10)

    def test_umol_to_mol(self):
        assert qu.Q(1.0, "umol").to("mol").value == pytest.approx(1e-6, rel=1e-10)

    def test_nmol_to_mol(self):
        assert qu.Q(1.0, "nmol").to("mol").value == pytest.approx(1e-9, rel=1e-10)