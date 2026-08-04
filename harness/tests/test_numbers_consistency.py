"""Paper-numbers self-test:
(1) paper/numbers.json regenerates byte-identically from raw + frozen tasks
    (deterministic scoring + seeded bootstrap);
(2) every {path} placeholder in paper/skeleton.md resolves inside numbers.json
    ('*' = all keys at that level; every expanded branch must resolve)."""

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


def test_numbers_json_regenerates_byte_identically():
    committed = (REPO / "paper" / "numbers.json").read_text(encoding="utf-8")
    rebuilt = json.dumps(pull_numbers.build(), indent=2, ensure_ascii=False)
    assert rebuilt == committed, (
        "paper/numbers.json is stale — rerun python3 paper/pull_numbers.py"
    )


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
    """numbers.json's audit block must equal a fresh dc3_compute.compute()
    (same arithmetic, no retyping), and no [pending: DC3] marker may remain
    in the skeleton now that DC3 is adjudicated (D29)."""
    spec = importlib.util.spec_from_file_location(
        "dc3_compute", REPO / "scripts" / "dc3_compute.py")
    dc3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dc3)
    r = dc3.compute()

    numbers = json.loads((REPO / "paper" / "numbers.json").read_text(encoding="utf-8"))
    au = numbers["audit"]
    for key in ("human_kappa", "consensus_n", "gate_agreement", "gate_kappa",
                "scorer_vs_A", "scorer_vs_B", "dc3_verdict"):
        assert au[key] == r[key], f"audit.{key} diverged from dc3_compute"
    assert au["dc3_verdict"] in ("PASS", "FAIL")
    assert 0.0 <= au["gate_agreement"] <= 1.0 and au["consensus_n"] <= 50

    skeleton = (REPO / "paper" / "skeleton.md").read_text(encoding="utf-8")
    assert "[pending: DC3]" not in skeleton
