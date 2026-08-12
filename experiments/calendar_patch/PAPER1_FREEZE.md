# Paper-1 Freeze — The Calendar Gap

This file is the boundary between the completed diagnostic pilot and the Calendar Patch intervention study.

## Frozen authority

- Repository: `al3obdi/arabic-failure-atlas`
- Paper-1 main commit: `33d1d9ae8c426d5a23ac0c4e2b86123e9779d071`
- Git tree at that commit: `e27b0c9e87a943d0b691d3611ddda382d910d439`
- Paper title: **The Calendar Gap: Mechanism-Level Diagnosis of Arabic Agentic Failures**
- Paper-1 scorer state: `scorer-freeze-v2`
- Paper-1 task pool: 39 matched sets / 107 records
- Paper-1 measured mechanisms: M2, M3 control, M4, M6

## Frozen submission artifacts at the boundary

The commit above is the complete content-addressed freeze. For quick human inspection, the submission tree at the boundary contains:

- `paper/submission/main.tex` — Git blob `4eb6e4a52e5ccc67ef5c9ffd3c4a9fe7967c2686`
- `paper/submission/main.pdf` — Git blob `89404b2c800a32a540d11286dfc2bfbb2b376cd9`
- `paper/submission/atlas_arxiv.tar.gz` — Git blob `ed70651d00b95cc0eb506d50b40b3495754efaf0`
- `paper/numbers.json` — Git blob `c4e9624a0306501cef08b21e9a0cb27c8a29cb0f`
- `paper/gate_report.md` — Git blob `88c43fd471011613e6aa7385a786977220da2b57`

## Non-negotiable separation rule

Calendar Patch is **not** a scorer iteration, amendment, or re-analysis of Paper 1.

1. No Calendar Patch code may change the meaning of a Paper-1 result.
2. No Paper-1 task is eligible for the Calendar Patch primary analysis.
3. No held-out Calendar Patch item may be committed to this repository before the intervention study is frozen and released under its own contamination decision.
4. `scorer-freeze-v2` remains the final Paper-1 scorer. The intervention has a separate, narrow date-commit endpoint.
5. Any future Paper-1 correction must be labeled as a Paper-1 erratum and may not be justified by Calendar Patch outcomes.

This boundary exists so a positive intervention result cannot retroactively reshape the diagnostic evidence that motivated it.
