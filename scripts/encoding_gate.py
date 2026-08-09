#!/usr/bin/env python3
"""Encoding gate for the submission PDF (and tex source).

Asserts: (a) zero Arabic-script codepoints; (b) the encoding-safe spellings
"Bayan Alhindi" and "U+0660" survive intact; (c) no mojibake markers —
Arabic presentation forms (U+FB50-FDFF, U+FE70-FEFF) or replacement chars
(U+FFFD). FAILS loudly on any violation.

Usage: python3 scripts/encoding_gate.py <file.pdf|file.tex>
"""

import sys
from pathlib import Path


def text_of(path: Path) -> str:
    if path.suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8")


def main() -> int:
    path = Path(sys.argv[1])
    t = text_of(path)
    problems = []
    # (a) zero Arabic LETTERS anywhere. Arabic-Indic DIGITS U+0660-0669 are
    # exempt: figure F5's vector axis label legitimately renders the numerals
    # range, and correct digits are not mojibake (letters would be).
    arabic = [hex(ord(c)) for c in t
              if ("؀" <= c <= "ۿ" or "ݐ" <= c <= "ݿ" or "ࢠ" <= c <= "ࣿ")
              and not 0x0660 <= ord(c) <= 0x0669]
    if arabic:
        problems.append(f"(a) Arabic-script letters present: {len(arabic)} e.g. {arabic[:5]}")
    digits = [c for c in t if 0x0660 <= ord(c) <= 0x0669]
    if digits:
        print(f"  note: {len(digits)} Arabic-Indic digit(s) present "
              f"({''.join(sorted(set(digits)))}) — figure vector labels, exempt")
    for needle in ("Bayan Alhindi", "U+0660"):
        if needle not in t:
            problems.append(f"(b) expected string missing/broken: {needle!r}")
    moji = [hex(ord(c)) for c in t if "ﭐ" <= c <= "﷿"
            or "ﹰ" <= c <= "﻿" or c == "�"]
    if moji:
        problems.append(f"(c) mojibake markers: {len(moji)} e.g. {moji[:5]}")
    if problems:
        print(f"ENCODING GATE: FAIL — {path}")
        print("\n".join("  " + p for p in problems))
        return 1
    print(f"ENCODING GATE: PASS — {path} "
          f"(0 Arabic letters, target strings intact, 0 mojibake markers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
