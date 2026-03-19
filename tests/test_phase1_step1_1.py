"""
Phase 1 Step 1.1 — Regression tests.

Every conversion value is traced to NIST SP811 or the NIST unit conversion
tables. These tests must never be deleted — they lock the conversion factors
against accidental future changes.
"""
import warnings
import pytest
import quantia as qu
from quantia._registry import _REGISTRY


# ── 1.1.1  Duplicate registration guard ──────────────────────────────────────

class TestDuplicateGuard:

    def test_duplicate_raises_by_default(self):
        from quantia._registry import register, Unit
        with pytest.raises(ValueError, match="already registered"):
            register("m", Unit("metre", "length", "m", 1.0, "m"))

    def test_duplicate_allowed_with_overwrite(self):
        from quantia._registry import register, Unit, get_unit
        original = get_unit("m").to_si
        register("m", Unit("metre", "length", "m", 1.0, "m"), overwrite=True)
        assert get_unit("m").to_si == original  # same value, just re-registered

    def test_new_symbol_registers_cleanly(self):
        # Registering a brand-new symbol must not raise
        from quantia._registry import register, Unit
        register("_test_unit_", Unit("test", "test", "m", 1.0, "_test_unit_"))
        assert "_test_unit_" in _REGISTRY
        # Cleanup
        del _REGISTRY["_test_unit_"]


# ── 1.1.2  Corrected conversion factors ──────────────────────────────────────

class TestCorrectedFactors:

    def test_knot_exact_nist(self):
        # NIST: 1 kn = 1852 m / 3600 s exactly (international nautical mile)
        assert qu.Q(1.0, "kn").to("m/s").value == pytest.approx(1852 / 3600, rel=1e-10)

    def test_knot_not_truncated(self):
        # Old value 0.514444 was truncated; 1852/3600 = 0.514444... recurring
        result = qu.Q(1.0, "kn").to("m/s").value
        assert result != pytest.approx(0.514444, rel=1e-7)

    def test_mph_exact_nist(self):
        # NIST: 1 mph = 4.4704 E-01 m/s (exact)
        assert qu.Q(1.0, "mph").to("m/s").value == pytest.approx(0.44704, rel=1e-10)

    def test_lbf_nist(self):
        # NIST: 1 lbf = 4.448 222 E+00 N
        assert qu.Q(1.0, "lbf").to("N").value == pytest.approx(4.4482216152605, rel=1e-9)

    def test_lb_nist(self):
        # NIST: 1 lb = 4.535 924 E-01 kg (exact)
        assert qu.Q(1.0, "lb").to("kg").value == pytest.approx(0.45359237, rel=1e-10)


# ── 1.1.3  Ambiguous unit warnings ───────────────────────────────────────────

class TestAmbiguousWarnings:

    def test_BTU_warns(self):
        with pytest.warns(UserWarning, match="BTU_IT"):
            qu.Q(1.0, "BTU")

    def test_BTU_redirects_to_IT(self):
        with pytest.warns(UserWarning):
            val = qu.Q(1.0, "BTU").to("J").value
        assert val == pytest.approx(1_055.056, rel=1e-5)

    def test_cal_warns(self):
        with pytest.warns(UserWarning, match="cal_th"):
            qu.Q(1.0, "cal")

    def test_kcal_warns(self):
        with pytest.warns(UserWarning, match="kcal_th"):
            qu.Q(1.0, "kcal")

    def test_BTU_IT_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning → error
            qu.Q(1.0, "BTU_IT")             # must not warn

    def test_BTU_th_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(1.0, "BTU_th")

    def test_cal_th_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(1.0, "cal_th")


# ── 1.1.3  BTU and calorie NIST values ───────────────────────────────────────

class TestBTUValues:

    def test_BTU_IT_nist(self):
        # NIST SP811: 1 BTU_IT = 1.055 056 E+03 J
        assert qu.Q(1.0, "BTU_IT").to("J").value == pytest.approx(1_055.056, rel=1e-6)

    def test_BTU_th_nist(self):
        # NIST SP811: 1 BTU_th = 1.054 350 E+03 J
        assert qu.Q(1.0, "BTU_th").to("J").value == pytest.approx(1_054.350, rel=1e-6)

    def test_BTU_IT_and_th_are_different(self):
        it = qu.Q(1.0, "BTU_IT").to("J").value
        th = qu.Q(1.0, "BTU_th").to("J").value
        assert abs(it - th) > 0.5  # they differ by ~0.7 J


class TestCalorieValues:

    def test_cal_th_nist(self):
        # NIST SP811: 1 cal_th = 4.184 J (exact)
        assert qu.Q(1.0, "cal_th").to("J").value == pytest.approx(4.184, rel=1e-10)

    def test_cal_IT_nist(self):
        # NIST SP811: 1 cal_IT = 4.1868 J
        assert qu.Q(1.0, "cal_IT").to("J").value == pytest.approx(4.1868, rel=1e-6)

    def test_kcal_th_nist(self):
        # NIST SP811: 1 kcal_th = 4.184 E+03 J
        assert qu.Q(1.0, "kcal_th").to("J").value == pytest.approx(4_184.0, rel=1e-10)

    def test_kcal_IT_nist(self):
        # NIST SP811: 1 kcal_IT = 4.1868 E+03 J
        assert qu.Q(1.0, "kcal_IT").to("J").value == pytest.approx(4_186.8, rel=1e-6)

    def test_cal_th_and_IT_are_different(self):
        assert qu.Q(1.0, "cal_th").to("J").value != pytest.approx(
            qu.Q(1.0, "cal_IT").to("J").value, rel=1e-4)


# ── 1.1.4  No duplicate registrations (atm/bar/mmHg only in common.py) ───────

class TestNoDuplicates:

    def test_atm_value_nist(self):
        # NIST: 1 atm = 1.013 25 E+05 Pa (exact by definition)
        assert qu.Q(1.0, "atm").to("Pa").value == pytest.approx(101_325.0, rel=1e-10)

    def test_bar_value_nist(self):
        # NIST: 1 bar = 1.0 E+05 Pa (exact)
        # "bar" is ambiguous — warns and redirects to "bara"
        with pytest.warns(UserWarning, match="bara"):
            val = qu.Q(1.0, "bar").to("Pa").value
        assert val == pytest.approx(100_000.0, rel=1e-10)

    def test_mmHg_value_nist(self):
        # NIST: 1 mmHg = 1.333 224 E+02 Pa
        assert qu.Q(1.0, "mmHg").to("Pa").value == pytest.approx(133.322387415, rel=1e-9)

    def test_atm_registered_exactly_once(self):
        # After removing from imperial.py, the registry must contain exactly one entry
        from quantia._registry import _REGISTRY
        assert "atm" in _REGISTRY
        # Count is implicitly 1 because dict keys are unique —
        # this test catches the case where the module fails to import due to the
        # duplicate guard raising during startup
        assert _REGISTRY["atm"].to_si == pytest.approx(101_325.0, rel=1e-10)


class TestCompoundSiUnitBugFix:
    """
    Regression tests for the to_si_compound() bug where units registered
    with a compound si_unit string (e.g. "m/s", "m3/s") were incompatible
    with their parsed equivalents.

    This affected: kn, mph, bbl/day, m3/day, Mscf/day, and any future
    unit registered with a compound si_unit string.
    """

    def test_kn_compatible_with_parsed_m_per_s(self):
        from quantia._compound import parse_unit
        kn_cu  = parse_unit("kn")
        mps_cu = parse_unit("m/s")
        assert kn_cu.is_compatible(mps_cu)

    def test_mph_compatible_with_parsed_m_per_s(self):
        from quantia._compound import parse_unit
        assert parse_unit("mph").is_compatible(parse_unit("m/s"))

    def test_bbl_day_compatible_with_m3_per_s(self):
        from quantia._compound import parse_unit
        assert parse_unit("bbl/day").is_compatible(parse_unit("m3/s"))

    def test_kn_to_mph_round_trip(self):
        # Cross-unit speed conversion — both go through SI base
        result = qu.Q(1.0, "kn").to("mph").value
        # 1 kn = 1852/3600 m/s; 1 mph = 0.44704 m/s
        expected = (1852 / 3600) / 0.44704
        assert result == pytest.approx(expected, rel=1e-9)

    def test_flow_rate_conversion(self):
        # bbl/day → m3/s — previously raised IncompatibleUnitsError
        result = qu.Q(1.0, "bbl/day").to("m3/s").value
        expected = 0.158987294928 / 86_400
        assert result == pytest.approx(expected, rel=1e-6)