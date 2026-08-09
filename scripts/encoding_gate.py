#!/usr/bin/env python3
"""Encoding gate v2 for the submission PDF.

Checks, each FAILING loudly:
(a) symbol preservation — for every mapped symbol, its count in the source
    markdown equals the count of its rendered glyph form(s) in the extracted
    PDF text (math glyphs may extract as unicode variants, e.g. Delta as
    U+0394 or U+2206 — equivalence sets below);
(b) sign integrity — every bracketed CI beginning with a minus in the source
    still begins with a minus-like glyph in the PDF text;
(c) Arabic/mojibake — zero Arabic letters (Arabic-Indic digits U+0660-0669
    exempt: figure F5's vector axis label), "Bayan Alhindi" and "U+0660"
    intact, no presentation forms or replacement chars;
(d) bibliography sanity — a References/thebibliography section with >= 8
    entries, each longer than 40 characters.

Usage: python3 scripts/encoding_gate.py <main.pdf> [source_full.md]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# symbol -> set of acceptable extracted glyph forms
SYMBOL_GLYPHS = {
    "Δ": {"Δ", "∆"},
    "κ": {"κ", "ϰ"},
    "≈": {"≈"},
    "≥": {"≥", "≧"},
    "≤": {"≤", "≦"},
    "−": {"−", "-", "–"},   # minus may extract as hyphen/en-dash
    "§": {"§"},
    "↔": {"↔"},
    "×": {"×"},
}
NAMES = {"−": "MINUS U+2212"}


def pdf_text(path: Path) -> tuple[str, str, int]:
    """(full_text, prose_text, n_figure_pages). Figure pages — identified by
    their 'Figure N: FN:' caption line — are excluded from symbol/CI/bib
    checks: their vector labels legitimately carry Δ and Arabic-Indic digit
    glyphs that would double-count against the prose source."""
    from pypdf import PdfReader
    full, prose, nfig = [], [], 0
    for p in PdfReader(str(path)).pages:
        t = p.extract_text() or ""
        full.append(t)
        if re.search(r"Figure \d+: F\d:", t):
            nfig += 1
        else:
            prose.append(t)
    return "\n".join(full), "\n".join(prose), nfig


def main() -> int:
    pdf = Path(sys.argv[1])
    src_path = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "paper" / "submission_full.md"
    src = src_path.read_text(encoding="utf-8")
    all_text, t, nfig = pdf_text(pdf)
    problems, report = [], []
    report.append(f"  figure pages excluded from symbol/CI/bib checks: {nfig}")

    # (a) symbol preservation
    for sym, glyphs in SYMBOL_GLYPHS.items():
        want = src.count(sym)
        got = sum(t.count(g) for g in glyphs)
        label = NAMES.get(sym, sym)
        ambiguous = sym == "−"  # hyphen-equivalents occur naturally in prose
        ok = got >= want if ambiguous else got == want
        report.append(f"  (a) {label}: source={want} pdf={got} "
                      f"{'OK' if ok else 'MISMATCH'}")
        if not ok:
            problems.append(f"(a) symbol {label}: source count {want} != pdf {got}")

    # (b) sign integrity on bracketed CIs
    neg_cis = sorted(set(re.findall(r"\[−[\d.]+,\s*−?[\d.]+\]", src)))
    missing = []
    for ci in neg_cis:
        pat = re.escape(ci)
        pat = (pat.replace("−", "\\s*[−\\-–]\\s*").replace(",\\ ", ",\\s*")
               .replace("\\[", "\\[\\s*"))
        if not re.search(pat, t):
            missing.append(ci)
    report.append(f"  (b) minus-leading CIs in source: {len(neg_cis)} distinct; "
                  + ("all found with sign intact" if not missing
                     else "MISSING: " + str(missing)))
    if missing:
        problems.append(f"(b) sign-dropped CIs: {missing}")

    # (c) Arabic / mojibake
    letters = [hex(ord(c)) for c in all_text
               if ("؀" <= c <= "ۿ" or "ݐ" <= c <= "ݿ" or "ࢠ" <= c <= "ࣿ")
               and not 0x0660 <= ord(c) <= 0x0669]
    digits = [c for c in all_text if 0x0660 <= ord(c) <= 0x0669]
    moji = [hex(ord(c)) for c in all_text
            if "ﭐ" <= c <= "﷿" or "ﹰ" <= c <= "﻿" or c == "�"]
    broken = [n for n in ("Bayan Alhindi", "U+0660") if n not in all_text]
    for n in broken:
        problems.append(f"(c) expected string missing/broken: {n!r}")
    if letters:
        problems.append(f"(c) Arabic letters present: {letters[:5]}")
    if moji:
        problems.append(f"(c) mojibake markers: {moji[:5]}")
    report.append(f"  (c) Arabic letters: {len(letters)}; Arabic-Indic digits "
                  f"(figure labels, exempt): {len(digits)}; mojibake: {len(moji)}; "
                  f"target strings {'intact' if not broken else 'BROKEN ' + str(broken)}")

    # (d) bibliography sanity
    m = re.search(r"References\n(.*?)(?=\nF\d:|\Z)", t, re.DOTALL)
    entries = []
    if m:
        parts = re.split(r"\[(?:P\d|S\d|MAST|MLCL)\]", m.group(1))[1:]
        entries = [p.strip().replace("\n", " ") for p in parts if len(p.strip()) > 40]
    report.append(f"  (d) References entries longer than 40 chars: {len(entries)} (need >= 8)")
    if len(entries) < 8:
        problems.append(f"(d) bibliography sanity: only {len(entries)} full entries found")

    print("\n".join(report))
    if problems:
        print(f"ENCODING GATE v2: FAIL — {pdf}")
        print("\n".join("  !! " + p for p in problems))
        return 1
    print(f"ENCODING GATE v2: PASS — {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
