"""extra_body params must be merged verbatim into every outgoing request body."""

from atlas.adapters.openai_compatible import OpenAICompatibleAdapter

TASK = {
    "system_prompt": "You are a test assistant.",
    "tools": [{"name": "noop", "description": "No-op.", "parameters": {"type": "object", "properties": {}}}],
    "messages": [{"role": "user", "content": "hi"}],
}


def make_adapter(**cfg):
    base = {"base_url": "https://example.invalid/v1", "model": "m", "api_key": "x"}
    base.update(cfg)
    return OpenAICompatibleAdapter(base)


def capture_payloads(adapter):
    seen = []

    def fake_post(payload):
        seen.append(payload)
        return {"choices": [{"message": {"content": "done"}}]}

    adapter._post = fake_post
    return seen


def test_think_param_passed_through_native():
    adapter = make_adapter(extra_body={"think": False})
    seen = capture_payloads(adapter)
    adapter.run_task(TASK)
    assert seen and seen[0]["think"] is False
    assert seen[0]["temperature"] == 0


def test_think_param_passed_through_prompt_style():
    adapter = make_adapter(invocation_style="prompt", extra_body={"think": True})
    seen = capture_payloads(adapter)
    adapter.run_task(TASK)
    assert seen and seen[0]["think"] is True


def test_no_extra_body_leaves_payload_clean():
    adapter = make_adapter()
    seen = capture_payloads(adapter)
    adapter.run_task(TASK)
    assert "think" not in seen[0]
