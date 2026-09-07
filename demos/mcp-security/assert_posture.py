#!/usr/bin/env python3
"""Assert AgentGuard mcp-posture JSON against expected route status/reasons."""

from __future__ import annotations

import json
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: assert_posture.py <protected|bypass>", file=sys.stderr)
        return 2
    mode = sys.argv[1]
    report = json.load(sys.stdin)
    routes = report.get("routes") or []
    reasons = [code for route in routes for code in route.get("reason_codes") or []]
    statuses = [route.get("status") for route in routes]

    if mode == "protected":
        if report.get("protected_count") != 1 or report.get("direct_count") != 0:
            print(f"unexpected protected counts: {report}", file=sys.stderr)
            return 1
        if statuses != ["protected"]:
            print(f"unexpected statuses: {statuses}", file=sys.stderr)
            return 1
        if "mcp.agentguard_proxy_enforced" not in reasons:
            print(f"missing mcp.agentguard_proxy_enforced in {reasons}", file=sys.stderr)
            return 1
        return 0

    if mode == "bypass":
        if report.get("direct_count", 0) < 1:
            print(f"expected a direct route: {report}", file=sys.stderr)
            return 1
        if "mcp.direct_connection_bypasses_agentguard" not in reasons:
            print(f"missing mcp.direct_connection_bypasses_agentguard in {reasons}", file=sys.stderr)
            return 1
        if "mcp.parallel_direct_bypass" not in reasons:
            print(f"missing mcp.parallel_direct_bypass in {reasons}", file=sys.stderr)
            return 1
        return 0

    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
