"""Disposición nativa de fases: las ocho reglas ordenadas del §6."""

from collections.abc import Callable
from dataclasses import dataclass

from tools.wct.evidence.pytest_types import XfailObservation

PHASE_RANKS = {"setup": 0, "call": 1, "teardown": 2}

PASS_PHASE_COUNT = 3


@dataclass(frozen=True)
class PhaseEvent:
    """Evento de fase ya emparejado con su instancia activa."""

    is_make: bool
    phase: str
    outcome: str
    wasxfail: bool
    exception_present: bool
    exception_type: str | None
    xfail: XfailObservation | None
    offset: int


@dataclass(frozen=True)
class _DispositionInput:
    """Datos de una fase para la cadena de reglas del §6."""

    phase: str
    outcome: str
    exception_present: bool
    wasxfail: bool
    xfail: XfailObservation | None


def _outcome_rule(outcome_value: str, verdict: str) -> Callable[[_DispositionInput], str | None]:
    """Regla por igualdad de outcome: si coincide, devuelve su veredicto."""

    def rule(data: _DispositionInput) -> str | None:
        if data.outcome == outcome_value:
            return verdict
        return None

    return rule


def _rule_passed_or_xfail(data: _DispositionInput) -> str | None:
    """Reglas 1-2: passed con excepción es inconsistente; skipped con wasxfail es xfail."""
    if data.outcome == "passed" and data.exception_present:
        return "inconsistent"
    if data.outcome == "skipped" and data.wasxfail:
        return "xfail"
    return None


def _rule_passed_wasxfail(data: _DispositionInput) -> str | None:
    """Regla 3: passed con wasxfail es xpass en call e inconsistente fuera."""
    if data.outcome == "passed" and data.wasxfail:
        return "xpass" if data.phase == "call" else "inconsistent"
    return None


def _rule_xpass_strict(data: _DispositionInput) -> str | None:
    """Regla 4: failed en call sin excepción con xfail estricto es xpass_strict."""
    if (
        data.outcome == "failed"
        and data.phase == "call"
        and not data.exception_present
        and data.xfail is not None
        and data.xfail.strict
    ):
        return "xpass_strict"
    return None


def _strict_xfail(data: _DispositionInput) -> bool:
    """El marker xfail de la fase está activo y es estricto."""
    return data.xfail is not None and data.xfail.strict


def _rule_passed_call_strict(data: _DispositionInput) -> str | None:
    """Regla 7: passed en call con xfail estricto es inconsistente."""
    if data.outcome == "passed" and data.phase == "call" and _strict_xfail(data):
        return "inconsistent"
    return None


_RULES = (
    _rule_passed_or_xfail,
    _rule_passed_wasxfail,
    _rule_xpass_strict,
    _outcome_rule("failed", "failed"),
    _outcome_rule("skipped", "skipped"),
    _rule_passed_call_strict,
)


def classify_disposition(
    phase: str,
    outcome: str,
    *,
    exception_present: bool,
    wasxfail: bool,
    xfail: XfailObservation | None,
) -> str:
    """Las ocho reglas ordenadas de §6; la primera aplicable decide."""
    data = _DispositionInput(
        phase=phase,
        outcome=outcome,
        exception_present=exception_present,
        wasxfail=wasxfail,
        xfail=xfail,
    )
    for rule in _RULES:
        verdict = rule(data)
        if verdict is not None:
            return verdict
    return "passed"
