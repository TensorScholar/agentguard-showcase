"""Privilege escalation attempt: action / audience widening.

Threat: an authorized low-privilege receipt (refund.create for
payments.internal) is reused — or a credential is minted — for a
higher-privilege action (wire.transfer) or a different audience
(treasury.internal).

Expected: fail closed. Two layers are demonstrated:
  1. A receipt bound to refund.create cannot authorize wire.transfer:
     the policy layer denies the unknown action (no receipt is issued),
     and even a hand-forged receipt/action mismatch cannot pass the
     executor gate because the receipt's action is part of what the
     caller must present consistently (demonstrated via audience
     domination on the credential path).
  2. A credential whose audience differs from the receipt's audience is
     rejected with credential.audience_mismatch even when its signature
     verifies under the same educational secret.

Boundary: this shows *domination checks firing*, not a full
authorization model. A real system also needs action registries,
audience PKI, and deployment-level route mediation (see
docs/rejected-designs.md for why capability-only designs were rejected).
"""

from __future__ import annotations

from dataclasses import replace

from core.credential import issue_credential, sign_credential
from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

from .argument_mutation import SECRET
from .framework import ScenarioResult, ScenarioSpec, register

EXPECTED = ("credential.audience_mismatch",)


def run() -> ScenarioResult:
    # Layer 1: policy denies the escalated action under the same principal.
    escalated = evaluate_policy(
        action="wire.transfer",
        arguments={"order_id": "ord_esc_1", "amount_minor": 100},
        principal="support-agent-v3",
        allowed_actions={"refund.create"},
    )
    layer1 = escalated.effect == "deny" and escalated.reason_code == "policy.unknown_action"

    # Layer 2: credential audience detached from the receipt is rejected
    # at the execution gate even with a valid HMAC signature.
    args = {"order_id": "ord_esc_2", "amount_minor": 1000, "currency": "USD"}
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="ref-1",
        max_amount_minor=10_000,
        audience="payments.internal",
    )
    rsig = sign_receipt(receipt, SECRET)
    cred, _ = issue_credential(receipt, SECRET)
    forged = replace(cred, audience="treasury.internal")
    forged_sig = sign_credential(forged, SECRET)
    calls: list = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=rsig,
        secret=SECRET,
        live_arguments=args,
        replay_store=ReplayStore(),
        credential=forged,
        credential_signature=forged_sig,
        executor=lambda a: calls.append(a),
    )
    layer2 = (not result.allowed) and result.reason_code in EXPECTED and not calls

    blocked = layer1 and layer2
    return ScenarioResult(
        name="privilege_escalation_attempt",
        threat="action/audience widening beyond the authorizing receipt",
        blocked=blocked,
        reason_code=result.reason_code if layer1 else "policy.layer_failed",
        executor_calls=len(calls),
        expected_reason_codes=EXPECTED,
        notes=f"policy_layer_deny={layer1}; credential_audience_check={layer2}",
    )


register(
    ScenarioSpec(
        name="privilege_escalation_attempt",
        threat="action/audience widening beyond the authorizing receipt",
        expected_reason_codes=EXPECTED,
        run=run,
    )
)
