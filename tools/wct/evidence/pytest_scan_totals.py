"""Cierres agregados, ausencias aplicables y límites entre procesos (§5)."""

from tools.wct.evidence.pytest_scan_state import _finding_scan, _ScanState
from tools.wct.evidence.pytest_scan_tests import _close_active
from tools.wct.evidence.pytest_types import ProtocolFinding


def _finding(
    code: str, execution_id: str, nodeid: str | None, offset: int | None
) -> ProtocolFinding:
    """Finding semántico con la ejecución y el evento causante."""
    return ProtocolFinding(
        code=code, execution_id=execution_id, nodeid=nodeid, phase=None, offset=offset
    )


def finish_scan(state: _ScanState) -> None:
    """Cierra instancias y agrega las ausencias aplicables del §5."""
    if state.active is not None:
        _close_active(state, None, ended=False)
    if not state.started:
        state.findings.append(_finding_scan("missing_execution", state, None, None))
        return
    if not state.session_started:
        state.findings.append(_finding_scan("missing_session_start", state, None, None))
    else:
        _absences(state)
        _unexpected_tests(state)
    if not state.channel_seen:
        state.findings.append(_finding_scan("missing_channel_end", state, None, None))
    if not state.execution_end_seen:
        state.findings.append(_finding_scan("missing_execution_end", state, None, None))


def _unexpected_tests(state: _ScanState) -> None:
    """Tests ejecutados fuera de la selección previa de la colección."""
    selected_ids = {nodeid for nodeid, _offset in state.selected}
    for test in state.tests:
        if test.nodeid not in selected_ids:
            state.findings.append(
                _finding_scan(
                    "unexpected_test", state, test.nodeid, state._test_starts[test.start_seq]
                )
            )


def _absences(state: _ScanState) -> None:
    """Cierres de la máquina con sesión activa, una vez que la sesión empezó."""
    if not state.options_seen:
        state.findings.append(_finding_scan("missing_options", state, None, None))
    if not state.collection_closed:
        state.findings.append(_finding_scan("missing_collection_end", state, None, None))
    if not state.plugins_closed:
        state.findings.append(_finding_scan("missing_plugins_end", state, None, None))
    if not state.session_closed:
        state.findings.append(_finding_scan("missing_session_end", state, None, None))


def _cross_execution_bounds(scans: list[_ScanState]) -> None:
    """Logs contiguos entre procesos: primer log_start 0 y encadenado."""
    collection, producer = scans
    _bounds_start(collection)
    if producer.start_payload is None or collection.end_payload is None:
        return
    if producer.start_payload.log_start != collection.end_payload.log_end:
        producer.findings.append(
            _finding("execution_bounds", producer.execution_id, None, producer.start_offset)
        )


def _bounds_start(collection: _ScanState) -> None:
    """El primer log del journal de colección empieza en 0."""
    if collection.start_payload is not None and collection.start_payload.log_start != 0:
        collection.findings.append(
            _finding("execution_bounds", collection.execution_id, None, collection.start_offset)
        )


def _execution_order(scans: list[_ScanState]) -> None:
    """El productor no comienza antes del execution_end de la colección."""
    collection, producer = scans
    if producer.first_seq is None:
        return
    if collection.end_seq is None or producer.first_seq < collection.end_seq:
        producer.findings.append(
            _finding("execution_order", producer.execution_id, None, producer.first_offset)
        )
