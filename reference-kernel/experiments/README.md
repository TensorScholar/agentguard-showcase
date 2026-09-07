# Experiments — AgentGuard reference kernel

Deterministic adversarial demonstrations. Validates the public reference
kernel only (L2). Does not prove private-core behavior.

## Run

From `reference-kernel/`:

```
python experiments/run_experiment.py
python experiments/run_experiment.py --fixtures fixtures --out experiments/results.json
```

Tests:

```
python -m pytest tests/ -q
```

## Layout

- `run_experiment.py` — deterministic runner (stdlib only, no network).
- `../fixtures/*.json` — deterministic preconditions per scenario.
- `results.json` — machine-readable output (regenerated on each run).
- `interpretation.md` — what PASS/FAIL means and what is NOT claimed.

## Result schema

Every entry in `results.json` carries:

```
scenario, threat, configuration, fixture,
expected_behavior, observed_behavior,
pass, evidence_level, limitations
```

## Scenarios (6)

1. `argument_mutation` — digest mismatch blocks mutated execution.
2. `replay_attack` — second presentation of a consumed receipt blocked.
3. `credential_mismatch` — widened credential ceiling rejected.
4. `stale_authorization` — expired receipt rejected before digest/consumption.
5. `privilege_escalation_attempt` — escalated action denied; forged audience rejected.
6. `prompt_injection_scenario` — boundary case: deny / escalate-to-approval / digest-bind. Injection NOT claimed solved.
