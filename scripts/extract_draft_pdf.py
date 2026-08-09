#!/usr/bin/env python3
"""Deterministic text extraction of a received draft PDF into gate-ready
markdown. FORMAT RECONSTRUCTION ONLY — no content edits: pypdf text, lines
unwrapped into paragraphs, known top-level section titles restored to
`## `, inline `N.N Title.` subsection leads re-bolded (the gate's SCI-1
whitelist keys on both). The received PDF stays the authoritative artifact.

Usage: python3 scripts/extract_draft_pdf.py <in.pdf> <out.md>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pypdf import PdfReader

SECTIONS = {
    "Abstract", "1. Introduction", "2. Related Work", "3. Method",
    "4. Results", "5. Discussion", "6. Limitations", "7. Conclusion",
    "Acknowledgments", "Appendix pointers",
}
SUBSEC = re.compile(r"^(\d\.\d\s+[A-Z][^.]{2,70}[.:])(\s*)")


def extract(pdf: Path) -> str:
    reader = PdfReader(str(pdf))
    lines: list[str] = []
    for page in reader.pages:
        lines += (page.extract_text() or "").splitlines()

    title = lines[0].strip()
    i = 1
    # title may wrap onto a second line before the author line
    while i < len(lines) and "—" not in lines[i]:
        title += " " + lines[i].strip()
        i += 1

    out = [f"<!-- extracted from the received draft_v3.pdf by "
           f"scripts/extract_draft_pdf.py — format reconstruction only -->",
           f"# {title}", ""]
    para: list[str] = []

    def flush():
        if para:
            text = " ".join(para)
            m = SUBSEC.match(text)
            if m:
                text = f"**{m.group(1)}** {text[m.end():]}"
            out.append(text)
            out.append("")
            para.clear()

    for line in lines[i:]:
        s = line.strip()
        if not s:
            continue
        if s in SECTIONS:
            flush()
            out.append(f"## {s}")
            out.append("")
        elif SUBSEC.match(s) and para:
            flush()
            para.append(s)
        else:
            para.append(s)
    flush()
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.write_text(extract(src), encoding="utf-8")
    print(f"wrote {dst}")
