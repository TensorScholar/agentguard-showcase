# LinkedIn Featured — AgentGuard

**Title**  
AgentGuard: when an AI agent is allowed to act, how do you keep the dispatched action bound to the action that was actually authorized?

**Description**  
Runtime execution-integrity boundary that treats the model as an untrusted proposer. Public evidence demonstrates post-authorization argument mutation rejection, decision-receipt replay prevention, and MCP bypass detection. Includes a small public reference kernel implementing the core digests, receipts, and execution gate so reviewers can inspect the invariant directly.

**Suggested post structure**  
1. Operational failure mode (authorize $85, execute $850).  
2. The invariant (authorized = credentialed = executed).  
3. Retained evidence + maturity level.  
4. Explicit non-claims.  
5. Link to the reference repository and reference kernel.
