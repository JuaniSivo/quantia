# tests/test_units_imperial.py
"""
Imperial / US customary unit regression tests.
All values from NIST SP811 conversion tables.
"""
import pytest
import quantia as qu


class TestLength:

    def test_angstrom_to_m(self):
        # NIST: 1 Å = 1.0 E-10 m (exact)
        assert qu.Q(1.0, "Å").to("m").value == pytest.approx(1e-10, rel=1e-10)

    def test_angstrom_to_nm(self):
        # NIST: 1 Å = 0.1 nm
        assert qu.Q(1.0, "Å").to("nm").value == pytest.approx(0.1, rel=1e-10)

    def test_nmi_to_m(self):
        # NIST: 1 nmi = 1852 m (exact)
        assert qu.Q(1.0, "nmi").to("m").value == pytest.approx(1852.0, rel=1e-10)

    def test_mil_to_m(self):
        # NIST: 1 mil = 2.54 E-05 m (exact)
        assert qu.Q(1.0, "mil").to("m").value == pytest.approx(2.54e-5, rel=1e-10)

    def test_mil_to_in(self):
        # 1000 mil = 1 inch
        assert qu.Q(1000.0, "mil").to("in").value == pytest.approx(1.0, rel=1e-9)


class TestArea:

    def test_ft2_to_m2(self):
        # NIST: 9.290 304 E-02 m² (exact)
        assert qu.Q(1.0, "ft2").to("m2").value == pytest.approx(9.290_304e-2, rel=1e-10)

    def test_in2_to_m2(self):
        # NIST: 6.4516 E-04 m² (exact)
        assert qu.Q(1.0, "in2").to("m2").value == pytest.approx(6.4516e-4, rel=1e-10)

    def test_yd2_to_m2(self):
        # NIST: 8.361 274 E-01 m²
        assert qu.Q(1.0, "yd2").to("m2").value == pytest.approx(8.361_274e-1, rel=1e-6)

    def test_mi2_to_m2(self):
        # NIST: 2.589 988 E+06 m²
        assert qu.Q(1.0, "mi2").to("m2").value == pytest.approx(2.589_988e6, rel=1e-6)

    def test_acre_to_m2(self):
        # NIST: 4.046 873 E+03 m²
        assert qu.Q(1.0, "acre").to("m2").value == pytest.approx(4.046_873e3, rel=1e-6)

    def test_144_in2_equals_1_ft2(self):
        assert qu.Q(144.0, "in2").to("ft2").value == pytest.approx(1.0, rel=1e-9)


class TestVolume:

    def test_ft3_to_m3(self):
        # NIST: 2.831 685 E-02 m³
        assert qu.Q(1.0, "ft3").to("m3").value == pytest.approx(2.831_685e-2, rel=1e-6)

    def test_in3_to_m3(self):
        # NIST: 1.638 706 E-05 m³
        assert qu.Q(1.0, "in3").to("m3").value == pytest.approx(1.638_706e-5, rel=1e-6)

    def test_gal_to_L(self):
        # NIST: 1 US gal = 3.785 412 E-03 m³ = 3.785 412 L
        assert qu.Q(1.0, "gal").to("L").value == pytest.approx(3.785_412, rel=1e-6)

    def test_gal_imp_to_L(self):
        # NIST: 1 Imperial gal = 4.546 09 E-03 m³ = 4.546 09 L
        assert qu.Q(1.0, "gal_imp").to("L").value == pytest.approx(4.546_09, rel=1e-6)

    def test_fl_oz_to_mL(self):
        # NIST: 2.957 353 E-05 m³ = 29.57 mL
        assert qu.Q(1.0, "fl_oz").to("mL").value == pytest.approx(29.57_353, rel=1e-6)

    def test_pt_to_L(self):
        # NIST: 4.731 765 E-04 m³ = 0.4731 L
        assert qu.Q(1.0, "pt").to("L").value == pytest.approx(0.4731_765, rel=1e-6)

    def test_8_pt_equals_1_gal(self):
        assert qu.Q(8.0, "pt").to("gal").value == pytest.approx(1.0, rel=1e-9)


class TestMass:

    def test_gr_to_mg(self):
        # NIST: 1 gr = 6.479 891 E-05 kg = 64.79 mg
        assert qu.Q(1.0, "gr").to("mg").value == pytest.approx(64.79_891, rel=1e-6)

    def test_slug_to_kg(self):
        # NIST: 1 slug = 1.459 390 E+01 kg
        assert qu.Q(1.0, "slug").to("kg").value == pytest.approx(14.59_390, rel=1e-6)

    def test_ton_short_to_lb(self):
        # 1 short ton = 2000 lb (exact by definition)
        assert qu.Q(1.0, "ton_short").to("lb").value == pytest.approx(2000.0, rel=1e-9)

    def test_ton_long_to_lb(self):
        # 1 long ton = 2240 lb (exact by definition)
        assert qu.Q(1.0, "ton_long").to("lb").value == pytest.approx(2240.0, rel=1e-9)

    def test_ton_long_gt_ton_short(self):
        assert qu.Q(1.0, "ton_long").to("kg").value > qu.Q(1.0, "ton_short").to("kg").value


class TestForce:

    def test_dyn_to_N(self):
        # NIST: 1 dyn = 1.0 E-05 N (exact)
        assert qu.Q(1.0, "dyn").to("N").value == pytest.approx(1e-5, rel=1e-10)

    def test_kgf_to_N(self):
        # NIST: 1 kgf = 9.806 65 N (exact — standard gravity)
        assert qu.Q(1.0, "kgf").to("N").value == pytest.approx(9.806_65, rel=1e-9)

    def test_kip_to_lbf(self):
        # 1 kip = 1000 lbf (exact by definition)
        assert qu.Q(1.0, "kip").to("lbf").value == pytest.approx(1000.0, rel=1e-9)

    def test_ozf_to_lbf(self):
        # 1 lbf = 16 ozf (exact)
        assert qu.Q(16.0, "ozf").to("lbf").value == pytest.approx(1.0, rel=1e-9)

    def test_pdl_to_N(self):
        # NIST: 1.382 550 E-01 N
        assert qu.Q(1.0, "pdl").to("N").value == pytest.approx(1.382_550e-1, rel=1e-6)


class TestPressure:

    def test_ksi_to_psia(self):
        # NIST: 1 ksi = 6.894 757 E+06 Pa; 1 psia = 6.894 757 E+03 Pa
        # → 1 ksi = 1000 psia (exact)
        assert qu.Q(1.0, "ksi").to("psia").value == pytest.approx(1000.0, rel=1e-9)

    def test_torr_to_Pa(self):
        # NIST: 1 torr = 1.333 224 E+02 Pa
        assert qu.Q(1.0, "torr").to("Pa").value == pytest.approx(133.3_224, rel=1e-6)

    def test_mmHg_torr_nearly_equal(self):
        # torr and mmHg are very close but not identical
        torr_pa = qu.Q(1.0, "torr").to("Pa").value
        mmhg_pa = qu.Q(1.0, "mmHg").to("Pa").value
        assert abs(torr_pa - mmhg_pa) < 0.001   # differ by < 0.001 Pa

    def test_inHg_to_Pa(self):
        # NIST: 3.386 389 E+03 Pa
        assert qu.Q(1.0, "inHg").to("Pa").value == pytest.approx(3.386_389e3, rel=1e-6)

    def test_mbar_to_Pa(self):
        # NIST: 1 mbar = 1.0 E+02 Pa (exact)
        assert qu.Q(1.0, "mbar").to("Pa").value == pytest.approx(100.0, rel=1e-10)

    def test_1000_mbar_equals_1_bara(self):
        assert qu.Q(1000.0, "mbar").to("bara").value == pytest.approx(1.0, rel=1e-9)


class TestEnergy:

    def test_ft_lbf_to_J(self):
        # NIST: 1 ft·lbf = 1.355 818 E+00 J
        assert qu.Q(1.0, "ft_lbf").to("J").value == pytest.approx(1.355_818, rel=1e-6)

    def test_therm_EC_to_BTU_IT(self):
        # 1 therm_EC = 100 000 BTU_IT (exact by EC definition)
        assert qu.Q(1.0, "therm_EC").to("BTU_IT").value == pytest.approx(100_000.0, rel=1e-6)

    def test_MMBtu_to_BTU_IT(self):
        # 1 MMBtu = 1e6 BTU_IT (exact)
        assert qu.Q(1.0, "MMBtu").to("BTU_IT").value == pytest.approx(1e6, rel=1e-6)

    def test_erg_to_J(self):
        # NIST: 1 erg = 1.0 E-07 J (exact)
        assert qu.Q(1.0, "erg").to("J").value == pytest.approx(1e-7, rel=1e-10)


class TestTemperatureRankine:

    def test_rankine_to_kelvin(self):
        # NIST: T(K) = T(°R) × 5/9
        assert qu.Q(1.0, "°R").to("K").value == pytest.approx(5/9, rel=1e-9)

    def test_absolute_zero_rankine(self):
        # 0 °R = 0 K (both absolute scales)
        assert qu.Q(0.0, "°R").to("K").value == pytest.approx(0.0, abs=1e-10)

    def test_459_67_rankine_to_fahrenheit(self):
        # 459.67 °R = 0 °F = 255.372 K
        assert qu.Q(459.67, "°R").to("°F").value == pytest.approx(0.0, abs=1e-3)

    def test_671_67_rankine_to_fahrenheit(self):
        # 671.67 °R = 212 °F (boiling point of water)
        assert qu.Q(671.67, "°R").to("°F").value == pytest.approx(212.0, abs=1e-2)


class TestVelocity:

    def test_ft_s_to_m_s(self):
        # NIST: 1 ft/s = 3.048 E-01 m/s (exact)
        assert qu.Q(1.0, "ft/s").to("m/s").value == pytest.approx(0.3048, rel=1e-10)

    def test_ft_min_to_m_s(self):
        # NIST: 5.08 E-03 m/s (exact)
        assert qu.Q(1.0, "ft/min").to("m/s").value == pytest.approx(5.08e-3, rel=1e-10)

    def test_km_h_to_m_s(self):
        # NIST: 2.777 778 E-01 m/s (exact)
        assert qu.Q(1.0, "km/h").to("m/s").value == pytest.approx(1/3.6, rel=1e-9)

    def test_60_ft_min_equals_1_ft_s(self):
        assert qu.Q(60.0, "ft/min").to("ft/s").value == pytest.approx(1.0, rel=1e-9)