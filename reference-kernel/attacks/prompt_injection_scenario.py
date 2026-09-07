"""Prompt-injection *proposal* vs execution binding.

What this does NOT claim:
    AgentGuard does not detect or neutralize prompt injection as a class.
    If an injected proposal is itself policy-allowable, the policy layer
    may authorize it.

What this DOES demonstrate:
    1. An injected over-ceiling proposal ($850 vs $100 ceiling) is denied
       at policy evaluation — no receipt is issued.
    2. An injected high-impact proposal from untrusted provenance is
       require_approval, not auto-allow.
    3. If a legitimate $85 receipt exists, a later injected mutation of
       arguments still fails at the execution gate.

The control plane is not a prompt firewall. It is a binding between
authorization and execution.
"""

from __future__ import annotations

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

from .argument_mutation import SECRET, AttackResult


def run() -> AttackResult:
    # Case 1: injected proposal exceeds policy ceiling
    injected_over = evaluate_policy(
        action="refund.create",
        arguments={"order_id": "ord_1", "amount_minor": 85000},
        principal="support-agent-v3",
        provenance=["untrusted_prompt"],
        max_amount_minor=10_000,
    )
    case1 = injected_over.effect == "deny" and injected_over.reason_code in {
        "policy.amount_exceeds_ceiling",
        "provenance.untrusted_high_impact",
    }

    # Case 2: injected but in-ceiling high-impact from untrusted provenance
    injected_untrusted = evaluate_policy(
        action="refund.create",
        arguments={"order_id": "ord_1", "amount_minor": 5000},
        principal="support-agent-v3",
        provenance=["untrusted_prompt", "authenticated_user_input"],
        max_amount_minor=10_000,
    )
    case2 = injected_untrusted.effect == "require_approval"

    # Case 3: legitimate auth, injected mutation at execution
    legit = {"order_id": "ord_1", "amount_minor": 8500, "currency": "USD"}
    d = evaluate_policy(
        action="refund.create",
        arguments=legit,
        principal="support-agent-v3",
        provenance=["authenticated_user_input", "internal_database"],
        max_amount_minor=10_000,
    )
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(legit),
        policy_revision=d.policy_revision,
        max_amount_minor=d.max_amount_minor or 10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    calls: list = []
    mutated = {**legit, "amount_minor": 85000}
    ex = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=mutated,
        replay_store=ReplayStore(),
        executor=lambda a: calls.append(a),
    )
    case3 = (not ex.allowed) and ex.reason_code == "execution.arguments_digest_mismatch" and not calls

    blocked = case1 and case2 and case3
    return AttackResult(
        name="prompt_injection_scenario",
        blocked=blocked,
        reason_code="composite:policy+provenance+digest",
        executor_calls=len(calls),
    )
