# tests/test_units_electromagnetic.py
"""
Electromagnetic unit regression tests — NIST SP811 and conversion tables.
"""
import pytest
import quantia as qu


class TestElectricCharge:

    def test_A_h_to_C(self):
        # NIST: 1 A·h = 3.6 E+03 C (exact)
        assert qu.Q(1.0, "A_h").to("C").value == pytest.approx(3600.0, rel=1e-10)

    def test_C_to_A_h(self):
        assert qu.Q(3600.0, "C").to("A_h").value == pytest.approx(1.0, rel=1e-10)


class TestMagneticFluxDensity:

    def test_gauss_to_T(self):
        # NIST: 1 G = 1.0 E-04 T (exact)
        assert qu.Q(1.0, "G").to("T").value == pytest.approx(1e-4, rel=1e-10)

    def test_10000_G_equals_1_T(self):
        assert qu.Q(10_000.0, "G").to("T").value == pytest.approx(1.0, rel=1e-9)

    def test_mT_to_T(self):
        assert qu.Q(1.0, "mT").to("T").value == pytest.approx(1e-3, rel=1e-10)

    def test_uT_to_T(self):
        assert qu.Q(1.0, "uT").to("T").value == pytest.approx(1e-6, rel=1e-10)

    def test_nT_to_T(self):
        # nT commonly used in geophysics
        assert qu.Q(1.0, "nT").to("T").value == pytest.approx(1e-9, rel=1e-10)

    def test_µT_uT_equivalent(self):
        assert qu.Q(1.0, "µT").to("T").value == pytest.approx(
               qu.Q(1.0, "uT").to("T").value, rel=1e-10)


class TestMagneticFlux:

    def test_maxwell_to_Wb(self):
        # NIST: 1 Mx = 1.0 E-08 Wb (exact)
        assert qu.Q(1.0, "Mx").to("Wb").value == pytest.approx(1e-8, rel=1e-10)

    def test_mWb_to_Wb(self):
        assert qu.Q(1.0, "mWb").to("Wb").value == pytest.approx(1e-3, rel=1e-10)


class TestResistivity:

    def test_Ω_m_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Ω_m").quantity == "resistivity"

    def test_uΩ_m_to_Ω_m(self):
        assert qu.Q(1.0, "uΩ_m").to("Ω_m").value == pytest.approx(1e-6, rel=1e-10)

    def test_µΩ_m_uΩ_m_equivalent(self):
        assert qu.Q(1.0, "µΩ_m").to("Ω_m").value == pytest.approx(
               qu.Q(1.0, "uΩ_m").to("Ω_m").value, rel=1e-10)