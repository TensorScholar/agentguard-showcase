"""Adversarial scenarios against the execution-integrity invariant.

Each module attempts a known failure mode and reports whether the gate
held via the shared ``framework`` (ScenarioResult / registry / fixtures).

Required coverage (v4):
  1. argument_mutation
  2. replay_attack
  3. credential_mismatch
  4. stale_authorization
  5. privilege_escalation_attempt
  6. prompt_injection_scenario (boundary case — injection NOT claimed solved)

These are educational attack *demonstrations*, not a red-team framework.
See docs/attack-taxonomy.md for the taxonomy and what is out of scope.
"""

from . import (  # noqa: F401
    argument_mutation,
    credential_mismatch,
    framework,
    privilege_escalation,
    prompt_injection_scenario,
    replay_attack,
    stale_authorization,
)
from .framework import REGISTRY  # noqa: F401

REQUIRED_SCENARIOS = (
    "argument_mutation",
    "replay_attack",
    "credential_mismatch",
    "stale_authorization",
    "privilege_escalation_attempt",
    "prompt_injection_scenario",
)
