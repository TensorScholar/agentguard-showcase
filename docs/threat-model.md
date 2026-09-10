# Threat model

This document describes threats the **current AgentGuard reference repository can demonstrate**, and risks that remain out of scope. Claims are bounded to traffic and configuration that actually enter AgentGuard.

## In scope: demonstrated on protected paths

### Post-authorization argument mutation

An $85 refund is authorized. Tool arguments are later changed to $850.

- Control: canonical `arguments_digest` on the decision receipt, rechecked at execution verification
- Observable: `execution.arguments_digest_mismatch`
- Demo: [`demos/refund-agent`](../demos/refund-agent)

### Decision-receipt replay

A consumed authorization is presented again on the protected execution path.

- Control: durable nonce reservation in AgentGuard state
- Observable: `decision_receipt.replayed`
- Demo: [`demos/replay-prevention`](../demos/replay-prevention)

### MCP unmediated / parallel bypass configuration

A client config includes a direct launch of the same downstream server that a proxy already mediates.

- Control: `mcp-posture --fail-on-bypass`
- Observables: `mcp.direct_connection_bypasses_agentguard`, `mcp.parallel_direct_bypass`, non-zero exit
- Demo: [`demos/mcp-security`](../demos/mcp-security)

### Credential scope exceeding decision authority

Core AgentGuard rejects a grant whose scopes exceed the signed ceiling (`credential.scope_exceeds_decision`). That path is exercised by `agentguard demo` in the core package. It is **not** a separate demonstration runner in this repository.

## Trust boundary

```text
Untrusted:  agent, model, prompts, mutated arguments, extra MCP routes
Enforced:   policy, receipt, grant ceiling, digest compare, nonce consume, posture scan
Assumed:    OS, signing keys, adapter identity labels, downstream provider honesty
```

## Out of scope

These are not solved by installing or running this reference repository:

| Risk | Why it is out of scope |
|---|---|
| Fully compromised host OS | Kernel, memory, and process control sit below AgentGuard |
| Stolen or malicious signing keys | Receipts are only as trustworthy as the key boundary |
| Actions that never enter AgentGuard | Uninstrumented executors bypass the kernel entirely |
| Hidden MCP/network routes not in the scanned file | `mcp-posture` audits supplied configuration, not the whole host |
| Malicious model weights by themselves | The model is an untrusted proposer; enforcement is at execution |
| Social engineering outside the protected path | Humans and out-of-band approvals are not this boundary |
| Malicious external systems after verified dispatch | AgentGuard binds what it sends; it does not vouch for provider business truth |
| Prompt injection as a complete class | Argument mutation after authorization is demonstrated; natural-language injection is not “solved” |
| Production certification | `0.2.0rc3` is an engineering-validated release candidate |

## Residual risk

Even on a correctly integrated path, AgentGuard cannot prove that another process did not call the same provider directly. Deployment isolation, identity, secret managers, and network policy remain necessary complementary controls.
