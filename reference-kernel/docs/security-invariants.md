# Security invariants — AgentGuard reference kernel

## What is protected

On a *protected path*, three things must be identical:

1. The action the policy authorized (bound in a signed decision receipt).
2. The credential issued from that receipt (audience, ceiling, TTL dominated by the receipt).
3. The payload that reaches the executor (live arguments digest equals receipt digest).

If any check fails, the path fails closed with a stable reason code and the executor is not invoked.

## Against what attack

| Attack | Protected? | Mechanism | Residual |
|--------|------------|-----------|----------|
| Post-authorization argument mutation | Yes (this kernel) | Arguments digest revalidation | Compromised signing key |
| Replay of a consumed receipt | Yes, single-host in-memory | Consumption record | Store rollback / multi-writer |
| Credential ceiling widening | Yes | Credential vs receipt domination | Attacker who also has signing secret |
| Direct bypass of the execution gate | **No** | Out of scope of this kernel | Must be a deployment property |
| Prompt injection as a class | **No** | Policy may still authorize an injected but allowable proposal | Provenance `require_approval` is a mitigation, not a proof |
| Host sandbox escape | **No** | Out of scope | — |

## Why the digest invariant holds (in this kernel)

The receipt stores `SHA-256(canonical_json(arguments))`. Execution recomputes the digest over the live arguments with the same canonicalization. Canonical JSON sorts keys and uses separators `(',', ':')`, so semantically identical objects hash equally and any field mutation hashes differently. The executor is invoked only after this comparison succeeds.

This argument is local to the kernel. It is not a proof about the private production core, and it is not a proof against an attacker who can replace the digest function or the execution gate itself.
