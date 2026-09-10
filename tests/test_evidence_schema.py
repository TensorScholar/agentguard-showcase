"""Repo-level evidence-schema tests (run from the repository root).

Guards the public contract: claims ledger shape, maturity vocabulary,
and experiment results schema. These run locally via `make verify` or `pytest`.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MATURITY = {"L0", "L1", "L2", "L3", "Conceptual"}

# Result target files relative to repo root: (path, allow_L3)
RESULT_TARGETS = [("reference-kernel/experiments/results.json", False)]

REQUIRED_CLAIM_FIELDS = {"id", "statement", "evidence_maturity", "scope", "falsification_condition"}
REQUIRED_RESULT_FIELDS = {
    "scenario",
    "configuration",
    "expected_behavior",
    "observed_behavior",
    "evidence_level",
    "limitations",
    "pass",
}


def test_claims_ledger_schema():
    claims = json.loads((ROOT / "evidence" / "claims.json").read_text(encoding="utf-8"))
    assert claims["claims"], "claims ledger must not be empty"
    ids = set()
    for c in claims["claims"]:
        missing = REQUIRED_CLAIM_FIELDS - set(c.keys())
        assert not missing, f"{c.get('id')}: missing {missing}"
        assert c["id"] not in ids, f"duplicate claim id {c['id']}"
        ids.add(c["id"])
        assert c["evidence_maturity"] in MATURITY, f"{c['id']}: bad maturity"


def test_no_unexpected_L3():
    claims = json.loads((ROOT / "evidence" / "claims.json").read_text(encoding="utf-8"))
    l3 = [c["id"] for c in claims["claims"] if c.get("evidence_maturity") == "L3"]
    assert not l3, f"unexpected L3 claims (no external validation in this repo): {l3}"


def test_results_schema():
    assert RESULT_TARGETS, "RESULT_TARGETS must contain at least one target result file"
    for rel, allow_l3 in RESULT_TARGETS:
        target_path = ROOT / rel
        assert target_path.is_file(), f"required result file missing: {rel}"
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        results = payload.get("results")
        assert results, f"{rel}: empty or missing results list"
        for r in results:
            missing = REQUIRED_RESULT_FIELDS - set(r.keys())
            assert not missing, f"{r.get('scenario')}: missing {missing}"
            if not allow_l3:
                assert r.get("evidence_level") != "L3", f"{r.get('scenario')}: L3 evidence level not allowed"
        assert payload.get("all_pass") is True, f"{rel}: all_pass is not true"
