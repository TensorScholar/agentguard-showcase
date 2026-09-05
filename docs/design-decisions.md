# Design decisions

These decisions explain why AgentGuard looks like a runtime authorization kernel rather than a chatbot filter.

## Deterministic enforcement vs generative authorization

Language models are probabilistic. Authorization for refunds, exports, and production mutations cannot be “the model said it was OK.”

AgentGuard keeps policy evaluation, receipt verification, digest comparison, and nonce reservation **out of the model loop**. The model may propose an `ActionIntent`. The kernel accepts or rejects it with stable reason codes.

## Authorization and execution are separate

Issuing a decision receipt is not the same as performing the action.

- `authorize` records what was allowed.
- `verify-execution` checks that a later intent still matches, without consuming the receipt.
- Protected execution claims the nonce and is the only step that should precede side effects.

That split is why an $85 receipt cannot authorize an $850 call, and why a preflight success is not a license to retry forever.

## Credential / action binding

A valid-looking credential is insufficient if it is wider than the decision. Grants are checked against the signed ceiling (`audience`, `scopes`, `tenant`, `TTL`). The showcase uses `broker-demo` to exhibit binding without pretending to be HashiCorp Vault or a cloud IAM service.

## Replay-safe decision state

Authorization material is treated as **single-use on the protected path** unless a future core contract explicitly says otherwise. Local SQLite reservation makes “retry the same receipt” a deterministic deny (`decision_receipt.replayed`) instead of a duplicate refund.

This is not a claim about every possible queue, browser tab, or uninstrumented replica.

## Model output is not an authorization boundary

Prompt filtering and guardrails reduce some unsafe text. They do not bind the bytes that later hit a payments API.

AgentGuard’s boundary is the structured action: tool, resource, arguments, effects, principal, policy digest. If those bytes change after signing, execution verification fails.

## Complements, not replacements

| Layer | What it owns | What it does not own |
|---|---|---|
| Guardrails / prompt filters | Natural-language risk reduction | Exact tool-argument integrity |
| IAM / workload identity | Who the caller is | Whether this exact refund was authorized |
| Policy engines | Permission design | Cryptographic binding + replay at execute time |
| Secret vaults | Long-term secret storage | Decision-scoped late use of those secrets |
| AgentGuard | Authorized = bound = executed on protected paths | Host isolation, model alignment, provider honesty |

Do not read these as a numbered industry-standard stack. They are adjacent jobs. AgentGuard is the runtime action-integrity job.
