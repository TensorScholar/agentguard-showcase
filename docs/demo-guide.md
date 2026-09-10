# Demo guide

Audience: security engineers, platform engineers, technical interviewers, CTOs evaluating a design partnership.

These demonstrations consume a local AgentGuard core install. The core repository is maintained separately; a random GitHub visitor cannot always run this core-dependent suite without that sibling checkout.

## Prerequisites

- macOS or Linux
- Python 3.11+
- Access to the AgentGuard core checkout used with these demonstrations (validated baseline: `0.2.0rc3`)
- Sibling layout, or `AGENTGUARD` pointing at a working CLI

```text
<parent>/
  agentguard/              # core
  agentguard-reference/    # this repo (or any folder name)
```

Do not assume `pip install agentguard` from PyPI is this project.

## Setup

If the sibling core already has `.venv/bin/agentguard`, the demo scripts discover it.

Otherwise, from this repository:

```bash
./scripts/bootstrap.sh --install
export AGENTGUARD="$PWD/.venv/bin/agentguard"
```

`bootstrap.sh --install` creates a **repository-local** virtualenv and installs the sibling core in editable mode. It does not modify core source files.

Check:

```bash
./scripts/bootstrap.sh
```

## One-command run

```bash
./run_demo.sh
```

Expected summary when all three real demos succeed:

```text
AgentGuard Reference Demos

Refund mutation         PASS
Replay prevention       PASS
MCP bypass detection    PASS

Overall                 PASS
```

`PASS` is printed only if that demo process exited 0 after checking AgentGuard’s actual result.

Preserve generated workspaces:

```bash
./run_demo.sh --keep-workspace
```

Workspaces are created under `.showcase-workspaces/` (gitignored). On macOS, `/tmp` cannot be used because AgentGuard refuses symlink path components such as `/var`.

## Expected outcomes

### Refund mutation — `demos/refund-agent`

| Step | Expected |
|---|---|
| `authorize` $85 | `ALLOW` |
| `verify-execution` $85 | exit 0, “Execution authority verified; nonce not consumed” |
| `verify-execution` $850 | non-zero exit, `execution.arguments_digest_mismatch` |

This is execution-authority verification, not a live refund.

### Replay prevention — `demos/replay-prevention`

| Step | Expected |
|---|---|
| First `execute_protected` | `status: success` |
| Second use of the same receipt | `decision_receipt.replayed` |
| Fake executor calls | `1` |

### MCP posture — `demos/mcp-security`

| Config | Expected |
|---|---|
| `protected.json` | exit 0, `mcp.agentguard_proxy_enforced` |
| `bypass.json` | exit 1, `mcp.direct_connection_bypasses_agentguard`, `mcp.parallel_direct_bypass` |

## Run demos separately

```bash
./demos/refund-agent/run.sh
./demos/replay-prevention/run.sh
./demos/mcp-security/run.sh
```

## Inspecting generated state

```bash
./demos/refund-agent/run.sh --keep-workspace
```

Then inspect the printed workspace path for `receipt.json`, `grant.json`, and `audit.sqlite`. Do not commit those files. They include signing keys.

Core also ships `agentguard demo` and `evidence-verify` for a bundled meeting scenario; that is optional and not required for this repository’s runner.

## Troubleshooting

| Symptom | What to check |
|---|---|
| `AgentGuard CLI was not found` | Sibling checkout, `AGENTGUARD`, or `./scripts/bootstrap.sh --install` |
| `unsafe symlink component: /var` | Workspace is not under `/tmp`; current scripts use `.showcase-workspaces/` |
| Mutated refund unexpectedly `ALLOW` | Policy/request files changed; demo must fail closed |
| Replay reason is not `decision_receipt.replayed` | Preflight-only `verify-execution` does not consume; use the replay demo as written |
| MCP bypass exits 0 | Confirm `--fail-on-bypass` and that `bypass.json` still contains the direct route |
| Wrong package | A different PyPI project named similarly will not produce these reason codes |

These demos were validated on macOS with AgentGuard `0.2.0rc3`. Cross-platform compatibility is not claimed beyond that.
