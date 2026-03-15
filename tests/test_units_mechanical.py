# tests/test_units_mechanical.py
"""
Mechanical unit regression tests.
All values from NIST SP811 / NIST conversion tables.
"""
import math
import pytest
import quantia as qu


class TestAngularVelocity:

    def test_rpm_to_rad_s(self):
        # NIST: 1 rpm = 2π/60 rad/s = 1.047 198 E-01 rad/s
        assert qu.Q(1.0, "rpm").to("rad/s").value == pytest.approx(
               math.pi / 30, rel=1e-9)

    def test_60_rpm_to_rad_s(self):
        # 60 rpm = 2π rad/s (one revolution per second)
        assert qu.Q(60.0, "rpm").to("rad/s").value == pytest.approx(
               2 * math.pi, rel=1e-9)

    def test_rad_s_to_rpm(self):
        assert qu.Q(2 * math.pi, "rad/s").to("rpm").value == pytest.approx(
               60.0, rel=1e-9)


class TestPermeability:

    def test_darcy_to_m2(self):
        # NIST: 1 D = 9.869 233 E-13 m²
        assert qu.Q(1.0, "D").to("m2").value == pytest.approx(9.869_233e-13, rel=1e-6)

    def test_mD_to_D(self):
        # 1 mD = 1e-3 D (exact)
        assert qu.Q(1000.0, "mD").to("D").value == pytest.approx(1.0, rel=1e-9)

    def test_uD_to_mD(self):
        # 1 mD = 1000 µD (exact)
        assert qu.Q(1000.0, "uD").to("mD").value == pytest.approx(1.0, rel=1e-9)

    def test_µD_uD_equivalent(self):
        assert qu.Q(1.0, "µD").to("m2").value == pytest.approx(
               qu.Q(1.0, "uD").to("m2").value, rel=1e-10)

    def test_mD_to_m2(self):
        # 1 mD = 9.869 233 E-16 m²
        assert qu.Q(1.0, "mD").to("m2").value == pytest.approx(9.869_233e-16, rel=1e-6)


class TestDynamicViscosity:

    def test_cP_to_Pa_s(self):
        # NIST: 1 cP = 1.0 E-03 Pa·s (exact)
        assert qu.Q(1.0, "cP").to("Pa_s").value == pytest.approx(1e-3, rel=1e-10)

    def test_P_to_Pa_s(self):
        # NIST: 1 P = 1.0 E-01 Pa·s (exact)
        assert qu.Q(1.0, "P").to("Pa_s").value == pytest.approx(0.1, rel=1e-10)

    def test_100_cP_equals_1_P(self):
        assert qu.Q(100.0, "cP").to("P").value == pytest.approx(1.0, rel=1e-9)

    def test_mPa_s_equals_cP(self):
        # 1 mPa·s = 1 cP (exact — both = 1e-3 Pa·s)
        assert qu.Q(1.0, "mPa_s").to("Pa_s").value == pytest.approx(
               qu.Q(1.0, "cP").to("Pa_s").value, rel=1e-10)

    def test_water_viscosity_at_20C(self):
        # Water at 20°C ≈ 1.002 cP — round-trip sanity
        v = qu.Q(1.002, "cP")
        assert v.to("Pa_s").value == pytest.approx(1.002e-3, rel=1e-6)


class TestKinematicViscosity:

    def test_cSt_to_m2_s(self):
        # NIST: 1 cSt = 1.0 E-06 m²/s (exact)
        assert qu.Q(1.0, "cSt").to("m2/s").value == pytest.approx(1e-6, rel=1e-10)

    def test_St_to_m2_s(self):
        # NIST: 1 St = 1.0 E-04 m²/s (exact)
        assert qu.Q(1.0, "St").to("m2/s").value == pytest.approx(1e-4, rel=1e-10)

    def test_100_cSt_equals_1_St(self):
        assert qu.Q(100.0, "cSt").to("St").value == pytest.approx(1.0, rel=1e-9)


class TestTorque:

    def test_lbf_ft_to_N_m(self):
        # NIST: 1 lbf·ft = 1.355 818 E+00 N·m
        assert qu.Q(1.0, "lbf_ft").si_value() == pytest.approx(1.355_818, rel=1e-6)

    def test_lbf_in_to_N_m(self):
        # NIST: 1 lbf·in = 1.129 848 E-01 N·m
        assert qu.Q(1.0, "lbf_in").si_value() == pytest.approx(1.129_848e-1, rel=1e-6)

    def test_12_lbf_in_equals_1_lbf_ft(self):
        assert qu.Q(12.0, "lbf_in").si_value() == pytest.approx(
               qu.Q(1.0, "lbf_ft").si_value(), rel=1e-9)

    def test_kgf_m_to_N_m(self):
        # NIST: 1 kgf·m = 9.806 65 N·m
        assert qu.Q(1.0, "kgf_m").si_value() == pytest.approx(9.806_65, rel=1e-9)

    def test_N_m_torque_tagged(self):
        # Torque unit must carry a semantic label — does not reduce to J
        u = qu.Q(1.0, "N_m_torque")
        assert str(u.unit) == "N_m_torque"