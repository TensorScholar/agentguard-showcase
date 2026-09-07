"""Canonical arguments digest.

The digest is the binding between an authorization decision and the exact
arguments that were authorized. Any post-authorization mutation of arguments
must change the digest and therefore fail revalidation at the execution gate.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def arguments_digest(arguments: dict[str, Any]) -> str:
    payload = canonical_json(arguments).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
