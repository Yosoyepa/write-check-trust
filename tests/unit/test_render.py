"""El agregado del resumen distingue PASS de SKIP (ADR-A1-03)."""

from __future__ import annotations

from tools.wct.model import GateResult, Status
from tools.wct.report.render import text_report


def _results(statuses: list[Status]) -> list[GateResult]:
    return [
        GateResult(f"G-{index:02d}", status, "resumen de prueba")
        for index, status in enumerate(statuses)
    ]


def _summary_line(report: str) -> str:
    # Con SKIPs el resumen honesto añade una línea tras el agregado (O-006):
    # localizar por contenido, no por posición.
    return next(line for line in report.splitlines() if "gates:" in line)


def test_summary_separates_pass_skip_fail() -> None:
    report = text_report(_results([Status.PASS, Status.SKIP, Status.FAIL]))

    line = _summary_line(report)
    assert "1 PASS" in line
    assert "1 SKIP" in line
    assert "1 FAIL/ERROR" in line
    assert "3/3" not in report
    assert "no bloqueantes" not in report


def test_summary_all_pass() -> None:
    report = text_report(_results([Status.PASS] * 7))

    assert _summary_line(report) == "7 gates: 7 PASS · 0 SKIP · 0 FAIL/ERROR"


def test_summary_counts_error_as_fail() -> None:
    """El tercer contador agrupa FAIL y ERROR según model.Status."""
    report = text_report(_results([Status.PASS, Status.ERROR]))

    line = _summary_line(report)
    assert "1 FAIL/ERROR" in line
    assert "2 gates" in line


def test_summary_with_only_skip_does_not_claim_full_pass() -> None:
    """Regresión del defecto original: SKIP≠PASS en el agregado."""
    report = text_report(_results([Status.SKIP]))

    line = _summary_line(report)
    assert "0 PASS" in line
    assert "1 SKIP" in line
    assert "1/1" not in report
    assert "no bloqueantes" not in report


def test_skip_still_non_blocking() -> None:
    """A1 no cambia la semántica de bloqueo: solo SKIP no bloquea."""
    result = GateResult("G-OPTIONAL", Status.SKIP, "herramienta ausente")

    assert result.blocking is False
