import math
import random
import array as _array
from mensura.prob._scalar import ProbUnitFloat
from mensura.prob._distributions import (
    _norm_cdf, icdf_uniform, icdf_normal, icdf_triangular, icdf_lognormal
)
from mensura.prob._config import _N_SAMPLES

_N_SAMPLES = 1000


class CorrelatedSource:
    """
    Generates correlated uniform percentile arrays via a Gaussian copula,
    then applies inverse CDFs to produce ProbUnitFloat instances.

    Construction
    ------------
    # Two variables with scalar correlation ρ:
    src = CorrelatedSource(n_vars=2, rho=0.9)

    # Arbitrary K×K correlation matrix:
    src = CorrelatedSource(corr_matrix=[[1, .8], [.8, 1]])

    Usage
    -----
    x = src.draw(slot=0, dist="normal",     mean=10, std=1,  unit="m")
    y = src.draw(slot=1, dist="triangular", low=4,   mode=5, high=6, unit="s")

    Available dist values: "uniform", "normal", "triangular", "lognormal"
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
                 n: int = _N_SAMPLES):
        if corr_matrix is not None:
            self._matrix = corr_matrix
            self._k      = len(corr_matrix)
        elif n_vars is not None and rho is not None:
            if not -1.0 < rho < 1.0:
                raise ValueError("rho must be in (-1, 1)")
            self._k      = n_vars
            self._matrix = [
                [1.0 if i == j else rho for j in range(n_vars)]
                for i in range(n_vars)
            ]
        else:
            raise ValueError("Provide either (n_vars, rho) or corr_matrix.")

        self._n        = n
        self._uniforms = gaussian_copula(n, self._matrix)
        self._used: set[int] = set()

    def draw(self, slot: int, dist: str, unit, **params) -> "ProbUnitFloat":
        """
        Draw a ProbUnitFloat from the given slot with the given distribution.

        Parameters
        ----------
        slot  : int    — which correlated variable to use (0-based)
        dist  : str    — "uniform", "normal", "triangular", or "lognormal"
        unit  : str | CompoundUnit
        **params       — distribution parameters:
                         uniform:    low, high
                         normal:     mean, std
                         triangular: low, mode, high
                         lognormal:  mean, std
        """
        from mensura.prob._scalar import ProbUnitFloat

        if slot < 0 or slot >= self._k:
            raise IndexError(
                f"Slot {slot} out of range for a {self._k}-variable source.")
        if slot in self._used:
            raise RuntimeError(
                f"Slot {slot} has already been drawn. "
                "Each slot can only be used once.")
        if dist not in self._DIST_MAP:
            raise ValueError(
                f"Unknown distribution '{dist}'. "
                f"Choose from: {list(self._DIST_MAP)}")

        icdf = self._DIST_MAP[dist]
        p    = self._uniforms[slot]

        try:
            samples = _array.array('d', (icdf(pi, **params) for pi in p))
        except TypeError as e:
            raise TypeError(
                f"Wrong parameters for distribution '{dist}': {e}") from e

        self._used.add(slot)
        return ProbUnitFloat._from_raw(samples, unit)

    # ── Convenience wrappers (optional shorthand) ─────────────────────────────

    def uniform(self, slot: int, low: float, high: float, unit) -> "ProbUnitFloat":
        return self.draw(slot, "uniform", unit, low=low, high=high)

    def normal(self, slot: int, mean: float, std: float, unit) -> "ProbUnitFloat":
        return self.draw(slot, "normal", unit, mean=mean, std=std)

    def triangular(self, slot: int, low: float, mode: float,
                   high: float, unit) -> "ProbUnitFloat":
        return self.draw(slot, "triangular", unit, low=low, mode=mode, high=high)

    def lognormal(self, slot: int, mean: float, std: float, unit) -> "ProbUnitFloat":
        return self.draw(slot, "lognormal", unit, mean=mean, std=std)


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    """Lower Cholesky factor L such that matrix = L·Lᵀ."""
    k = len(matrix)
    L = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(i + 1):
            s = sum(L[i][m] * L[j][m] for m in range(j))
            if i == j:
                val = matrix[i][i] - s
                if val < 0:
                    raise ValueError(
                        "Correlation matrix is not positive definite. "
                        "Check that all |ρ| < 1 and the matrix is consistent.")
                L[i][j] = math.sqrt(val)
            else:
                L[i][j] = (matrix[i][j] - s) / L[j][j]
    return L


def gaussian_copula(n: int, corr_matrix: list[list[float]]) -> list[_array.array]:
    """
    Generate K arrays of n correlated uniform samples in (0, 1).

    Steps
    -----
    1. Cholesky-decompose the K×K correlation matrix: R = L·Lᵀ
    2. Draw K independent standard normals z for each sample
    3. Compute u = L·z  →  correlated standard normals
    4. Apply Φ to each u  →  correlated uniforms in (0, 1)
    """
    k   = len(corr_matrix)
    L   = _cholesky(corr_matrix)
    eps = 1e-9

    result = [_array.array('d', [0.0] * n) for _ in range(k)]
    for s in range(n):
        z = [random.gauss(0, 1) for _ in range(k)]
        for i in range(k):
            u = sum(L[i][j] * z[j] for j in range(i + 1))
            result[i][s] = max(eps, min(1 - eps, _norm_cdf(u)))
    return result