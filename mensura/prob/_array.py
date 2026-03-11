from __future__ import annotations
import array as _array, math, operator, statistics
from typing import Iterable, Iterator
from mensura._compound import CompoundUnit, _make_unit
from mensura._array import UnitArray
from mensura._scalar import UnitFloat
from mensura.prob._scalar import ProbUnitFloat
from mensura._exceptions import IncompatibleUnitsError
from mensura.prob._copula import _N_SAMPLES


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

    def means(self)  ->UnitArray: return UnitArray([sum(self._row(i))/self._n for i in range(self._len)],self._unit)
    def stds(self)   ->UnitArray: return UnitArray([statistics.stdev(self._row(i)) for i in range(self._len)],self._unit)
    def medians(self)->UnitArray: return UnitArray([statistics.median(self._row(i)) for i in range(self._len)],self._unit)
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