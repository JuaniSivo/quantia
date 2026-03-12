"""Tests for core scalar, array, and probabilistic arithmetic."""
import math, pytest
import quantia as qu
import quantia.math as mmath


# ── UnitFloat arithmetic ──────────────────────────────────────────────────────

def test_add_compatible():
    a = qu.Q(1.0, "km")
    b = qu.Q(500.0, "m")
    c = a + b
    assert c.value == pytest.approx(1.5)
    assert str(c.unit) == "km"

def test_sub_compatible():
    a = qu.Q(2.0, "m"); b = qu.Q(50.0, "cm")
    assert (a - b).value == pytest.approx(1.5)

def test_mul_units():
    f = qu.Q(10.0, "N"); d = qu.Q(2.0, "m")
    e = f * d
    assert e.value == pytest.approx(20.0)
    assert str(e.unit) == "J"

def test_div_units():
    s = qu.Q(100.0, "m"); t = qu.Q(10.0, "s")
    v = s / t
    assert v.value == pytest.approx(10.0)

def test_pow():
    a = qu.Q(3.0, "m")
    assert (a ** 2).value == pytest.approx(9.0)

def test_incompatible_add_raises():
    from quantia import IncompatibleUnitsError
    with pytest.raises(IncompatibleUnitsError):
        qu.Q(1.0, "m") + qu.Q(1.0, "s")

def test_temperature_conversion():
    t = qu.Q(100.0, "°C")
    k = t.to("K")
    assert k.value == pytest.approx(373.15)
    f = t.to("°F")
    assert f.value == pytest.approx(212.0, rel=1e-5)


# ── UnitArray ─────────────────────────────────────────────────────────────────

def test_unitarray_sum():
    ua = qu.QA([1.0, 2.0, 3.0], "m")
    assert ua.sum().value == pytest.approx(6.0)

def test_unitarray_mean():
    ua = qu.QA([10.0, 20.0, 30.0], "m")
    assert ua.mean().value == pytest.approx(20.0)

def test_unitarray_to():
    ua  = qu.QA([1.0, 2.0], "km")
    ua2 = ua.to("m")
    assert list(ua2.values) == pytest.approx([1000.0, 2000.0])


# ── Boolean mask (6c) ─────────────────────────────────────────────────────────

def test_bool_mask_filter():
    speeds = qu.QA([8.0, 12.0, 15.0, 7.0, 20.0], "m/s")
    mask   = speeds > qu.Q(10.0, "m/s")
    fast   = speeds[mask]
    assert list(fast.values) == pytest.approx([12.0, 15.0, 20.0])

def test_bool_mask_wrong_length():
    ua = qu.QA([1.0, 2.0, 3.0], "m")
    with pytest.raises(IndexError):
        _ = ua[[True, False]]   # length mismatch

def test_index_list():
    ua = qu.QA([10.0, 20.0, 30.0, 40.0], "m")
    assert list(ua[[0, 2]].values) == pytest.approx([10.0, 30.0])


# ── quantia.math dispatch ─────────────────────────────────────────────────────

def test_mmath_log10_float():
    assert mmath.log10(100.0) == pytest.approx(2.0)

def test_mmath_log10_unitfloat():
    x = qu.Q(100.0, "1")
    r = mmath.log10(x)
    assert r.value == pytest.approx(2.0)

def test_mmath_sqrt_preserves_unit():
    x = qu.Q(4.0, "m^2")
    r = mmath.sqrt(x)
    assert r.value == pytest.approx(2.0)
    assert str(r.unit) == "m"

def test_mmath_sin_angle():
    x = qu.Q(math.pi / 2, "rad")
    assert mmath.sin(x).value == pytest.approx(1.0)

def test_mmath_sin_bad_unit():
    from quantia import DimensionError
    with pytest.raises(DimensionError):
        mmath.sin(qu.Q(1.0, "m"))

def test_mmath_prob_log10():
    with qu.config(seed=1):
        x = qu.ProbUnitFloat.uniform(10.0, 100.0, "1", n=200)
    r = mmath.log10(x)
    assert r.mean().value == pytest.approx(math.log10(55.0), rel=0.1)


# ── eval-able repr (6a) ───────────────────────────────────────────────────────

def test_unitfloat_repr_eval():
    uf = qu.Q(5.0, "km")
    from quantia import UnitFloat
    uf2 = eval(repr(uf))
    assert uf2.value == uf.value
    assert str(uf2.unit) == str(uf.unit)

def test_unitarray_repr_eval_small():
    ua = qu.QA([1.0, 2.0, 3.0], "m/s")
    from quantia import UnitArray
    ua2 = eval(repr(ua))
    assert list(ua2.values) == pytest.approx(list(ua.values))