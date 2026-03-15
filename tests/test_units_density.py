# tests/test_units_density.py
"""
Density and concentration unit regression tests.
All values from NIST SP811 (Mass Divided by Volume).
"""
import pytest
import quantia as qu


class TestMassDensity:

    def test_g_cm3_to_kg_m3(self):
        # NIST: 1 g/cm³ = 1.0 E+03 kg/m³ (exact)
        assert qu.Q(1.0, "g/cm3").to("kg/m3").value == pytest.approx(1e3, rel=1e-10)

    def test_kg_L_to_kg_m3(self):
        # 1 kg/L = 1000 kg/m³ (exact)
        assert qu.Q(1.0, "kg/L").to("kg/m3").value == pytest.approx(1e3, rel=1e-10)

    def test_g_cm3_equals_kg_L(self):
        assert qu.Q(1.0, "g/cm3").to("kg/m3").value == pytest.approx(
               qu.Q(1.0, "kg/L").to("kg/m3").value, rel=1e-10)

    def test_g_mL_equals_g_cm3(self):
        assert qu.Q(1.0, "g/mL").to("kg/m3").value == pytest.approx(
               qu.Q(1.0, "g/cm3").to("kg/m3").value, rel=1e-10)

    def test_lb_ft3_to_kg_m3(self):
        # NIST: 1 lb/ft³ = 1.601 846 E+01 kg/m³
        assert qu.Q(1.0, "lb/ft3").to("kg/m3").value == pytest.approx(
               16.01_846, rel=1e-6)

    def test_lb_gal_to_kg_m3(self):
        # NIST: 1 lb/gal = 1.198 264 E+02 kg/m³
        assert qu.Q(1.0, "lb/gal").to("kg/m3").value == pytest.approx(
               119.8_264, rel=1e-6)

    def test_lb_in3_to_kg_m3(self):
        # NIST: 2.767 990 E+04 kg/m³
        assert qu.Q(1.0, "lb/in3").to("kg/m3").value == pytest.approx(
               2.767_990e4, rel=1e-6)

    def test_sg_water_to_kg_m3(self):
        # sg=1 → 1000 kg/m³ (water at 4°C by definition)
        assert qu.Q(1.0, "sg").to("kg/m3").value == pytest.approx(1e3, rel=1e-10)

    def test_sg_equals_g_cm3(self):
        # sg=1 and g/cm3=1 both represent the same density
        assert qu.Q(1.0, "sg").to("kg/m3").value == pytest.approx(
               qu.Q(1.0, "g/cm3").to("kg/m3").value, rel=1e-10)

    def test_typical_oil_density(self):
        # Light crude: ~850 kg/m³ = 0.85 g/cm³ = 0.85 sg
        oil = qu.Q(850.0, "kg/m3")
        assert oil.to("g/cm3").value == pytest.approx(0.85, rel=1e-9)
        assert oil.to("sg").value    == pytest.approx(0.85, rel=1e-9)

    def test_typical_mud_weight_lb_gal(self):
        # Typical drilling mud: 10 lb/gal (ppg) → 1198 kg/m³
        assert qu.Q(10.0, "lb/gal").to("kg/m3").value == pytest.approx(
               1198.264, rel=1e-6)


class TestConcentration:

    def test_mg_L_to_kg_m3(self):
        # 1 mg/L = 1e-3 g / 1e-3 m³ = 1e-3 kg/m³
        assert qu.Q(1.0, "mg/L").to("kg/m3").value == pytest.approx(1e-3, rel=1e-10)

    def test_ppm_equals_mg_L(self):
        # For dilute aqueous solutions: 1 ppm ≈ 1 mg/L
        assert qu.Q(1.0, "ppm").to("kg/m3").value == pytest.approx(
               qu.Q(1.0, "mg/L").to("kg/m3").value, rel=1e-10)

    def test_ppb_to_ppm(self):
        # 1000 ppb = 1 ppm
        assert qu.Q(1000.0, "ppb").to("ppm").value == pytest.approx(1.0, rel=1e-9)

    def test_ppb_to_mg_L(self):
        # 1 ppb = 0.001 mg/L = 1 µg/L
        assert qu.Q(1.0, "ppb").to("mg/L").value == pytest.approx(1e-3, rel=1e-9)