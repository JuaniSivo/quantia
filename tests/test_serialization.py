"""Tests for Phase 5: to_dict / from_dict, save/load, CSV export."""
import json, csv, math, tempfile
from pathlib import Path
import pytest
import quantia as qu


# ── UnitFloat ─────────────────────────────────────────────────────────────────

def test_unitfloat_roundtrip():
    uf = qu.Q(9.81, "m/s^2")
    d  = uf.to_dict()
    assert d["type"]  == "UnitFloat"
    assert d["value"] == pytest.approx(9.81)
    assert d["unit"]  == "m/s^2"
    uf2 = qu.UnitFloat.from_dict(d)
    assert uf2.value == pytest.approx(uf.value)
    assert str(uf2.unit) == str(uf.unit)

def test_unitfloat_from_dict_wrong_type():
    with pytest.raises(ValueError, match="UnitFloat"):
        qu.UnitFloat.from_dict({"type": "UnitArray", "values": [], "unit": "m"})


# ── UnitArray ─────────────────────────────────────────────────────────────────

def test_unitarray_roundtrip():
    ua  = qu.QA([1.0, 2.0, 3.0], "km")
    d   = ua.to_dict()
    ua2 = qu.UnitArray.from_dict(d)
    assert list(ua2.values) == pytest.approx(list(ua.values))
    assert str(ua2.unit) == "km"

def test_unitarray_to_csv():
    ua = qu.QA([10.0, 20.0, 30.0], "m")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    ua.to_csv(path)
    rows = list(csv.reader(open(path)))
    assert rows[0] == ["value [m]"]
    assert float(rows[1][0]) == pytest.approx(10.0)
    assert len(rows) == 4   # header + 3 data rows


# ── ProbUnitFloat ─────────────────────────────────────────────────────────────

def test_probunitfloat_roundtrip():
    with qu.config(seed=42):
        pf = qu.QP(0.0, 1.0, "m", n=200)
    d   = pf.to_dict()
    assert d["type"] == "ProbUnitFloat"
    assert len(d["samples"]) == 200
    pf2 = qu.ProbUnitFloat.from_dict(d)
    assert list(pf2._samples) == pytest.approx(list(pf._samples))
    assert str(pf2._unit) == "m"

def test_probunitfloat_from_dict_wrong_type():
    with pytest.raises(ValueError):
        qu.ProbUnitFloat.from_dict({"type": "UnitFloat", "value": 1.0, "unit": "m"})


# ── ProbUnitArray ─────────────────────────────────────────────────────────────

def test_probunitarray_roundtrip():
    with qu.config(seed=0):
        elems = [qu.QP(float(i), float(i)+1, "m", n=50) for i in range(3)]
    pa  = qu.QPA(elems)
    d   = pa.to_dict()
    pa2 = qu.ProbUnitArray.from_dict(d)
    assert pa2._len == pa._len
    assert pa2._n   == pa._n
    assert list(pa2._data) == pytest.approx(list(pa._data))

def test_probunitarray_to_csv():
    with qu.config(seed=7):
        elems = [qu.ProbUnitFloat.normal(float(i)*10, 1.0, "m", n=500) for i in range(4)]
    pa = qu.QPA(elems)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    pa.to_csv(path)
    rows = list(csv.reader(open(path)))
    assert len(rows) == 5   # header + 4 elements
    assert "mean" in rows[0][0]
    assert "std"  in rows[0][1]

def test_probunitarray_samples_to_csv():
    with qu.config(seed=3):
        elems = [qu.ProbUnitFloat.normal(1.0, 0.1, "kg", n=100) for _ in range(5)]
    pa = qu.QPA(elems)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    pa.samples_to_csv(path)
    rows = list(csv.reader(open(path)))
    assert len(rows) == 6   # header + 5 element rows
    assert len(rows[0]) == 100   # 100 sample columns


# ── Top-level save / load ─────────────────────────────────────────────────────

def test_save_load_unitfloat(tmp_path):
    uf = qu.Q(42.0, "kJ")
    p  = tmp_path / "val.json"
    qu.save(uf, p)
    uf2 = qu.load(p)
    assert uf2.value == pytest.approx(42.0)
    assert str(uf2.unit) == "kJ"

def test_save_load_probunitfloat(tmp_path):
    with qu.config(seed=99):
        pf = qu.ProbUnitFloat.normal(100.0, 5.0, "Pa", n=300)
    p  = tmp_path / "pf.json"
    qu.save(pf, p)
    pf2 = qu.load(p)
    assert pf2.mean().value == pytest.approx(pf.mean().value, rel=1e-6)

def test_from_dict_unknown_type():
    with pytest.raises(ValueError, match="Unknown quantia type"):
        qu.from_dict({"type": "Banana"})