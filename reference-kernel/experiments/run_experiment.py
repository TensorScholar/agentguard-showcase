#!/usr/bin/env python3
"""Publicly reproducible AgentGuard reference experiments (v4).

Runs six deterministic adversarial scenarios against the educational
kernel and writes a machine-readable results.json using the
portfolio-wide experiment schema:

    scenario, configuration, expected_behavior, observed_behavior,
    evidence_level, limitations

This experiment validates the *reference kernel*, not the private core.
Evidence maturity for these results is L2 (publicly reproducible).

Usage:
    python experiments/run_experiment.py [--fixtures DIR] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from attacks.argument_mutation import run as run_mutation  # noqa: E402
from attacks.credential_mismatch import run as run_cred  # noqa: E402
from attacks.framework import EVIDENCE_LEVEL, LIMITATIONS, load_fixtures  # noqa: E402
from attacks.privilege_escalation import run as run_escalation  # noqa: E402
from attacks.prompt_injection_scenario import run as run_injection  # noqa: E402
from attacks.replay_attack import run as run_replay  # noqa: E402
from attacks.stale_authorization import run as run_stale  # noqa: E402

CONFIGURATION = "in-memory replay store, HMAC educational signatures, deterministic fixtures"

SCENARIOS: list[tuple] = [
    (
        run_mutation,
        "argument_mutation",
        "post-authorization argument mutation",
        "attack blocked with execution.arguments_digest_mismatch; executor never called",
    ),
    (
        run_replay,
        "replay_attack",
        "replay of a consumed single-use receipt",
        "first use allowed, second blocked with decision_receipt.replayed; executor called exactly once",
    ),
    (
        run_cred,
        "credential_mismatch",
        "credential ceiling detached from the authorizing receipt",
        "attack blocked with credential.ceiling_exceeds_receipt; executor never called",
    ),
    (
        run_stale,
        "stale_authorization",
        "expired receipt presented after TTL",
        "attack blocked with execution.receipt_expired; executor never called",
    ),
    (
        run_escalation,
        "privilege_escalation_attempt",
        "action/audience widening beyond the authorizing receipt",
        "escalated action denied at policy; forged audience rejected with credential.audience_mismatch",
    ),
    (
        run_injection,
        "prompt_injection_scenario",
        "prompt-injection boundary case (injection NOT claimed solved)",
        "over-ceiling injected proposal denied; untrusted-provenance proposal escalated to require_approval; "
        "post-auth injected mutation blocked at digest binding",
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default=str(ROOT / "fixtures"))
    ap.add_argument("--out", default=str(ROOT / "experiments" / "results.json"))
    args = ap.parse_args()

    fixtures = load_fixtures(Path(args.fixtures))
    records = []
    for fn, name, threat, expected in SCENARIOS:
        s = fn()
        assert s.name == name, f"scenario name drift: {s.name} != {name}"
        observed: dict = {
            "blocked": bool(s.blocked),
            "reason_code": s.reason_code,
            "executor_calls": s.executor_calls,
        }
        if name == "prompt_injection_scenario":
            # Machine-readable guard against misreading this scenario:
            # the boundary held, but injection as a class is NOT solved.
            observed["prompt_injection_solved"] = False
            observed["demonstrates"] = [
                "over-ceiling injected proposal denied at policy",
                "untrusted-provenance high-impact proposal escalated to require_approval",
                "post-authorization injected mutation blocked by digest binding",
            ]
        records.append(
            {
                "scenario": s.name,
                "threat": threat,
                "configuration": CONFIGURATION,
                "fixture": fixtures.get(name, {}),
                "expected_behavior": expected,
                "observed_behavior": observed,
                "pass": bool(s.blocked),
                "evidence_level": EVIDENCE_LEVEL,
                "limitations": list(LIMITATIONS),
            }
        )
    payload = {
        "project": "AgentGuard",
        "artifact": "reference-kernel",
        "evidence_maturity": EVIDENCE_LEVEL,
        "note": "Validates the public reference kernel only. Does not prove private-core production behavior. "
        "Prompt injection is NOT claimed solved; the boundary scenario shows detection boundary, "
        "provenance requirement, approval escalation, and digest binding.",
        "results": records,
        "all_pass": all(r["pass"] for r in records),
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_pass"]:
        print("FAIL: one or more invariants did not hold", file=sys.stderr)
        return 1
    print(f"PASS: {len(records)} scenarios blocked as specified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
