# Attack taxonomy — AgentGuard reference kernel

Scope: the public reference kernel only. Private-core attack surface
(MCP posture, SQLite durability, multi-process races) is described in
`docs/threat-model.md` at the showcase root and is **not** re-claimed here.

## Taxonomy

| # | Class | Demonstration | Expected control-plane response | Residual risk |
|---|-------|---------------|---------------------------------|---------------|
| 1 | Post-authorization argument mutation | `attacks/argument_mutation.py` + `fixtures/argument_mutation.json` | `execution.arguments_digest_mismatch`; executor never called | Attacker with signing secret can issue a fresh receipt for the mutated arguments |
| 2 | Replay of a consumed receipt | `attacks/replay_attack.py` | first use allowed, second `decision_receipt.replayed`; executor called exactly once | Store rollback / multi-writer races; process restart wipes in-memory store |
| 3 | Credential mismatch (ceiling widening) | `attacks/credential_mismatch.py` | `credential.ceiling_exceeds_receipt` | Attacker with signing secret still cannot exceed the *receipt* ceiling, but can mint equal-ceiling credentials — receipts must therefore stay narrow |
| 4 | Stale authorization (expired receipt) | `attacks/stale_authorization.py` | `execution.receipt_expired` before digest/consumption | Trustworthy local time assumed; clock control is out of scope |
| 5 | Privilege escalation (action/audience widening) | `attacks/privilege_escalation.py` | `policy.unknown_action` at policy layer; `credential.audience_mismatch` at gate | No PKI/audience registry in kernel; deployment must mediate routes (see rejected-designs.md) |
| 6 | Prompt-injection boundary case | `attacks/prompt_injection_scenario.py` | over-ceiling injected proposal denied; untrusted-provenance high-impact proposal → `require_approval`; post-auth mutation → digest mismatch | **Injection as a class is NOT detected or solved.** An injected proposal that is itself policy-allowable will be authorized. The kernel binds authorization to execution; it is not a prompt firewall |

## What this taxonomy explicitly does NOT cover

- Compromise of the HMAC secret (kernel uses HMAC for pedagogy; production needs asymmetric signatures + HSM).
- Replacement of the execution gate or hidden routes that never enter `execute_protected`.
- Host sandbox escape, timing side channels, multi-process races on `ReplayStore`.
- Semantic judgment of *whether* a policy-allowable proposal was attacker-influenced.

## Reading guide for reviewers

Start with scenario 6 if you care about prompt injection: it is a
three-case boundary demonstration (deny / escalate / bind), and its
fixture (`fixtures/prompt_injection_boundary.json`) states the expected
effect of each case. The honest summary is: provenance requirement +
approval escalation + digest binding. Detection of injection itself is
out of scope and unclaimed.
