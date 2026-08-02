"""Anthropic Messages API adapter (native tool use)."""

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

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


class AnthropicAdapter(Adapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.model = config["model"]
        key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        self.api_key = os.environ.get(key_env, "")
        self.max_tokens = config.get("max_tokens", 2048)
        self.timeout = config.get("timeout_s", 120)
        self.base_url = config.get("base_url", API_URL)

    def _post(self, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": API_VERSION,
        }
        try:
            resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            raise TransportError(str(exc)) from exc
        if resp.status_code >= 500 or resp.status_code in (408, 429, 529):
            raise TransportError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    def run_task(self, task: dict) -> AdapterResult:
        tools = [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"],
            }
            for t in task["tools"]
        ]
        messages = [dict(m) for m in task["messages"]]
        transcript, pred_calls = [], []
        final_text, output_error = "", None

        for _ in range(MAX_TOOL_ROUNDS + 1):
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": task["system_prompt"],
                "messages": messages,
                "tools": tools,
                "temperature": 0,
            }
            data = self._post(payload)
            transcript.append({"request": payload, "response": data})
            content = data.get("content", [])
            tool_uses = [b for b in content if b.get("type") == "tool_use"]
            texts = [b.get("text", "") for b in content if b.get("type") == "text"]
            if not tool_uses:
                final_text = "\n".join(t for t in texts if t)
                break
            messages.append({"role": "assistant", "content": content})
            results = []
            for block in tool_uses:
                pred_calls.append({"name": block.get("name"), "args": block.get("input", {}) or {}})
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.get("id", ""),
                        "content": canned_tool_output(block.get("name", "")),
                    }
                )
            messages.append({"role": "user", "content": results})
        else:
            output_error = f"no final answer after {MAX_TOOL_ROUNDS} tool rounds"

        return AdapterResult(
            pred_calls=pred_calls,
            final_text=final_text,
            invocation_style="native",
            raw_request={"model": self.model},
            raw_response=transcript,
            output_error=output_error,
        )
