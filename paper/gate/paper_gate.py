#!/usr/bin/env python3
"""Publication quality gate — deterministic, stdlib-only, held to scorer standard.

Checks SCI-1..7 and STY-1..5 (see gate_report.md it emits). PASS only when every
check passes. The core is a pure function `run_gate(...)` so the pytest smoke
fixtures can exercise it with synthetic inputs; the CLI wires the repo files.

Usage: python3 paper/gate/paper_gate.py [paper.md]
  default input preference (v1.1): draft_v4.md > draft_v3.md > draft_v2.md > draft_v1.md > skeleton.md
  output: paper/gate_report.md (+ exit 0/1)
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

CAUSAL_VERBS = ["proves", "demonstrates conclusively", "causes"]
OVERCLAIMS = ["all closed", "state-of-the-art", "first ever", "guarantees",
              # external-review prep pass additions:
              "flawless", "perfect", "solves", "eliminates", "definitively",
              "unprecedented"]
BANNED = ["delve", "showcase", "leverage", "tapestry", "pivotal", "crucially",
          "notably", "importantly", "arguably", "holistic", "intricate",
          "underscores", "testament to", "moreover", "furthermore",
          "it is worth noting", "in conclusion", "in summary"]
INVERSIONS = [r"\bnot\s+\w+\s+but\s+\w+", r"\bis not the\s+\w+;", r",\s*not\s+\w+"]

# Numeric tokens that are never claims: years, arXiv ids, ISO dates, Hijri years,
# section/figure/mechanism ids, model-name fragments, list markers.
WHITELIST_PATTERNS = [
    r"\b(?:19|20)\d{2}\b",                 # years
    r"\b\d{4}\.\d{4,5}\b",                 # arXiv ids
    r"\b\d{4}-\d{2}-\d{2}\b",              # ISO dates
    r"\b14\d{2}\b",                        # Hijri years
    r"\b(?:F|M|H|E|D|DC|R)\d+\b",          # figure/mechanism/hypothesis ids
    r"TABLE-R\d+", r"AUD-\d{3}",
    r"§\s?\d+(?:\.\d+)*", r"\bv\d+\b",
    r"[A-Za-z][\w.\-]*\d[\w.\-]*",         # model-name-like tokens (gemini-3.5, 20b)
    r"\b\d+(?:\.\d+)?%?\s*(?:dp|pt|pts)\b",
    # gate v1.1 (D32):
    r"\*\*\d+(?:\.\d+)?",                  # bold section headers (**3.5 ...**)
    r"\(\d\)",                             # parenthesized enumerations (1)..(9)
    r"\b\d{1,3},\d{3}\b",                  # thousands-separated (1,600) kept whole
    r"\bn\s*=\s*\d+",                      # statistical n = k phrasing
]

# Literature-owned sentences: numerals in a sentence carrying one of these
# bracketed cite tokens are refs-bound (claims ledger), not numbers.json-bound.
CITE_RE = re.compile(
    r"\[(?:P\d|S\d|MAST|AgentErrorBench|ToolScan|AgentHallu|Aegis|AgentAtlas)"
    r"\b[^\]]*\]")


def _sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'\(\[])", text.replace("\n", " "))
    return [s.strip() for s in raw if len(s.strip()) > 2]


def _sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## +(.+)$", text, flags=re.MULTILINE)
    out = {"_preamble": parts[0]}
    for i in range(1, len(parts) - 1, 2):
        out[parts[i].strip()] = parts[i + 1]
    return out


def _collect_numbers(node, acc):
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        acc.add(round(float(node), 6))
    elif isinstance(node, dict):
        for v in node.values():
            _collect_numbers(v, acc)
    elif isinstance(node, list):
        for v in node:
            _collect_numbers(v, acc)


def _numeric_ok(tok: str, allowed: set[float]) -> bool:
    v = float(tok)
    for signed in allowed:
        # prose tokens are unsigned (the minus sign sits outside the token),
        # so match against the magnitude of stored values (D32 addendum)
        a = abs(signed)
        if abs(a - v) < 5e-7 or abs(round(a, 2) - v) < 5e-3:
            return True
        if 0 <= a <= 1 and abs(round(a * 100, 1) - v) < 5e-2:  # percent form
            return True
    return False


def run_gate(paper: str, numbers: dict, inventory: str, refs: str,
             ledger: str | None = None) -> dict:
    checks: dict[str, dict] = {}
    lines = paper.splitlines()
    sents = _sentences(paper)
    sections = _sections(paper)
    words = re.findall(r"\b\w+\b", paper)
    n_words = max(1, len(words))

    # SCI-1 number provenance
    allowed: set[float] = set()
    _collect_numbers(numbers, allowed)
    orphans = []
    for ln, line in enumerate(paper.splitlines(), 1):
        if line.lstrip().startswith(("```", "<!--")):
            continue
        # v1.1 (D32): drop cite-bearing sentences BEFORE whitelist scrubbing
        # (the model-name pattern would eat P1/S1 cite tokens) — their
        # numerals are literature-owned and live in the claims ledger.
        kept = " ".join(s for s in re.split(r"(?<=[.!?])\s+", line)
                        if not CITE_RE.search(s))
        for pat in WHITELIST_PATTERNS:
            kept = re.sub(pat, " ", kept)
        for tok in re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w.\-])", kept):
            if not _numeric_ok(tok, allowed):
                orphans.append(f"L{ln}: {tok}")
    checks["SCI-1"] = {"passed": not orphans, "count": len(orphans),
                       "details": orphans[:25]}

    # SCI-2 stats discipline (D33: fire only on sentences REPORTING a numeric
    # delta value — a delta symbol/name adjacent to a number; methodology
    # prose that merely discusses deltas is exempt)
    delta_near_num = re.compile(
        r"(?:Δ\S*|\bdeltas?\b)[^.;]{0,40}?\d|\d[^.;]{0,40}?(?:Δ\S*|\bdeltas?\b)",
        re.IGNORECASE)
    viol = []
    for s in sents:
        if delta_near_num.search(s) and not ("[" in s and "]" in s):
            viol.append(f"delta sentence without bracketed CI: {s[:80]}")
    for m in re.finditer(r"\bsignificant", paper, re.IGNORECASE):
        window = paper[m.start(): m.end() + 40]
        if "holm" not in window.lower():
            viol.append(f"'significant' without nearby 'Holm': ...{window[:60]}")
    for verb in CAUSAL_VERBS:
        for m in re.finditer(re.escape(verb), paper, re.IGNORECASE):
            viol.append(f"causal verb '{verb}'")
    checks["SCI-2"] = {"passed": not viol, "count": len(viol), "details": viol[:15]}

    # SCI-3 overclaims (+ "frontier" as a label, raw run ids exempt)
    hits = []
    for phrase in OVERCLAIMS:
        hits += [f"'{phrase}'" for _ in re.finditer(re.escape(phrase), paper, re.IGNORECASE)]
    for m in re.finditer(r"\bfrontier\b(?!-gemini)", paper, re.IGNORECASE):
        ctx = paper[max(0, m.start() - 20): m.end() + 20].replace("\n", " ")
        if "'frontier'" not in ctx and '"frontier"' not in ctx:  # mentions-as-word ok
            hits.append(f"'frontier' label: ...{ctx}...")
    checks["SCI-3"] = {"passed": not hits, "count": len(hits), "details": hits[:15]}

    # SCI-4 terminology consistency
    term = []
    for m in re.finditer(r"gemini[\w.\-]*", paper, re.IGNORECASE):
        tok = m.group(0).rstrip(".,;:")
        if tok.lower() not in ("gemini-3.5-flash-lite", "gemini"):
            term.append(f"nonstandard closed-arm token '{tok}'")
    for m in re.finditer(r"\b(?:the )?(?:hijri|calendar|date|name|digit) mechanism\b",
                         paper, re.IGNORECASE):
        term.append(f"loose mechanism name '{m.group(0)}' (use M-id or fixed name)")
    checks["SCI-4"] = {"passed": not term, "count": len(term), "details": term[:15]}

    # SCI-5 submission blockers
    todo = len(re.findall(r"TODO-verify", refs))
    pending = len(re.findall(r"\[pending: DC3\]", paper))
    det = ([f"refs.bib TODO-verify entries: {todo}"] if todo else []) + \
          ([f"[pending: DC3] placeholders: {pending}"] if pending else [])
    checks["SCI-5"] = {"passed": todo == 0 and pending == 0,
                       "count": todo + pending, "details": det}

    # SCI-6 limitation coverage
    lim_section = ""
    for title, body in sections.items():
        if "limitation" in title.lower():
            lim_section = body.lower()
    misses = []
    for bullet in re.findall(r"^- (.+)$", inventory, flags=re.MULTILINE):
        keys = [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{5,}", bullet)][:6]
        if keys and not any(k.lower() in lim_section for k in keys):
            misses.append(bullet[:70])
    checks["SCI-6"] = {"passed": not misses, "count": len(misses),
                       "details": misses[:15]}

    # SCI-7 claims ledger
    if ledger is None:
        ledger_path = REPO / "paper" / "claims_ledger.md"
        ledger = ledger_path.read_text(encoding="utf-8") if ledger_path.exists() else None
    # v1.1 (D32): UNVERIFIED, MANUAL, and PENDING-REFS all block — only
    # VERIFIED / VERIFIED-BY-REFERENCE rows clear the check.
    if ledger is not None:
        by_status = {st: len(re.findall(rf"\| *{st} *\|?$", ledger,
                                        flags=re.MULTILINE))
                     for st in ("UNVERIFIED", "MANUAL", "PENDING-REFS")}
        unverified = sum(by_status.values())
    else:
        unverified, by_status = -1, {}
    checks["SCI-7"] = {
        "passed": unverified == 0, "count": max(unverified, 0),
        "details": (["claims_ledger.md missing — run claims_ledger.py"]
                    if unverified < 0 else
                    [f"{st} ledger rows: {n}" for st, n in by_status.items()
                     if n] if unverified else []),
    }

    # STY-1 punctuation density
    em = paper.count("—") * 1000 / n_words
    semi = paper.count(";") * 1000 / n_words
    checks["STY-1"] = {"passed": em <= 5 and semi <= 4,
                       "count": round(em, 1),
                       "details": [f"em-dash/1000w = {em:.1f} (max 5)",
                                   f"semicolon/1000w = {semi:.1f} (max 4)"]}

    # STY-2 banned phrases + rhetorical question marks
    b = []
    for phrase in BANNED:
        b += [f"'{phrase}'" for _ in re.finditer(r"\b" + re.escape(phrase), paper, re.IGNORECASE)]
    nq = sum(1 for s in sents if s.rstrip().endswith("?"))
    if nq:
        b.append(f"rhetorical question marks: {nq}")
    checks["STY-2"] = {"passed": not b, "count": len(b), "details": b[:15]}

    # STY-3 inversion budget (v1.1: exact matched spans printed)
    inv_spans = []
    for p in INVERSIONS:
        for m in re.finditer(p, paper, re.IGNORECASE):
            ctx = paper[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
            inv_spans.append(f"span '{m.group(0)}' in: ...{ctx}...")
    inv = len(inv_spans)
    checks["STY-3"] = {"passed": inv <= 3, "count": inv,
                       "details": [f"inversion-family matches: {inv} (max 3)"]
                       + inv_spans[:12]}

    # STY-4 burstiness + repeated non-technical 4-grams
    sty4 = []
    for title, body in sections.items():
        ss = _sentences(body)
        lens = [len(s.split()) for s in ss]
        if len(lens) >= 6:  # v1.1 (D32): skip short sections (< 6 sentences)
            ratio = statistics.pstdev(lens) / max(1e-9, statistics.mean(lens))
            if ratio < 0.45:
                sty4.append(f"section '{title[:30]}' burstiness {ratio:.2f} < 0.45")
    toks = [w.lower() for w in re.findall(r"[A-Za-z]+", paper)]
    grams: dict[tuple, int] = {}
    for i in range(len(toks) - 3):
        g = tuple(toks[i:i + 4])
        grams[g] = grams.get(g, 0) + 1
    for g, c in grams.items():
        if c > 2 and not any(len(w) <= 2 for w in g):
            sty4.append(f"4-gram x{c}: '{' '.join(g)}'")
    checks["STY-4"] = {"passed": not sty4, "count": len(sty4), "details": sty4[:15]}

    # STY-5 opener variety
    sty5 = []
    for title, body in sections.items():
        ss = _sentences(body)
        if len(ss) < 5:
            continue
        first = {}
        for s in ss:
            t = re.match(r"[A-Za-z]+", s)
            if t:
                first[t.group(0)] = first.get(t.group(0), 0) + 1
        for tok, c in first.items():
            if c / len(ss) > 0.40:
                sty5.append(f"section '{title[:30]}': opener '{tok}' {c}/{len(ss)}")
    checks["STY-5"] = {"passed": not sty5, "count": len(sty5), "details": sty5[:15]}

    overall = all(c["passed"] for c in checks.values())
    return {"overall_pass": overall, "checks": checks}


def to_markdown(result: dict, source: str) -> str:
    lines = [f"# Paper Quality Gate Report — `{source}`", "",
             f"**OVERALL: {'PASS' if result['overall_pass'] else 'FAIL'}**", "",
             "| check | result | count |", "|---|---|---|"]
    for cid, c in result["checks"].items():
        lines.append(f"| {cid} | {'PASS' if c['passed'] else 'FAIL'} | {c['count']} |")
    lines.append("")
    for cid, c in result["checks"].items():
        if c["details"]:
            lines.append(f"## {cid}")
            lines += [f"- {d}" for d in c["details"]]
            lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        src = Path(argv[0]).resolve()
    else:  # v1.1 (D32) input preference
        src = next((p for p in (REPO / "paper" / "draft_v4.md",
                                REPO / "paper" / "draft_v3.md",
                                REPO / "paper" / "draft_v2.md",
                                REPO / "paper" / "draft_v1.md")
                    if p.exists()), REPO / "paper" / "skeleton.md")
    result = run_gate(
        src.read_text(encoding="utf-8"),
        json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8")),
        (REPO / "paper" / "limitations_inventory.md").read_text(encoding="utf-8"),
        (REPO / "paper" / "refs.bib").read_text(encoding="utf-8"),
    )
    try:
        label = str(src.relative_to(REPO))
    except ValueError:
        label = str(src)
    report = to_markdown(result, label)
    (REPO / "paper" / "gate_report.md").write_text(report, encoding="utf-8")
    print(report)
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
