"""Minimal policy evaluator.

Educational subset: allow / deny / require_approval with financial ceilings
and a coarse provenance check.

Does not implement the full production policy language (MCP routing,
credential audiences beyond a string, multi-rule priority tables).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence

Effect = Literal["allow", "deny", "require_approval"]

UNTRUSTED_PROVENANCE = frozenset(
    {
        "external_email",
        "external_web_content",
        "third_party_document",
        "other_agent_message",
        "untrusted_prompt",
    }
)

HIGH_IMPACT_ACTIONS = frozenset({"refund.create", "wire.transfer", "bulk_export"})


@dataclass(frozen=True)
class PolicyDecision:
    effect: Effect
    reason_code: str
    max_amount_minor: int | None = None
    policy_revision: str = "ref-1"
    audience: str = "payments.internal"


def evaluate_policy(
    *,
    action: str,
    arguments: dict[str, Any],
    principal: str,
    provenance: Sequence[str] | None = None,
    allowed_actions: set[str] | None = None,
    max_amount_minor: int = 10_000,
) -> PolicyDecision:
    allowed_actions = allowed_actions or {"refund.create"}
    provenance_set = set(provenance or [])

    if action not in allowed_actions:
        return PolicyDecision(effect="deny", reason_code="policy.unknown_action")

    amount = int(arguments.get("amount_minor", 0))
    if amount <= 0:
        return PolicyDecision(effect="deny", reason_code="policy.invalid_amount")
    if amount > max_amount_minor:
        return PolicyDecision(
            effect="deny",
            reason_code="policy.amount_exceeds_ceiling",
            max_amount_minor=max_amount_minor,
        )

    if action in HIGH_IMPACT_ACTIONS and provenance_set & UNTRUSTED_PROVENANCE:
        return PolicyDecision(
            effect="require_approval",
            reason_code="provenance.untrusted_high_impact",
            max_amount_minor=max_amount_minor,
        )

    # principal is part of the authorization identity even in this toy evaluator
    if not principal:
        return PolicyDecision(effect="deny", reason_code="policy.missing_principal")

    return PolicyDecision(
        effect="allow",
        reason_code="policy.bounded_allow",
        max_amount_minor=max_amount_minor,
        policy_revision="ref-1",
    )
