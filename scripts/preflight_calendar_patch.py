#!/usr/bin/env python3
"""Non-diagnostic endpoint/tool-call preflight for Calendar Patch v1.

This script MUST run before any held-out model output is produced. It intentionally
contains no Hijri date, no held-out content, and no calendar-conversion task, so it
cannot leak treatment performance before the study. A model is considered callable
if its endpoint returns a model response; failure to follow this trivial synthetic
tool instruction is recorded but is NOT grounds for replacing the arm.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "harness"))

from atlas.adapters import ADAPTERS, TransportError  # noqa: E402
from atlas.run import git_commit_hash, load_dotenv, redact  # noqa: E402

ALLOWED_ADAPTERS = {"openai_compatible", "ollama_native"}
NONCE = "CALPATCH-PREFLIGHT-DO-NOT-SCORE"
SYNTHETIC_TASK = {
    "task_id": "CALPATCH-PREFLIGHT",
    "set_id": "CALPATCH-PREFLIGHT",
    "mechanism": "PREFLIGHT",
    "condition": "endpoint_tool_ping",
    "system_prompt": (
        "This is a connectivity preflight, not an evaluation task. "
        "Call the provided ping tool once with the exact nonce, then finish."
    ),
    "messages": [{"role": "user", "content": "Run the connectivity ping now."}],
    "tools": [
        {
            "name": "calendar_patch_preflight_ping",
            "description": "Connectivity-only preflight tool.",
            "parameters": {
                "type": "object",
                "properties": {"nonce": {"type": "string"}},
                "required": ["nonce"],
                "additionalProperties": False,
            },
        }
    ],
    "tool_outputs": {
        "calendar_patch_preflight_ping": '{"status":"success","message":"preflight acknowledged"}'
    },
}


def _inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO.resolve())
        return True
    except ValueError:
        return False


def _safe_error(exc: Exception) -> str:
    # Never serialize request headers/config/key material. Exception text from the
    # adapters contains transport/HTTP status and a bounded response body only.
    return f"{type(exc).__name__}: {str(exc)[:500]}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=REPO / "models.yaml")
    parser.add_argument("--out", required=True, type=Path,
                        help="summary JSON path outside this repository")
    parser.add_argument("--allow-inrepo-fixture", action="store_true")
    args = parser.parse_args(argv)

    if not args.allow_inrepo_fixture and _inside_repo(args.out):
        raise SystemExit("live Calendar Patch preflight output must remain outside the repo")
    if not args.allow_inrepo_fixture:
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO, text=True
        ).strip()
        if dirty:
            raise SystemExit("refusing live preflight from a dirty git worktree")

    load_dotenv(REPO / ".env")
    cfg = yaml.safe_load(args.models.read_text(encoding="utf-8"))
    models = cfg.get("models", [])
    if not models:
        raise SystemExit("no models configured")
    if len({model["name"] for model in models}) != len(models):
        raise SystemExit("duplicate model names in pre-registered roster")
    unsupported = [
        model["name"] for model in models if model.get("adapter") not in ALLOWED_ADAPTERS
    ]
    if unsupported:
        raise SystemExit(f"unsupported Calendar Patch adapters: {unsupported}")

    result = {
        "experiment": "calendar-patch-v1",
        "purpose": "non-diagnostic endpoint/tool-call preflight",
        "git_commit": git_commit_hash(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "synthetic_task_id": SYNTHETIC_TASK["task_id"],
        "models": {},
        "frozen_roster": [redact(model) for model in models],
    }

    for model in models:
        name = model["name"]
        adapter = ADAPTERS[model["adapter"]](model)
        try:
            response = adapter.run_task(SYNTHETIC_TASK)
            tool_ok = any(
                call.get("name") == "calendar_patch_preflight_ping"
                and (call.get("args") or {}).get("nonce") == NONCE
                for call in response.pred_calls
            )
            result["models"][name] = {
                "callable": True,
                "tool_call_ok": tool_ok,
                "output_error": response.output_error,
                "invocation_style": response.invocation_style,
                "n_pred_calls": len(response.pred_calls),
                "replacement_eligible_on_this_evidence": False,
                "note": (
                    "Endpoint returned a model response. Tool-following quality is not "
                    "an arm-replacement criterion."
                ),
            }
        except TransportError as exc:
            result["models"][name] = {
                "callable": False,
                "tool_call_ok": False,
                "error_class": "transport",
                "error": _safe_error(exc),
                "replacement_eligible_on_this_evidence": True,
            }
        except Exception as exc:  # configuration / endpoint hard failure
            result["models"][name] = {
                "callable": False,
                "tool_call_ok": False,
                "error_class": "configuration_or_endpoint",
                "error": _safe_error(exc),
                "replacement_eligible_on_this_evidence": True,
            }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    unavailable = [name for name, row in result["models"].items() if not row["callable"]]
    print(json.dumps({"callable": len(models) - len(unavailable), "unavailable": unavailable}))
    return 0 if not unavailable else 2


if __name__ == "__main__":
    raise SystemExit(main())
