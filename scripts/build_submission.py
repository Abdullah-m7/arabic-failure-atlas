#!/usr/bin/env python3
"""Deterministic submission build: paper/submission_full.md -> main.tex.

- pandoc --top-level-division=section, LaTeX numbering suppressed (headings
  carry their own numbers).
- Every non-ASCII symbol is mapped to a LaTeX command (SYMBOL_MAP); verbatim
  reproductions become wrapped small-tt quote blocks so symbols render there
  too and long lines wrap instead of clipping.
- Abstract wrapped in the abstract environment; author block per research
  lead; References as an explicit thebibliography generated from refs.bib.
- Verifies every bracketed cite tag used in the text resolves to a
  bibliography label.
"""

from __future__ import annotations

import re
from pathlib import Path

import pypandoc

REPO = Path(__file__).resolve().parents[1]

# unicode -> (text-mode latex, rendered-glyph equivalents for the gate)
SYMBOL_MAP = {
    "Δ": r"$\Delta$",
    "κ": r"$\kappa$",
    "≈": r"$\approx$",
    "≥": r"$\geq$",
    "≤": r"$\leq$",
    "\u2212": r"$-$",          # minus sign
    "§": r"\S{}",
    "↔": r"$\leftrightarrow$",
    "×": r"$\times$",
    "±": r"$\pm$",
    "\u2192": r"$\rightarrow$",
    "\u2190": r"$\leftarrow$",
    "µ": r"$\mu$",
}

TEX_SPECIALS = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
                "$": r"\$", "&": r"\&", "#": r"\#", "%": r"\%",
                "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

TAGS = [("P1", "kubrak2026arabicprompts"), ("P2", "ersoy2025toolcalling"),
        ("P3", "nacar2026language"), ("P4", "bariah2026telcoagent"),
        ("S1", "kulkarni2025massive"), ("S2", "arabicsurvey2025"),
        ("MAST", "cemri2025mast"), ("MLCL", "luo2026lost")]


def esc_verbatim_line(line: str) -> str:
    out = "".join(TEX_SPECIALS.get(c, c) for c in line)
    for u, cmd in SYMBOL_MAP.items():
        out = out.replace(u, cmd)
    # lmtt has no dash ligatures/glyphs via inputenc — name them explicitly
    out = out.replace("\u2014", "\\textemdash{}")
    out = out.replace("\u2013", "\\textendash{}")
    return out


def convert_verbatims(tex: str) -> str:
    def repl(m):
        body = m.group(1).strip("\n")
        lines = [esc_verbatim_line(ln) if ln.strip() else r"\ " for ln in body.splitlines()]
        joined = "\\\\\n".join(lines)
        return ("\\begin{quote}\\footnotesize\\ttfamily\\raggedright\n"
                + joined + "\n\\end{quote}")
    return re.sub(r"\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}", repl,
                  tex, flags=re.DOTALL)


def bibliography() -> str:
    bib = (REPO / "paper" / "refs.bib").read_text(encoding="utf-8")
    entries = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.DOTALL):
        fields = dict(re.findall(r"(\w+)\s*=\s*\{(.*?)\}[,\n]", m.group(2), re.DOTALL))
        entries[m.group(1).strip()] = fields
    items = []
    for tag, key in TAGS:
        f = entries[key]
        bits = []
        if "author" in f:
            bits.append(f["author"].replace(" and ", ", ") + ".")
        bits.append("``" + re.sub(r"\s+", " ", f["title"].strip()) + ".''")
        if "booktitle" in f:
            bits.append(re.sub(r"\s+", " ", f["booktitle"]) + ".")
        if "pages" in f:
            bits.append("pp.\\ " + f["pages"] + ".")
        if "eprint" in f:
            bits.append("arXiv:" + f["eprint"] + ".")
        if "year" in f:
            bits.append(f["year"] + ".")
        text = " ".join(bits).replace("&", "\\&").replace("_", "\\_")
        assert len(text) > 40, f"suspiciously short citation for {key}: {text!r}"
        items.append(f"\\bibitem[{tag}]{{{key}}} {text}")
    return ("\\begin{thebibliography}{MLCL}\n"
            "\\setlength{\\itemsep}{2pt}\n"
            + "\n".join(items) + "\n\\end{thebibliography}\n")


def figures_block() -> str:
    caps = [
        ("F1_fingerprints", "F1: strict-score fingerprints per arm and mechanism."),
        ("F2_hijri_money", "F2: the calendar gap (greg\\_ar vs hijri\\_ar per arm)."),
        ("F3_hijri_forensics", "F3: forensic classes of failed hijri\\_ar records."),
        ("F4_h4_reasoning_toggle", "F4: reasoning toggle (H4) by mechanism."),
        ("F5_m3_numerals", "F5: Eastern-numerals control (M3)."),
    ]
    return "\n".join(
        f"\\begin{{figure}}[p]\\centering"
        f"\\includegraphics[width=\\textwidth]{{{n}}}"
        f"\\caption{{{c}}}\\end{{figure}}" for n, c in caps)


def main() -> None:
    src_md = (REPO / "paper" / "submission_full.md").read_text(encoding="utf-8")

    body = pypandoc.convert_file(
        str(REPO / "paper" / "submission_full.md"), "latex",
        format="markdown",
        extra_args=["--wrap=preserve", "--top-level-division=section",
                    "--shift-heading-level-by=-1"])

    # drop the duplicated md title + author line (maketitle covers them)
    body = re.sub(r"\\section\{The Calendar Gap[^}]*\}\\label\{[^}]*\}\n+", "", body)
    body = re.sub(r"\\textbf\{Abdullah Almohammedi\}[^\n]*\n+", "", body, count=1)

    # abstract -> proper environment
    m = re.search(r"\\section\{Abstract\}\\label\{abstract\}\n+(.*?)(?=\\section\{)",
                  body, re.DOTALL)
    assert m, "abstract section not found"
    body = body[:m.start()] + "\\begin{abstract}\n" + m.group(1).strip() \
        + "\n\\end{abstract}\n\n" + body[m.end():]

    body = convert_verbatims(body)
    for u, cmd in SYMBOL_MAP.items():
        body = body.replace(u, cmd)

    # every bracketed cite tag used in the text must resolve
    used = set(re.findall(r"\[(P\d|S\d|MLCL|MAST)[\];]", src_md))
    labels = {t for t, _ in TAGS}
    assert used <= labels, f"unresolved cite tags: {used - labels}"

    tex = (
        "\\documentclass[11pt]{article}\n"
        "\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n"
        "\\usepackage{cmap}\n"
        "\\usepackage{graphicx}\n\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{hyperref}\n\\usepackage{longtable,booktabs,array}\n"
        "\\usepackage{calc,etoolbox}\n"
        "\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}}\n"
        "\\setcounter{secnumdepth}{0}\n"  # headings carry their own numbers
        "\\graphicspath{{./figures/}}\n"
        "\\title{The Calendar Gap: Mechanism-Level Diagnosis of Arabic Agentic Failures}\n"
        "\\author{Abdullah Almohammedi \\\\ Independent Researcher, Rabigh, Saudi Arabia"
        " \\\\ ORCID 0009-0001-0832-0995 \\\\ abdullah.m.almohammedi@gmail.com}\n"
        "\\date{2026}\n\\begin{document}\n\\maketitle\n"
        + body + "\n" + bibliography() + "\n" + figures_block()
        + "\n\\end{document}\n")
    out = REPO / "paper" / "submission" / "main.tex"
    out.write_text(tex, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)} ({len(tex)} chars); "
          f"cite tags used: {sorted(used)}")


if __name__ == "__main__":
    main()
