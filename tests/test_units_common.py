# tests/test_units_common.py
"""
NIST Table 8 non-SI accepted units added in Step 1.4.
"""
import math
import pytest
import quantia as qu


class TestTimeUnits:

    def test_d_to_s(self):
        # NIST Table 8: 1 d = 86 400 s (exact)
        assert qu.Q(1.0, "d").to("s").value == pytest.approx(86_400.0, rel=1e-10)

    def test_day_alias_for_d(self):
        # "day" must be an alias — same numeric result
        assert qu.Q(1.0, "day").to("s").value == pytest.approx(
               qu.Q(1.0, "d").to("s").value, rel=1e-10)

    def test_week_to_d(self):
        assert qu.Q(1.0, "week").to("d").value == pytest.approx(7.0, rel=1e-10)

    def test_yr_to_d(self):
        assert qu.Q(1.0, "yr").to("d").value == pytest.approx(365.0, rel=1e-10)

    def test_h_to_d(self):
        assert qu.Q(24.0, "h").to("d").value == pytest.approx(1.0, rel=1e-10)


class TestAngleUnits:

    def test_degree_alias(self):
        # "°" must alias "deg" — same SI value
        assert qu.Q(1.0, "°").to("rad").value == pytest.approx(
               qu.Q(1.0, "deg").to("rad").value, rel=1e-10)

    def test_deg_to_rad_nist(self):
        # NIST: 1° = 1.745 329 E-02 rad
        assert qu.Q(1.0, "deg").to("rad").value == pytest.approx(
               math.pi / 180, rel=1e-9)

    def test_arcmin_nist(self):
        # NIST: 1′ = 2.908 882 E-04 rad
        assert qu.Q(1.0, "arcmin").to("rad").value == pytest.approx(
               2.908_882e-4, rel=1e-6)

    def test_prime_alias_for_arcmin(self):
        assert qu.Q(1.0, "′").to("rad").value == pytest.approx(
               qu.Q(1.0, "arcmin").to("rad").value, rel=1e-10)

    def test_arcsec_nist(self):
        # NIST: 1″ = 4.848 137 E-06 rad
        assert qu.Q(1.0, "arcsec").to("rad").value == pytest.approx(
               4.848_137e-6, rel=1e-6)

    def test_60_arcmin_equals_1_deg(self):
        assert qu.Q(60.0, "arcmin").to("deg").value == pytest.approx(1.0, rel=1e-9)

    def test_3600_arcsec_equals_1_deg(self):
        assert qu.Q(3600.0, "arcsec").to("deg").value == pytest.approx(1.0, rel=1e-9)


class TestAreaUnits:

    def test_ha_to_m2(self):
        # NIST Table 8: 1 ha = 1.0 E+04 m² (exact)
        assert qu.Q(1.0, "ha").to("m2").value == pytest.approx(1e4, rel=1e-10)

    def test_ha_to_km2(self):
        # 100 ha = 1 km²
        assert qu.Q(100.0, "ha").to("km2").value == pytest.approx(1.0, rel=1e-10)


class TestMassUnits:

    def test_Da_to_kg(self):
        # NIST Table 8: 1 Da = 1.660 539 040 E-27 kg
        assert qu.Q(1.0, "Da").to("kg").value == pytest.approx(
               1.660_539_040e-27, rel=1e-9)


class TestLogarithmicUnits:

    def test_Np_registered(self):
        from quantia._registry import get_unit
        assert get_unit("Np").symbol == "Np"

    def test_dB_registered(self):
        from quantia._registry import get_unit
        assert get_unit("dB").symbol == "dB"