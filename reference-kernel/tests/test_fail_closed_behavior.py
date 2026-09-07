from dataclasses import replace

from core.credential import issue_credential, sign_credential
from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"test-secret-key"


def _receipt(args, **kw):
    return make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="1",
        max_amount_minor=10_000,
        **kw,
    )


def test_invalid_signature_fails_closed():
    args = {"amount_minor": 1000, "order_id": "o"}
    receipt = _receipt(args)
    result = execute_protected(
        receipt=receipt,
        receipt_signature="deadbeef",
        secret=SECRET,
        live_arguments=args,
        replay_store=ReplayStore(),
    )
    assert result.allowed is False
    assert result.reason_code == "execution.invalid_signature"
    assert result.executor_called is False


def test_unknown_action_denied_before_receipt():
    d = evaluate_policy(
        action="wire.transfer",
        arguments={"amount_minor": 100},
        principal="agent",
        allowed_actions={"refund.create"},
    )
    assert d.effect == "deny"
    assert d.reason_code == "policy.unknown_action"


def test_untrusted_provenance_requires_approval():
    d = evaluate_policy(
        action="refund.create",
        arguments={"amount_minor": 1000},
        principal="agent",
        provenance=["external_email"],
    )
    assert d.effect == "require_approval"


def test_widened_credential_ceiling_fails_closed():
    args = {"amount_minor": 1000, "order_id": "o"}
    receipt = _receipt(args)
    rsig = sign_receipt(receipt, SECRET)
    cred, _ = issue_credential(receipt, SECRET)
    forged = replace(cred, max_amount_minor=999_999)
    result = execute_protected(
        receipt=receipt,
        receipt_signature=rsig,
        secret=SECRET,
        live_arguments=args,
        replay_store=ReplayStore(),
        credential=forged,
        credential_signature=sign_credential(forged, SECRET),
    )
    assert result.allowed is False
    assert result.reason_code == "credential.ceiling_exceeds_receipt"
