"""Clasificación cerrada de la respuesta Semgrep: estados y diagnósticos (addenda §3).

La cobertura es una condición de conjuntos, nunca de cardinalidad:
U = E - S. Clasificación cerrada: ERROR por JSON ilegible, esquema o tipos
inválidos, errors del instrumento, exit fuera de 0/1, exit incoherente con
los hallazgos o U no vacío sin hallazgos; FAIL por hallazgos validados (la
omisión se añade al resumen sin ocultar el defecto); PASS sólo si el
resultado es coherente y U es vacío. S_extra queda como diagnóstico y jamás
compensa una omisión.
"""

from __future__ import annotations

from typing import NamedTuple

from tools.wct.gate.semgrep_schema import response
from tools.wct.gate.semgrep_scope import SemgrepScopeError
from tools.wct.model import Status


class Verdict(NamedTuple):
    """Resultado clasificado de una respuesta del instrumento."""

    status: Status
    summary: str
    details: tuple[str, ...]


def _coherent(exit_code: int, findings: list[tuple[str, str, int]]) -> Verdict | None:
    """El par exit/hallazgos debe explicarse: sin hallazgos no hay exit 1, y viceversa."""
    if exit_code not in (0, 1):
        return Verdict(Status.ERROR, "exit fuera de contrato", (f"exit observado: {exit_code}",))
    if exit_code == 1 and not findings:
        return Verdict(Status.ERROR, "exit sin finding explicativo", ())
    if exit_code == 0 and findings:
        return Verdict(Status.ERROR, "exit incoherente con hallazgos", ())
    return None


def _details(
    findings: list[tuple[str, str, int]], omitted: set[str], extras: set[str]
) -> tuple[str, ...]:
    lines = [f"{check_id} {path}:{line}" for check_id, path, line in sorted(findings)]
    lines += [f"omitida: {path}" for path in sorted(omitted)]
    lines += [f"S_extra (diagnóstico, no compensa): {path}" for path in sorted(extras)]
    return tuple(lines)


def _finding_summary(findings: list[tuple[str, str, int]], omitted: set[str]) -> str:
    check_id, path, line = sorted(findings)[0]
    summary = f"{check_id} {path}:{line}"
    if omitted:
        summary += f" (omitidas: {', '.join(sorted(omitted))})"
    return summary


def _instrument_error(messages: list[str]) -> Verdict:
    return Verdict(
        Status.ERROR,
        "error del instrumento",
        tuple(f"error del instrumento: {message}" for message in messages),
    )


def _pass_verdict(demanded: set[str], details: tuple[str, ...]) -> Verdict:
    if not demanded:
        return Verdict(Status.PASS, "sin fuentes aplicables: 0", details)
    return Verdict(Status.PASS, f"{len(demanded)} fuentes analizadas, 0 hallazgos", details)


def _omission_verdict(
    demanded: set[str], reported: set[str], omitted: set[str], details: tuple[str, ...]
) -> Verdict:
    if reported - demanded:
        return Verdict(Status.ERROR, "ruta distinta no compensa", details)
    if not (demanded & reported):
        return Verdict(Status.ERROR, f"0 de {len(demanded)} fuentes", details)
    return Verdict(Status.ERROR, f"falta {', '.join(sorted(omitted))}", details)


def _scope_verdict(
    demanded: set[str],
    reported: set[str],
    findings: list[tuple[str, str, int]],
) -> Verdict:
    omitted = demanded - reported
    extras = reported - demanded
    details = _details(findings, omitted, extras)
    if findings:
        return Verdict(Status.FAIL, _finding_summary(findings, omitted), details)
    if omitted:
        return _omission_verdict(demanded, reported, omitted, details)
    return _pass_verdict(demanded, details)


def _verdict(
    demanded: set[str],
    reported: set[str],
    messages: list[str],
    findings: list[tuple[str, str, int]],
    exit_code: int,
) -> Verdict:
    if messages:
        return _instrument_error(messages)
    coherent = _coherent(exit_code, findings)
    if coherent is not None:
        return coherent
    return _scope_verdict(demanded, reported, findings)


def classify(required: list[str], payload: str, exit_code: int) -> Verdict:
    """Clasifica una respuesta Semgrep sobre el alcance exigible (addenda §3)."""
    try:
        reported, messages, found = response(payload)
    except SemgrepScopeError as exc:
        return Verdict(Status.ERROR, str(exc), ())
    return _verdict(set(required), reported, messages, found, exit_code)
