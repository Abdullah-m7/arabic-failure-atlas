#!/usr/bin/env python3
"""Quota-gentle probe of Ollama Cloud models: auth, tool calling, think toggle.

One tiny tool-call request per invocation. Usage (from repo root):
  PYTHONPATH=harness python3 scripts/probe_ollama.py <model_id> [--think true|false]
      [--native] [--max-tokens N]

--native uses Ollama's native /api/chat (where `think` is a first-class field);
default is the OpenAI-compatible /v1/chat/completions with `think` in the body.
Prints a one-line JSON verdict; never prints the API key.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "harness"))
from atlas.run import load_dotenv  # noqa: E402

PROBE_TOOL = {
    "name": "get_current_time",
    "description": "Get the current local time for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string", "enum": ["Riyadh", "London"]}},
        "required": ["city"],
    },
}
PROBE_MSG = "What time is it in Riyadh right now? Use the tool."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--think", choices=["true", "false"])
    ap.add_argument("--native", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=400)
    args = ap.parse_args()

    load_dotenv(REPO / ".env")
    key = os.environ.get("OLLAMA_API_KEY", "")
    if not key:
        print(json.dumps({"error": "OLLAMA_API_KEY missing"}))
        return 2
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    think = None if args.think is None else (args.think == "true")

    verdict = {"model": args.model, "endpoint": "native" if args.native else "v1",
               "think_requested": think}
    try:
        if args.native:
            body = {
                "model": args.model,
                "messages": [{"role": "user", "content": PROBE_MSG}],
                "tools": [{"type": "function", "function": PROBE_TOOL}],
                "stream": False,
                "options": {"temperature": 0, "num_predict": args.max_tokens},
            }
            if think is not None:
                body["think"] = think
            r = requests.post("https://ollama.com/api/chat", headers=headers,
                              json=body, timeout=180)
            verdict["http"] = r.status_code
            data = r.json() if r.status_code == 200 else {"error": r.text[:300]}
            msg = data.get("message", {})
            calls = msg.get("tool_calls") or []
            verdict["tool_calls"] = [
                {"name": c.get("function", {}).get("name"),
                 "args": c.get("function", {}).get("arguments")} for c in calls
            ]
            verdict["thinking_present"] = bool(msg.get("thinking"))
            verdict["content_snippet"] = (msg.get("content") or "")[:120]
            if r.status_code != 200:
                verdict["error"] = data.get("error")
        else:
            body = {
                "model": args.model,
                "messages": [{"role": "user", "content": PROBE_MSG}],
                "tools": [{"type": "function", "function": PROBE_TOOL}],
                "temperature": 0,
                "max_tokens": args.max_tokens,
            }
            if think is not None:
                body["think"] = think
            r = requests.post("https://ollama.com/v1/chat/completions",
                              headers=headers, json=body, timeout=180)
            verdict["http"] = r.status_code
            if r.status_code == 200:
                data = r.json()
                msg = (data.get("choices") or [{}])[0].get("message", {})
                calls = msg.get("tool_calls") or []
                verdict["tool_calls"] = [
                    {"name": c.get("function", {}).get("name"),
                     "args": c.get("function", {}).get("arguments")} for c in calls
                ]
                verdict["thinking_present"] = bool(
                    msg.get("reasoning") or msg.get("reasoning_content") or msg.get("thinking")
                )
                verdict["content_snippet"] = (msg.get("content") or "")[:120]
            else:
                verdict["error"] = r.text[:300]
    except requests.RequestException as exc:
        verdict["transport_error"] = str(exc)

    print(json.dumps(verdict, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
