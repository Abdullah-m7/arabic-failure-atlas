# Paper-1 Reproducibility Remediation 002 — clean-clone evidence boundary

**Classification:** transparency/reproducibility correction only; **not** a scorer iteration, result correction, task amendment, or Calendar Patch outcome amendment.

## Trigger

The second clean local Calendar Patch pre-execution gate was run at parent HEAD:

`c7069826726f40002f5496f2993570315d80f5cb`

The first DC3-specific missing-raw defect had been remediated, and the gate improved from 94/96 to **95/96** tests. The sole remaining failure was:

`tests/test_numbers_consistency.py::test_numbers_json_regenerates_byte_identically`

The load-bearing exception was a `FileNotFoundError` when `paper/pull_numbers.py` tried to read:

`results/raw/20260803T081111Z/gpt-oss-20b.jsonl`

No focused Calendar Patch gate, model preflight, live canary, held-out task generation, or held-out execution occurred.

## Finding

The repository's `.gitignore` excludes `results/raw/`. The complete original model-output corpus used to construct all Paper-1 statistics was not committed to Git. Therefore a **fresh clone cannot truthfully perform full raw-to-paper regeneration** for all five arms and all four measured mechanisms.

This is broader than the DC3 issue fixed in remediation 001. The repository does preserve useful evidence:

- the content-addressed frozen `paper/numbers.json` artifact;
- four 80-row scored projections for the original open-arm frozen run under `results/summaries/20260803T081111Z/`;
- the exact 50-record blind DC3 audit sample with `pred_calls` and `final_text`, allowing independent clean-clone re-scoring of the audit;
- frozen tasks, scorer code, statistical code, run metadata, paper artifacts, and git chronology.

But those committed artifacts are **not equivalent to the missing complete raw transcripts**. In particular, the clean clone does not contain the full row-level original outputs for the M3 control run or the closed-weight arm, and the committed open-arm scored projections are not substitutes for original transcripts when attempting a full scorer-v2 re-score.

## Correction of the reproducibility claim

The repository must no longer make the binary claim that a clean clone can always regenerate `paper/numbers.json` from original raw outputs.

The truthful contract is now two-mode:

1. **Full-raw mode.** If all original raw files are available in the local workspace, `pull_numbers.build()` must still regenerate `paper/numbers.json` byte-identically. Any difference is a hard Paper-1 correction trigger; the numbers may not be rewritten merely to make the test pass.
2. **Clean-clone mode.** When the uncommitted raw corpus is absent, tests verify the exact frozen `paper/numbers.json` Git blob recorded in `PAPER1_FREEZE.md`, verify the committed scored-evidence row counts, and independently recompute the DC3 audit from its committed blind sample. This mode is **artifact integrity + partial evidence verification**, not full raw reproduction.

The machine-readable boundary is recorded in:

`paper/repro_status.json`

## Why this is scientifically preferable to a fake green build

Creating synthetic raw transcripts, reconstructing unknown model outputs from aggregate numbers, copying `numbers.json` into a second file and calling it evidence, or weakening comparisons silently would manufacture provenance that did not exist at Paper-1 freeze time.

This remediation does none of those things. It makes the missing-evidence boundary explicit and preserves the frozen scientific outputs unchanged.

## Frozen artifacts that must not change

- Paper-1 frozen commit: `33d1d9ae8c426d5a23ac0c4e2b86123e9779d071`;
- `paper/numbers.json` Git blob: `c4e9624a0306501cef08b21e9a0cb27c8a29cb0f`;
- scorer state: `scorer-freeze-v2`;
- all Paper-1 tasks, model identities, human annotations, thresholds, conclusions, and submitted-paper artifacts.

## Admission gate after this remediation

A new clean local gate must prove:

- the full repository suite passes in clean-clone mode;
- `paper/numbers.json` still hashes to the exact frozen Git blob above;
- all four committed 80-row open-arm scored evidence files remain complete;
- `dc3_compute.compute_v2()` reproduces the frozen Paper-1 audit block from the committed 50-row blind audit sample;
- all focused Calendar Patch/runner/preflight tests pass;
- the non-diagnostic final-roster preflight is produced at that same exact parent commit;
- no live canary or held-out task exists before those gates pass.

## Publication follow-up

The existing reproducibility appendix wording that says paper numbers "regenerate" from repository state and that scorer states are re-derivable offline from raw is stronger than what a clean clone actually supports. Before the next Paper-1 public revision, that wording should be corrected to distinguish:

- frozen artifact integrity and committed partial evidence;
- independently recomputable DC3 audit evidence; and
- complete raw-model-output reproduction, which is unavailable from the repository alone unless the original raw corpus is separately recovered and released.

This correction changes no empirical result. It narrows the reproducibility claim to what the preserved evidence actually supports.
