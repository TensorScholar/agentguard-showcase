# Demonstrations

Three executable demonstrations. Every PASS/DENY comes from AgentGuard, not from hard-coded success text.

| Demo | Attack | Observable |
|---|---|---|
| [refund-agent](refund-agent) | Post-authorization $85 → $850 | `execution.arguments_digest_mismatch` |
| [replay-prevention](replay-prevention) | Reuse consumed receipt | `decision_receipt.replayed` |
| [mcp-security](mcp-security) | Unmediated / parallel MCP route | `mcp.direct_connection_bypasses_agentguard`, `mcp.parallel_direct_bypass` |

Run all three:

```bash
./run_demo.sh
```
