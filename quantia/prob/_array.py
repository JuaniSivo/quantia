from __future__ import annotations
import array as _array, math, operator
from typing import Iterable, Iterator
from quantia._compound import CompoundUnit, _make_unit
from quantia._array import UnitArray
from quantia._scalar import UnitFloat
from quantia.prob._scalar import ProbUnitFloat
from quantia._exceptions import IncompatibleUnitsError


class ProbUnitArray:
    def __init__(self, elements: Iterable[ProbUnitFloat]):
        elems=list(elements)
        if not elems: raise ValueError("ProbUnitArray requires at least one element")
        self._unit=elems[0]._unit; self._n=elems[0]._n; self._len=len(elems)
        flat=[]
        for i,el in enumerate(elems):
            if not el._unit.is_compatible(self._unit): raise IncompatibleUnitsError(el._unit,self._unit)
            if el._n!=self._n: raise ValueError(f"Element {i} has {el._n} samples; expected {self._n}")
            f=el._unit.si_factor()/self._unit.si_factor()
            flat.extend(v*f for v in el._samples)
        self._data=_array.array('d',flat)

    @classmethod
    def _from_flat(cls,data,unit,length,n):
        obj=object.__new__(cls); obj._data=data; obj._unit=_make_unit(unit)
        obj._len=length; obj._n=n; return obj

    def _row(self,i): return self._data[i*self._n:(i+1)*self._n]
    def __len__(self): return self._len
    def __iter__(self) -> Iterator[ProbUnitFloat]:
        for i in range(self._len): yield ProbUnitFloat._from_raw(self._row(i),self._unit)
    def __getitem__(self,idx):
        if isinstance(idx,slice):
            indices=range(*idx.indices(self._len)); flat=_array.array('d')
            for i in indices: flat.extend(self._row(i))
            return ProbUnitArray._from_flat(flat,self._unit,len(indices),self._n)
        i=idx if idx>=0 else self._len+idx
        return ProbUnitFloat._from_raw(self._row(i),self._unit)

    def to_si(self):
        f=self._unit.si_factor(); cu=self._unit.to_si_compound()
        return ProbUnitArray._from_flat(_array.array('d',(v*f for v in self._data)),cu,self._len,self._n)
    def to(self,target):
        tcu=_make_unit(target)
        if not self._unit.is_compatible(tcu): raise IncompatibleUnitsError(self._unit,tcu)
        f=self._unit.si_factor()/tcu.si_factor()
        return ProbUnitArray._from_flat(_array.array('d',(v*f for v in self._data)),tcu,self._len,self._n)

    def _apply(self,o,op,result_unit):
        if isinstance(o,ProbUnitArray):
            if len(o)!=self._len: raise ValueError("Length mismatch")
            f=o._unit.si_factor()/self._unit.si_factor()
            out=_array.array('d',(op(a,b*f) for a,b in zip(self._data,o._data)))
        elif isinstance(o,ProbUnitFloat):
            f=o._unit.si_factor()/self._unit.si_factor(); b=_array.array('d',(v*f for v in o._samples))
            out=_array.array('d')
            for i in range(self._len): out.extend(op(a,b[j]) for j,a in enumerate(self._row(i)))
        elif isinstance(o,(int,float)): out=_array.array('d',(op(v,float(o)) for v in self._data))
        else: return NotImplemented
        return ProbUnitArray._from_flat(out,result_unit,self._len,self._n)

    def _apply_mul(self,o,op):
        if isinstance(o,(ProbUnitArray,ProbUnitFloat)):
            cu=op(self._unit,o._unit); cu=CompoundUnit.dimensionless() if cu.is_dimensionless() else cu
            return self._apply(o,op,cu)
        if isinstance(o,(int,float)):
            out=_array.array('d',(op(v,float(o)) for v in self._data))
            return ProbUnitArray._from_flat(out,self._unit,self._len,self._n)
        return NotImplemented

    def __add__(self,o): return self._apply(o,operator.add,self._unit)
    def __radd__(self,o): return self.__add__(o)
    def __sub__(self,o): return self._apply(o,operator.sub,self._unit)
    def __mul__(self,o): return self._apply_mul(o,operator.mul)
    def __rmul__(self,o):
        if isinstance(o,(int,float)):
            out=_array.array('d',(v*float(o) for v in self._data))
            return ProbUnitArray._from_flat(out,self._unit,self._len,self._n)
        return NotImplemented
    def __truediv__(self,o): return self._apply_mul(o,operator.truediv)
    def __pow__(self,e):
        out=_array.array('d',(v**e for v in self._data))
        return ProbUnitArray._from_flat(out,self._unit**e,self._len,self._n)
    def __neg__(self):
        out=_array.array('d',(-v for v in self._data))
        return ProbUnitArray._from_flat(out,self._unit,self._len,self._n)

    def _welford_row(self, i: int) -> tuple[float, float]:
        n = 0; mean = 0.0; M2 = 0.0
        for x in self._row(i):
            n += 1
            delta = x - mean
            mean += delta / n
            M2   += delta * (x - mean)
        v = M2 / (n - 1) if n >= 2 else 0.0
        return mean, v

    def means(self) -> UnitArray:
        return UnitArray(
            [sum(self._row(i)) / self._n for i in range(self._len)],
            self._unit
        )

    def stds(self) -> UnitArray:
        return UnitArray([self._welford_row(i)[1] ** 0.5 for i in range(self._len)], self._unit)
    
    def medians(self) -> UnitArray:
        vals = []
        for i in range(self._len):
            s   = sorted(self._row(i))
            mid = self._n // 2
            m   = s[mid] if self._n % 2 else (s[mid - 1] + s[mid]) / 2
            vals.append(m)
        return UnitArray(vals, self._unit)
    
    def intervals(self,confidence=0.95):
        tail=(1-confidence)/2; result=[]
        for i in range(self._len):
            s=sorted(self._row(i))
            result.append((UnitFloat(s[int(math.floor(tail*self._n))],self._unit),
                           UnitFloat(s[int(math.ceil((1-tail)*self._n))-1],self._unit)))
        return result

    def __repr__(self):
        ms=[f"{sum(self._row(i))/self._n:.4g}" for i in range(min(4,self._len))]
        dots=", ..." if self._len>4 else ""
        return f"ProbUnitArray(means=[{', '.join(ms)}{dots}], unit='{self._unit}', len={self._len}, n={self._n})"
    def __str__(self): return self.__repr__()

    # ── Serialization ─────────────────────────────────────────────────────────────
    
    def to_dict(self) -> dict:
        return {
            "type": "ProbUnitArray",
            "unit": str(self._unit),
            "len":  self._len,
            "n":    self._n,
            "data": list(self._data),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProbUnitArray":
        if d.get("type") != "ProbUnitArray":
            raise ValueError(f"Expected type 'ProbUnitArray', got {d.get('type')!r}")
        import array as _array
        return cls._from_flat(_array.array('d', d["data"]), d["unit"], d["len"], d["n"])
    
    def to_csv(self, path, confidence: float = 0.95) -> None:
        """
        Write per-element statistics (mean, std, CI bounds) to CSV.

        Columns: mean, std, ci_lo, ci_hi  — all in the array's unit.
        """
        import csv, math
        from pathlib import Path
        unit_str = str(self._unit)
        tail = (1 - confidence) / 2
        lo_lbl = f"ci_{tail*100:.1f}pct [{unit_str}]"
        hi_lbl = f"ci_{(1-tail)*100:.1f}pct [{unit_str}]"
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([f"mean [{unit_str}]", f"std [{unit_str}]", lo_lbl, hi_lbl])
            for i in range(self._len):
                mean, var = self._welford_row(i)
                s   = sorted(self._row(i))
                lo  = s[int(math.floor(tail * self._n))]
                hi  = s[int(math.ceil((1 - tail) * self._n)) - 1]
                w.writerow([mean, var ** 0.5, lo, hi])

    def samples_to_csv(self, path) -> None:
        """
        Write the full sample matrix to CSV.

        Shape: self._len rows × self._n columns.
        Header row: sample_0, sample_1, …
        """
        import csv
        from pathlib import Path
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([f"sample_{j}" for j in range(self._n)])
            for i in range(self._len):
                w.writerow(list(self._row(i)))