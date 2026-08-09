"""Paired significance tests for the headline deltas — deterministic, stdlib only.

For each delta contrast (variant A vs variant B) within an arm, the per-set
strict outcomes form matched binary pairs. The exact McNemar / sign test uses
only the discordant pairs: n01 = sets where A passed and B failed, n10 = the
reverse. Under H0 the discordant direction is Bin(n, 0.5); the exact two-sided
p-value is 2 * min(P(X <= k), P(X >= k)) capped at 1, with k = n01.

Holm-Bonferroni is applied across the full delta x arm family.
"""

from __future__ import annotations

from math import comb


def binom_cdf(k: int, n: int) -> float:
    """P(X <= k) for X ~ Bin(n, 0.5)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)


def exact_sign_test(n01: int, n10: int) -> float:
    """Exact two-sided McNemar/sign test p-value on discordant counts."""
    n = n01 + n10
    if n == 0:
        return 1.0
    lower = binom_cdf(n01, n)
    upper = 1.0 - binom_cdf(n01 - 1, n)
    return min(1.0, 2.0 * min(lower, upper))


def paired_counts(pairs: list[tuple[float, float]]) -> tuple[int, int]:
    """(n01, n10): A-pass/B-fail and A-fail/B-pass counts over per-set pairs."""
    n01 = sum(1 for a, b in pairs if a >= 0.5 > b)
    n10 = sum(1 for a, b in pairs if b >= 0.5 > a)
    return n01, n10


def holm_bonferroni(pvalues: dict) -> dict:
    """Holm step-down adjustment. Keys arbitrary; returns key -> adjusted p."""
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running_max = {}, 0.0
    for rank, (key, p) in enumerate(items):
        adj = min(1.0, (m - rank) * p)
        running_max = max(running_max, adj)  # enforce monotonicity
        adjusted[key] = running_max
    return adjusted


def _binom_cdf(k: int, n: int, p: float) -> float:
    from math import comb
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact (Clopper-Pearson) two-sided CI for a binomial proportion k/n,
    solved by bisection on the exact binomial tails (stdlib-only).

    lower: largest p with P(X >= k | p) = alpha/2  (0 when k == 0)
    upper: smallest p with P(X <= k | p) = alpha/2 (1 when k == n)
    """
    assert 0 <= k <= n and n > 0

    def solve(f, increasing):
        # find p in (0,1) with f(p) == alpha/2; f monotone in p
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            too_high = f(mid) > alpha / 2
            if too_high == increasing:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    # P(X >= k | p) increases with p; P(X <= k | p) decreases with p
    lower = 0.0 if k == 0 else solve(
        lambda p: 1 - _binom_cdf(k - 1, n, p), increasing=True)
    upper = 1.0 if k == n else solve(
        lambda p: _binom_cdf(k, n, p), increasing=False)
    return lower, upper
