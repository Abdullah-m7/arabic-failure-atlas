# Cross-Tool Interference v2 — Implementation Gate Remediation 001

Status: **historical pre-held-out implementation-only remediation**.

Classification: **test numeric-comparison precision only; no scientific logic change**.

## Trigger

The first clean implementation gate at parent HEAD `f6107b1ad59dfa61f7e295b468d6d0f7b1ec5909` collected 99 tests and produced one failure:

`harness/tests/test_cross_tool_interference_v2.py::test_v2_h6_passes_for_target_interference_and_stable_control`

The failing assertion compared the computed regression from 8 losses among 80 matched sets directly with the decimal literal `0.1` using exact Python float equality. The stored computation evaluated to `0.09999999999999998`, which is the ordinary IEEE-754 representation artifact from subtracting binary floating-point accuracies.

All other tests passed (98/99), the focused v2 suite was 2/3, both v2 Python files compiled successfully, no fresh held-out spec had been authored, and no model call had occurred.

## Admitted remediation

Only the test assertion was changed:

- add the existing test dependency `pytest` to the test module;
- replace exact float equality for the expected 0.1 diagnostic with `pytest.approx(0.1)`.

At this remediation stage, the production implementation was byte-unchanged. The following scientific quantities remained unchanged:

- `H6_TOOLSET_EXPANSION_INTERFERENCE`;
- 80-set design;
- four conditions;
- three-arm roster;
- primary endpoint;
- `MIN_TARGET_REGRESSION = 0.08`;
- Holm family and `p <= 0.05` criterion;
- negative-control `<= 0.03` guardrail;
- guarded-converter secondary interpretation;
- task authoring semantics;
- fresh-split requirement;
- no-v1-reuse rules.

## Why this did not alter the scientific test

The failing test fixture intentionally creates 8/80 = 10% loss and was checking the reported metric value, not defining the pass threshold. No held-out data existed for v2, so this remediation was fully pre-call and pre-outcome.

## Later remediation chain

A second exact-float test assertion was subsequently identified and documented in `IMPLEMENTATION_GATE_REMEDIATION_002.md`. A third clean gate then revealed a production **numeric representation** issue at the preregistered inclusive guarded-recovery boundary; that separate issue is documented and corrected in `IMPLEMENTATION_GATE_REMEDIATION_003.md` without changing the scientific formula or thresholds.

This file remains the historical record of remediation 001 and should not be read as claiming that the later remediation 003 left production representation byte-unchanged.
