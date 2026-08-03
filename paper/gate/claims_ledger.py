#!/usr/bin/env python3
"""Claims ledger (SCI-7 input): every sentence containing a numeral or a
superlative becomes a ledger row (claim | expected source | status).

All rows start UNVERIFIED; the research lead flips rows to VERIFIED with the
source path filled in. The gate FAILS while any row is UNVERIFIED.

Usage: python3 paper/gate/claims_ledger.py [paper.md]  -> paper/claims_ledger.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SUPERLATIVES = r"\b(best|worst|largest|smallest|first|most|least|highest|lowest|strongest|weakest|universal|every|all five|none)\b"


def sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'\(\[])", text.replace("\n", " "))
    return [s.strip() for s in raw if len(s.strip()) > 2]


def build_ledger(paper: str) -> str:
    rows = []
    for s in sentences(paper):
        has_num = re.search(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w.\-])", s)
        has_sup = re.search(SUPERLATIVES, s, re.IGNORECASE)
        if has_num or has_sup:
            claim = s.replace("|", "\\|")[:160]
            expected = "numbers.json:<path>" if has_num else "raw/log or citation"
            rows.append(f"| {claim} | {expected} | UNVERIFIED |")
    lines = ["# Claims Ledger", "",
             "Every numeral/superlative sentence. The research lead verifies each",
             "row (fill the source, set VERIFIED). Gate check SCI-7 fails while",
             "any row is UNVERIFIED.", "",
             "| claim | expected source | status |", "|---|---|---|"] + rows
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        src = Path(argv[0])
    else:
        draft = REPO / "paper" / "draft_v1.md"
        src = draft if draft.exists() else REPO / "paper" / "skeleton.md"
    ledger = build_ledger(src.read_text(encoding="utf-8"))
    (REPO / "paper" / "claims_ledger.md").write_text(ledger, encoding="utf-8")
    n = ledger.count("| UNVERIFIED |")
    print(f"wrote paper/claims_ledger.md ({n} rows, all UNVERIFIED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
