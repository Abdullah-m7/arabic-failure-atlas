import json

import atlas.run as runner
from atlas.adapters.base import AdapterResult


class _FixtureAdapter:
    def __init__(self, config):
        self.config = config

    def run_task(self, task):
        return AdapterResult(pred_calls=[], final_text="ok", invocation_style="fixtures")


def test_run_model_preserves_legacy_variant_and_accepts_experiment_condition(tmp_path, monkeypatch):
    monkeypatch.setitem(runner.ADAPTERS, "condition-fixture", _FixtureAdapter)
    config = {"name": "fixture", "adapter": "condition-fixture"}
    tasks = [
        {
            "task_id": "PAPER1-001",
            "set_id": "PAPER1",
            "mechanism": "M2",
            "variant": "greg_ar",
        },
        {
            "task_id": "CP-001-hijri_baseline",
            "set_id": "CP-001",
            "mechanism": "CP-M2",
            "condition": "hijri_baseline",
        },
    ]
    runner.run_model(config, tasks, tmp_path, {"git_commit": "test", "seed": 1})
    records = [
        json.loads(line)
        for line in (tmp_path / "fixture.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert records[0]["variant"] == "greg_ar"
    assert records[1]["variant"] == "hijri_baseline"
