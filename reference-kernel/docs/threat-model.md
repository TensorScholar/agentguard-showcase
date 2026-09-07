# Threat model — reference kernel

Scope: this educational kernel only. See also `docs/threat-model.md` at the showcase root for the private-core framing.

## Assets

- Binding between authorized arguments and executed arguments
- Single-use of a decision receipt
- Domination of credential ceilings by the receipt

## Adversaries in scope

- A component that can mutate arguments after receipt issuance but cannot forge HMAC signatures
- A component that can re-present a previously used receipt on the same ReplayStore
- A component that can construct a credential object with a widened ceiling and obtain a signature under the same educational secret (this last case is included to show *domination checks still fire even if the signature verifies*)

## Adversaries out of scope

- Compromise of the HMAC secret
- Replacement of the execution gate
- Hidden routes that never enter `execute_protected`
- Multi-process races on ReplayStore
- Timing side channels

## Assumptions that, if false, invalidate the demonstrations

1. All protected side effects go through `execute_protected`.
2. Canonical JSON is used on both authorize and execute.
3. ReplayStore is the same instance for both presentations.
4. The educational HMAC secret is not available to the attacker *except* in the credential-widening demo, which signs the forged credential deliberately to isolate the domination check.
