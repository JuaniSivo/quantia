"""
tests/test_dispatch.py
======================
Comprehensive tests for the unified arithmetic dispatcher (_dispatch.py).

For every operator (+, -, *, /, **) and every type-pair combination,
verifies:
  - output type matches the 2×2 rule
  - output values are numerically correct
  - both orderings (a op b and b op a) are covered

For invalid combinations, verifies the correct error is raised.

Fixtures
--------
All dimensional fixtures use unit "m".
All dimensionless fixtures use unit "1".
n=4 for all probabilistic fixtures (ProbUnitFloat, ProbUnitArray).
len=3 for all array fixtures (UnitArray, ProbUnitArray).

ProbUnitArray layout  (len=3, n=4):
  element 0: [1, 2, 3, 4]
  element 1: [5, 6, 7, 8]
  element 2: [9, 10, 11, 12]

  flat index:  data[i * n + j]
"""
from __future__ import annotations
import array as _array
import pytest

from quantia._scalar import UnitFloat
from quantia._array import UnitArray
from quantia.prob._scalar import ProbUnitFloat
from quantia.prob._array import ProbUnitArray
from quantia._exceptions import IncompatibleUnitsError, DimensionError


# ── Module-level fixtures ─────────────────────────────────────────────────────

F    = 2.0                                  # plain float

# ── dimensional, unit="m" ────────────────────────────────────────────────────
UF   = UnitFloat(3.0, "m")

PUF  = ProbUnitFloat._from_raw(
    _array.array('d', [1., 2., 3., 4.]), "m")

UA   = UnitArray(
    _array.array('d', [10., 20., 30.]), "m")

PUA  = ProbUnitArray._from_flat(
    _array.array('d', [1.,2.,3.,4., 5.,6.,7.,8., 9.,10.,11.,12.]),
    "m", 3, 4)

# ── dimensionless, unit="1" ───────────────────────────────────────────────────
UF1  = UnitFloat(3.0, "1")

PUF1 = ProbUnitFloat._from_raw(
    _array.array('d', [1., 2., 3., 4.]), "1")

UA1  = UnitArray(
    _array.array('d', [1., 2., 3.]), "1")          # small values — safe as exponents

PUA1 = ProbUnitArray._from_flat(
    _array.array('d', [1.,2.,3.,4., 1.,2.,3.,4., 1.,2.,3.,4.]),
    "1", 3, 4)

# ── different dimension — for incompatibility tests ───────────────────────────
UFS  = UnitFloat(2.0, "s")

# ── shape-mismatch fixtures ───────────────────────────────────────────────────
PUF3 = ProbUnitFloat._from_raw(_array.array('d', [1., 2., 3.]), "m")   # n=3
UA2  = UnitArray(_array.array('d', [10., 20.]), "m")          # len=2


# ── Helper ────────────────────────────────────────────────────────────────────

def _flat(x) -> list[float]:
    """Return all numeric values from any quantia type as a plain list."""
    if isinstance(x, UnitFloat):     return [x._value]
    if isinstance(x, UnitArray):     return list(x._data)
    if isinstance(x, ProbUnitFloat): return list(x._samples)
    if isinstance(x, ProbUnitArray): return list(x._data)
    raise TypeError(type(x))


# ═══════════════════════════════════════════════════════════════════════════════
# Addition
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdd:
    """
    14 dispatch-relevant type pairs for +.
    Both orderings are tested in every method.
    float operands use dimensionless fixtures because float is coerced
    to UnitFloat("1") and "1"+"m" would be incompatible.
    """

    # ── float pairs (dimensionless) ───────────────────────────────────────────

    def test_float_unitfloat1(self):
        r = F + UF1;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(5.0)
        r = UF1 + F;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(5.0)

    def test_float_probunitfloat1(self):
        r = F + PUF1; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 4., 5., 6.])
        r = PUF1 + F; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 4., 5., 6.])

    def test_float_unitarray1(self):
        r = F + UA1;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([3., 4., 5.])
        r = UA1 + F;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([3., 4., 5.])

    def test_float_probunitarray1(self):
        # PUA1 flat: [1,2,3,4, 1,2,3,4, 1,2,3,4]
        expected = [3.,4.,5.,6., 3.,4.,5.,6., 3.,4.,5.,6.]
        r = F + PUA1; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA1 + F; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    # ── dimensional pairs (unit="m") ──────────────────────────────────────────

    def test_unitfloat_unitfloat(self):
        r = UF + UF;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(6.0)
        assert str(r._unit) == "m"

    def test_unitfloat_probunitfloat(self):
        # UF(3) + PUF([1,2,3,4]) = [4,5,6,7]
        r = UF + PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([4., 5., 6., 7.])
        r = PUF + UF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([4., 5., 6., 7.])

    def test_unitfloat_unitarray(self):
        # UF(3) + UA([10,20,30]) = [13,23,33]
        r = UF + UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([13., 23., 33.])
        r = UA + UF;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([13., 23., 33.])

    def test_unitfloat_probunitarray(self):
        # UF(3) broadcasts over i and j
        # i=0: [3+1,3+2,3+3,3+4]=[4,5,6,7]
        # i=1: [3+5,3+6,3+7,3+8]=[8,9,10,11]
        # i=2: [3+9,3+10,3+11,3+12]=[12,13,14,15]
        expected = [4.,5.,6.,7., 8.,9.,10.,11., 12.,13.,14.,15.]
        r = UF + PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA + UF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitfloat_probunitfloat(self):
        r = PUF + PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([2., 4., 6., 8.])

    def test_probunitfloat_unitarray(self):
        # PUF[j] + UA[i]  → ProbUnitArray(len=3, n=4)
        # i=0: [1+10,2+10,3+10,4+10]=[11,12,13,14]
        # i=1: [1+20,2+20,3+20,4+20]=[21,22,23,24]
        # i=2: [1+30,2+30,3+30,4+30]=[31,32,33,34]
        expected = [11.,12.,13.,14., 21.,22.,23.,24., 31.,32.,33.,34.]
        r = PUF + UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = UA + PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitfloat_probunitarray(self):
        # PUF[j] + PUA[i][j]  (same n=4)
        # i=0: [1+1,2+2,3+3,4+4]=[2,4,6,8]
        # i=1: [1+5,2+6,3+7,4+8]=[6,8,10,12]
        # i=2: [1+9,2+10,3+11,4+12]=[10,12,14,16]
        expected = [2.,4.,6.,8., 6.,8.,10.,12., 10.,12.,14.,16.]
        r = PUF + PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA + PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_unitarray_unitarray(self):
        r = UA + UA; assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([20., 40., 60.])

    def test_unitarray_probunitarray(self):
        # UA[i] + PUA[i][j]
        # i=0: [10+1,10+2,10+3,10+4]=[11,12,13,14]
        # i=1: [20+5,20+6,20+7,20+8]=[25,26,27,28]
        # i=2: [30+9,30+10,30+11,30+12]=[39,40,41,42]
        expected = [11.,12.,13.,14., 25.,26.,27.,28., 39.,40.,41.,42.]
        r = UA + PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA + UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitarray_probunitarray(self):
        # PUA[i][j] + PUA[i][j]
        # i=0: [2,4,6,8]  i=1: [10,12,14,16]  i=2: [18,20,22,24]
        expected = [2.,4.,6.,8., 10.,12.,14.,16., 18.,20.,22.,24.]
        r = PUA + PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_unit_conversion_on_add(self):
        # Ensure b is scaled to a's unit before adding
        a = UnitFloat(1.0, "km")
        b = UnitFloat(500.0, "m")
        r = a + b
        assert isinstance(r, UnitFloat)
        assert str(r._unit) == "km"
        assert r._value == pytest.approx(1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# Subtraction
# ═══════════════════════════════════════════════════════════════════════════════

class TestSub:
    """Both orderings always differ in value for subtraction."""

    def test_float_unitfloat1(self):
        r = F - UF1;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(-1.0)   # 2 - 3
        r = UF1 - F;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(1.0)    # 3 - 2

    def test_float_probunitfloat1(self):
        r = F - PUF1; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 0., -1., -2.])    # 2-[1,2,3,4]
        r = PUF1 - F; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([-1., 0., 1., 2.])     # [1,2,3,4]-2

    def test_float_unitarray1(self):
        r = F - UA1;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([1., 0., -1.])         # 2-[1,2,3]
        r = UA1 - F;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([-1., 0., 1.])         # [1,2,3]-2

    def test_float_probunitarray1(self):
        r = F - PUA1; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([1.,0.,-1.,-2., 1.,0.,-1.,-2., 1.,0.,-1.,-2.])
        r = PUA1 - F; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([-1.,0.,1.,2., -1.,0.,1.,2., -1.,0.,1.,2.])

    def test_unitfloat_unitfloat(self):
        r = UF - UF; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(0.0)

    def test_unitfloat_probunitfloat(self):
        r = UF - PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([2., 1., 0., -1.])     # 3-[1,2,3,4]
        r = PUF - UF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([-2., -1., 0., 1.])    # [1,2,3,4]-3

    def test_unitfloat_unitarray(self):
        r = UF - UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([-7., -17., -27.])     # 3-[10,20,30]
        r = UA - UF;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([7., 17., 27.])        # [10,20,30]-3

    def test_unitfloat_probunitarray(self):
        # UF(3) - PUA[i][j]
        # i=0: [3-1,3-2,3-3,3-4]=[2,1,0,-1]
        # i=1: [3-5,3-6,3-7,3-8]=[-2,-3,-4,-5]
        # i=2: [3-9,3-10,3-11,3-12]=[-6,-7,-8,-9]
        expected_uf  = [2.,1.,0.,-1., -2.,-3.,-4.,-5., -6.,-7.,-8.,-9.]
        expected_pua = [-2.,-1.,0.,1., 2.,3.,4.,5., 6.,7.,8.,9.]
        r = UF - PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected_uf)
        r = PUA - UF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected_pua)

    def test_probunitfloat_probunitfloat(self):
        r = PUF - PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([0., 0., 0., 0.])

    def test_probunitfloat_unitarray(self):
        # PUF[j] - UA[i]
        # i=0: [1-10,2-10,3-10,4-10]=[-9,-8,-7,-6]
        # i=1: [1-20,2-20,3-20,4-20]=[-19,-18,-17,-16]
        # i=2: [1-30,2-30,3-30,4-30]=[-29,-28,-27,-26]
        exp_puf_ua = [-9.,-8.,-7.,-6., -19.,-18.,-17.,-16., -29.,-28.,-27.,-26.]
        exp_ua_puf = [9.,8.,7.,6., 19.,18.,17.,16., 29.,28.,27.,26.]
        r = PUF - UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_puf_ua)
        r = UA - PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_ua_puf)

    def test_probunitfloat_probunitarray(self):
        # PUF[j] - PUA[i][j]
        # i=0: [1-1,2-2,3-3,4-4]=[0,0,0,0]
        # i=1: [1-5,2-6,3-7,4-8]=[-4,-4,-4,-4]
        # i=2: [1-9,2-10,3-11,4-12]=[-8,-8,-8,-8]
        r = PUF - PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([0.,0.,0.,0., -4.,-4.,-4.,-4., -8.,-8.,-8.,-8.])
        r = PUA - PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([0.,0.,0.,0., 4.,4.,4.,4., 8.,8.,8.,8.])

    def test_unitarray_unitarray(self):
        r = UA - UA; assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([0., 0., 0.])

    def test_unitarray_probunitarray(self):
        # UA[i] - PUA[i][j]
        # i=0: [10-1,10-2,10-3,10-4]=[9,8,7,6]
        # i=1: [20-5,20-6,20-7,20-8]=[15,14,13,12]
        # i=2: [30-9,30-10,30-11,30-12]=[21,20,19,18]
        exp_ua_pua  = [9.,8.,7.,6., 15.,14.,13.,12., 21.,20.,19.,18.]
        exp_pua_ua  = [-9.,-8.,-7.,-6., -15.,-14.,-13.,-12., -21.,-20.,-19.,-18.]
        r = UA - PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_ua_pua)
        r = PUA - UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_pua_ua)

    def test_probunitarray_probunitarray(self):
        r = PUA - PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([0.] * 12)


# ═══════════════════════════════════════════════════════════════════════════════
# Multiplication
# ═══════════════════════════════════════════════════════════════════════════════

class TestMul:
    """Units combine algebraically — no compatibility requirement."""

    def test_float_unitfloat(self):
        # "1" * "m" = "m"
        r = F * UF;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(6.0)
        assert str(r._unit) == "m"
        r = UF * F;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(6.0)

    def test_float_probunitfloat(self):
        r = F * PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([2., 4., 6., 8.])
        r = PUF * F; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([2., 4., 6., 8.])

    def test_float_unitarray(self):
        r = F * UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([20., 40., 60.])
        r = UA * F;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([20., 40., 60.])

    def test_float_probunitarray(self):
        expected = [2.,4.,6.,8., 10.,12.,14.,16., 18.,20.,22.,24.]
        r = F * PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA * F; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_unitfloat_unitfloat_same_unit(self):
        # m * m = m^2
        r = UF * UF; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(9.0)
        assert str(r._unit) == "m^2"

    def test_unitfloat_unitfloat_different_units(self):
        # m * s  (no unit check — both orderings differ in value position only)
        r = UF * UFS; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(6.0)   # 3*2

    def test_unitfloat_probunitfloat(self):
        # m * m = m^2
        r = UF * PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 6., 9., 12.])
        assert str(r._unit) == "m^2"
        r = PUF * UF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 6., 9., 12.])

    def test_unitfloat_unitarray(self):
        r = UF * UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([30., 60., 90.])
        assert str(r._unit) == "m^2"
        r = UA * UF;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([30., 60., 90.])

    def test_unitfloat_probunitarray(self):
        # UF(3) * PUA → values 3× each element
        expected = [3.,6.,9.,12., 15.,18.,21.,24., 27.,30.,33.,36.]
        r = UF * PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA * UF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitfloat_probunitfloat(self):
        r = PUF * PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 4., 9., 16.])
        assert str(r._unit) == "m^2"

    def test_probunitfloat_unitarray(self):
        # PUF[j] * UA[i]
        # i=0: [1*10,2*10,3*10,4*10]=[10,20,30,40]
        # i=1: [1*20,2*20,3*20,4*20]=[20,40,60,80]
        # i=2: [1*30,2*30,3*30,4*30]=[30,60,90,120]
        expected = [10.,20.,30.,40., 20.,40.,60.,80., 30.,60.,90.,120.]
        r = PUF * UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = UA * PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitfloat_probunitarray(self):
        # PUF[j] * PUA[i][j]
        # i=0: [1*1,2*2,3*3,4*4]=[1,4,9,16]
        # i=1: [1*5,2*6,3*7,4*8]=[5,12,21,32]
        # i=2: [1*9,2*10,3*11,4*12]=[9,20,33,48]
        expected = [1.,4.,9.,16., 5.,12.,21.,32., 9.,20.,33.,48.]
        r = PUF * PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA * PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_unitarray_unitarray(self):
        r = UA * UA; assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([100., 400., 900.])
        assert str(r._unit) == "m^2"

    def test_unitarray_probunitarray(self):
        # UA[i] * PUA[i][j]
        # i=0: [10,20,30,40]
        # i=1: [100,120,140,160]
        # i=2: [270,300,330,360]
        expected = [10.,20.,30.,40., 100.,120.,140.,160., 270.,300.,330.,360.]
        r = UA * PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        r = PUA * UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_probunitarray_probunitarray(self):
        # i=0: [1,4,9,16]  i=1: [25,36,49,64]  i=2: [81,100,121,144]
        expected = [1.,4.,9.,16., 25.,36.,49.,64., 81.,100.,121.,144.]
        r = PUA * PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)

    def test_unit_combines_to_dimensionless(self):
        # m * (1/m) — result should be dimensionless
        inv = UnitFloat(2.0, "1") / UF   # UnitFloat(2/3, "1/m")
        r   = UF * inv
        assert isinstance(r, UnitFloat)
        assert r._unit.is_dimensionless()


# ═══════════════════════════════════════════════════════════════════════════════
# Division
# ═══════════════════════════════════════════════════════════════════════════════

class TestDiv:
    """Both orderings always differ in unit and/or value for division."""

    def test_float_unitfloat(self):
        # UnitFloat("1") / UnitFloat("m") → unit = "1/m"
        r = F / UF;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(2 / 3)
        # UnitFloat("m") / UnitFloat("1") → unit = "m"
        r = UF / F;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(1.5)
        assert str(r._unit) == "m"

    def test_float_probunitfloat(self):
        r = F / PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([2., 1., 2/3, 0.5])
        r = PUF / F; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([0.5, 1., 1.5, 2.])

    def test_float_unitarray(self):
        r = F / UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([2/10, 2/20, 2/30])
        r = UA / F;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([5., 10., 15.])
        assert str(r._unit) == "m"

    def test_float_probunitarray(self):
        r = F / PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(
            [2/1,2/2,2/3,2/4, 2/5,2/6,2/7,2/8, 2/9,2/10,2/11,2/12])
        r = PUA / F; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(
            [0.5,1.,1.5,2., 2.5,3.,3.5,4., 4.5,5.,5.5,6.])

    def test_unitfloat_unitfloat_same_unit(self):
        # m / m = dimensionless
        r = UF / UF; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(1.0)
        assert r._unit.is_dimensionless()

    def test_unitfloat_unitfloat_different_units(self):
        # m / s = m/s
        r = UF / UFS; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(1.5)

    def test_unitfloat_probunitfloat(self):
        # m / m → dimensionless values
        r = UF / PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 1.5, 1., 0.75])
        r = PUF / UF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1/3, 2/3, 1., 4/3])

    def test_unitfloat_unitarray(self):
        r = UF / UA;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([3/10, 3/20, 3/30])
        r = UA / UF;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([10/3, 20/3, 10.])

    def test_unitfloat_probunitarray(self):
        # UF(3) / PUA[i][j]
        exp_uf_pua  = [3/1,3/2,1.,3/4, 3/5,0.5,3/7,3/8, 1/3,0.3,3/11,0.25]
        exp_pua_uf  = [1/3,2/3,1.,4/3, 5/3,2.,7/3,8/3, 3.,10/3,11/3,4.]
        r = UF / PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_uf_pua)
        r = PUA / UF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_pua_uf)

    def test_probunitfloat_probunitfloat(self):
        # m / m → dimensionless
        r = PUF / PUF; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 1., 1., 1.])
        assert r._unit.is_dimensionless()

    def test_probunitfloat_unitarray(self):
        # PUF[j] / UA[i]
        # i=0: [1/10,2/10,3/10,4/10]
        # i=1: [1/20,2/20,3/20,4/20]
        # i=2: [1/30,2/30,3/30,4/30]
        exp_puf_ua = [0.1,0.2,0.3,0.4, 0.05,0.1,0.15,0.2, 1/30,2/30,3/30,4/30]
        exp_ua_puf = [10.,5.,10/3,2.5, 20.,10.,20/3,5., 30.,15.,10.,7.5]
        r = PUF / UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_puf_ua)
        r = UA / PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_ua_puf)

    def test_probunitfloat_probunitarray(self):
        # PUF[j] / PUA[i][j]
        # i=0: [1/1,2/2,3/3,4/4]=[1,1,1,1]
        # i=1: [1/5,2/6,3/7,4/8]
        # i=2: [1/9,2/10,3/11,4/12]
        exp_puf_pua = [1.,1.,1.,1., 0.2,1/3,3/7,0.5, 1/9,0.2,3/11,1/3]
        exp_pua_puf = [1.,1.,1.,1., 5.,3.,7/3,2., 9.,5.,11/3,3.]
        r = PUF / PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_puf_pua)
        r = PUA / PUF; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_pua_puf)

    def test_unitarray_unitarray(self):
        r = UA / UA; assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([1., 1., 1.])
        assert r._unit.is_dimensionless()

    def test_unitarray_probunitarray(self):
        # UA[i] / PUA[i][j]
        # i=0: [10/1,10/2,10/3,10/4]=[10,5,10/3,2.5]
        # i=1: [20/5,20/6,20/7,20/8]=[4,10/3,20/7,2.5]
        # i=2: [30/9,30/10,30/11,30/12]=[10/3,3,30/11,2.5]
        exp_ua_pua  = [10.,5.,10/3,2.5, 4.,10/3,20/7,2.5, 10/3,3.,30/11,2.5]
        exp_pua_ua  = [0.1,0.2,0.3,0.4, 0.25,0.3,0.35,0.4, 0.3,1/3,11/30,0.4]
        r = UA / PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_ua_pua)
        r = PUA / UA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(exp_pua_ua)

    def test_probunitarray_probunitarray(self):
        r = PUA / PUA; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx([1.] * 12)
        assert r._unit.is_dimensionless()


# ═══════════════════════════════════════════════════════════════════════════════
# Exponentiation
# ═══════════════════════════════════════════════════════════════════════════════

class TestPow:
    """
    Rules:
      - Exponent must always be dimensionless.
      - Base may be dimensional only when exponent is a single value
        (float coerced to UnitFloat, or UnitFloat directly).
      - Base must be dimensionless when exponent has multiple values
        (UnitArray, ProbUnitFloat, ProbUnitArray).
    """

    # ── float / UnitFloat("1") exponent → base may be dimensional ────────────

    def test_unitfloat_float_exp(self):
        r = UF ** 2.0;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(9.0)
        assert str(r._unit) == "m^2"

    def test_unitfloat1_float_exp(self):
        r = UF1 ** 3.0; assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(27.0)
        assert r._unit.is_dimensionless()

    def test_unitarray_float_exp(self):
        r = UA ** 2.0;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([100., 400., 900.])
        assert str(r._unit) == "m^2"

    def test_unitarray1_float_exp(self):
        r = UA1 ** 2.0; assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([1., 4., 9.])
        assert r._unit.is_dimensionless()

    def test_probunitfloat_float_exp(self):
        r = PUF ** 2.0; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 4., 9., 16.])
        assert str(r._unit) == "m^2"

    def test_probunitfloat1_float_exp(self):
        r = PUF1 ** 2.0; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 4., 9., 16.])
        assert r._unit.is_dimensionless()

    def test_probunitarray_float_exp(self):
        r = PUA ** 2.0; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(
            [1.,4.,9.,16., 25.,36.,49.,64., 81.,100.,121.,144.])
        assert str(r._unit) == "m^2"

    def test_probunitarray1_float_exp(self):
        r = PUA1 ** 2.0; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(
            [1.,4.,9.,16., 1.,4.,9.,16., 1.,4.,9.,16.])
        assert r._unit.is_dimensionless()

    def test_unitfloat_unitfloat1_exp(self):
        # UF("m") ** UF1("1") = m^3  (exponent value = 3.0)
        r = UF ** UF1;  assert isinstance(r, UnitFloat)
        assert r._value == pytest.approx(3.0 ** 3.0)
        assert str(r._unit) == "m^3"

    def test_unitarray_unitfloat1_exp(self):
        r = UA ** UF1;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([10.**3, 20.**3, 30.**3])
        assert str(r._unit) == "m^3"

    def test_probunitfloat_unitfloat1_exp(self):
        r = PUF ** UF1; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1.**3, 2.**3, 3.**3, 4.**3])
        assert str(r._unit) == "m^3"

    def test_probunitarray_unitfloat1_exp(self):
        r = PUA ** UF1; assert isinstance(r, ProbUnitArray)
        expected = [v**3 for v in [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.]]
        assert _flat(r) == pytest.approx(expected)
        assert str(r._unit) == "m^3"

    # ── multi-value exponent → base must be dimensionless ────────────────────

    def test_unitfloat1_probunitfloat1_exp(self):
        # base=3("1"), exp=[1,2,3,4]("1") → [3,9,27,81]
        r = UF1 ** PUF1; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([3., 9., 27., 81.])
        assert r._unit.is_dimensionless()

    def test_unitfloat1_unitarray1_exp(self):
        # base=3("1"), exp=[1,2,3]("1") → [3,9,27]
        r = UF1 ** UA1;  assert isinstance(r, UnitArray)
        assert _flat(r) == pytest.approx([3., 9., 27.])
        assert r._unit.is_dimensionless()

    def test_unitfloat1_probunitarray1_exp(self):
        # base=3("1"), exp=PUA1([1,2,3,4,1,2,3,4,1,2,3,4])
        r = UF1 ** PUA1; assert isinstance(r, ProbUnitArray)
        expected = [3.**v for v in [1.,2.,3.,4., 1.,2.,3.,4., 1.,2.,3.,4.]]
        assert _flat(r) == pytest.approx(expected)
        assert r._unit.is_dimensionless()

    def test_unitarray1_probunitfloat1_exp(self):
        # UA1([1,2,3]) ** PUF1([1,2,3,4]) → ProbUnitArray(len=3, n=4)
        # i=0: [1^1,1^2,1^3,1^4]=[1,1,1,1]
        # i=1: [2^1,2^2,2^3,2^4]=[2,4,8,16]
        # i=2: [3^1,3^2,3^3,3^4]=[3,9,27,81]
        expected = [1.,1.,1.,1., 2.,4.,8.,16., 3.,9.,27.,81.]
        r = UA1 ** PUF1; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        assert r._unit.is_dimensionless()

    def test_probunitfloat1_probunitfloat1_exp(self):
        # PUF1[j] ** PUF1[j]: [1^1,2^2,3^3,4^4]=[1,4,27,256]
        r = PUF1 ** PUF1; assert isinstance(r, ProbUnitFloat)
        assert _flat(r) == pytest.approx([1., 4., 27., 256.])
        assert r._unit.is_dimensionless()

    def test_probunitarray1_unitarray1_exp(self):
        # PUA1[i][j] ** UA1[i]  → ProbUnitArray
        # i=0: [1^1,2^1,3^1,4^1]=[1,2,3,4]
        # i=1: [1^2,2^2,3^2,4^2]=[1,4,9,16]
        # i=2: [1^3,2^3,3^3,4^3]=[1,8,27,64]
        expected = [1.,2.,3.,4., 1.,4.,9.,16., 1.,8.,27.,64.]
        r = PUA1 ** UA1; assert isinstance(r, ProbUnitArray)
        assert _flat(r) == pytest.approx(expected)
        assert r._unit.is_dimensionless()


# ═══════════════════════════════════════════════════════════════════════════════
# Error cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrors:

    # ── add / sub: incompatible units ─────────────────────────────────────────

    def test_add_incompatible_dimensional_units(self):
        with pytest.raises(IncompatibleUnitsError):
            UF + UFS    # m + s

    def test_add_float_plus_dimensional_unit(self):
        # float coerced to "1"; "1" is not compatible with "m"
        with pytest.raises(IncompatibleUnitsError):
            F + UF

    def test_sub_incompatible_units(self):
        with pytest.raises(IncompatibleUnitsError):
            UF - UFS

    def test_sub_float_minus_dimensional(self):
        with pytest.raises(IncompatibleUnitsError):
            F - UF

    # ── add / sub: shape mismatches ───────────────────────────────────────────

    def test_add_n_mismatch(self):
        with pytest.raises(ValueError, match="Sample count mismatch"):
            PUF + PUF3    # n=4 vs n=3

    def test_add_len_mismatch(self):
        with pytest.raises(ValueError, match="Length mismatch"):
            UA + UA2      # len=3 vs len=2

    def test_add_n_mismatch_probunitarray(self):
        pua_n3 = ProbUnitArray._from_flat(
            _array.array('d', [1.,2.,3., 4.,5.,6., 7.,8.,9.]), "m", 3, 3)
        with pytest.raises(ValueError, match="Sample count mismatch"):
            PUA + pua_n3    # n=4 vs n=3

    # ── pow: non-dimensionless exponent ──────────────────────────────────────

    def test_pow_dimensional_unitfloat_exponent(self):
        with pytest.raises(DimensionError):
            UF ** UF    # exponent unit = "m"

    def test_pow_dimensional_probunitfloat_exponent(self):
        with pytest.raises(DimensionError):
            UF1 ** PUF  # exponent unit = "m"

    def test_pow_dimensional_unitarray_exponent(self):
        with pytest.raises(DimensionError):
            UF1 ** UA   # exponent unit = "m"

    # ── pow: dimensional base with multi-value exponent ───────────────────────

    def test_pow_dimensional_base_probunitfloat_exp(self):
        with pytest.raises(DimensionError):
            UF ** PUF1    # base="m", multi-value exp

    def test_pow_dimensional_base_unitarray_exp(self):
        with pytest.raises(DimensionError):
            UF ** UA1     # base="m", multi-value exp

    def test_pow_dimensional_base_probunitarray_exp(self):
        with pytest.raises(DimensionError):
            UA ** PUF1    # base="m" array, multi-value exp

    def test_pow_dimensional_base_probunitarray_probunitarray_exp(self):
        with pytest.raises(DimensionError):
            PUA ** PUA1   # base="m", multi-value exp

    # ── unsupported type ──────────────────────────────────────────────────────

    def test_unsupported_type_raises_typeerror(self):
        from quantia._dispatch import _dispatch
        with pytest.raises(TypeError):
            _dispatch("add", "not_a_unit", UF)