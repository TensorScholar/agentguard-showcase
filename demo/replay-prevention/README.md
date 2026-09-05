# Replay prevention

A signed decision receipt is not a reusable ticket. After the protected execution path **claims** the receipt, a second use of the same authorization is rejected.

`agentguard verify-execution` is a **non-consuming preflight**. Replay is enforced when AgentGuard reserves the decision nonce during protected execution (`reserve_execution` / `execute_protected`).

## What this demo does

1. `init`, `authorize`, and `broker-demo` create real authorization material (same $85 refund intent as the hero demo).
2. `verify-execution` is run once to show that preflight does **not** consume the receipt.
3. A thin showcase consumer calls AgentGuard `execute_protected`:
   - first use: protected execution authority is claimed
   - second use: AgentGuard raises `decision_receipt.replayed`
4. The script exits 0 only when that reason code is observed.

The consumer uses AgentGuard's `DeterministicFakeExecutor`. No payment processor is contacted.

## Why a small Python consumer exists

The current AgentGuard CLI exposes:

- `verify-execution` — preflight, nonce not consumed
- `mcp-proxy-v2` / HTTP gateway — protected execution for live MCP traffic
- `demo` — bundled meeting scenario that also consumes internally

This showcase keeps the MCP demo focused on posture auditing, so replay is exercised through the same protected-execution service the CLI and adapters use, rather than by wrapping `agentguard demo`.

## Run

```bash
./run.sh
```

Preserve generated receipts and ledger:

```bash
./run.sh --keep-workspace
```

## Expected result

```text
FIRST USE
  protected execution status: success

SECOND USE OF THE SAME RECEIPT
  rejected: decision_receipt.replayed
```
