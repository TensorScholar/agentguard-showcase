#!/usr/bin/env python3
"""Claim a decision receipt once on AgentGuard's protected execution path.

This file is a showcase consumer. It does not reimplement authorization,
cryptography, or ledger logic. AgentGuard itself validates the receipt,
reserves the nonce, and rejects replay.

The executor is AgentGuard's DeterministicFakeExecutor: first use proves
that protected execution authority was claimed, not that a live provider
was contacted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from agentguard.adapters.crypto import Ed25519BrokerGrantVerifier, Ed25519Signer, Ed25519Verifier
from agentguard.adapters.executor import DeterministicFakeExecutor
from agentguard.adapters.storage.sqlite import SQLiteState
from agentguard.application import AgentGuardService
from agentguard.domain import ActionIntent, CredentialGrant, DecisionReceipt, PolicyDocument
from agentguard.engine.execution import ExecutionGuardError


def _load_policy(path: Path) -> PolicyDocument:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PolicyDocument.model_validate_json(json.dumps(payload))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--grant", type=Path, required=True)
    parser.add_argument("--decision-key", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--broker-public-key", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--broker-id", default="mock-broker")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    intent = ActionIntent.model_validate_json(args.request.read_text(encoding="utf-8"))
    receipt = DecisionReceipt.model_validate_json(args.receipt.read_text(encoding="utf-8"))
    grant = CredentialGrant.model_validate_json(args.grant.read_text(encoding="utf-8"))
    policy = _load_policy(args.policy)
    signer = Ed25519Signer.load_private(args.decision_key)
    verifier = Ed25519Verifier.from_public_file(args.public_key)
    broker_verifier = Ed25519BrokerGrantVerifier.from_public_file(
        args.broker_public_key,
        broker_id=args.broker_id,
    )
    service = AgentGuardService(
        signer,
        verifier,
        SQLiteState(args.ledger),
        broker_verifier,
    )
    executor = DeterministicFakeExecutor()

    first = service.execute_protected(
        intent,
        receipt,
        grant,
        executor,
        current_policy=policy,
    )
    first_payload = {
        "status": first.status.value,
        "execution_id": first.execution_id,
        "executor_calls": len(executor.calls),
    }

    replay_reason = None
    try:
        service.execute_protected(
            intent,
            receipt,
            grant,
            executor,
            current_policy=policy,
        )
    except ExecutionGuardError as exc:
        replay_reason = str(exc)

    result = {
        "first_use": first_payload,
        "second_use": {
            "accepted": replay_reason is None,
            "reason": replay_reason,
            "executor_calls": len(executor.calls),
        },
    }
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")

    if first.status.value != "success":
        print("first protected use did not succeed", file=sys.stderr)
        return 2
    if replay_reason is None:
        print("second protected use was unexpectedly accepted", file=sys.stderr)
        return 3
    if replay_reason != "decision_receipt.replayed":
        print(f"unexpected replay reason: {replay_reason}", file=sys.stderr)
        return 4
    if len(executor.calls) != 1:
        print("replay reached the executor more than once", file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
