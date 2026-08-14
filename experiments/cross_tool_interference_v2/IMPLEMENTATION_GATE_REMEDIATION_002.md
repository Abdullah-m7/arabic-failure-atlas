# Cross-Tool Interference v2 — Implementation Gate Remediation 002

Status: **historical pre-held-out implementation-only remediation**.

Classification: **test numeric-comparison precision completion; no scientific logic change at this remediation stage**.

## Trigger

The remediated clean implementation gate at parent HEAD `e83fa866fbe48726567c836896489b4c0c0f4482` again collected 99 tests and produced one failure in:

`harness/tests/test_cross_tool_interference_v2.py::test_v2_h6_passes_for_target_interference_and_stable_control`

Remediation 001 had corrected the first exact floating-point equality assertion for `absolute_regression`, but the same synthetic test function still contained a second exact float equality:

`guard_recovery_fraction == 0.5`

The computed value was `0.49999999999999944`, an ordinary IEEE-754 representation artifact from the then-current recovery-fraction calculation. Full pytest was 98/99, focused v2 was 2/3, Python compilation passed, no v2 held-out spec existed, and no model call had occurred.

## Admitted remediation

Only the remaining synthetic floating-point assertion was changed:

- `guard_recovery_fraction == 0.5`
- became `guard_recovery_fraction == pytest.approx(0.5)`.

The entire v2 test module was then reviewed for exact-equality assertions against computed floating-point metrics. The only such metric assertions in that test module were represented with `pytest.approx` (`absolute_regression` and `guard_recovery_fraction`). Integer-count, Boolean, string-label, and threshold inequality assertions remained exact by design.

## Scientific invariants unchanged

At remediation 002, no production or scientific code was changed. In particular, all of the following remained unchanged:

- `H6_TOOLSET_EXPANSION_INTERFERENCE`;
- 80 fresh sets;
- four conditions;
- three-arm roster;
- primary endpoint;
- `MIN_TARGET_REGRESSION = 0.08`;
- Holm family of four target-arm tests;
- `MAX_HOLM_P = 0.05`;
- `MAX_NEGATIVE_CONTROL_REGRESSION = 0.03`;
- `GUARD_RECOVERY_LABEL_THRESHOLD = 0.50`;
- guarded-converter secondary role;
- matched-extra-tool definition;
- authoring/novelty constraints;
- fresh held-out requirement.

## Later boundary finding

The next clean gate at `e20ad69d...` correctly passed the test-module exact-float audit but exposed a different problem: the production calculation represented an exact matched-count recovery of `4/8 = 0.50` as `0.49999999999999944`, causing the already-inclusive `>= 0.50` label rule to miss its mathematical boundary. That distinct production representation issue is documented and corrected in `IMPLEMENTATION_GATE_REMEDIATION_003.md`.

No threshold or scientific formula was changed by remediation 003; matched equal-denominator quantities are now derived from integer success counts before division.
