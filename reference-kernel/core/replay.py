"""Replay detection.

A consumed decision receipt must not be reusable on the same durable state
boundary. This reference uses an in-memory set. Production systems need a
crash-safe durable store; that is an explicit non-claim of this kernel.
"""

from __future__ import annotations

import threading


class ReplayError(Exception):
    """Raised when a receipt is presented after consumption."""


class ReplayStore:
    """In-memory single-use consumption record.

    Thread-safe for same-process use via a lock (check-and-consume is
    atomic). Still NOT crash-safe, NOT multi-process, NOT distributed —
    those remain explicit non-claims (see docs/threat-model.md).
    """

    def __init__(self) -> None:
        self._consumed: set[str] = set()
        self._lock = threading.Lock()

    def is_consumed(self, receipt_id: str) -> bool:
        with self._lock:
            return receipt_id in self._consumed

    def consume(self, receipt_id: str) -> None:
        with self._lock:
            if receipt_id in self._consumed:
                raise ReplayError(f"receipt already consumed: {receipt_id}")
            self._consumed.add(receipt_id)

    def reset(self) -> None:
        with self._lock:
            self._consumed.clear()
