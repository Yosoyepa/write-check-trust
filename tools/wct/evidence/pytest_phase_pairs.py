"""Parejas make/log, orden de fases y requerimientos por instancia (§6)."""

from tools.wct.evidence.pytest_disposition import PHASE_RANKS, PhaseEvent
from tools.wct.evidence.pytest_types import ProtocolFinding


def _finding(code: str, nodeid: str, offset: int | None, execution_id: str) -> ProtocolFinding:
    return ProtocolFinding(
        code=code, execution_id=execution_id, nodeid=nodeid, phase=None, offset=offset
    )


def _order_finding(
    events: tuple[PhaseEvent, ...], nodeid: str, execution_id: str
) -> ProtocolFinding | None:
    """Primera disminución de rango en la secuencia observada (§6).

    El orden setup→call→teardown rige cada evento; reentrar a una fase
    anterior —no solo invertir dos primeras apariciones— es inversión.
    """
    previous: int | None = None
    for event in events:
        rank = PHASE_RANKS[event.phase]
        if previous is not None and rank < previous:
            return _finding("phase_order", nodeid, event.offset, execution_id)
        previous = rank
    return None


def _unexpected_call(
    makes: dict[str, list[PhaseEvent]],
    events: tuple[PhaseEvent, ...],
    nodeid: str,
    execution_id: str,
) -> ProtocolFinding | None:
    """Call tras un setup no-PASS; no depende del tipo de excepción."""
    setup = makes["setup"]
    if not setup or setup[0].outcome == "passed":
        return None
    for event in events:
        if event.phase == "call":
            return _finding("unexpected_phase", nodeid, event.offset, execution_id)
    return None


def _pair_findings(
    makes: dict[str, list[PhaseEvent]],
    logs: dict[str, list[PhaseEvent]],
    nodeid: str,
    execution_id: str,
) -> list[ProtocolFinding]:
    """Un duplicate_phase por make/log repetido; cardinalidad 1-a-1 y coherencia."""
    findings: list[ProtocolFinding] = []
    for phase in PHASE_RANKS:
        phase_makes, phase_logs = makes[phase], logs[phase]
        for extra in (*phase_makes[1:], *phase_logs[1:]):
            findings.append(_finding("duplicate_phase", nodeid, extra.offset, execution_id))
        mismatch = _pair_mismatch(phase_makes, phase_logs, nodeid, execution_id)
        if mismatch is not None:
            findings.append(mismatch)
    return findings


def _first_event(phase_makes: list[PhaseEvent], phase_logs: list[PhaseEvent]) -> PhaseEvent | None:
    """Primer evento de la pareja, si existe alguno."""
    if phase_makes:
        return phase_makes[0]
    if phase_logs:
        return phase_logs[0]
    return None


def _pair_mismatch(
    makes: list[PhaseEvent],
    logs: list[PhaseEvent],
    nodeid: str,
    execution_id: str,
) -> ProtocolFinding | None:
    """Cardinalidad 1-a-1 y coherencia de la pareja make/log."""
    first = _first_event(makes, logs)
    if first is None:
        return None
    if len(makes) != 1 or len(logs) != 1:
        return _finding("report_pair_mismatch", nodeid, first.offset, execution_id)
    if _incoherent_pair(makes[0], logs[0]):
        return _finding("report_pair_mismatch", nodeid, logs[0].offset, execution_id)
    return None


def _incoherent_pair(phase_make: PhaseEvent, phase_log: PhaseEvent) -> bool:
    """Outcome o wasxfail distintos, o el make llega después del log."""
    return (
        phase_make.outcome != phase_log.outcome
        or phase_make.wasxfail != phase_log.wasxfail
        or phase_make.offset > phase_log.offset
    )


def _required_findings(
    makes: dict[str, list[PhaseEvent]],
    logs: dict[str, list[PhaseEvent]],
    nodeid: str,
    execution_id: str,
) -> list[ProtocolFinding]:
    """Setup y teardown siempre; call solo tras setup passed.

    Una fase con solo log ya tiene report_pair_mismatch: no es ausente.
    """
    findings: list[ProtocolFinding] = []

    def absent(phase: str) -> bool:
        return not makes[phase] and not logs[phase]

    if absent("setup"):
        findings.append(_finding("missing_phase", nodeid, None, execution_id))
    required = ["teardown"]
    if makes["setup"] and makes["setup"][0].outcome == "passed":
        required.append("call")
    for phase in required:
        if absent(phase):
            findings.append(_finding("missing_phase", nodeid, None, execution_id))
    return findings
