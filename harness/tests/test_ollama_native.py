"""ollama_native adapter: think passthrough, native response parsing, canned
tool outputs (incl. task-declared overrides)."""

import json

from atlas.adapters.ollama_native import OllamaNativeAdapter

TASK = {
    "system_prompt": "You are a test assistant.",
    "tools": [{"name": "find_x", "description": "Find x.",
               "parameters": {"type": "object", "properties": {"q": {"type": "string"}},
                              "required": ["q"]}}],
    "messages": [{"role": "user", "content": "find foo"}],
    "tool_outputs": {"find_x": json.dumps({"status": "success", "record_id": "RID-77"})},
}


def adapter(think):
    a = OllamaNativeAdapter({"model": "m", "extra_body": {"think": think}})
    a.api_key = "test"
    return a


def test_think_in_body_and_native_parse():
    seen = []
    responses = [
        {"message": {"role": "assistant", "thinking": "...",
                     "tool_calls": [{"function": {"name": "find_x",
                                                  "arguments": {"q": "foo"}}}]}},
        {"message": {"role": "assistant", "content": "done"}},
    ]
    a = adapter(think=False)
    a._post = lambda payload: (seen.append(payload), responses[len(seen) - 1])[1]
    res = a.run_task(TASK)

    assert seen[0]["think"] is False
    assert seen[0]["options"]["temperature"] == 0
    assert seen[0]["stream"] is False
    assert res.pred_calls == [{"name": "find_x", "args": {"q": "foo"}}]
    assert res.final_text == "done"
    assert res.invocation_style == "native"
    # task-declared canned output was fed back as the tool result
    tool_msgs = [m for m in seen[1]["messages"] if m.get("role") == "tool"]
    assert tool_msgs and "RID-77" in tool_msgs[0]["content"]


def test_string_arguments_parsed():
    responses = [
        {"message": {"role": "assistant",
                     "tool_calls": [{"function": {"name": "find_x",
                                                  "arguments": '{"q": "bar"}'}}]}},
        {"message": {"role": "assistant", "content": "ok"}},
    ]
    a = adapter(think=True)
    n = iter(responses)
    a._post = lambda payload: next(n)
    res = a.run_task(TASK)
    assert res.pred_calls == [{"name": "find_x", "args": {"q": "bar"}}]
    assert res.output_error is None
