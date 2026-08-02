# Ollama Cloud switch — probe + smoke report (2026-08-02)

## Status: CONFIGURED AND TESTED OFFLINE; LIVE SMOKE DEFERRED (weekly quota exhausted)

## Step results

| Step | Result |
|------|--------|
| Key | `OLLAMA_API_KEY` found in session env, written to gitignored `.env` (never echoed/committed) |
| Catalog | `GET https://ollama.com/v1/models` → HTTP 200, **18 cloud models** (auth works) |
| models.yaml | 4 entries filled from live catalog (below) |
| Adapter patch | `extra_body` pass-through added + 3 unit tests; pytest **54 passed**; validate OK (35 records, 0 errors) |
| Probes | **HTTP 429 — weekly usage limit reached** (account-wide; verified on qwen3.5:397b think=true/false and gpt-oss:20b, then stopped to save nothing further) |
| Smoke (C only) | **NOT RUN** — blocked by the same 429. No task content was exposed to any model. |

## Catalog snapshot (2026-08-02)

deepseek-v4-flash, deepseek-v4-flash:0731, deepseek-v4-pro, gemma4:31b, glm-5.1,
glm-5.2, gpt-oss:120b, gpt-oss:20b, kimi-k2.6, kimi-k2.7-code, kimi-k3,
minimax-m2.7, minimax-m3, mistral-large-3:675b, nemotron-3-nano:30b,
nemotron-3-super, nemotron-3-ultra, qwen3.5:397b

## Roster (models.yaml)

| Entry | Model | Role | Basis |
|-------|-------|------|-------|
| A `deepseek-v4-flash-think` | deepseek-v4-flash, `think: true` | H4 arm 1 | model page documents no-think/think/max-think; Medium usage; 13B-active MoE |
| B `deepseek-v4-flash-nothink` | deepseek-v4-flash, `think: false` | H4 arm 2 | same weights, toggled reasoning |
| C `gpt-oss-20b` | gpt-oss:20b | P1-comparable, level-1 | present in catalog |
| D `qwen3.5-397b` | qwen3.5:397b | different family, defaults | Medium usage; think-toggle undocumented → not used for A/B |

Why not qwen3 for A/B: no classic qwen3 hybrid-think model in the cloud catalog;
qwen3.5's toggle is undocumented; mission fallback rule ("any hybrid-thinking
model") points at the deepseek line → deepseek-v4-flash (v3.1's successor). D21.

## Adapter deviations

- `extra_body` per-model params merged into request bodies (D20). Primary path
  for the think toggle is OpenAI-compat `/v1/chat/completions` with `think` in
  the body; whether Ollama's compat layer accepts it is UNVERIFIED (429 hit
  before any param validation). Fallback (native `/api/chat`) is already
  implemented in `scripts/probe_ollama.py --native`; if the post-reset probe
  shows `/v1` rejecting or ignoring `think`, a thin native-chat adapter variant
  gets added and D20 updated.

## Resume checklist (after the weekly window resets)

```bash
cd /home/user/arabic-failure-atlas
# 1. probes (4 tiny calls + 1 native-endpoint check on the think arm):
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think true
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think false
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think true --native
PYTHONPATH=harness python3 scripts/probe_ollama.py gpt-oss:20b
PYTHONPATH=harness python3 scripts/probe_ollama.py qwen3.5:397b
# expect: http 200, tool_calls non-empty; thinking_present toggles between A/B
# 2. smoke = 3 live seed sets on C ONLY:
cd harness
TS=$(date -u +%Y%m%dT%H%M%SZ)
python -m atlas.run    --tasks ../tasks/pilot --models ../models.yaml \
                       --out ../results/raw/$TS --seed 1234 --only-model gpt-oss-20b
python -m atlas.report --raw ../results/raw/$TS --tasks ../tasks/pilot \
                       --out ../results/summaries/$TS-ollama-smoke
# 3. commit results/summaries/$TS-ollama-smoke; DO NOT run the full pilot yet.
```
