from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import re
import shutil
import subprocess

from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.integrity.engine import require_approval_evidence
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.ratchet.engine import (
    baseline,
    compare,
    debt_findings,
    ignores_count,
    suppression_count,
)
from tools.wct.size.engine import oversized as size_oversized
from tools.wct.util.git import head_sha

MIN_APPROVER = 2
MIN_REASON = 12
PERCENT = re.compile(r"actual:\s*(\d+(?:\.\d+)?)%")


def interrogate_percent(text: str) -> float | None:
    """Extrae el 'actual: N%' de la salida de interrogate."""
    match = PERCENT.search(text)
    return float(match.group(1)) if match else None


def docstring_coverage(root: Path) -> float | None:
    """Cobertura de docstrings medida por interrogate (None si la tool falta)."""
    if shutil.which("interrogate") is None:
        return None
    completed = subprocess.run(
        ["interrogate", "src"], cwd=root, text=True, capture_output=True, check=False
    )
    return interrogate_percent(completed.stdout + completed.stderr)


def measurements(root: Path) -> dict[str, float]:
    architecture = analyze_architecture(root)
    tests = analyze_tests(root)
    metrics = {
        "suppressions": float(suppression_count(root)),
        "debt-markers": float(len(debt_findings(root))),
        "introverted-tests": float(tests["counts"].get("introverted", 0)),
        "archmetrics-zones": float(
            sum(item["zone"] != "healthy" for item in architecture["metrics"])
        ),
        "per-file-ignores": float(ignores_count(root)),
        "file-size": float(len(size_oversized(root)["files"])),
    }
    docstrings = docstring_coverage(root)
    if docstrings is not None:
        metrics["docstring-coverage"] = docstrings
    return metrics


def check(root: Path) -> list[str]:
    failures: list[str] = []
    for name, current in measurements(root).items():
        expected = baseline(root, name)
        if not compare(current, expected):
            failures.append(f"{name}: actual={current:g}, baseline={expected['value']}")
    return failures


def record(root: Path, approved_by: str, reason: str) -> list[Path]:
    if len(approved_by.strip()) < MIN_APPROVER or len(reason.strip()) < MIN_REASON:
        raise ValueError("approved-by y reason >=12 caracteres son obligatorios")
    require_approval_evidence(reason)
    written: list[Path] = []
    for name, current in measurements(root).items():
        path = root / "governance/baselines" / f"{name}.json"
        document = baseline(root, name)
        document.update(
            {
                "value": current,
                "recorded_at": datetime.now(UTC).isoformat(),
                "recorded_by": approved_by,
                "commit": head_sha(root),
            }
        )
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    with (root / "governance/ratchet-log.md").open("a", encoding="utf-8") as stream:
        stream.write(
            f"\n## {datetime.now(UTC).isoformat()}\n\n"
            f"- Approved by: {approved_by}\n- Reason: {reason}\n"
        )
    return written
