#!/usr/bin/env python3
"""Claims ledger v1.1 (SCI-7 input) — provenance automation per D32.

Every sentence containing a numeral or a superlative becomes a ledger row
(claim | source | status). Status is now resolved automatically where the
provenance is mechanical:

- VERIFIED              every numeral in the sentence matches numbers.json
                        (same matcher + whitelist as gate check SCI-1);
                        source lists the resolved numbers.json paths.
- VERIFIED-BY-REFERENCE the sentence carries a bracketed cite token; source
                        is the mapped refs.bib key(s), and the status holds
                        only while those entries carry no TODO-verify.
- PENDING-REFS          cite-bearing row whose bib entry still carries
                        TODO-verify — flips to VERIFIED-BY-REFERENCE when
                        the reference clears (ties into SCI-5).
- MANUAL                everything else: research-lead line-by-line sign-off.

Gate check SCI-7 passes only when no UNVERIFIED/MANUAL/PENDING-REFS rows
remain.

Usage: python3 paper/gate/claims_ledger.py [paper.md] -> paper/claims_ledger.md
  default input preference (v1.1): draft_v4.md > draft_v3.md > draft_v2.md > draft_v1.md > skeleton.md
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "paper_gate", Path(__file__).with_name("paper_gate.py"))
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

SUPERLATIVES = r"\b(best|worst|largest|smallest|first|most|least|highest|lowest|strongest|weakest|universal|every|all five|none)\b"

CITE_TO_BIBKEY = {
    "P1": "kubrak2026arabicprompts",
    "P2": "ersoy2025toolcalling",
    "P3": "nacar2026language",
    "P4": "bariah2026telcoagent",
    "S1": "kulkarni2025massive",
    "S2": "arabicsurvey2025",
    "MAST": "cemri2025mast",
    "AgentErrorBench": "agenterror2025",
    "ToolScan": "toolscan",
    "AgentHallu": "agenthallu",
    "Aegis": "aegis2025",
    "AgentAtlas": "agentatlas2026",
}
CITE_TOKEN_RE = re.compile(
    r"P\d\s*[–-]\s*P\d|P\d|S\d|MAST|AgentErrorBench|ToolScan|AgentHallu|Aegis|AgentAtlas")


def sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'\(\[])", text.replace("\n", " "))
    return [s.strip() for s in raw if len(s.strip()) > 2]


def _bib_entries(refs: str) -> dict[str, str]:
    entries = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)(?=@\w+\{|\Z)", refs, re.DOTALL):
        entries[m.group(1).strip()] = m.group(2)
    return entries


def _cite_keys(sentence: str) -> list[str]:
    keys = []
    for bracket in gate.CITE_RE.findall(sentence):
        for tok in CITE_TOKEN_RE.findall(bracket):
            rng = re.match(r"P(\d)\s*[–-]\s*P(\d)", tok)
            toks = ([f"P{i}" for i in range(int(rng.group(1)), int(rng.group(2)) + 1)]
                    if rng else [tok])
            for t in toks:
                k = CITE_TO_BIBKEY.get(t)
                if k and k not in keys:
                    keys.append(k)
    return keys


def _path_values(node, prefix, acc):
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        acc.append((prefix, float(node)))
    elif isinstance(node, dict):
        for k, v in node.items():
            _path_values(v, f"{prefix}.{k}" if prefix else k, acc)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _path_values(v, f"{prefix}[{i}]", acc)


def _resolve_paths(tok: str, paths: list[tuple[str, float]]) -> list[str]:
    return [p for p, v in paths if gate._numeric_ok(tok, {v})]


def _load_signoffs() -> list[dict]:
    p = Path(__file__).with_name("ledger_signoffs.json")
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("signoffs", [])


def build_ledger(paper: str, numbers: dict | None = None,
                 refs: str | None = None,
                 signoffs: list[dict] | None = None) -> str:
    paths: list[tuple[str, float]] = []
    if numbers:
        _path_values(numbers, "", paths)
    allowed = {v for _, v in paths}
    bib = _bib_entries(refs) if refs else {}

    rows = []
    for s in sentences(paper):
        scrubbed = s
        for pat in gate.WHITELIST_PATTERNS:
            scrubbed = re.sub(pat, " ", scrubbed)
        toks = re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w.\-])", scrubbed)
        has_sup = re.search(SUPERLATIVES, s, re.IGNORECASE)
        if not toks and not has_sup:
            continue
        claim = s.replace("|", "\\|")[:160]
        cite_keys = _cite_keys(s)
        if cite_keys:
            dirty = [k for k in cite_keys
                     if k not in bib or "TODO-verify" in bib[k]]
            status = "PENDING-REFS" if dirty else "VERIFIED-BY-REFERENCE"
            source = "refs:" + ",".join(cite_keys)
        elif toks:
            resolved, unresolved = [], []
            for tok in dict.fromkeys(toks):
                hits = _resolve_paths(tok, paths) if allowed else []
                (resolved.append((tok, hits[0])) if hits
                 else unresolved.append(tok))
            if not unresolved:
                status = "VERIFIED"
                source = "; ".join(f"{p}={t}" for t, p in resolved[:4]) or "numbers.json"
            else:
                status = "MANUAL"
                source = f"numbers.json:<path> (unmatched: {', '.join(unresolved[:5])})"
        else:
            status = "MANUAL"
            source = "raw/log or citation"
        # research-lead sign-offs (ledger_signoffs.json) override, keyed on
        # claim-text substring so they survive regeneration
        for so in (signoffs if signoffs is not None else _load_signoffs()):
            if so["match"] in s:
                if so["status"] == "INTERPRETIVE":  # D34 constraints
                    assert not toks, f"D34: INTERPRETIVE on numeral row: {s[:60]}"
                    assert "\u00a7" in so["source"] or "SS" in so["source"], \
                        f"D34: INTERPRETIVE without section ref: {so['match']}"
                status, source = so["status"], so["source"]
                break
        rows.append(f"| {claim} | {source.replace('|', '/')} | {status} |")

    lines = ["# Claims Ledger (v1.1 — D32 provenance automation)", "",
             "VERIFIED = all numerals resolve in numbers.json (SCI-1 matcher).",
             "VERIFIED-BY-REFERENCE = cite-bound, bib entry clean.",
             "PENDING-REFS = cite-bound, bib entry still TODO-verify.",
             "VERIFIED-BY-DOC = grounded in a repository document (cycle-6",
             "sign-offs; path + anchor in the source column).",
             "INTERPRETIVE = reads the evidence of a named section (D34);",
             "non-blocking, forbidden on numeral rows.",
             "MANUAL = needs research-lead line-by-line sign-off.",
             "Gate SCI-7 passes only when no UNVERIFIED/MANUAL/PENDING-REFS",
             "rows remain.", "",
             "| claim | source | status |", "|---|---|---|"] + rows
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        src = Path(argv[0]).resolve()
    else:
        src = next((p for p in (REPO / "paper" / "draft_v4.md",
                                REPO / "paper" / "draft_v3.md",
                                REPO / "paper" / "draft_v2.md",
                                REPO / "paper" / "draft_v1.md")
                    if p.exists()), REPO / "paper" / "skeleton.md")
    numbers = json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8"))
    refs = (REPO / "paper" / "refs.bib").read_text(encoding="utf-8")
    ledger = build_ledger(src.read_text(encoding="utf-8"), numbers, refs)
    (REPO / "paper" / "claims_ledger.md").write_text(ledger, encoding="utf-8")
    counts = {st: ledger.count(f"| {st} |")
              for st in ("VERIFIED", "VERIFIED-BY-REFERENCE", "VERIFIED-BY-DOC",
                         "INTERPRETIVE", "PENDING-REFS", "MANUAL",
                         "UNVERIFIED")}
    print(f"wrote paper/claims_ledger.md ({sum(counts.values())} rows): "
          + ", ".join(f"{k}={v}" for k, v in counts.items() if v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
