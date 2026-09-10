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

AgentGuard demonstrates a deterministic execution-integrity boundary that binds authorized intent to bounded credential authority and admitted dispatch:

```text
Authorized Intent
    -> Bounded Credential Authority
    -> Admitted Dispatch
    -> Evidence-Bound Outcome
```

The protected boundary verifies that the dispatched normalized action remains bound to the authorization decision. It does not independently prove the final provider-side business effect. The public reference kernel models this boundary for educational inspection; it does not prove current core behavior.

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

On protected execution paths, AgentGuard verifies that the dispatched normalized action matches the authorization decision:

```text
Authorized Intent
    -> Bounded Credential Authority
    -> Admitted Dispatch
    -> Evidence-Bound Outcome
```

before dispatching external execution. The protected boundary verifies that the dispatched normalized action remains bound to the authorization decision; it does not independently prove the final provider-side business effect.

---

## Replay Prevention

Previously consumed authorization decisions are invalidated on protected paths; reuse attempts are deterministically rejected.

---

## Evidence Integrity

On protected paths, AgentGuard can record verifiable evidence:

- decision records
- execution results
- integrity metadata

Core CLI commands include `evidence-build` and `evidence-verify`. This reference repository does not treat evidence packaging as a separate attack demo.

---

# Public Reference Kernel

This repository contains a standalone, zero-dependency reference kernel located in [`reference-kernel/`](reference-kernel/):

- **Role**: Pedagogical and bounded reference implementation of the execution-integrity invariant.
- **Zero Dependencies**: Uses Python standard library only (`hashlib`, `hmac`, `json`, `threading`).
- **Independently Runnable**: Run tests and adversarial experiments directly without requiring the AgentGuard core:
  ```bash
  make verify
  # or directly:
  python3 experiments/run_experiment.py
  python3 -m pytest reference-kernel/tests/ -v
  ```
- **Evidence Maturity**: Public **L2 evidence** (publicly reproducible) in this repository applies strictly to this reference kernel.
- **Bounded Scope**: Demonstrates post-authorization argument mutation rejection, in-memory single-use replay detection, credential ceiling domination, stale authorization expiry, privilege escalation blocking, and the prompt-injection boundary. It uses illustrative HMAC signing and an in-memory replay store; it is not the production core.

See [`reference-kernel/README.md`](reference-kernel/README.md) and [`reference-kernel/docs/`](reference-kernel/docs/) for threat model, security invariants, attack taxonomy, and rejected designs.

---

# Core-Dependent Demonstration Harnesses

The `demos/` directory contains demonstration harnesses that evaluate the full AgentGuard core implementation (`TensorScholar/agentguard`):

- **Requirement**: Depends on a local sibling checkout or installed CLI of the AgentGuard core (`0.2.0rc3`).
- **Boundary**: These harnesses exercise core components (SQLite persistent state, Ed25519 cryptography, MCP posture scanner). They do not make the reference kernel equivalent to the core.
- **Historical Baseline**: Baseline evidence for these demonstrations remains pinned to historical core snapshot `8c3c69ea12e434e2223b7452654c23dece858d34` (`0.2.0rc3`).

## 1. Argument Mutation Attack

[demos/refund-agent](demos/refund-agent)

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

[demos/replay-prevention](demos/replay-prevention)

A previously consumed decision receipt is presented again on the protected execution path.

AgentGuard rejects reuse with:

```text
decision_receipt.replayed
```

`verify-execution` is a non-consuming preflight. Replay is enforced when the protected path claims the receipt.

---

## 3. MCP Unmediated Route

[demos/mcp-security](demos/mcp-security)

AgentGuard posture audits detect client configurations where tools can bypass a protected proxy, including a parallel direct route to the same downstream.

Observed reasons include:

```text
mcp.agentguard_proxy_enforced
mcp.direct_connection_bypasses_agentguard
mcp.parallel_direct_bypass
```

This audits supplied MCP configuration. It does not make arbitrary MCP servers invulnerable.

Credential scope inflation (`credential.scope_exceeds_decision`) is validated in AgentGuard core (`agentguard demo`) and is not a separate demonstration runner in this repository.

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

The complete implementation is maintained in the primary repository:

- [AgentGuard Core Repository](https://github.com/TensorScholar/agentguard)

This reference repository provides demonstration harnesses that consume that core and an independent reference kernel that models its invariant. It does not vendor the core engine.

---

# Running Demonstrations

Requires a local AgentGuard core install (sibling checkout or `AGENTGUARD`). PyPI `pip install agentguard` is not assumed.

```bash
./scripts/bootstrap.sh --install   # optional, sibling core required
./run_demo.sh
```

| Demo | Observable |
|---|---|
| [demos/refund-agent](demos/refund-agent) | `execution.arguments_digest_mismatch` |
| [demos/replay-prevention](demos/replay-prevention) | `decision_receipt.replayed` |
| [demos/mcp-security](demos/mcp-security) | MCP bypass reasons, non-zero exit |

Setup and expected results: [docs/demo-guide.md](docs/demo-guide.md).

---

# Project Status

Engineering-validated against AgentGuard core baseline `0.2.0rc3` (`8c3c69ea12e434e2223b7452654c23dece858d34`):

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
