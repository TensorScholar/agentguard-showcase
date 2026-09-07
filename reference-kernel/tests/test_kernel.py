"""Tests for the AgentGuard reference kernel.

Corrected in v4: imports use the real ``core.*`` package and the current
``execute_protected`` signature (receipt_signature=...). The stale v3 file
imported a non-existent ``src.*`` layout and never ran in CI.
"""

from __future__ import annotations

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt, verify_receipt
from core.replay import ReplayStore

SECRET = b"test-secret-key"


def test_arguments_digest_stable_and_sensitive():
    a = {"amount_minor": 8500, "order_id": "x"}
    b = {"order_id": "x", "amount_minor": 8500}  # key order different
    c = {"amount_minor": 8501, "order_id": "x"}
    assert arguments_digest(a) == arguments_digest(b)
    assert arguments_digest(a) != arguments_digest(c)


def test_policy_allow_and_ceiling():
    d = evaluate_policy(
        action="refund.create",
        arguments={"amount_minor": 5000},
        principal="agent",
        max_amount_minor=10_000,
    )
    assert d.effect == "allow"
    assert d.max_amount_minor == 10_000

    d2 = evaluate_policy(
        action="refund.create",
        arguments={"amount_minor": 15_000},
        principal="agent",
        max_amount_minor=10_000,
    )
    assert d2.effect == "deny"
    assert d2.reason_code == "policy.amount_exceeds_ceiling"


def test_receipt_roundtrip():
    r = make_receipt(
        principal="p",
        action="refund.create",
        arguments_digest="abc",
        policy_revision="1",
        max_amount_minor=1000,
    )
    sig = sign_receipt(r, SECRET)
    assert verify_receipt(r, sig, SECRET)
    assert not verify_receipt(r, "deadbeef", SECRET)


def test_mutation_rejected():
    store = ReplayStore()
    args = {"amount_minor": 8500, "order_id": "o1"}
    digest = arguments_digest(args)
    receipt = make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=digest,
        policy_revision="1",
        max_amount_minor=10_000,
    )
    sig = sign_receipt(receipt, SECRET)

    mutated = {"amount_minor": 85000, "order_id": "o1"}
    calls = []

    def ex(a):
        calls.append(a)

    result = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=mutated,
        replay_store=store,
        executor=ex,
    )
    assert result.allowed is False
    assert result.reason_code == "execution.arguments_digest_mismatch"
    assert len(calls) == 0


def test_replay_rejected():
    store = ReplayStore()
    args = {"amount_minor": 1000, "order_id": "o2"}
    digest = arguments_digest(args)
    receipt = make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=digest,
        policy_revision="1",
        max_amount_minor=10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    calls = []

    def ex(a):
        calls.append(a)

    r1 = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=ex,
    )
    assert r1.allowed is True
    assert len(calls) == 1

    r2 = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=ex,
    )
    assert r2.allowed is False
    assert r2.reason_code == "decision_receipt.replayed"
    assert len(calls) == 1  # executor not called again
