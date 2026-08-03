"""Smoke tests for the publication quality gate (held to scorer standard):
one clean fixture must PASS every check, one sloppy fixture must FAIL the
right checks, and the claims ledger must flag numeral/superlative sentences."""

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "paper" / "gate" / "fixtures"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load("paper_gate", REPO / "paper" / "gate" / "paper_gate.py")
ledger = _load("claims_ledger", REPO / "paper" / "gate" / "claims_ledger.py")

NUMBERS = {"score": 0.9, "ci": [0.7, 1.0], "n_sets": 10}
INVENTORY = "- pilot scale bounds mechanism coverage\n"
REFS_CLEAN = "@misc{x, title={y}}"
REFS_TODO = "@misc{x, note={TODO-verify later}}"
LEDGER_CLEAN = "| claim | source | status |\n|---|---|---|\n| s | numbers.json | VERIFIED |\n"
LEDGER_DIRTY = "| claim | source | status |\n|---|---|---|\n| s | numbers.json | UNVERIFIED |\n"


def test_pass_fixture_passes_every_check():
    paper = (FIX / "pass_fixture.md").read_text(encoding="utf-8")
    res = gate.run_gate(paper, NUMBERS, INVENTORY, REFS_CLEAN, ledger=LEDGER_CLEAN)
    failing = [cid for cid, c in res["checks"].items() if not c["passed"]]
    assert res["overall_pass"], f"clean fixture failed: {failing}"


def test_fail_fixture_fails_the_right_checks():
    paper = (FIX / "fail_fixture.md").read_text(encoding="utf-8")
    res = gate.run_gate(paper, NUMBERS, INVENTORY, REFS_TODO, ledger=LEDGER_DIRTY)
    assert not res["overall_pass"]
    c = res["checks"]
    assert not c["SCI-1"]["passed"]      # 0.123 orphan
    assert not c["SCI-2"]["passed"]      # delta w/o CI, significant w/o Holm, proves
    assert not c["SCI-3"]["passed"]      # state-of-the-art + frontier label
    assert not c["SCI-4"]["passed"]      # gemini-3.6-flash + "calendar mechanism"
    assert not c["SCI-5"]["passed"]      # refs TODO-verify
    assert not c["SCI-6"]["passed"]      # no Limitations coverage
    assert not c["SCI-7"]["passed"]      # UNVERIFIED ledger row
    assert not c["STY-2"]["passed"]      # delve/moreover/testament + question mark
    assert not c["STY-5"]["passed"]      # "The" opener repetition


def test_claims_ledger_flags_numerals_and_superlatives():
    text = ("All five arms failed. The score was 0.42 overall. "
            "Nothing numeric or superlative lives here at last.")
    md = ledger.build_ledger("# t\n\n## s\n\n" + text)
    assert md.count("UNVERIFIED") >= 2
    assert "0.42" in md
