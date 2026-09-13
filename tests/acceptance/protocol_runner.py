"""Deliberate process fixture for exercising the acceptance supervisor."""

import json
import os
from pathlib import Path
import signal
import sys
import time

MODES = {
    "pass",
    "mismatch",
    "missing_receipt",
    "wrong_identity",
    "mixed_error",
    "crash",
    "import",
    "signal",
    "timeout",
    "output",
    "semantic",
}


def main() -> int:
    """Emit valid or deliberately defective evidence selected by arguments."""
    phase = os.environ["WCT_ACCEPT_PHASE"]
    mode = sys.argv[1] if phase == "baseline" else sys.argv[2]
    if mode not in MODES:
        print("unknown runner fixture mode", file=sys.stderr)
        return 2
    ir = json.loads(Path(os.environ["WCT_ACCEPT_IR"]).read_text())
    if mode == "missing_receipt":
        return 1
    if mode == "crash":
        raise RuntimeError("deliberate runner crash")
    if mode == "import":
        __import__("wct_deliberately_absent_acceptance_fixture")
    if mode == "signal":
        os.kill(os.getpid(), signal.SIGTERM)
    if mode == "timeout":
        time.sleep(60)
    if mode == "output":
        os.write(1, b"x" * (2 * 1024 * 1024))
    if mode == "semantic":
        mode = "pass" if ir["scenarios"][0]["examples"][0]["value"] == "2" else "mismatch"
    status = "mismatch" if mode in {"mismatch", "mixed_error"} else "pass"
    code = 1 if status == "mismatch" else 0
    receipt = {
        "schema_version": 1,
        "attempt_id": "old" if mode == "wrong_identity" else os.environ["WCT_ACCEPT_ATTEMPT_ID"],
        "ir_sha256": os.environ["WCT_ACCEPT_IR_SHA256"],
        "exit": code,
        "cases": [{"scenario": index, "status": status} for index in range(len(ir["scenarios"]))],
        "errors": ["deliberate teardown error"] if mode == "mixed_error" else [],
    }
    Path(os.environ["WCT_ACCEPT_RECEIPT"]).write_text(json.dumps(receipt))
    return code


if __name__ == "__main__":
    sys.exit(main())
