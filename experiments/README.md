# Experiments — AgentGuard

The canonical 6-scenario adversarial suite lives with the kernel it
validates: [`reference-kernel/experiments/`](../reference-kernel/experiments/)
(runner, deterministic `fixtures/`, `results.json`, `interpretation.md`).

## Run (repository root)

```
python experiments/run_experiment.py
```

This file delegates to the canonical runner; there is one suite and one
`results.json` (`reference-kernel/experiments/results.json`). See
[`reference-kernel/experiments/README.md`](../reference-kernel/experiments/README.md)
for the scenario list and result schema.
