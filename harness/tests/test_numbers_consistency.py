"""Paper-1 frozen-number consistency tests.

Full byte-identical regeneration is still performed whenever the original raw
model-output files are present. A clean clone cannot do that because
``results/raw/`` was gitignored and the complete model-output corpus was never
committed. In that case we do NOT pretend to regenerate the paper numbers: we
verify the content-addressed frozen numbers artifact, the committed row-level
open-arm scored evidence, and the independently recomputable DC3 audit.

This distinction is intentional and documented in
experiments/calendar_patch/PAPER1_REPRODUCIBILITY_REMEDIATION_002.md.
"""

import hashlib
import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "pull_numbers", REPO / "paper" / "pull_numbers.py")
pull_numbers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pull_numbers)

PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.*]*)\}")
OPEN_ARMS = (
    "gpt-oss-20b",
    "deepseek-v4-flash-think",
    "deepseek-v4-flash-nothink",
    "qwen3.5-397b",
)


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _full_raw_inputs_present() -> bool:
    manifest = json.loads((REPO / "paper" / "run_manifest.json").read_text(encoding="utf-8"))
    frozen = manifest["frozen"]
    m3 = manifest["m3"]
    frontier = manifest["frontier"]
    required = []
    for arm in OPEN_ARMS:
        required.append(REPO / "results" / "raw" / frozen / f"{arm}.jsonl")
        required.append(REPO / "results" / "raw" / m3 / f"{arm}.jsonl")
    required.append(REPO / "results" / "raw" / frontier / "frontier-gemini.jsonl")
    return all(path.is_file() for path in required)


def _expected_numbers_blob_from_freeze() -> str:
    freeze = (REPO / "experiments" / "calendar_patch" / "PAPER1_FREEZE.md").read_text(
        encoding="utf-8"
    )
    match = re.search(r"paper/numbers\.json` — Git blob `([0-9a-f]{40})`", freeze)
    assert match, "Paper-1 freeze no longer records the numbers.json blob"
    return match.group(1)


def test_numbers_json_full_regeneration_or_frozen_integrity():
    numbers_path = REPO / "paper" / "numbers.json"
    committed = numbers_path.read_text(encoding="utf-8")

    if _full_raw_inputs_present():
        rebuilt = json.dumps(pull_numbers.build(), indent=2, ensure_ascii=False)
        assert rebuilt == committed, (
            "paper/numbers.json is stale relative to the complete raw evidence; "
            "do not rewrite it without a Paper-1 correction decision"
        )
        return

    # Clean-clone mode: full raw re-scoring is impossible, so verify exactly
    # what is actually preserved rather than silently weakening the claim.
    status = json.loads((REPO / "paper" / "repro_status.json").read_text(encoding="utf-8"))
    assert status["full_raw_model_outputs_committed"] is False
    assert status["clean_clone_mode"] == "frozen_artifact_integrity_plus_partial_row_evidence"

    expected_blob = _expected_numbers_blob_from_freeze()
    actual_blob = _git_blob_sha(numbers_path)
    assert actual_blob == expected_blob == status["paper_numbers_git_blob"], (
        "frozen paper/numbers.json bytes changed"
    )

    # The original four-arm 80-task scored projections are committed and must
    # remain complete even though they are not substitutes for the missing raw
    # transcripts or the later M3/closed-arm outputs.
    summary_dir = REPO / "results" / "summaries" / "20260803T081111Z"
    for arm in OPEN_ARMS:
        path = summary_dir / f"{arm}.scored.jsonl"
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(rows) == 80, f"committed scored evidence incomplete for {arm}: {len(rows)}"

    audit_rows = [
        line for line in (REPO / "docs" / "audit_kit" / "audit_sample.jsonl")
        .read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    sealed_rows = [
        line for line in (REPO / "docs" / "audit_kit" / "SEALED_scorer_verdicts.jsonl")
        .read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(audit_rows) == len(sealed_rows) == 50


def _resolve(node, parts):
    if not parts:
        return True
    head, rest = parts[0], parts[1:]
    if head == "*":
        if not isinstance(node, dict) or not node:
            return False
        return all(_resolve(v, rest) for v in node.values())
    if not isinstance(node, dict) or head not in node:
        return False
    return _resolve(node[head], rest)


def test_all_skeleton_placeholders_resolve():
    numbers = json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8"))
    skeleton = (REPO / "paper" / "skeleton.md").read_text(encoding="utf-8")
    failures = []
    for match in PLACEHOLDER_RE.finditer(skeleton):
        path = match.group(1)
        if "." not in path:  # prose braces, not a data path
            continue
        if not _resolve(numbers, path.split(".")):
            failures.append(path)
    assert not failures, f"unresolvable skeleton placeholders: {failures}"


def test_audit_block_matches_dc3_compute_and_no_pending_markers():
    """The frozen audit block must equal a fresh DC3-v2 recomputation from the
    committed blind audit evidence, and no pending marker may remain."""
    spec = importlib.util.spec_from_file_location(
        "dc3_compute", REPO / "scripts" / "dc3_compute.py")
    dc3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dc3)
    r = dc3.compute_v2()

    numbers = json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8"))
    au = numbers["audit"]
    for key in ("human_kappa", "consensus_n", "gate_v1", "gate_v2",
                "gate_agreement", "gate_kappa", "scorer_vs_A", "scorer_vs_B",
                "dc3_verdict"):
        assert au[key] == r[key], f"audit.{key} diverged from dc3_compute"
    assert au["dc3_verdict"] in ("PASS", "FAIL")
    assert au["gate_agreement"] == au["gate_v2"]
    assert 0.0 <= au["gate_agreement"] <= 1.0 and au["consensus_n"] <= 50

    skeleton = (REPO / "paper" / "skeleton.md").read_text(encoding="utf-8")
    assert "[pending: DC3]" not in skeleton
