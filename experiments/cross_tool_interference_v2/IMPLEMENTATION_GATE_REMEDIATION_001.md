# Cross-Tool Interference v2 — Implementation Gate Remediation 001

Status: **pre-held-out implementation-only remediation**.

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

The production implementation in `harness/atlas/cross_tool_interference_v2.py` is byte-unchanged by this remediation. The following remain unchanged:

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

## Why this does not alter the scientific test

The v2 outcome proportions lie on a discrete 1/80 grid. The frozen `0.08` interference threshold is not altered and is not at the representational value involved in the failing assertion. The failing test fixture intentionally creates 8/80 = 10% loss and was checking the reported metric value, not defining the pass threshold.

No held-out data exists for v2, so this remediation is fully pre-call and pre-outcome.

## Required next action

Run the complete clean implementation gate again at the new exact parent HEAD. Do not author the fresh held-out split until full pytest, focused v2 tests, and Python compilation all pass.
