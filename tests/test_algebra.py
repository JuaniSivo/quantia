"""Property-style tests: unit algebra invariants."""
import pytest
import quantia as qu

LENGTHS = [("1.0", "m"), ("2.5", "km"), ("0.5", "cm")]
TIMES   = [("1.0", "s"), ("60.0", "min"), ("3600.0", "h")]


@pytest.mark.parametrize("v,u", LENGTHS)
def test_mul_div_identity(v, u):
    a = qu.Q(float(v), u)
    b = qu.Q(2.0, u)
    result = (a * b) / b
    assert result.si_value() == pytest.approx(a.si_value(), rel=1e-9)


@pytest.mark.parametrize("v,u", LENGTHS)
def test_add_sub_identity(v, u):
    a = qu.Q(float(v), u)
    b = qu.Q(1.0, u)
    assert (a + b - b).si_value() == pytest.approx(a.si_value(), rel=1e-9)


@pytest.mark.parametrize("lv,lu", LENGTHS)
@pytest.mark.parametrize("tv,tu", TIMES)
def test_speed_unit_cancellation(lv, lu, tv, tu):
    s   = qu.Q(float(lv), lu)
    t   = qu.Q(float(tv), tu)
    spd = s / t
    # round-trip: speed * time == distance
    dist = spd * t
    assert dist.si_value() == pytest.approx(s.si_value(), rel=1e-9)


def test_prob_mean_within_bounds():
    """Mean of uniform(a, b) should be ≈ (a+b)/2."""
    with qu.config(seed=42, n_samples=5000):
        x = qu.ProbUnitFloat.uniform(10.0, 20.0, "m")
    assert x.mean().value == pytest.approx(15.0, rel=0.05)


def test_prob_std_within_tolerance():
    """Std of normal(mu, sigma) should be ≈ sigma."""
    with qu.config(seed=42, n_samples=5000):
        x = qu.ProbUnitFloat.normal(0.0, 3.0, "m")
    assert x.std().value == pytest.approx(3.0, rel=0.05)