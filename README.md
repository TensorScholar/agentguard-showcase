# AgentGuard

## Runtime Authorization Infrastructure for AI Agents

AI agents are moving from conversations into real systems.

They can now:
- issue refunds
- access private data
- call external APIs
- modify business systems
- trigger real-world side effects

But model output is not a security boundary.

An agent can produce a valid-looking action while:
- instructions are manipulated,
- arguments are mutated,
- credentials exceed intended scope,
- previously approved actions are replayed,
- external execution diverges from authorization.

AgentGuard introduces a deterministic runtime authorization layer that enforces:

**Authorized action = Credential-bound action = Executed action**

---

# The Problem

Traditional AI safety approaches focus on model behavior:

```text
User
|
v
LLM
|
v
Tool Call
|
v
External System
```

Traditional AI systems often lack a deterministic execution-time authorization boundary.

Once an agent receives permission to call tools, the system must answer:

- Was this exact action authorized?
- Was this credential intended for this action?
- Did execution match the approved request?
- Can this action be replayed?
- Can evidence be verified later?

---

# The AgentGuard Model

AgentGuard enforces controls at the execution boundary:

```text
             AI Agent

                |
                v

         Action Intent

                |
                v

    +-----------------------+
    |   AgentGuard Runtime  |
    |                       |
    | Authorization         |
    | Credential Binding    |
    | Execution Verification|
    +-----------------------+

                |
                v

      External Tool Execution

                |
                v

        Evidence & Audit
```

---

# Core Security Properties

## Deterministic Authorization

Authorization decisions are explicit, reproducible, and independent from probabilistic model behavior.

---

## Credential Bound Execution

Credentials are constrained by the authorized action scope.

A valid credential is not enough.

It must match:

- intended action
- allowed scope
- execution context

---

## Execution-Time Verification

On protected execution paths, AgentGuard verifies that:

```text
Requested Action
==
Authorized Action
==
Executed Action
```

before dispatching external execution.

---

## Replay Prevention

Previously consumed authorization decisions are invalidated on protected paths; reuse attempts are deterministically rejected.

---

## Evidence Integrity

On protected paths, AgentGuard can record verifiable evidence:

- decision records
- execution results
- integrity metadata

Core CLI commands include `evidence-build` and `evidence-verify`. This showcase does not treat evidence packaging as a separate attack demo.

---

# Attack Demonstrations

These demonstrations are executable in this repository. Results come from AgentGuard `0.2.0rc3`, not from mocked PASS output.

## 1. Argument Mutation Attack

[demo/refund-agent](demo/refund-agent)

A support agent is authorized to issue:

```text
Refund: $85
```

After authorization, execution arguments are changed to:

```text
Refund: $850
```

AgentGuard rejects the mutated intent with:

```text
execution.arguments_digest_mismatch
```

This is execution-authority verification. The demo does not contact a payment processor.

---

## 2. Replay Attack

[demo/replay-prevention](demo/replay-prevention)

A previously consumed decision receipt is presented again on the protected execution path.

AgentGuard rejects reuse with:

```text
decision_receipt.replayed
```

`verify-execution` is a non-consuming preflight. Replay is enforced when the protected path claims the receipt.

---

## 3. MCP Unmediated Route

[demo/mcp-security](demo/mcp-security)

AgentGuard posture audits detect client configurations where tools can bypass a protected proxy, including a parallel direct route to the same downstream.

Observed reasons include:

```text
mcp.agentguard_proxy_enforced
mcp.direct_connection_bypasses_agentguard
mcp.parallel_direct_bypass
```

This audits supplied MCP configuration. It does not make arbitrary MCP servers invulnerable.

Credential scope inflation (`credential.scope_exceeds_decision`) is validated in AgentGuard core (`agentguard demo`) and is not a separate showcase runner.

---

# Why Runtime Authorization?

Existing layers solve different problems:

| Layer | Purpose |
|---|---|
| Guardrails | Reduce unsafe model outputs |
| Prompt filtering | Detect malicious instructions |
| Policy engines | Define permissions |
| AgentGuard | Enforce authorized execution on protected paths |

AI agents need security controls at the moment where actions create external impact.

---

# Architecture

AgentGuard separates:

```text
Intent
|
Authorization
|
Credential Authority
|
Execution
|
Evidence
```

The authorization path remains deterministic and auditable.

See [docs/architecture.md](docs/architecture.md), [docs/threat-model.md](docs/threat-model.md), [docs/security-properties.md](docs/security-properties.md), and [docs/design-decisions.md](docs/design-decisions.md).

---

# Core Implementation

The complete implementation is maintained in the primary repository (private):

- [AgentGuard Core Repository](https://github.com/TensorScholar/agentguard)

This showcase is a **consumer** of that core. It does not vendor the engine.

---

# Demo

Requires a local AgentGuard install (sibling checkout or `AGENTGUARD`). PyPI `pip install agentguard` is not assumed.

```bash
./scripts/bootstrap.sh --install   # optional, sibling core required
./run_demo.sh
```

| Demo | Observable |
|---|---|
| [demo/refund-agent](demo/refund-agent) | `execution.arguments_digest_mismatch` |
| [demo/replay-prevention](demo/replay-prevention) | `decision_receipt.replayed` |
| [demo/mcp-security](demo/mcp-security) | MCP bypass reasons, non-zero exit |

Setup and expected results: [docs/demo-guide.md](docs/demo-guide.md).

---

# Project Status

Engineering-validated against AgentGuard `0.2.0rc3`:

- Runtime authorization
- Credential binding
- Execution verification
- Replay prevention on the protected path
- MCP posture / bypass detection
- Evidence generation in core CLI

This is not a production-certification claim. 

---

# Design Philosophy

AgentGuard follows one principle:

> AI agents can be intelligent, but security boundaries must be deterministic.

Probabilistic intelligence still requires deterministic enforcement at the moment an action would take effect.
