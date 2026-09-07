# Changelog — AgentGuard showcase

## v4 (2026-09-07) — standalone public repository

- Adversarial scenario framework: 6 scenarios (argument mutation, replay,
  credential mismatch, stale authorization, privilege escalation,
  prompt-injection boundary) with deterministic fixtures and
  machine-readable results.
- `prompt_injection_solved: false` stated in machine-readable output.
  Prompt injection is not claimed solved.
- Thread-safe in-memory replay store (+ concurrency test). Crash safety and
  multi-process use remain explicitly out of scope.
- Docs: attack taxonomy, rejected designs, operational lessons, tradeoffs.
- Standalone repo layout: `make verify`, CI workflow, LICENSE, examples.

Evidence: reference-kernel results are L2 (publicly reproducible).
Private-core claims remain L1. No L3 claimed. No production users claimed.

## v3 — reference kernel + experiments

- Control-plane kernel (digest, receipt, policy, credential, executor
  boundary), 4 attack demos, experiment runner, evidence ledger.
