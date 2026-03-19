"""
API gravity conversion function tests.

All values derived from the API MPMS definition:
    SG = 141.5 / (°API + 131.5)

Key identities
--------------
api_to_sg(10.0)  == 1.0     (water = 10 °API by definition)
sg_to_api(1.0)   == 10.0    (inverse of above)
api_to_sg(sg_to_api(x)) == x for all valid x  (round-trip)
"""
import math
import pytest
import quantia as qu
from quantia.petroleum_conversions import api_to_sg, sg_to_api


# ── api_to_sg ─────────────────────────────────────────────────────────────────

class TestApiToSg:

    def test_water_definition(self):
        # API MPMS: water = 10 °API = SG 1.0 by definition
        assert api_to_sg(10.0) == pytest.approx(1.0, rel=1e-10)

    def test_medium_crude(self):
        # 35 °API crude: SG = 141.5 / (35 + 131.5) = 0.8498
        assert api_to_sg(35.0) == pytest.approx(141.5 / 166.5, rel=1e-10)

    def test_light_crude(self):
        # 45 °API: SG = 141.5 / 176.5 = 0.8017
        assert api_to_sg(45.0) == pytest.approx(141.5 / 176.5, rel=1e-10)

    def test_heavy_crude(self):
        # 15 °API: SG = 141.5 / 146.5 = 0.9659
        assert api_to_sg(15.0) == pytest.approx(141.5 / 146.5, rel=1e-10)

    def test_condensate(self):
        # 60 °API condensate: SG = 141.5 / 191.5 = 0.7389
        assert api_to_sg(60.0) == pytest.approx(141.5 / 191.5, rel=1e-10)

    def test_higher_api_gives_lower_sg(self):
        # Physical sanity: lighter oil has higher API and lower SG
        assert api_to_sg(40.0) < api_to_sg(30.0)

    def test_zero_api(self):
        # 0 °API: SG = 141.5 / 131.5 = 1.0760
        assert api_to_sg(0.0) == pytest.approx(141.5 / 131.5, rel=1e-10)

    def test_negative_api(self):
        # Negative API is physically unusual but formula still valid > -131.5
        assert api_to_sg(-10.0) == pytest.approx(141.5 / 121.5, rel=1e-10)

    def test_invalid_api_raises(self):
        # API <= -131.5 produces zero or negative SG — must raise
        with pytest.raises(ValueError, match="-131.5"):
            api_to_sg(-131.5)
        with pytest.raises(ValueError):
            api_to_sg(-200.0)

    def test_unitfloat_input(self):
        # UnitFloat with °API unit
        api = qu.Q(35.0, "°API")
        result = api_to_sg(api)
        assert result == pytest.approx(141.5 / 166.5, rel=1e-10)

    def test_returns_float_for_float_input(self):
        result = api_to_sg(35.0)
        assert isinstance(result, float)

    def test_returns_float_for_unitfloat_input(self):
        result = api_to_sg(qu.Q(35.0, "°API"))
        assert isinstance(result, float)


# ── sg_to_api ─────────────────────────────────────────────────────────────────

class TestSgToApi:

    def test_water_definition(self):
        # SG=1.0 → 10 °API (water by definition)
        assert sg_to_api(1.0) == pytest.approx(10.0, rel=1e-10)

    def test_medium_crude(self):
        # SG=0.85: °API = 141.5/0.85 - 131.5 = 35.03
        assert sg_to_api(0.85) == pytest.approx(141.5 / 0.85 - 131.5, rel=1e-10)

    def test_heavy_crude(self):
        # SG=0.97: °API = 141.5/0.97 - 131.5 = 14.47
        assert sg_to_api(0.97) == pytest.approx(141.5 / 0.97 - 131.5, rel=1e-10)

    def test_higher_sg_gives_lower_api(self):
        assert sg_to_api(0.9) < sg_to_api(0.8)

    def test_invalid_sg_zero_raises(self):
        with pytest.raises(ValueError, match="> 0"):
            sg_to_api(0.0)

    def test_invalid_sg_negative_raises(self):
        with pytest.raises(ValueError):
            sg_to_api(-1.0)

    def test_unitfloat_input(self):
        result = sg_to_api(qu.Q(0.85, "1"))
        assert result == pytest.approx(141.5 / 0.85 - 131.5, rel=1e-10)


# ── Round-trip identity ───────────────────────────────────────────────────────

class TestRoundTrip:

    @pytest.mark.parametrize("api", [0.0, 10.0, 20.0, 35.0, 45.0, 60.0])
    def test_api_sg_api_roundtrip(self, api):
        # api_to_sg → sg_to_api must recover original value
        assert sg_to_api(api_to_sg(api)) == pytest.approx(api, rel=1e-10)

    @pytest.mark.parametrize("sg", [0.7, 0.8, 0.85, 0.9, 1.0, 1.05])
    def test_sg_api_sg_roundtrip(self, sg):
        # sg_to_api → api_to_sg must recover original value
        assert api_to_sg(sg_to_api(sg)) == pytest.approx(sg, rel=1e-10)


# ── ProbUnitFloat dispatch ────────────────────────────────────────────────────

class TestProbDispatch:

    def test_prob_api_to_sg_returns_probunitfloat(self):
        with qu.config(seed=42, n_samples=500):
            api = qu.ProbUnitFloat.uniform(30.0, 40.0, "1")
        result = api_to_sg(api)
        from quantia.prob._scalar import ProbUnitFloat
        assert isinstance(result, ProbUnitFloat)

    def test_prob_api_to_sg_mean(self):
        # mean of uniform(30, 40) = 35 → api_to_sg(35) = 141.5/166.5
        with qu.config(seed=42, n_samples=5000):
            api = qu.ProbUnitFloat.uniform(30.0, 40.0, "1")
        result = api_to_sg(api)
        expected_mean = api_to_sg(35.0)
        assert result.mean().value == pytest.approx(expected_mean, rel=0.02)

    def test_prob_sg_to_api_returns_probunitfloat(self):
        with qu.config(seed=0, n_samples=500):
            sg = qu.ProbUnitFloat.uniform(0.80, 0.90, "1")
        result = sg_to_api(sg)
        from quantia.prob._scalar import ProbUnitFloat
        assert isinstance(result, ProbUnitFloat)

    def test_prob_sg_to_api_mean(self):
        # mean of uniform(0.80, 0.90) = 0.85 → sg_to_api(0.85)
        with qu.config(seed=1, n_samples=5000):
            sg = qu.ProbUnitFloat.uniform(0.80, 0.90, "1")
        result = sg_to_api(sg)
        expected_mean = sg_to_api(0.85)
        assert result.mean().value == pytest.approx(expected_mean, rel=0.02)

    def test_prob_round_trip_mean(self):
        # api_to_sg then sg_to_api on probabilistic input
        with qu.config(seed=2, n_samples=3000):
            api = qu.ProbUnitFloat.normal(35.0, 2.0, "1")
        sg     = api_to_sg(api)
        api_rt = sg_to_api(sg)
        assert api_rt.mean().value == pytest.approx(35.0, rel=0.02)

    def test_prob_api_to_sg_std_positive(self):
        # Uncertain API must produce uncertain SG
        with qu.config(seed=3, n_samples=1000):
            api = qu.ProbUnitFloat.uniform(25.0, 45.0, "1")
        result = api_to_sg(api)
        assert result.std().value > 0

    def test_prob_higher_api_gives_lower_sg(self):
        # Physical sanity holds in probabilistic domain
        with qu.config(seed=4, n_samples=2000):
            api_light = qu.ProbUnitFloat.normal(45.0, 1.0, "1")
            api_heavy = qu.ProbUnitFloat.normal(25.0, 1.0, "1")
        sg_light = api_to_sg(api_light)
        sg_heavy = api_to_sg(api_heavy)
        assert sg_light.mean().value < sg_heavy.mean().value