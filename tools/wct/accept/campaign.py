"""Baseline-first acceptance campaigns; raw failures never imply kills."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any
import uuid

from tools.wct.accept.mutation_cases import mutations
from tools.wct.accept.process import run_process
from tools.wct.accept.receipt import validate_receipt

ATTEMPT_SECONDS = 30.0
CAMPAIGN_SECONDS = 600.0


def _environment(directory: Path, phase: str, raw: bytes) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        WCT_ACCEPT_IR=str(directory / "ir.json"),
        WCT_ACCEPT_RECEIPT=str(directory / "receipt.json"),
        WCT_ACCEPT_ATTEMPT_ID=uuid.uuid4().hex,
        WCT_ACCEPT_IR_SHA256=hashlib.sha256(raw).hexdigest(),
        WCT_ACCEPT_PHASE=phase,
    )
    plugins = env.get("PYTEST_PLUGINS", "").split(",")
    own = "tools.wct.accept.pytest_receipt"
    if own not in plugins:
        plugins.append(own)
    env["PYTEST_PLUGINS"] = ",".join(value for value in plugins if value)
    env["PYTEST_DEBUG_TEMPROOT"] = str(directory)
    env["TMPDIR"] = str(directory)
    return env


def _attempt(
    ir: dict[str, Any], command: list[str], directory: Path, phase: str, deadline: float
) -> dict[str, Any]:
    directory.mkdir()
    raw = json.dumps(ir, ensure_ascii=False).encode("utf-8")
    (directory / "ir.json").write_bytes(raw)
    env = _environment(directory, phase, raw)
    remaining = min(ATTEMPT_SECONDS, deadline - time.monotonic())
    result = run_process(command, env, directory, remaining)
    if result["reason"]:
        status, reason = "invalid", result["reason"]
    else:
        status, reason = validate_receipt(
            directory / "receipt.json",
            attempt_id=env["WCT_ACCEPT_ATTEMPT_ID"],
            ir_sha256=env["WCT_ACCEPT_IR_SHA256"],
            exit_code=result["exit"],
            scenario_count=len(ir["scenarios"]),
        )
    result.update(
        status=status,
        reason=reason,
        attempt_id=env["WCT_ACCEPT_ATTEMPT_ID"],
        ir_sha256=env["WCT_ACCEPT_IR_SHA256"],
        argv=command,
        cwd=str(Path.cwd()),
    )
    (directory / "attempt.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def _results(
    inventory: list[dict[str, Any]],
    baseline: dict[str, Any],
    command: list[str],
    directory: Path,
    deadline: float,
) -> list[dict[str, Any]]:
    results = []
    stopped = baseline["status"] != "pass"
    for index, mutation in enumerate(inventory):
        result = {key: value for key, value in mutation.items() if key != "ir"}
        result.update(
            id=index, status="not_run", exit=None, reason="prior attempt did not pass protocol"
        )
        if not stopped:
            attempt = _attempt(
                mutation["ir"], command, directory / f"mutation-{index}", "mutation", deadline
            )
            result.update(
                exit=attempt["exit"],
                reason=attempt["reason"],
                status={"pass": "survived", "mismatch": "killed", "invalid": "error"}[
                    attempt["status"]
                ],
            )
            stopped = attempt["status"] == "invalid"
        results.append(result)
    return results


def run_mutations(ir: dict[str, Any], command: list[str]) -> dict[str, Any]:
    """Persist original/mutant evidence; stop on invalid baseline or instrument."""
    parent = Path("build/tmp").resolve()
    parent.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="wct-accept-", dir=parent))
    inventory = mutations(ir)
    deadline = time.monotonic() + CAMPAIGN_SECONDS
    phase = "baseline"
    baseline = _attempt(ir, command, directory / phase, phase, deadline)
    results = _results(inventory, baseline, command, directory, deadline)
    report = {
        "schema_version": 1,
        "baseline": baseline,
        "results": results,
        "planned": len(inventory),
        "evidence_dir": str(directory),
    }
    for counter, status in (
        ("killed", "killed"),
        ("survived", "survived"),
        ("errors", "error"),
        ("not_run", "not_run"),
    ):
        report[counter] = sum(item["status"] == status for item in results)
    (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
