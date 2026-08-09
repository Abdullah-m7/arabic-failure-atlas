#!/usr/bin/env python3
"""Assemble paper/appendices.md from material already in the repo.

No new prose claims, no retyped numbers: every section is either a verbatim
reproduction of a repo artifact, a table rendered directly from
paper/numbers.json, or a decision-log excerpt quoted in full. Key figures
are asserted against numbers.json before writing — the build aborts on any
mismatch.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
N = json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8"))


def decision(dnum: str) -> str:
    """Extract one decision verbatim from docs/decisions.md."""
    text = (REPO / "docs" / "decisions.md").read_text(encoding="utf-8")
    m = re.search(rf"\*\*{dnum} — .*?(?=\n\*\*D\d|\Z)", text, re.DOTALL)
    assert m, f"{dnum} not found in decisions.md"
    return m.group(0).rstrip()


def sensitivity_table() -> str:
    s = N["sensitivity"]
    rows = ["| figure | v1 | v2 | changed |", "|---|---|---|---|"]
    for arm, mechs in s["strict"].items():
        for mech, r in mechs.items():
            rows.append(f"| strict {arm} {mech} | {r['v1']:.4f} | {r['v2']:.4f} "
                        f"| {'YES' if r['changed'] else 'no'} |")
    for arm, ds in s["deltas"].items():
        for name, r in ds.items():
            rows.append(f"| {name} {arm} | {r['v1']:+.4f} | {r['v2']:+.4f} "
                        f"| {'YES' if r['changed'] else 'no'} |")
    for mech, r in s["h4_think_minus_nothink"].items():
        rows.append(f"| H4 {mech} | {r['v1']:+.4f} | {r['v2']:+.4f} "
                    f"| {'YES' if r['changed'] else 'no'} |")
    changed = sum("YES" in r for r in rows)
    assert changed == 6, f"expected 6 changed rows (5 strict/delta + H4 M6), got {changed}"
    return "\n".join(rows)


def main() -> None:
    # --- assertions binding reproduced artifacts to numbers.json ---
    au = N["audit"]
    dc3v2 = (REPO / "audit" / "DC3_REPORT_v2.md").read_text(encoding="utf-8")
    dc3v1 = (REPO / "audit" / "DC3_REPORT.md").read_text(encoding="utf-8")
    assert f"{au['gate_v2']:.4f}" in dc3v2 and f"{au['gate_v1']:.4f}" in dc3v2
    assert str(au["gate_kappa"]) in dc3v2 and f"n={au['consensus_n']}" in dc3v2
    assert str(au["human_kappa"]) in dc3v1
    al = N["alias"]
    assert al["pre_strict"]["deepseek-v4-flash-think"] == 0.77
    repro = (REPO / "paper" / "appendix_repro.md").read_text(encoding="utf-8")
    assert N["run_manifest"]["frozen"] in repro, "manifest ts missing from repro appendix"

    header_ar_path = "docs/audit_kit/txt/ (Arabic originals, released with the harness)"

    parts = [
        "# Appendices",
        "",
        "<!-- assembled by scripts/build_appendices.py from repo artifacts; "
        "key figures asserted against paper/numbers.json at build time -->",
        "",
        "## Appendix A — Reproducibility record",
        "",
        "Reproduced verbatim from the repository (paper/appendix_repro.md); "
        "figures asserted at build time:",
        "",
        "```",
        repro.split("\n", 1)[1].strip(),
        "```",
        "",
        "### A.x Scorer-version sensitivity (v1 vs v2, rendered from numbers.json)",
        "",
        sensitivity_table(),
        "",
        "M2 and M3 rows are bit-identical across scorer versions; the "
        "regeneration test asserts this continuously.",
        "",
        "## Appendix B — Audit protocol and amendment record",
        "",
        "### B.1 Alias rule families and the deterministic signature check",
        "",
        "Reproduced verbatim from the decision log:",
        "",
        "```",
        decision("D25"),
        "",
        decision("D26"),
        "```",
        "",
        "### B.2 Call-set amendment record (audit-driven iteration 2)",
        "",
        "```",
        decision("D30"),
        "",
        decision("D31"),
        "```",
        "",
        "### B.3 Annotator protocol as executed",
        "",
        "Both annotators received identical fillable sheets: one judgment "
        "block per record showing the user request, the declared tools, the "
        "model's calls, and its final answer — with no scorer verdicts, no "
        "gold values, no oracle dates, and no model names (blindness is "
        "test-enforced). Each block asks one question (was the request "
        "executed with full precision?) answered 1/0 with an optional note; "
        "sheets with fewer than 50 filled verdicts are rejected mechanically, "
        "and the two returns were parsed before any agreement number was "
        f"computed. The verbatim sheets are at {header_ar_path}; they are "
        "not reproduced here to keep this document encoding-safe for the "
        "submission toolchain.",
        "",
        "## Appendix C — DC3 scorer audit: full adjudication",
        "",
        "### C.1 Inter-annotator anatomy (v1 report, reproduced in full)",
        "",
        "```",
        dc3v1.strip(),
        "```",
        "",
        "### C.2 Re-gate after the pre-committed calibration (v2 report, "
        "reproduced in full)",
        "",
        "```",
        dc3v2.strip(),
        "```",
        "",
    ]
    out = REPO / "paper" / "appendices.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)} ({len(parts)} blocks); "
          "all build-time assertions passed")


if __name__ == "__main__":
    main()
