"""
quantia/profiling/benchmark.py
==============================
Profile quantia across three sample sizes: 1k, 10k, 100k.

Run with:
    python -m quantia.profiling.benchmark
    python -m quantia.profiling.benchmark --profile   # cProfile detail

Measures wall time for each operation category so we know exactly
where to focus Phase 4 optimizations.
"""

import time
import math
import random
import cProfile
import pstats
import io
import argparse
from typing import Callable


# ── Timer helper ─────────────────────────────────────────────────────────────

class Timer:
    def __init__(self, label: str, n_samples: int):
        self.label    = label
        self.n_samples = n_samples
        self._start   = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        elapsed = time.perf_counter() - self._start
        print(f"  {self.label:<45s} {elapsed*1000:>10.2f} ms")


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def subsection(title: str, n: int):
    print(f"\n  ── n={n:,} ──────────────────────────────────────────")


# ── Benchmark groups ─────────────────────────────────────────────────────────

def bench_construction(n: int):
    import quantia as qu

    subsection("Construction", n)

    with Timer("UnitFloat(5, 'km')", n):
        for _ in range(n):
            qu.Q(5, "km")

    with Timer("UnitArray([...], 'km')  1k elements", n):
        vals = list(range(1000))
        for _ in range(max(1, n // 1000)):
            qu.QA(vals, "km")

    with Timer("ProbUnitFloat.uniform(0, 1, 'm')", n):
        qu.ProbUnitFloat.uniform(0, 1, "m", n=n)

    with Timer("ProbUnitFloat.normal(10, 1, 'm')", n):
        qu.ProbUnitFloat.normal(10, 1, "m", n=n)

    with Timer("ProbUnitFloat.triangular(8,10,12,'m')", n):
        qu.ProbUnitFloat.triangular(8, 10, 12, "m", n=n)

    with Timer("ProbUnitFloat.lognormal(0, 0.1, 'm')", n):
        qu.ProbUnitFloat.lognormal(0, 0.1, "m", n=n)

    with Timer("CorrelatedSource(n_vars=3, rho=0.8)", n):
        src = qu.CorrelatedSource(n_vars=3, rho=0.8, n=n)
        src.draw(0, "normal", "m",  mean=10, std=1)
        src.draw(1, "normal", "s",  mean=2,  std=0.1)
        src.draw(2, "normal", "kg", mean=70, std=5)


def bench_scalar_arithmetic(n: int):
    import quantia as qu

    subsection("ProbUnitFloat arithmetic", n)

    a = qu.ProbUnitFloat.uniform(8, 12, "m",  n=n)
    b = qu.ProbUnitFloat.uniform(1, 3,  "s",  n=n)
    c = qu.ProbUnitFloat.normal(70, 5,  "kg", n=n)
    d = qu.ProbUnitFloat.uniform(1, 2,  "m",  n=n)

    with Timer("a + d  (compatible units)", n):
        _ = a + d

    with Timer("a - d  (compatible units)", n):
        _ = a - d

    with Timer("a * c  (compound unit)", n):
        _ = a * c

    with Timer("a / b  (compound unit → m/s)", n):
        _ = a / b

    with Timer("a ** 2 (unit exponent)", n):
        _ = a ** 2

    with Timer("chain: (a * c) / b  (F=ma style)", n):
        _ = (a * c) / b

    with Timer("chain: a / b / c    (3-step compound)", n):
        _ = a / b / c


def bench_statistics(n: int):
    import quantia as qu

    subsection("ProbUnitFloat statistics", n)

    x = qu.ProbUnitFloat.normal(100, 10, "m", n=n)

    with Timer("mean()", n):
        _ = x.mean()

    with Timer("std()", n):
        _ = x.std()

    with Timer("median()", n):
        _ = x.median()

    with Timer("interval(0.95)", n):
        _ = x.interval(0.95)

    with Timer("percentile(10)", n):
        _ = x.percentile(10)

    with Timer("histogram(bins=20)", n):
        _ = x.histogram(bins=20)

    with Timer("prob_lt(other ProbUnitFloat)", n):
        y = qu.ProbUnitFloat.normal(105, 10, "m", n=n)
        _ = x.prob_lt(y)


def bench_conversion(n: int):
    import quantia as qu

    subsection("Conversion", n)

    x = qu.ProbUnitFloat.uniform(50, 150, "km", n=n)
    uf = qu.Q(100, "km")

    with Timer("ProbUnitFloat.to('m')", n):
        _ = x.to("m")

    with Timer("ProbUnitFloat.to_si()", n):
        _ = x.to_si()

    with Timer("UnitFloat.to('mi')  [exact]", n):
        for _ in range(n):
            _ = uf.to("mi")


def bench_prob_array(n: int):
    import quantia as qu

    k = 20   # number of elements in ProbUnitArray

    subsection(f"ProbUnitArray  (k={k} elements)", n)

    elems = [qu.ProbUnitFloat.normal(float(i), 0.5, "m", n=n) for i in range(k)]

    with Timer("ProbUnitArray construction", n):
        arr = qu.ProbUnitArray(elems)

    arr = qu.ProbUnitArray(elems)   # pre-built for remaining tests

    with Timer("arr.means()   → UnitArray", n):
        _ = arr.means()

    with Timer("arr.stds()    → UnitArray", n):
        _ = arr.stds()

    with Timer("arr.intervals(0.95)", n):
        _ = arr.intervals(0.95)

    elems2 = [qu.ProbUnitFloat.normal(1.0, 0.1, "s", n=n) for _ in range(k)]
    arr2   = qu.ProbUnitArray(elems2)

    with Timer("arr / arr2    (element-wise compound)", n):
        _ = arr / arr2


def bench_parse(n: int):
    import quantia as qu

    subsection("parse_unit  (called repeatedly)", n)

    exprs = [
        "kg·m/s^2",
        "m^(1/2)",
        "kg/m^2/s",
        "N·m/s",
        "kg·m^(2/3)/s^2",
    ]

    with Timer(f"parse_unit × {n} calls (5 expressions)", n):
        for i in range(n):
            qu.parse_unit(exprs[i % len(exprs)])


def bench_correlated_source(n: int):
    import quantia as qu

    subsection("CorrelatedSource (Gaussian copula generation)", n)

    for k in (2, 5, 10):
        with Timer(f"gaussian_copula  k={k} vars", n):
            src = qu.CorrelatedSource(n_vars=k, rho=0.7, n=n)
            for i in range(k):
                src.draw(i, "normal", "m", mean=10, std=1)


# ── Rs correlation (real-world petroleum example) ────────────────────────────

def bench_rs_correlation(n: int):
    import quantia as qu
    import quantia.math as mmath

    subsection("Rs correlation (petroleum, full pipeline)", n)

    a1, a2, a3, a4, a5 = 0.3818, -5.506, 2.902, 1.327, -0.7355

    SG_g = 0.65
    Tsp  = qu.Q(10, "°C").to("°F")
    Psp  = qu.Q(1, "atm").to("psi")

    with Timer("SG_o = ProbUnitFloat.uniform(0.92, 0.96)", n):
        SG_o = qu.ProbUnitFloat.uniform(0.92, 0.96, "1", n=n)

    with Timer("log10(SG_o)", n):
        l_SGo = mmath.log10(SG_o)

    with Timer("full Rs expression", n):
        log_Rst = (a1
                 + a2 * l_SGo
                 + a3 * math.log10(SG_g)
                 + a4 * math.log10(Psp.value)
                 + a5 * math.log10(Tsp.value))
        Rst = mmath.exp(log_Rst)

    with Timer("Rst.mean() + interval(0.95)", n):
        _ = Rst.mean()
        _ = Rst.interval(0.95)


# ── Main ─────────────────────────────────────────────────────────────────────

SAMPLE_SIZES = [1_000, 10_000, 100_000]

BENCHMARKS: list[Callable] = [
    bench_construction,
    bench_scalar_arithmetic,
    bench_statistics,
    bench_conversion,
    bench_prob_array,
    bench_parse,
    bench_correlated_source,
    bench_rs_correlation,
]


def run_all(sizes=SAMPLE_SIZES):
    random.seed(42)
    for bench in BENCHMARKS:
        section(bench.__name__.replace("bench_", "").replace("_", " ").title())
        for n in sizes:
            bench(n)


def run_cprofile(n: int = 10_000):
    """Detailed cProfile run at a single sample size."""
    import quantia as qu
    import quantia.math as mmath

    pr = cProfile.Profile()
    pr.enable()

    # Run the most expensive operations
    a = qu.ProbUnitFloat.normal(10, 1, "m", n=n)
    b = qu.ProbUnitFloat.normal(2, 0.2, "s", n=n)
    c = qu.ProbUnitFloat.normal(70, 5, "kg", n=n)
    speed   = a / b
    force   = c * (a / b)
    energy  = force * a
    log_e   = mmath.log10(energy)
    _ = log_e.mean()
    _ = log_e.interval(0.95)

    src = qu.CorrelatedSource(n_vars=3, rho=0.8, n=n)
    x = src.draw(0, "normal", "m",  mean=10, std=1)
    y = src.draw(1, "normal", "s",  mean=2,  std=0.1)
    z = src.draw(2, "normal", "kg", mean=70, std=5)
    _ = (x * z) / y

    pr.disable()

    s  = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    print(s.getvalue())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="quantia benchmark")
    parser.add_argument("--profile", action="store_true",
                        help="Run cProfile detail at n=10k instead of wall-time benchmarks")
    parser.add_argument("--n", type=int, default=None,
                        help="Run at a single sample size instead of all three")
    args = parser.parse_args()

    if args.profile:
        n = args.n or 10_000
        print(f"\ncProfile detail  n={n:,}\n{'='*60}")
        run_cprofile(n)
    else:
        sizes = [args.n] if args.n else SAMPLE_SIZES
        run_all(sizes)