# tests/test_phase1_step1_3.py
"""
Phase 1 Step 1.3 — Pressure hierarchy regression tests.

Covers
------
- psia, psig, bara, barg registration and NIST values
- Gauge ↔ absolute conversions  (mirrors °C ↔ K pattern)
- Cross-family conversions       (psig → bara, psig → Pa, etc.)
- Ambiguous warnings for "psi" and "bar"
- AffineUnit generalization      (temperature still works)
- ProbUnitFloat pressure paths
- Error cases

All pressure values traced to NIST SP811.
Standard atmosphere offset: 101 325 Pa (exact).
"""
import warnings
import pytest
import quantia as qu
from quantia.prob._scalar import ProbUnitFloat


ATM_PA = 101_325.0          # standard atmosphere, Pa (exact)
PSI_TO_PA = 6_894.757293168  # NIST: 6.894 757 E+03 Pa/psi


# ── Registration ──────────────────────────────────────────────────────────────

class TestRegistration:

    def test_psia_registered(self):
        from quantia._registry import get_unit
        u = get_unit("psia")
        assert u.symbol == "psia"

    def test_psig_registered(self):
        from quantia._registry import get_unit
        u = get_unit("psig")
        assert u.symbol == "psig"

    def test_bara_registered(self):
        from quantia._registry import get_unit
        u = get_unit("bara")
        assert u.symbol == "bara"

    def test_barg_registered(self):
        from quantia._registry import get_unit
        u = get_unit("barg")
        assert u.symbol == "barg"


# ── Ambiguous warnings ────────────────────────────────────────────────────────

class TestAmbiguousWarnings:

    def test_psi_warns(self):
        with pytest.warns(UserWarning, match="psia"):
            qu.Q(100.0, "psi")

    def test_psi_redirects_to_psia(self):
        with pytest.warns(UserWarning):
            v = qu.Q(100.0, "psi").to("Pa").value
        assert v == pytest.approx(100 * PSI_TO_PA, rel=1e-9)

    def test_bar_warns(self):
        with pytest.warns(UserWarning, match="bara"):
            qu.Q(1.0, "bar")

    def test_bar_redirects_to_bara(self):
        with pytest.warns(UserWarning):
            v = qu.Q(1.0, "bar").to("Pa").value
        assert v == pytest.approx(100_000.0, rel=1e-10)

    def test_psia_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(100.0, "psia")

    def test_psig_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(100.0, "psig")

    def test_bara_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(1.0, "bara")

    def test_barg_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            qu.Q(1.0, "barg")


# ── psia — absolute psi ───────────────────────────────────────────────────────

class TestPsia:

    def test_psia_to_pa(self):
        # NIST: 1 psi = 6.894 757 E+03 Pa
        assert qu.Q(1.0, "psia").to("Pa").value == pytest.approx(PSI_TO_PA, rel=1e-9)

    def test_psia_to_kpa(self):
        assert qu.Q(1.0, "psia").to("kPa").value == pytest.approx(PSI_TO_PA / 1000, rel=1e-9)

    def test_psia_to_atm(self):
        # 1 atm = 14.6959 psia
        assert qu.Q(1.0, "atm").to("Pa").value == pytest.approx(
            qu.Q(14.6959, "psia").to("Pa").value, rel=1e-4)

    def test_psia_round_trip(self):
        v = 500.0
        result = qu.Q(v, "psia").to("Pa").to("psia").value
        assert result == pytest.approx(v, rel=1e-9)


# ── psig — gauge psi ──────────────────────────────────────────────────────────

class TestPsig:

    def test_zero_psig_equals_one_atm_in_pa(self):
        # 0 psig = 1 atm = 101 325 Pa (fundamental gauge definition)
        assert qu.Q(0.0, "psig").to("Pa").value == pytest.approx(ATM_PA, rel=1e-10)

    def test_zero_psig_to_psia(self):
        # 0 psig = 14.6959 psia (1 atm in psi)
        result = qu.Q(0.0, "psig").to("psia").value
        assert result == pytest.approx(ATM_PA / PSI_TO_PA, rel=1e-6)

    def test_psig_to_psia_100(self):
        # 100 psig = 100 + 14.696 psia
        result = qu.Q(100.0, "psig").to("psia").value
        expected = 100.0 + ATM_PA / PSI_TO_PA
        assert result == pytest.approx(expected, rel=1e-6)

    def test_psia_to_psig_100(self):
        # Round-trip from above
        result = qu.Q(114.696, "psia").to("psig").value
        assert result == pytest.approx(100.0, rel=1e-4)

    def test_psig_to_pa(self):
        # 100 psig → Pa
        result = qu.Q(100.0, "psig").to("Pa").value
        expected = 100.0 * PSI_TO_PA + ATM_PA
        assert result == pytest.approx(expected, rel=1e-9)

    def test_psig_round_trip(self):
        v = 250.0
        result = qu.Q(v, "psig").to("Pa").to("psig").value
        assert result == pytest.approx(v, rel=1e-9)


# ── bara and barg ─────────────────────────────────────────────────────────────

class TestBara:

    def test_bara_to_pa(self):
        assert qu.Q(1.0, "bara").to("Pa").value == pytest.approx(100_000.0, rel=1e-10)

    def test_bara_round_trip(self):
        v = 50.0
        assert qu.Q(v, "bara").to("Pa").to("bara").value == pytest.approx(v, rel=1e-9)


class TestBarg:

    def test_zero_barg_equals_one_atm_in_pa(self):
        assert qu.Q(0.0, "barg").to("Pa").value == pytest.approx(ATM_PA, rel=1e-10)

    def test_zero_barg_to_bara(self):
        result = qu.Q(0.0, "barg").to("bara").value
        assert result == pytest.approx(ATM_PA / 100_000.0, rel=1e-6)

    def test_barg_to_bara_10(self):
        result = qu.Q(10.0, "barg").to("bara").value
        expected = 10.0 + ATM_PA / 100_000.0
        assert result == pytest.approx(expected, rel=1e-9)

    def test_barg_round_trip(self):
        v = 10.0
        assert qu.Q(v, "barg").to("Pa").to("barg").value == pytest.approx(v, rel=1e-9)


# ── Cross-family conversions ──────────────────────────────────────────────────

class TestCrossFamily:

    def test_psig_to_bara(self):
        # 100 psig → Pa → bara
        pa = 100.0 * PSI_TO_PA + ATM_PA
        result = qu.Q(100.0, "psig").to("bara").value
        assert result == pytest.approx(pa / 100_000.0, rel=1e-6)

    def test_barg_to_psia(self):
        # 10 barg → Pa → psia
        pa = 10.0 * 100_000.0 + ATM_PA
        result = qu.Q(10.0, "barg").to("psia").value
        assert result == pytest.approx(pa / PSI_TO_PA, rel=1e-6)

    def test_psia_to_kpa(self):
        result = qu.Q(14.6959, "psia").to("kPa").value
        assert result == pytest.approx(ATM_PA / 1000, rel=1e-4)


# ── AffineUnit generalization: temperature still works ────────────────────────

class TestTemperatureUnaffected:
    """Ensure the to_si_value/from_si_value rename did not break temperature."""

    def test_celsius_to_kelvin(self):
        assert qu.Q(100.0, "°C").to("K").value == pytest.approx(373.15, rel=1e-9)

    def test_fahrenheit_to_celsius(self):
        assert qu.Q(32.0, "°F").to("°C").value == pytest.approx(0.0, abs=1e-9)

    def test_fahrenheit_to_kelvin(self):
        assert qu.Q(212.0, "°F").to("K").value == pytest.approx(373.15, rel=1e-6)

    def test_kelvin_to_celsius(self):
        assert qu.Q(0.0, "K").to("°C").value == pytest.approx(-273.15, rel=1e-9)

    def test_temperature_to_si(self):
        assert qu.Q(0.0, "°C").to_si().value == pytest.approx(273.15, rel=1e-9)


# ── Error cases ───────────────────────────────────────────────────────────────

class TestErrors:

    def test_mixing_affine_and_non_affine_raises(self):
        from quantia import DimensionError
        with pytest.raises(DimensionError):
            qu.Q(100.0, "psig").to("m")

    def test_incompatible_pressure_and_length(self):
        from quantia import IncompatibleUnitsError
        with pytest.raises(IncompatibleUnitsError):
            qu.Q(100.0, "psia") + qu.Q(1.0, "m")

    def test_psig_in_compound_expression_raises(self):
        # psig cannot be used in compound expressions (non-zero offset)
        from quantia import DimensionError
        with pytest.raises(DimensionError):
            qu.Q(100.0, "psig") * qu.Q(1.0, "m")


# ── ProbUnitFloat pressure ────────────────────────────────────────────────────

class TestProbPressure:

    def test_prob_psia_to_pa(self):
        with qu.config(seed=42, n_samples=500):
            p = qu.ProbUnitFloat.uniform(100.0, 200.0, "psia")
        result = p.to("Pa")
        assert result.mean().value == pytest.approx(
            p.mean().value * PSI_TO_PA, rel=1e-6)

    def test_prob_psig_to_psia(self):
        with qu.config(seed=42, n_samples=500):
            p = qu.ProbUnitFloat.uniform(0.0, 100.0, "psig")
        result = p.to("psia")
        # 0 psig → 14.696 psia;  100 psig → 114.696 psia
        # mean of uniform(0,100) psig = 50 psig → 50 + 14.696 psia
        expected_mean = 50.0 + ATM_PA / PSI_TO_PA
        assert result.mean().value == pytest.approx(expected_mean, rel=1e-3)

    def test_prob_psig_to_si(self):
        with qu.config(seed=0, n_samples=200):
            p = qu.ProbUnitFloat.uniform(0.0, 0.0, "psig")  # degenerate: all 0
        si = p.to_si()
        assert si.mean().value == pytest.approx(ATM_PA, rel=1e-6)

    def test_prob_temperature_unaffected(self):
        with qu.config(seed=1, n_samples=500):
            t = qu.ProbUnitFloat.uniform(0.0, 100.0, "°C")
        result = t.to_si()
        # mean of uniform(0,100) °C = 50 °C → 323.15 K
        assert result.mean().value == pytest.approx(323.15, rel=1e-3)