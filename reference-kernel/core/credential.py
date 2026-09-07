"""Credential issuance bounded by a decision receipt.

A credential cannot authorize a larger effect than the receipt that
justified it. Audience, amount ceiling, and TTL are inherited (or strictly
narrowed) from the receipt.

This is the binding between "what was authorized" and "what credential
the executor may present."
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import asdict, dataclass

from .receipt import DecisionReceipt


@dataclass(frozen=True)
class Credential:
    credential_id: str
    receipt_id: str
    audience: str
    max_amount_minor: int
    issued_at: float
    ttl_seconds: int
    single_use: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    def is_expired(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        return (now - self.issued_at) > self.ttl_seconds


def _payload(cred: Credential) -> bytes:
    return json.dumps(cred.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_credential(cred: Credential, secret: bytes) -> str:
    return hmac.new(secret, _payload(cred), hashlib.sha256).hexdigest()


def verify_credential_signature(cred: Credential, signature: str, secret: bytes) -> bool:
    return hmac.compare_digest(sign_credential(cred, secret), signature)


def issue_credential(receipt: DecisionReceipt, secret: bytes) -> tuple[Credential, str]:
    cred = Credential(
        credential_id=str(uuid.uuid4()),
        receipt_id=receipt.receipt_id,
        audience=receipt.audience,
        max_amount_minor=receipt.max_amount_minor,
        issued_at=receipt.issued_at,
        ttl_seconds=min(receipt.ttl_seconds, 60),
        single_use=True,
    )
    return cred, sign_credential(cred, secret)


def verify_credential_against_receipt(
    cred: Credential,
    signature: str,
    secret: bytes,
    receipt: DecisionReceipt,
) -> str | None:
    """Return a reason_code if the credential is not valid for this receipt."""
    if not verify_credential_signature(cred, signature, secret):
        return "credential.invalid_signature"
    if cred.receipt_id != receipt.receipt_id:
        return "credential.receipt_mismatch"
    if cred.audience != receipt.audience:
        return "credential.audience_mismatch"
    if cred.max_amount_minor > receipt.max_amount_minor:
        return "credential.ceiling_exceeds_receipt"
    if cred.is_expired():
        return "credential.expired"
    return None
