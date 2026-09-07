# Rejected designs — AgentGuard reference kernel

Records alternatives that were considered and deliberately not taken, so
reviewers can see the judgment, not just the outcome.

## 1. Capability-only tokens (no receipt binding) — REJECTED

Proposal: issue bearer credentials at policy time; executor trusts any
validly signed credential.

Rejected because: a bearer credential cannot distinguish "authorized for
these exact arguments" from "authorized for this ceiling." Post-authorization
mutation becomes undetectable. The receipt's arguments-digest binding exists
specifically to close this gap. Cost accepted: every protected execution
pays one digest recomputation + one signature verification.

## 2. Expiry-only replay protection (no consumption record) — REJECTED

Proposal: rely on short TTLs instead of single-use consumption.

Rejected because: within the TTL window a receipt is freely replayable.
For irreversible financial effects, "replayable for 60 seconds" is a
double-spend primitive. Consumption records are the actual mechanism;
expiry is defense in depth (scenario 4 proves expiry fires independently).

## 3. Credential ceilings independent of receipts — REJECTED

Proposal: let credentials carry their own ceilings, verified by signature alone.

Rejected because: any signer (or key compromise) can then mint arbitrary
authority. Domination (credential ≤ receipt on audience, ceiling, TTL) means
a leaked credential-signer still cannot exceed the narrowest authorizing
receipt. Cost accepted: credential issuance must reference a live receipt.

## 4. Prompt-content firewall as the injection defense — REJECTED

Proposal: scan tool arguments / prompts for injection patterns and block matches.

Rejected because: pattern matching over adversarial text is an arms race with
false negatives that fail open and false positives that break legitimate
workflows. The kernel instead enforces a boundary it *can* hold: untrusted
provenance escalates high-impact proposals to approval, and digest binding
makes post-authorization mutation unexecutable. Injection detection itself is
explicitly unclaimed (see attack-taxonomy.md class 6).

## 5. Asymmetric signatures in the reference kernel — DEFERRED, not rejected

Ed25519 + key rotation is the right production shape and is documented as
the migration path. HMAC-SHA256 stays in the *reference* kernel because it
is verifiable with stdlib only (`hmac`, `hashlib`), keeping `make verify`
dependency-free. The tradeoff is stated wherever signatures appear: the
kernel demonstrates binding logic, not key management.
