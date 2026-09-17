"""Validación tipada del JSON de Semgrep: documento, scanned, errors y hallazgos.

Cada campo consumido se valida por tipo y estructura, no sólo por presencia
(addenda §3): documento objeto, paths.scanned lista de rutas relativas
normalizables, errors con mensaje string y hallazgos atribuibles a regla,
ruta y línea válidas con severidad bloqueante. Toda violación levanta
SemgrepScopeError con el diagnóstico de la clasificación cerrada.
"""

from __future__ import annotations

import json
from typing import Any

from tools.wct.gate.semgrep_scope import SemgrepScopeError, relative_path


def document(payload: str) -> dict[str, Any]:
    """Documento JSON objeto con paths de mapa; la salida ilegible es ERROR."""
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SemgrepScopeError("salida ilegible") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("paths"), dict):
        raise SemgrepScopeError("esquema incompleto")
    return parsed


def scanned_path(item: Any) -> str:
    """Entrada de paths.scanned validada: str relativa y normalizable bajo R."""
    pure = relative_path(item)
    if pure is None:
        raise SemgrepScopeError("esquema incompleto")
    return pure.as_posix()


def scanned_set(raw: Any) -> set[str]:
    """paths.scanned validado por tipo y forma de cada entrada."""
    if not isinstance(raw, list):
        raise SemgrepScopeError("esquema incompleto")
    return {scanned_path(item) for item in raw}


def error_messages(errors: Any) -> list[str]:
    """Mensajes del instrumento; cada error del resumen debe exponer message string."""
    if not isinstance(errors, list):
        raise SemgrepScopeError("esquema incompleto")
    messages: list[str] = []
    for error in errors:
        message = error.get("message") if isinstance(error, dict) else None
        if not isinstance(message, str) or not message:
            raise SemgrepScopeError("esquema incompleto")
        messages.append(message)
    return messages


def check_id(finding: dict[str, Any]) -> str:
    """check_id string no vacío: la regla que imputa el hallazgo."""
    value = finding.get("check_id")
    if not isinstance(value, str) or not value:
        raise SemgrepScopeError("esquema incompleto")
    return value


def line(start: Any) -> int:
    """start.line int exacto positivo: la línea atribuible del hallazgo."""
    value = start.get("line") if isinstance(start, dict) else None
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise SemgrepScopeError("esquema incompleto")
    return value


def severity(extra: Any) -> None:
    """El extra debe exponer la severidad bloqueante esperada del comando."""
    if not isinstance(extra, dict) or extra.get("severity") != "ERROR":
        raise SemgrepScopeError("esquema incompleto")


def finding(item: Any) -> tuple[str, str, int]:
    """Hallazgo atribuible a regla, ruta y línea válidas, con severidad bloqueante."""
    if not isinstance(item, dict):
        raise SemgrepScopeError("esquema incompleto")
    pure = relative_path(item.get("path"))
    if pure is None:
        raise SemgrepScopeError("esquema incompleto")
    severity(item.get("extra"))
    return check_id(item), pure.as_posix(), line(item.get("start"))


def findings(results: Any) -> list[tuple[str, str, int]]:
    if not isinstance(results, list):
        raise SemgrepScopeError("esquema incompleto")
    return [finding(item) for item in results]


def response(payload: str) -> tuple[set[str], list[str], list[tuple[str, str, int]]]:
    """Respuesta consumida: rutas reportadas, mensajes de error y hallazgos."""
    parsed = document(payload)
    return (
        scanned_set(parsed["paths"].get("scanned")),
        error_messages(parsed.get("errors")),
        findings(parsed.get("results")),
    )
