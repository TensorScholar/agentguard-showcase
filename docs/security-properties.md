# Security properties

Properties below are those this showcase **demonstrates** with AgentGuard `0.2.0rc3`. They apply on protected paths. They are not a general “AI is safe” guarantee.

## 1. Authorized arguments equal execution arguments

**Property.** On execution verification, `arguments_digest(live intent)` must equal `arguments_digest` stored on the signed decision receipt.

**Mechanism.** Canonical JSON digest of tool arguments is bound into the receipt at `authorize`. `verify-execution` / `validate_execution_authority` recomputes it.

**Demonstrated attack.** $85 authorized, $850 arguments submitted.

**Observable.** Non-zero CLI exit; `execution.arguments_digest_mismatch`.

**Limitation.** Only live intents that enter AgentGuard are compared. Fields other than arguments have their own digest checks (`action`, `effects`, `principal`, …). This demo mutates arguments only.

## 2. Credential authority does not exceed decision authority

**Property.** `Credential_Authority <= Decision_Authority` (audience, scopes, tenant, TTL ceiling).

**Mechanism.** Grant verification against the receipt `credential_ceiling`.

**Demonstrated attack.** Core `agentguard demo` inflates grant scopes and records `credential.scope_exceeds_decision`.

**Observable.** `credential.scope_exceeds_decision` (core meeting demo / tests). Not a separate folder in this repository.

**Limitation.** `broker-demo` is a development adapter. Production secret minting is a separate authority integration.

## 3. Consumed receipts are not reusable on the protected path

**Property.** After protected execution reserves a decision nonce, the same receipt is not accepted again.

**Mechanism.** Durable `reserve_execution` / consumed-nonce state.

**Demonstrated attack.** Second `execute_protected` with the same $85 receipt and grant.

**Observable.** `decision_receipt.replayed`. Executor call count remains 1.

**Limitation.** `verify-execution` does **not** consume the nonce. Replay is a protected-execution property, not a preflight property. State is local SQLite; it is not distributed consensus.

## 4. MCP configs with unmediated routes fail a bypass audit

**Property.** When `--fail-on-bypass` is set, a configuration that includes a direct route (including a parallel route to a proxied downstream) exits non-zero.

**Mechanism.** `mcp-posture` classifies `agentguard mcp-proxy … -- <downstream>` as protected and direct command/URL routes as unmediated.

**Demonstrated attack.** Protected proxy plus direct `python customer_operations_server.py` for the same downstream.

**Observables.** Exit 1; `mcp.direct_connection_bypasses_agentguard`; `mcp.parallel_direct_bypass`. Protected-only config exits 0 with `mcp.agentguard_proxy_enforced`.

**Limitation.** The scanner only sees files it is given. It does not make MCP servers invulnerable and cannot prove absence of hidden routes.

## What is not claimed

- Unhackable / 100% secure / production certified
- Solves prompt injection as a class
- Prevents every replay in every architecture
- Makes MCP secure
- Contacts a real payment processor in these demos
