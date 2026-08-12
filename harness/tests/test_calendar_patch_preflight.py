import importlib.util
from pathlib import Path

from atlas.adapters import TransportError


REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "calendar_patch_preflight", REPO / "scripts" / "preflight_calendar_patch.py"
)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def test_preflight_nonce_is_explicit_but_contains_no_calendar_probe():
    task = preflight.SYNTHETIC_TASK
    joined = " ".join(
        [task["system_prompt"]]
        + [message.get("content", "") for message in task.get("messages", [])]
    )
    assert preflight.NONCE in joined
    assert "hijri" not in joined.lower()
    assert "umm" not in joined.lower()
    assert all(tool["name"] != "convert_umm_al_qura" for tool in task["tools"])


def test_preflight_retries_transport_only_and_returns_retry_count(monkeypatch):
    class FakeAdapter:
        def __init__(self):
            self.calls = 0

        def run_task(self, task):
            self.calls += 1
            if self.calls < 3:
                raise TransportError("temporary")
            return {"ok": True}

    sleeps = []
    monkeypatch.setattr(preflight.time, "sleep", lambda seconds: sleeps.append(seconds))
    adapter = FakeAdapter()
    result, retries = preflight._run_with_transport_retries(
        adapter,
        {"transport_retries": 2, "transport_backoff_s": [0.1, 0.2]},
    )
    assert result == {"ok": True}
    assert retries == 2
    assert adapter.calls == 3
    assert sleeps == [0.1, 0.2]
