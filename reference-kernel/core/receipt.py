"""Decision receipt model and signing.

A DecisionReceipt is the durable, signed artifact of a successful policy
evaluation. It binds principal, action, arguments digest, policy revision,
resource ceilings, and issuance metadata.

HMAC-SHA256 is used here for educational simplicity. Production systems
would use asymmetric signatures with hardware-backed or HSM-managed keys.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DecisionReceipt:
    receipt_id: str
    principal: str
    action: str
    arguments_digest: str
    policy_revision: str
    max_amount_minor: int
    max_records: int
    audience: str
    issued_at: float
    ttl_seconds: int
    single_use: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_expired(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        return (now - self.issued_at) > self.ttl_seconds


def _signing_payload(receipt: DecisionReceipt) -> bytes:
    return json.dumps(receipt.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_receipt(receipt: DecisionReceipt, secret: bytes) -> str:
    return hmac.new(secret, _signing_payload(receipt), hashlib.sha256).hexdigest()


def verify_receipt(receipt: DecisionReceipt, signature: str, secret: bytes) -> bool:
    expected = sign_receipt(receipt, secret)
    return hmac.compare_digest(expected, signature)


def make_receipt(
    *,
    principal: str,
    action: str,
    arguments_digest: str,
    policy_revision: str,
    max_amount_minor: int,
    audience: str = "payments.internal",
    max_records: int = 1,
    ttl_seconds: int = 60,
    single_use: bool = True,
    issued_at: float | None = None,
) -> DecisionReceipt:
    return DecisionReceipt(
        receipt_id=str(uuid.uuid4()),
        principal=principal,
        action=action,
        arguments_digest=arguments_digest,
        policy_revision=policy_revision,
        max_amount_minor=max_amount_minor,
        max_records=max_records,
        audience=audience,
        issued_at=issued_at if issued_at is not None else time.time(),
        ttl_seconds=ttl_seconds,
        single_use=single_use,
    )
