import math


def _norm_cdf(x: float) -> float:
    """Φ(x) — standard normal CDF (Abramowitz & Stegun, error < 7.5e-8)."""
    a = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * a)
    p = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937
        + t * (-1.821255978 + t * 1.330274429))))
    c = 1.0 - (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * a * a) * p
    return c if x >= 0 else 1.0 - c


def _norm_ppf(p: float) -> float:
    """Φ⁻¹(p) — inverse standard normal CDF (Beasley-Springer-Moro)."""
    if not (0.0 < p < 1.0):
        raise ValueError(f"p must be in (0, 1), got {p}")
    a = (-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00)
    d = ( 7.784695709041462e-03,  3.224671290700398e-01,
          2.445134137142996e+00,  3.754408661907416e+00)
    lo, hi = 0.02425, 1 - 0.02425
    if p < lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= hi:
        q = p - 0.5; r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


# ── Inverse CDFs ─────────────────────────────────────────────────────────────

def icdf_uniform(p: float, low: float, high: float) -> float:
    return low + p * (high - low)

def icdf_normal(p: float, mean: float, std: float) -> float:
    return mean + std * _norm_ppf(p)

def icdf_triangular(p: float, low: float, mode: float, high: float) -> float:
    fc = (mode - low) / (high - low)
    if p < fc:
        return low  + math.sqrt(p * (high - low) * (mode - low))
    else:
        return high - math.sqrt((1 - p) * (high - low) * (high - mode))

def icdf_lognormal(p: float, mean: float, std: float) -> float:
    """mean, std are parameters of the underlying normal (ln X ~ N(mean, std))."""
    return math.exp(mean + std * _norm_ppf(p))