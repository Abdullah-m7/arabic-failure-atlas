import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]

RUN_SPEC = importlib.util.spec_from_file_location(
    "run_calendar_patch", REPO / "scripts" / "run_calendar_patch.py"
)
run_cp = importlib.util.module_from_spec(RUN_SPEC)
RUN_SPEC.loader.exec_module(run_cp)

SCORE_SPEC = importlib.util.spec_from_file_location(
    "score_calendar_patch", REPO / "scripts" / "score_calendar_patch.py"
)
score_cp = importlib.util.module_from_spec(SCORE_SPEC)
SCORE_SPEC.loader.exec_module(score_cp)


def _roster():
    return [
        {
            "name": "arm-a",
            "adapter": "openai_compatible",
            "base_url": "https://example.invalid/v1",
            "api_key_env": "TEST_KEY",
            "model": "fixture-model",
            "invocation_style": "native",
        }
    ]


def _payload(commit="abc123"):
    models = _roster()
    return {
        "experiment": "calendar-patch-v1",
        "purpose": "non-diagnostic endpoint/tool-call preflight",
        "git_commit": commit,
        "frozen_roster": [run_cp.redact(model) for model in models],
        "models": {
            "arm-a": {
                "callable": True,
                "tool_call_ok": False,
                "replacement_candidate": False,
            }
        },
    }


def test_runner_binds_valid_preflight_by_exact_bytes(tmp_path):
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(_payload(), sort_keys=True), encoding="utf-8")
    _, digest = run_cp._load_and_validate_preflight(
        path,
        current_commit="abc123",
        all_models=_roster(),
    )
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == expected


def test_runner_rejects_preflight_from_different_execution_commit(tmp_path):
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(_payload(commit="old")), encoding="utf-8")
    with pytest.raises(SystemExit, match="preflight git commit differs"):
        run_cp._load_and_validate_preflight(
            path,
            current_commit="new",
            all_models=_roster(),
        )


def test_scorer_rejects_byte_tampering_after_execution_freeze(tmp_path):
    path = tmp_path / "preflight.json"
    payload = _payload()
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    meta = {
        "git_commit": "abc123",
        "models": payload["frozen_roster"],
        "preflight_sha256": digest,
    }
    assert score_cp._validate_preflight_artifact(path, meta) == digest

    payload["models"]["arm-a"]["note"] = "post-freeze mutation"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    with pytest.raises(SystemExit, match="preflight SHA mismatch"):
        score_cp._validate_preflight_artifact(path, meta)
