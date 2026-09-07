# Interpretation — AgentGuard experiment results

## What `all_pass: true` means

All six attack demonstrations were blocked (or escalated, for the
untrusted-provenance injection case) with the expected stable reason
codes, and the executor was invoked only where specified (exactly once
for the first replay presentation, never for attacks).

Concretely: the kernel's check ordering — signature → expiry → digest →
credential domination → single-use consumption → executor — held on every
demonstrated shape.

## What it does NOT mean

- Not a proof of private-core behavior. The private core has its own
  SQLite store, MCP posture auditing, and UNKNOWN reconciliation; none of
  that is exercised here.
- Not a prompt-injection solution. Scenario 6 shows the *boundary*:
  deny over-ceiling proposals, require approval for untrusted-provenance
  high-impact proposals, bind execution to authorized arguments. An
  injected proposal that is itself policy-allowable will still be
  authorized — that is stated in the payload note and in
  `docs/attack-taxonomy.md`.
- Not deployment certification. HMAC secret management, route mediation
  (all side effects through the gate), clock trust, and store durability
  are assumptions listed in `docs/threat-model.md`. If any is false, the
  demonstrations do not transfer.

## How to challenge this

1. Mutate a fixture (e.g. raise `max_amount_minor` past the receipt
   ceiling) and confirm the runner reports `pass: false` for that
   scenario — the harness is sensitive, not tautological.
2. Present a seventh attack shape (e.g. receipt for action A presented
   with action B at the gate) and check whether the kernel binds it.
   If it does not, that is a finding — file it; the taxonomy is meant
   to grow.
3. Ask for the private-core walkthrough: crash-recovery of the
   consumption store and MCP bypass fixtures are the next validation
   steps (see `docs/validation-roadmap.md`).
