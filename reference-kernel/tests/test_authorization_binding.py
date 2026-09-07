from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"test-secret-key"


def test_digest_is_order_insensitive_and_value_sensitive():
    a = {"amount_minor": 8500, "order_id": "x"}
    b = {"order_id": "x", "amount_minor": 8500}
    c = {"amount_minor": 8501, "order_id": "x"}
    assert arguments_digest(a) == arguments_digest(b)
    assert arguments_digest(a) != arguments_digest(c)


def test_mutated_arguments_never_reach_executor():
    store = ReplayStore()
    args = {"amount_minor": 8500, "order_id": "o1"}
    receipt = make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="1",
        max_amount_minor=10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    calls = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments={"amount_minor": 85000, "order_id": "o1"},
        replay_store=store,
        executor=lambda a: calls.append(a),
    )
    assert result.allowed is False
    assert result.reason_code == "execution.arguments_digest_mismatch"
    assert calls == []
