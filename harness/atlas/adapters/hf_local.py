"""Local HuggingFace transformers adapter (only if configured).

Uses the tokenizer's chat template with prompt-style tool calling (the
<tool_call> convention shared with openai_compatible's prompt fallback).
Requires `transformers` + `torch` installed; import happens lazily so the rest
of the harness works without them.
"""

from __future__ import annotations

import json

from .base import Adapter, AdapterResult, MAX_TOOL_ROUNDS, canned_tool_output
from .openai_compatible import PROMPT_STYLE_INSTRUCTIONS, _TOOL_CALL_RE


class HFLocalAdapter(Adapter):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415
        except ImportError as exc:  # pragma: no cover - env dependent
            raise RuntimeError(
                "hf_local adapter requires `pip install transformers torch`"
            ) from exc
        self.model_id = config["model"]
        self.max_new_tokens = config.get("max_new_tokens", 1024)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, device_map=config.get("device_map", "auto")
        )

    def _generate(self, messages: list[dict]) -> str:
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model.device)
        out = self.model.generate(
            inputs, max_new_tokens=self.max_new_tokens, do_sample=False
        )
        return self.tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)

    def run_task(self, task: dict) -> AdapterResult:
        system = task["system_prompt"] + PROMPT_STYLE_INSTRUCTIONS.format(
            tools=json.dumps(task["tools"], ensure_ascii=False)
        )
        messages = [{"role": "system", "content": system}] + [dict(m) for m in task["messages"]]
        transcript, pred_calls = [], []
        final_text, output_error = "", None

        for _ in range(MAX_TOOL_ROUNDS + 1):
            content = self._generate(messages)
            transcript.append({"generated": content})
            found = _TOOL_CALL_RE.findall(content)
            if not found:
                final_text = content
                break
            messages.append({"role": "assistant", "content": content})
            tool_msgs = []
            for blob in found:
                try:
                    call = json.loads(blob)
                except json.JSONDecodeError as exc:
                    output_error = f"unparseable <tool_call> JSON: {exc}"
                    continue
                name = call.get("name")
                pred_calls.append(
                    {"name": name, "args": call.get("arguments", call.get("args", {})) or {}}
                )
                tool_msgs.append(f"Tool {name} returned: {canned_tool_output(name, task)}")
            messages.append({"role": "user", "content": "\n".join(tool_msgs) or "Tool output unavailable."})
        else:
            output_error = output_error or f"no final answer after {MAX_TOOL_ROUNDS} tool rounds"

        return AdapterResult(
            pred_calls=pred_calls,
            final_text=final_text,
            invocation_style="prompt",
            raw_request={"model": self.model_id, "local": True},
            raw_response=transcript,
            output_error=output_error,
        )
