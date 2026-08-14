from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = _load_script("preflight_cross_tool_interference_v2")
runner = _load_script("run_cross_tool_interference_v2")
scorer = _load_script("score_cross_tool_interference_v2")


def test_v2_frozen_runtime_roster_is_exact_three_arm_order():
    path = REPO / "experiments/cross_tool_interference_v2/models.yaml"
    models = preflight.load_frozen_models(path)
    assert [row["name"] for row in models] == [
        "gpt-oss-20b",
        "qwen3.5-397b",
        "deepseek-v4-flash-nothink",
    ]
    assert [row["name"] for row in runner.load_models(path)] == [row["name"] for row in models]


def test_v2_preflight_is_non_diagnostic_and_intervention_free():
    payload = json.dumps(preflight.SYNTHETIC_TASK, ensure_ascii=False)
    forbidden = [
        "convert_umm_al_qura",
        "normalize_reference_code",
        "Hijri",
        "Gregorian",
        "هجري",
        "ميلادي",
    ]
    assert all(token not in payload for token in forbidden)
    assert preflight.SYNTHETIC_TASK["task_id"] == "CTI-V2-PREFLIGHT"


def test_v2_arm_shuffle_seed_is_stable_and_arm_specific():
    a = runner.stable_arm_seed(20260814, "gpt-oss-20b")
    b = runner.stable_arm_seed(20260814, "qwen3.5-397b")
    assert a == runner.stable_arm_seed(20260814, "gpt-oss-20b")
    assert a != b


def test_v2_preflight_validation_binds_commit_roster_and_callability(tmp_path):
    models = runner.load_models(REPO / "experiments/cross_tool_interference_v2/models.yaml")
    commit = "a" * 40
    payload = {
        "experiment": runner.EXPERIMENT,
        "purpose": runner.PREFLIGHT_PURPOSE,
        "git_commit": commit,
        "frozen_roster": [runner.redact(row) for row in models],
        "models": {name: {"callable": True} for name in runner.FROZEN_NAMES},
    }
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    _, digest = runner.validate_preflight(path, commit, models)
    assert len(digest) == 64

    payload["models"]["qwen3.5-397b"]["callable"] = False
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match="unavailable"):
        runner.validate_preflight(path, commit, models)


def test_v2_scorer_interpretation_labels_are_frozen():
    summary = {
        "pre_registered_readout": {
            "target_arm_contrast_pass": {
                "gpt-oss-20b": {
                    "greg_matched_extra_tool": False,
                    "greg_converter_available": True,
                },
                "qwen3.5-397b": {
                    "greg_matched_extra_tool": True,
                    "greg_converter_available": False,
                },
            },
            "negative_control_pass": False,
        }
    }
    out = scorer.interpretation(summary)
    assert out["target_arm_labels"]["gpt-oss-20b"] == "CALENDAR_SEMANTIC_INTERFERENCE"
    assert (
        out["target_arm_labels"]["qwen3.5-397b"]
        == "GENERIC_TOOLSET_INTERFERENCE_WITH_NONREPLICATED_CONVERTER_EFFECT"
    )
    assert out["negative_control_label"] == "NON_SPECIFIC_TOOLSET_COST"


def test_v2_scorer_markdown_handles_incomplete_optional_pvalues():
    model_row = {
        "complete": False,
        "condition_metrics": {
            name: {"primary_accuracy": 0.0}
            for name in (
                "greg_baseline",
                "greg_matched_extra_tool",
                "greg_converter_available",
                "greg_converter_guarded",
            )
        },
        "contrasts": {
            "greg_matched_extra_tool": {"absolute_regression": 0.0, "p_holm": None},
            "greg_converter_available": {"absolute_regression": 0.0, "p_holm": None},
        },
        "guard_recovery_fraction": None,
    }
    summary = {
        "pre_registered_readout": {"verdict": "INCOMPLETE"},
        "models": {name: dict(model_row) for name in scorer.FROZEN_NAMES},
    }
    rendered = scorer.render_markdown(summary)
    assert "Verdict: INCOMPLETE" in rendered
    assert "—" in rendered
