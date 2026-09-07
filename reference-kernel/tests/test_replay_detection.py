from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"test-secret-key"


def test_consumed_receipt_cannot_be_replayed():
    store = ReplayStore()
    args = {"amount_minor": 1000, "order_id": "o2"}
    receipt = make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="1",
        max_amount_minor=10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    calls = []
    r1 = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=lambda a: calls.append(a),
    )
    r2 = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=lambda a: calls.append(a),
    )
    assert r1.allowed is True
    assert r2.allowed is False
    assert r2.reason_code == "decision_receipt.replayed"
    assert len(calls) == 1
