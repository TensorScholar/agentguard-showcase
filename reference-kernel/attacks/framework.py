"""Adversarial scenario framework for the AgentGuard reference kernel.

Each scenario is a deterministic, fixture-driven attack demonstration:

- A scenario declares its threat, preconditions, and expected blocking
  reason code(s) up front.
- ``run()`` executes against the educational kernel and returns a
  machine-readable ``ScenarioResult``.
- The experiment runner serializes results with the portfolio-wide schema:
  scenario, configuration, expected_behavior, observed_behavior,
  evidence_level, limitations.

This is a *demonstration* framework, not a red-team harness: it shows that
the kernel's checks fire on known attack shapes. It cannot prove the
absence of bypasses (see docs/attack-taxonomy.md and rejected-designs.md).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

EVIDENCE_LEVEL = "L2"
LIMITATIONS = [
    "Validates the public reference kernel only, not the private core.",
    "HMAC-SHA256 signatures and in-memory replay store are pedagogical.",
    "Assumes all protected side effects go through execute_protected.",
]


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    threat: str
    blocked: bool
    reason_code: str
    executor_calls: int
    expected_reason_codes: tuple[str, ...] = ()
    notes: str = ""


@dataclass
class ScenarioSpec:
    name: str
    threat: str
    expected_reason_codes: tuple[str, ...]
    run: Callable[[], ScenarioResult]
    fixtures: dict = field(default_factory=dict)


REGISTRY: dict[str, ScenarioSpec] = {}


def register(spec: ScenarioSpec) -> ScenarioSpec:
    REGISTRY[spec.name] = spec
    return spec


def load_fixtures(fixture_dir: Path) -> dict[str, dict]:
    """Load deterministic JSON fixtures; missing dir yields {} (no crash)."""
    out: dict[str, dict] = {}
    if not fixture_dir.is_dir():
        return out
    for p in sorted(fixture_dir.glob("*.json")):
        out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return out


def to_record(
    result: ScenarioResult,
    *,
    configuration: str,
    expected_behavior: str,
) -> dict:
    return {
        "scenario": result.name,
        "threat": result.threat,
        "configuration": configuration,
        "expected_behavior": expected_behavior,
        "expected_reason_codes": list(result.expected_reason_codes),
        "observed_behavior": {
            "blocked": result.blocked,
            "reason_code": result.reason_code,
            "executor_calls": result.executor_calls,
            "notes": result.notes,
        },
        "pass": bool(result.blocked),
        "evidence_level": EVIDENCE_LEVEL,
        "limitations": list(LIMITATIONS),
    }


def as_json_record(result: ScenarioResult, **kw) -> dict:
    return to_record(result, **kw)


def dump_records(records: list[dict]) -> dict:
    return {
        "project": "AgentGuard",
        "artifact": "reference-kernel",
        "evidence_maturity": EVIDENCE_LEVEL,
        "note": "Validates the public reference kernel only. Does not prove private-core production behavior.",
        "results": records,
        "all_pass": all(r["pass"] for r in records),
    }
