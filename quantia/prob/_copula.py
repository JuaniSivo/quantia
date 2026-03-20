from __future__ import annotations
import math, random
import array as _array
from typing import Union
from quantia._compound import CompoundUnit
from quantia.prob._scalar import ProbUnitFloat
from quantia.prob._distributions import (
    _norm_cdf, icdf_uniform, icdf_normal, icdf_triangular, icdf_lognormal
)

_N_SAMPLES = 1000


def _cholesky(matrix):
    k = len(matrix); L = [[0.0]*k for _ in range(k)]
    for i in range(k):
        for j in range(i+1):
            s = sum(L[i][m]*L[j][m] for m in range(j))
            if i==j:
                val=matrix[i][i]-s
                if val<0: raise ValueError("Correlation matrix is not positive definite.")
                L[i][j]=math.sqrt(val)
            else: L[i][j]=(matrix[i][j]-s)/L[j][j]
    return L


def _validate_corr_matrix(matrix: list[list[float]]) -> None:
    """2d: validate correlation matrix."""
    k = len(matrix)
    for i, row in enumerate(matrix):
        if len(row) != k:
            raise ValueError(f"Correlation matrix row {i} has {len(row)} elements, expected {k}")
        if not math.isclose(matrix[i][i], 1.0):
            raise ValueError(f"Diagonal element [{i}][{i}] must be 1.0, got {matrix[i][i]}")
        for j, v in enumerate(row):
            if abs(v) > 1.0 + 1e-9:
                raise ValueError(f"Correlation [{i}][{j}]={v} outside [-1, 1]")
            if not math.isclose(v, matrix[j][i]):
                raise ValueError(f"Matrix is not symmetric at [{i}][{j}]")


def gaussian_copula(n, corr_matrix):
    k=len(corr_matrix); L=_cholesky(corr_matrix); eps=1e-9
    result=[_array.array('d',[0.0]*n) for _ in range(k)]
    for s in range(n):
        z=[random.gauss(0,1) for _ in range(k)]
        for i in range(k):
            u=sum(L[i][j]*z[j] for j in range(i+1))
            result[i][s]=max(eps,min(1-eps,_norm_cdf(u)))
    return result


class CorrelatedSource:
    """
    Generates correlated ProbUnitFloat samples via a Gaussian copula.

    Construction
    ------------
    src = CorrelatedSource(n_vars=2, rho=0.9)
    src = CorrelatedSource(corr_matrix=[[1,.8],[.8,1]])

    Usage
    -----
    x = src.draw(slot=0, dist="normal",     mean=10, std=1,  unit="N")
    y = src.draw(slot=1, dist="triangular", low=4,   mode=5, high=6, unit="m")
    """

    _DIST_MAP = {
        "uniform":    icdf_uniform,
        "normal":     icdf_normal,
        "triangular": icdf_triangular,
        "lognormal":  icdf_lognormal,
    }

    def __init__(self,
                 n_vars: int | None = None,
                 rho: float | None = None,
                 corr_matrix: list[list[float]] | None = None,
                 n: int | None = None) -> None:
        from quantia.prob._scalar import _default_n
        n = _default_n(n)

        if corr_matrix is not None:
            _validate_corr_matrix(corr_matrix)   # 2d
            self._matrix = corr_matrix
            self._k      = len(corr_matrix)
        elif n_vars is not None and rho is not None:
            if not isinstance(n_vars, int) or n_vars < 2:
                raise ValueError(f"n_vars must be an integer >= 2, got {n_vars!r}")
            if not -1.0 < rho < 1.0:
                raise ValueError(f"rho must be in (-1, 1), got {rho}")
            self._k      = n_vars
            self._matrix = [[1.0 if i==j else rho for j in range(n_vars)]
                            for i in range(n_vars)]
        else:
            raise ValueError("Provide either (n_vars, rho) or corr_matrix.")

        if not isinstance(n, int) or n < 1:
            raise ValueError(f"n must be a positive integer, got {n!r}")
        
        from quantia.prob._scalar import _default_n
        self._n        = n
        self._uniforms = gaussian_copula(n, self._matrix)
        self._used: set[int] = set()

    def draw(self, slot: int, dist: str,
             unit: Union[str, "CompoundUnit"],
             **params) -> "ProbUnitFloat":
        from quantia.prob._scalar import ProbUnitFloat
        if not isinstance(slot, int) or slot < 0 or slot >= self._k:
            raise IndexError(f"Slot {slot} out of range [0, {self._k-1}]")
        if slot in self._used:
            raise RuntimeError(f"Slot {slot} already drawn. Each slot can only be used once.")
        if dist not in self._DIST_MAP:
            raise ValueError(f"Unknown distribution '{dist}'. Choose from: {list(self._DIST_MAP)}")
        icdf = self._DIST_MAP[dist]
        p    = self._uniforms[slot]
        try:
            samples = _array.array('d', (icdf(pi, **params) for pi in p))
        except TypeError as e:
            raise TypeError(f"Wrong parameters for distribution '{dist}': {e}") from e
        self._used.add(slot)
        return ProbUnitFloat._from_raw(samples, unit)

    def uniform(self, slot: int, low: float, high: float,
                unit: Union[str, "CompoundUnit"]) -> "ProbUnitFloat":
        return self.draw(slot, "uniform", unit, low=low, high=high)
    def normal(self, slot: int, mean: float, std: float,
               unit: Union[str, "CompoundUnit"]) -> "ProbUnitFloat":
        return self.draw(slot, "normal", unit, mean=mean, std=std)
    def triangular(self, slot: int, low: float, mode: float, high: float,
                   unit: Union[str, "CompoundUnit"]) -> "ProbUnitFloat":
        return self.draw(slot, "triangular", unit, low=low, mode=mode, high=high)
    def lognormal(self, slot: int, mean: float, std: float,
                  unit: Union[str, "CompoundUnit"]) -> "ProbUnitFloat":
        return self.draw(slot, "lognormal", unit, mean=mean, std=std)