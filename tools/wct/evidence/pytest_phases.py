"""Instancias de test: ensamblado de fases, terminal y disposición (§6).

Las reglas de disposición viven en ``pytest_disposition`` y las reglas
de pareja/orden en ``pytest_phase_pairs``.
"""

from dataclasses import dataclass

from tools.wct.evidence.pytest_disposition import (
    PASS_PHASE_COUNT,
    PHASE_RANKS,
    PhaseEvent,
    classify_disposition,
)
from tools.wct.evidence.pytest_phase_pairs import (
    _finding,
    _order_finding,
    _pair_findings,
    _required_findings,
    _unexpected_call,
)
from tools.wct.evidence.pytest_types import PhaseObservation, ProtocolFinding, TestObservation


def _by_phase(events: tuple[PhaseEvent, ...], *, is_make: bool) -> dict[str, list[PhaseEvent]]:
    grouped: dict[str, list[PhaseEvent]] = {name: [] for name in PHASE_RANKS}
    for event in events:
        if event.is_make is is_make:
            grouped[event.phase].append(event)
    return grouped


def _phase_observations(
    events: tuple[PhaseEvent, ...], nodeid: str, findings: list[ProtocolFinding], execution_id: str
) -> tuple[PhaseObservation, ...]:
    """Una PhaseObservation por make válido, en orden, duplicados incluidos."""
    observations: list[PhaseObservation] = []
    for event in events:
        if not event.is_make:
            continue
        disposition = classify_disposition(
            event.phase,
            event.outcome,
            exception_present=event.exception_present,
            wasxfail=event.wasxfail,
            xfail=event.xfail,
        )
        if disposition == "inconsistent":
            findings.append(_finding("report_inconsistent", nodeid, event.offset, execution_id))
        observations.append(
            PhaseObservation(
                nodeid=nodeid,
                phase=event.phase,
                outcome=event.outcome,
                exception_present=event.exception_present,
                exception_type=event.exception_type,
                wasxfail=event.wasxfail,
                xfail=event.xfail,
                disposition=disposition,
            )
        )
    return tuple(observations)


def _call_disposition(makes: dict[str, list[PhaseEvent]]) -> str:
    """Observed / not_scheduled / missing según §6."""
    if makes["call"]:
        return "observed"
    if len(makes["setup"]) == 1 and makes["setup"][0].outcome != "passed":
        return "not_scheduled"
    return "missing"


@dataclass(frozen=True)
class InstanceEvaluation:
    """TestObservation junto a los findings de fase que la invalidan."""

    test: TestObservation
    findings: tuple[ProtocolFinding, ...]


def observe_instance(
    execution_id: str,
    nodeid: str,
    start_seq: int,
    events: tuple[PhaseEvent, ...],
    *,
    ended: bool,
) -> InstanceEvaluation:
    """Evalúa una instancia completa y conserva todos sus defectos."""
    makes = _by_phase(events, is_make=True)
    logs = _by_phase(events, is_make=False)
    findings: list[ProtocolFinding] = []
    order = _order_finding(events, nodeid, execution_id)
    if order is not None:
        findings.append(order)
    unexpected = _unexpected_call(makes, events, nodeid, execution_id)
    if unexpected is not None:
        findings.append(unexpected)
    findings.extend(_pair_findings(makes, logs, nodeid, execution_id))
    phases = _phase_observations(events, nodeid, findings, execution_id)
    findings.extend(_required_findings(makes, logs, nodeid, execution_id))
    disposition = _call_disposition(makes)
    terminal = ended and not findings
    test = TestObservation(
        nodeid=nodeid,
        start_seq=start_seq,
        phases=phases,
        terminal=terminal,
        pass_eligible=_pass_eligible(phases, terminal=terminal),
        call_disposition=disposition,
    )
    return InstanceEvaluation(test=test, findings=tuple(findings))


def _pass_eligible(phases: tuple[PhaseObservation, ...], *, terminal: bool) -> bool:
    """Terminal con las fases PASS completas y todas passed."""
    return (
        terminal
        and len(phases) == PASS_PHASE_COUNT
        and all(phase.disposition == "passed" for phase in phases)
    )
