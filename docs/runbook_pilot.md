# Pilot Runbook — trigger: "resume ollama smoke" (quota window reset)

Hard rules for the run session: temperature 0 everywhere (enforced by harness);
NEVER retry on 429 or on model-output errors (a failure is data; 429 = stop and
report); transport-only retries are already built into the runner.

## 0. Preflight (offline)

```bash
cd /home/user/arabic-failure-atlas/harness
python -m pytest                          # must be green (54)
python -m atlas.validate ../tasks/pilot   # must print OK: 80 records, 0 errors
```

## 1. Probes (5 tiny calls, per results/summaries/20260802-ollama-smoke/README.md)

```bash
cd /home/user/arabic-failure-atlas
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think true
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think false
PYTHONPATH=harness python3 scripts/probe_ollama.py deepseek-v4-flash --think true --native
PYTHONPATH=harness python3 scripts/probe_ollama.py gpt-oss:20b
PYTHONPATH=harness python3 scripts/probe_ollama.py qwen3.5:397b
```

Expected: http 200 + non-empty tool_calls on all; `thinking_present` TRUE for
think=true and FALSE for think=false (arms A vs B). If /v1 ignores or rejects
`think`: switch A/B to the native /api/chat path (thin adapter variant, update
D20) BEFORE the full pilot; smoke (step 2) may proceed meanwhile — model C
doesn't use the toggle.

## 2. Smoke — 3 seed sets on C ONLY

`atlas.run` executes every task in the dir it is given (80), so build a
seed-only dir first — the smoke is 8 tasks:

```bash
cd harness
TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p /tmp/smoke-tasks
cp ../tasks/pilot/m2_seed.jsonl ../tasks/pilot/m4_seed.jsonl ../tasks/pilot/m6_seed.jsonl /tmp/smoke-tasks/
python -m atlas.run --tasks /tmp/smoke-tasks --models ../models.yaml \
    --out ../results/raw/$TS-smoke --seed 1234 --only-model gpt-oss-20b
python -m atlas.report --raw ../results/raw/$TS-smoke --tasks /tmp/smoke-tasks \
    --out ../results/summaries/$TS-ollama-smoke
```

Eyeball the fingerprint (results/summaries/$TS-ollama-smoke/summary.md) before
continuing. Commit the smoke summaries.

## 3. Full pilot — sequenced by expected GPU-time, cheapest first

Order: **C → A → B → D**. D (qwen3.5:397b) is the heaviest and runs LAST so a
mid-run quota wall costs the least-critical arm, never the H4 pair (A/B).

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
for M in gpt-oss-20b deepseek-v4-flash-think deepseek-v4-flash-nothink qwen3.5-397b; do
  python -m atlas.run --tasks ../tasks/pilot --models ../models.yaml \
      --out ../results/raw/$TS --seed 1234 --only-model $M
  echo "== $M done; check run_summary/429s before continuing =="
done
```

After EACH model: pause; print progress + any 429 counts from the run output.
On any 429: STOP the sequence and report which arms completed — partial results
are valid data; never retry-loop against the quota.

## 4. Report + commit

```bash
python -m atlas.report --raw ../results/raw/$TS --tasks ../tasks/pilot \
    --out ../results/summaries/$TS
```

Commit `results/summaries/$TS/` + the raw run's `meta.json` + `run_summary.json`
(the rest of results/raw is gitignored by policy). Print the four failure
fingerprints (mechanism × metric per model) and every headline delta
(Delta_M2_hijri, Delta_M2_lang, Delta_M4_crosscall, Delta_M6_discipline) with
bootstrap CIs. Read against the pre-registered criteria in docs/phase0.md
(discrimination ≥15 pts; H2 ≥30%; H4 directional).
