from atlas.report import bootstrap_ci, compute_deltas, fingerprint


def scored(set_id, variant, score, mechanism=None, lang_user="ar"):
    return {
        "set_id": set_id,
        "task_id": f"{set_id}-{variant}",
        "mechanism": mechanism or set_id.split("-")[0],
        "variant": variant,
        "lang_user": lang_user,
        "score": score,
        "pass": bool(score),
        "components": {
            "ast": {"pass": bool(score)},
            "lang": {
                "pass": bool(score),
                "leakage_rate": {"args_arabic_leakage": 0.0, "answer_leakage": 0.0},
            },
        },
    }


def test_bootstrap_ci_deterministic():
    pairs = [(1.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)]
    d1 = bootstrap_ci(pairs, 500, seed=42)
    d2 = bootstrap_ci(pairs, 500, seed=42)
    assert d1 == d2
    delta, lo, hi = d1
    assert abs(delta - 0.5) < 1e-9
    assert lo <= delta <= hi


def test_bootstrap_ci_empty():
    delta, lo, hi = bootstrap_ci([], 100, seed=1)
    assert delta != delta  # NaN


def test_compute_deltas_paired_by_set():
    recs = []
    # Two M2 sets: greg_ar passes, hijri_ar fails -> Delta_M2_hijri = 1.0
    for s in ("M2-001", "M2-002"):
        recs.append(scored(s, "greg_ar", 1.0))
        recs.append(scored(s, "hijri_ar", 0.0))
        recs.append(scored(s, "greg_en", 1.0, lang_user="en"))
    out = compute_deltas(recs, n_resamples=200, seed=7)
    assert out["Delta_M2_hijri"]["delta"] == 1.0
    assert out["Delta_M2_hijri"]["n_sets"] == 2
    assert out["Delta_M2_lang"]["delta"] == 0.0
    # No M4/M6 records -> NaN deltas with zero sets
    assert out["Delta_M4_crosscall"]["n_sets"] == 0


def test_fingerprint_shape():
    recs = [
        scored("M2-001", "greg_ar", 1.0),
        scored("M2-001", "hijri_ar", 0.0),
    ]
    fp = fingerprint(recs)
    assert fp["M2"]["n"] == 2
    assert fp["M2"]["strict"] == 0.5
    assert fp["M2"]["by_variant"] == {"greg_ar": 1.0, "hijri_ar": 0.0}
    assert fp["M2"]["consistency_pass"] is None
