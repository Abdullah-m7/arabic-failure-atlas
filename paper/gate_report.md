# Paper Quality Gate Report — `paper/skeleton.md`

**OVERALL: FAIL**

| check | result | count |
|---|---|---|
| SCI-1 | FAIL | 5 |
| SCI-2 | FAIL | 1 |
| SCI-3 | PASS | 0 |
| SCI-4 | PASS | 0 |
| SCI-5 | FAIL | 11 |
| SCI-6 | FAIL | 9 |
| SCI-7 | FAIL | 10 |
| STY-1 | FAIL | 19.8 |
| STY-2 | PASS | 0 |
| STY-3 | PASS | 1 |
| STY-4 | PASS | 0 |
| STY-5 | PASS | 0 |

## SCI-1
- L80: 95
- L91: 5
- L105: 5
- L111: 400
- L115: 0.33

## SCI-2
- delta sentence without bracketed CI: The embedded canary string enables   post-release leak detection in model output

## SCI-5
- refs.bib TODO-verify entries: 11

## SCI-6
- Closed-weight arm is a lite-tier model of a current generation (gemini
- H4 pair limited to one family (deepseek-v4-flash think/nothink) — [mit
- MSA only; dialects excluded by design — [mitigated-by: reserved for ca
- AST-style strict scoring bounds (ordered calls, exact enums) — [acknow
- human audit pending — DC3 gate (≥95% agreement, 50 items, 2 annotators
- chat-surface probe not yet run (API-only evidence) — [future-work]
- Hijri tasks span one year window (1448 AH) — [acknowledged; future-wor
- forensic classes assigned by deterministic heuristics on date args — [
- P1/P3 and taxonomy-line sources carded from Phase-0 scan, not re-read 

## SCI-7
- UNVERIFIED ledger rows: 10

## STY-1
- em-dash/1000w = 19.8 (max 5)
- semicolon/1000w = 28.7 (max 4)

## STY-3
- inversion-family matches: 1 (max 3)
