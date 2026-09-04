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

Every protected execution produces verifiable evidence:

- decision records
- execution results
- integrity metadata

---

# Attack Demonstrations

## 1. Argument Mutation Attack

Scenario:

A support agent is authorized to issue:

```text
Refund: $85
```

An attacker attempts to mutate execution:

```text
Refund: $850
```

On the protected path, AgentGuard intercepts the action with:

```text
execution.arguments_digest_mismatch
```

before protected external execution dispatch occurs.

---

## 2. Credential Scope Inflation

A credential attempts to access permissions beyond the authorized boundary.

AgentGuard rejects the invocation with:

```text
credential.scope_exceeds_decision
```

---

## 3. Replay Attack

A previously approved action receipt is reused.

AgentGuard prevents execution and rejects with:

```text
decision_receipt.replayed
```

---

# MCP Security

Model Context Protocol (MCP) introduces new execution paths for AI agents.

AgentGuard posture audits detect configurations where tools can bypass protected execution boundaries.

Example:

```text
Agent
|
+---- Protected MCP Gateway
|
+---- Direct Unsafe Tool Route ❌
```

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

---

# Core Implementation

The complete implementation is maintained in the primary repository:

- [AgentGuard Core Repository](https://github.com/TensorScholar/agentguard)

---

# Demo

The showcase demonstrates:

- refund agent protection
- MCP security boundaries
- replay prevention
- credential scope enforcement

See:

- `demo/refund-agent`
- `demo/replay-prevention`
- `demo/mcp-security`

---

# Project Status

Current validated capabilities:

✅ Runtime authorization  
✅ Credential binding  
✅ Execution verification  
✅ MCP protection  
✅ Replay prevention  
✅ Evidence generation  
✅ Production-oriented validation workflow  

---

# Design Philosophy

AgentGuard follows one principle:

> AI agents can be intelligent, but security boundaries must be deterministic.


Probabilistic intelligence + Deterministic enforcement

Safer autonomous systems
