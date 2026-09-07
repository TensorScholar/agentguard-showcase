# AgentGuard reference kernel

Educational implementation of the execution-integrity invariant.

```
reference-kernel/
  core/          digest, receipt, policy, credential, executor boundary, replay
  attacks/       framework + 6 scenarios: mutation, replay, credential
                 mismatch, stale authorization, privilege escalation,
                 prompt-injection boundary case
  fixtures/      deterministic JSON preconditions per scenario
  tests/         binding, replay, fail-closed, stale + escalation
  experiments/   run_experiment.py → results.json (+ README, interpretation)
  docs/          threat model, security invariants, attack taxonomy,
                 rejected designs
```

## Run

From this directory:

```
python -m pytest tests/ -q
python experiments/run_experiment.py
```

## What this is not

Not the production kernel. HMAC secrets, in-memory replay, and the policy language are illustrative. Passing these tests does not certify a deployment.
