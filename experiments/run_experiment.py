#!/usr/bin/env python3
"""Root experiment entry point — delegates to the canonical kernel suite.

The canonical runner lives at reference-kernel/experiments/run_experiment.py
(next to the kernel it validates, and referenced by evidence/manifest.json).
This shim exists so `python experiments/run_experiment.py` works from the
repository root like every other showcase. There is exactly one suite and
one results.json (reference-kernel/experiments/results.json).
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "reference-kernel" / "experiments" / "run_experiment.py"


def main() -> int:
    sys.argv = [str(CANONICAL), *sys.argv[1:]]
    runpy.run_path(str(CANONICAL), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
