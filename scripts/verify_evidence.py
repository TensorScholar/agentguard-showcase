#!/usr/bin/env python3
"""Verify integrity of the public evidence package (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "manifest.json"
CLAIMS = ROOT / "evidence" / "claims.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not MANIFEST.exists() or not CLAIMS.exists():
        fail("missing evidence manifest or claim ledger")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))

    artifacts = manifest.get("artifacts", {})
    if not artifacts:
        fail("manifest contains no artifacts")

    for rel, expected in artifacts.items():
        p = ROOT / rel
        if not p.is_file():
            fail(f"missing artifact: {rel}")
        if not expected or expected == "PLACEHOLDER_DIGEST" or len(expected) != 64:
            fail(f"placeholder or invalid digest for artifact: {rel}")
        try:
            int(expected, 16)
        except ValueError:
            fail(f"non-hexadecimal digest for artifact: {rel}")
        actual = digest(p)
        if actual != expected:
            fail(f"digest mismatch for {rel}: expected {expected}, got {actual}")

    ids = set()
    for claim in claims.get("claims", []):
        cid = claim.get("id")
        if not cid or cid in ids:
            fail(f"missing/duplicate claim id: {cid!r}")
        ids.add(cid)
        for field in ("statement", "evidence_maturity", "scope", "falsification_condition"):
            if not claim.get(field):
                fail(f"{cid}: missing {field}")
        if claim.get("hero") and claim.get("evidence_maturity") in {"L0", "Conceptual"}:
            fail(f"{cid}: conceptual claim cannot be hero evidence")

    forbidden = ("TODO", "TBD", "CHANGEME", "INSERT RESULT", "PLACEHOLDER_DIGEST")
    for rel in ("README.md", "evidence/claims.json", "evidence/results.json", "evidence/manifest.json"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                fail(f"placeholder token {token!r} in {rel}")

    print(
        f"PASS: {manifest.get('project', 'unknown')} evidence integrity "
        f"({len(claims.get('claims', []))} claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
