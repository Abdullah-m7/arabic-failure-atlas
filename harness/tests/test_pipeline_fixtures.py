"""End-to-end proof of the pipeline on fixture model outputs (no credentials):
run -> raw results -> report -> fingerprint + deltas."""

import json
from pathlib import Path

from atlas import report, run

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _models_yaml(tmp_path: Path) -> Path:
    cfg = f"""
models:
  - name: fixtures-pass
    adapter: fixtures
    fixtures_path: {FIXTURES / 'model_outputs_pass.jsonl'}
  - name: fixtures-fail
    adapter: fixtures
    fixtures_path: {FIXTURES / 'model_outputs_fail.jsonl'}
"""
    path = tmp_path / "models.yaml"
    path.write_text(cfg, encoding="utf-8")
    return path


def test_full_pipeline_on_fixtures(tmp_path):
    raw = tmp_path / "raw"
    summaries = tmp_path / "summaries"

    assert run.main([
        "--tasks", str(REPO / "tasks" / "pilot"),
        "--models", str(_models_yaml(tmp_path)),
        "--out", str(raw),
        "--seed", "7",
    ]) == 0

    meta = json.loads((raw / "meta.json").read_text())
    assert meta["temperature"] == 0
    assert meta["seed"] == 7
    assert meta["git_commit"] != "unknown" and len(meta["git_commit"]) == 40
    assert (raw / "fixtures-pass.jsonl").exists()
    first = json.loads((raw / "fixtures-pass.jsonl").read_text().splitlines()[0])
    assert first["git_commit"] == meta["git_commit"]  # stamped into every record

    assert report.main([
        "--raw", str(raw),
        "--tasks", str(REPO / "tasks" / "pilot"),
        "--out", str(summaries),
        "--bootstrap", "200",
        "--seed", "7",
    ]) == 0

    summary = json.loads((summaries / "summary.json").read_text())
    ok = summary["models"]["fixtures-pass"]
    bad = summary["models"]["fixtures-fail"]

    # The perfect model passes everything, all deltas 0.
    for mech, row in ok["fingerprint"].items():
        assert row["strict"] == 1.0, (mech, row)
    for d in ok["deltas"].values():
        if d["n_sets"]:
            assert d["delta"] == 0.0

    # The failing model exhibits exactly the designed failure fingerprint.
    fp = bad["fingerprint"]
    assert fp["M2"]["by_variant"] == {"greg_ar": 1.0, "greg_en": 1.0, "hijri_ar": 0.0}
    assert fp["M4"]["by_variant"]["en_anchor"] == 1.0
    assert fp["M4"]["by_variant"]["cross_call_ar"] == 0.0   # inconsistent aliases
    assert fp["M4"]["by_variant"]["single_mention_ar"] == 0.0  # alias-invalid
    assert fp["M6"]["by_variant"] == {"ar_user_en_tools": 0.0, "en_user_en_tools": 1.0}
    assert fp["M6"]["args_arabic_leakage"] > 0  # Arabic city in English enum arg

    assert bad["deltas"]["Delta_M2_hijri"]["delta"] == 1.0
    assert bad["deltas"]["Delta_M4_crosscall"]["delta"] == 1.0
    assert bad["deltas"]["Delta_M6_discipline"]["delta"] == 1.0

    assert (summaries / "summary.md").read_text().startswith("# Atlas report")
    assert (summaries / "fixtures-fail.scored.jsonl").exists()
