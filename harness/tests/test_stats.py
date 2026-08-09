from atlas.stats import binom_cdf, exact_sign_test, holm_bonferroni, paired_counts


def test_binom_cdf_basics():
    assert binom_cdf(-1, 10) == 0.0
    assert binom_cdf(10, 10) == 1.0
    assert abs(binom_cdf(5, 10) - 0.623046875) < 1e-9


def test_exact_sign_test_known_values():
    # 10 discordant pairs all in one direction: p = 2 * (1/1024)
    assert abs(exact_sign_test(10, 0) - 2 / 1024) < 1e-12
    assert abs(exact_sign_test(0, 10) - 2 / 1024) < 1e-12
    # balanced discordance is maximally insignificant
    assert exact_sign_test(5, 5) == 1.0
    # no discordant pairs -> p = 1
    assert exact_sign_test(0, 0) == 1.0
    # 8 vs 2: 2 * P(X <= 2) = 2 * (1+10+45)/1024
    assert abs(exact_sign_test(2, 8) - 2 * 56 / 1024) < 1e-12


def test_paired_counts():
    pairs = [(1.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.0, 0.0)]
    assert paired_counts(pairs) == (2, 1)


def test_holm_bonferroni():
    p = {"a": 0.01, "b": 0.04, "c": 0.03}
    adj = holm_bonferroni(p)
    assert abs(adj["a"] - 0.03) < 1e-12          # 3 * 0.01
    assert abs(adj["c"] - 0.06) < 1e-12          # 2 * 0.03
    assert abs(adj["b"] - 0.06) < 1e-12          # monotonicity: max(0.04, 0.06)
    assert all(0 <= v <= 1 for v in adj.values())


def test_clopper_pearson_reference_values():
    from atlas.stats import clopper_pearson
    for k, n, lo_ref, hi_ref in [(10, 10, 0.6915, 1.0), (0, 10, 0.0, 0.3085),
                                 (9, 10, 0.5550, 0.9975), (8, 10, 0.4439, 0.9748)]:
        lo, hi = clopper_pearson(k, n)
        assert abs(lo - lo_ref) < 5e-4 and abs(hi - hi_ref) < 5e-4, (k, n, lo, hi)
