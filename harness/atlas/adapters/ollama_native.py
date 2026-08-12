"""Ollama native /api/chat adapter — exists ONLY for the think on/off toggle.

The probe run (2026-08-03) showed Ollama's OpenAI-compat /v1 layer ignores the
`think` parameter (thinking stayed on with think=false), while native /api/chat
honors it. H4 arms A/B therefore route through this adapter; models that don't
need the toggle stay on openai_compatible. See docs/decisions.md D20/D23.

Config: model, api_key_env, extra_body ({think: true|false} merged into the
request body root), optional base_url (default https://ollama.com/api/chat),
timeout_s, max_tokens (mapped to options.num_predict).
"""

from __future__ import annotations

import os

import requests

from .base import (
    Adapter,
    AdapterResult,
    MAX_TOOL_ROUNDS,
    TransportError,
    canned_tool_output,
)

DEFAULT_URL = "https://ollama.com/api/chat"


class OllamaNativeAdapter(Adapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.model = config["model"]
        key_env = config.get("api_key_env", "OLLAMA_API_KEY")
        self.api_key = os.environ.get(key_env, "")
        self.base_url = config.get("base_url", DEFAULT_URL)
        self.timeout = config.get("timeout_s", 300)
        self.extra_body = dict(config.get("extra_body") or {})
        self.num_predict = config.get("max_tokens")

    def _post(self, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            resp = requests.post(self.base_url, headers=headers, json=payload,
                                 timeout=self.timeout)
        except requests.RequestException as exc:
            raise TransportError(str(exc)) from exc
        if resp.status_code >= 500 or resp.status_code in (408, 429):
            raise TransportError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    def run_task(self, task: dict) -> AdapterResult:
        tools = [{"type": "function", "function": t} for t in task["tools"]]
        messages = [{"role": "system", "content": task["system_prompt"]}] + [
            dict(m) for m in task["messages"]
        ]
        transcript, pred_calls = [], []
        final_text, output_error = "", None

        for _ in range(MAX_TOOL_ROUNDS + 1):
            options = {"temperature": 0}
            if self.num_predict:
                options["num_predict"] = self.num_predict
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
                "options": options,
                **self.extra_body,
            }
            data = self._post(payload)
            transcript.append({"request": payload, "response": data})
            msg = data.get("message", {}) or {}
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                final_text = msg.get("content") or ""
                break
            messages.append(msg)
            for tc in tool_calls:
                fn = tc.get("function", {}) or {}
                args = fn.get("arguments") or {}
                if isinstance(args, str):  # some builds return JSON strings
                    import json as _json
                    try:
                        args = _json.loads(args)
                    except _json.JSONDecodeError as exc:
                        args = {}
                        output_error = f"unparseable arguments JSON: {exc}"
                pred_calls.append({"name": fn.get("name"), "args": args})
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": fn.get("name", ""),
                        "content": canned_tool_output(fn.get("name", ""), task, args),
                    }
                )
        else:
            output_error = output_error or f"no final answer after {MAX_TOOL_ROUNDS} tool rounds"

        return AdapterResult(
            pred_calls=pred_calls,
            final_text=final_text,
            invocation_style="native",
            raw_request={"model": self.model, "base_url": self.base_url,
                         "think": self.extra_body.get("think")},
            raw_response=transcript,
            output_error=output_error,
        )
