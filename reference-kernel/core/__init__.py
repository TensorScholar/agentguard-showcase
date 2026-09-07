"""AgentGuard reference kernel core.

Educational implementation of execution-integrity invariants.
Not a production security control.
"""

from .digest import arguments_digest, canonical_json
from .receipt import DecisionReceipt, make_receipt, sign_receipt, verify_receipt
from .replay import ReplayError, ReplayStore
from .policy import PolicyDecision, evaluate_policy
from .credential import Credential, issue_credential, verify_credential_against_receipt
from .executor_boundary import ExecutionResult, execute_protected

__all__ = [
    "arguments_digest",
    "canonical_json",
    "DecisionReceipt",
    "make_receipt",
    "sign_receipt",
    "verify_receipt",
    "ReplayError",
    "ReplayStore",
    "PolicyDecision",
    "evaluate_policy",
    "Credential",
    "issue_credential",
    "verify_credential_against_receipt",
    "ExecutionResult",
    "execute_protected",
]
