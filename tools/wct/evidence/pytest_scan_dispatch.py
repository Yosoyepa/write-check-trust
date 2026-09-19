"""Encaminamiento FSM: tabla de transición y handlers por kind (§5)."""

from collections.abc import Callable
from typing import cast

from tools.wct.evidence.pytest_payload_classes import TestEnd
from tools.wct.evidence.pytest_scan_closers import (
    _on_channel_end,
    _on_session_end,
    _on_session_end_error,
)
from tools.wct.evidence.pytest_scan_open import (
    _on_collect_report,
    _on_collection_end,
    _on_deselected,
    _on_event_order,
    _on_execution_start,
    _on_item,
    _on_node_declaration,
    _on_options,
    _on_selected,
    _on_session_start,
)
from tools.wct.evidence.pytest_scan_state import (
    _COLLECTION_KINDS,
    _PRE_CHANNEL_CLOSERS,
    _SESSION_ALTERNATIVES,
    _SESSION_SCOPED,
    _TEST_PHASE_KINDS,
    _ScanState,
)
from tools.wct.evidence.pytest_scan_tests import (
    _invalidate_last_instance,
    _on_internal_error,
    _on_interrupted,
    _on_phase_log,
    _on_phase_make,
    _on_plugin,
    _on_plugins_end,
    _on_test_end,
    _on_test_start,
)
from tools.wct.evidence.pytest_termination import _on_execution_end
from tools.wct.evidence.pytest_types import JournalEvent


def _reject_out_of_order(state: _ScanState, event: JournalEvent) -> None:
    """Event_order y, para un test_end, invalidación de su instancia (§6).

    El terminal exige test_end único aunque el rechazo ocurra antes de
    alcanzar el handler: plugins_end/session_end/canal cerrados no blinda
    la elegibilidad PASS de la instancia ya cerrada. Si el end pertenece a
    la instancia activa, no se atribuye a ninguna histórica: queda abierta
    y finish_scan la cierra incompleta con su missing_test_end.
    """
    _on_event_order(state, event)
    if event.kind == "test_end":
        nodeid = cast(TestEnd, event.payload).nodeid
        if state.active is None or state.active[0] != nodeid:
            _invalidate_last_instance(state, nodeid)


def feed_scan(state: _ScanState, event: JournalEvent) -> None:
    """Encamina un evento por la máquina; fuera de orden es event_order."""
    if state.first_seq is None:
        state.first_seq = event.seq
        state.first_offset = event.offset
    if not state.started:
        _feed_unstarted(state, event)
        return
    if state.ended:
        _feed_ended(state, event)
        return
    if _gate_blocks(state, event):
        _reject_out_of_order(state, event)
        return
    _HANDLERS[event.kind](state, event)


def _feed_unstarted(state: _ScanState, event: JournalEvent) -> None:
    """Antes del execution_start solo ese kind es aceptado."""
    if event.kind == "execution_start":
        _on_execution_start(state, event)
    else:
        _on_event_order(state, event)


def _feed_ended(state: _ScanState, event: JournalEvent) -> None:
    """Tras execution_end solo se acepta repetir execution_end."""
    if event.kind == "execution_end":
        _HANDLERS[event.kind](state, event)
    else:
        _reject_out_of_order(state, event)


def _gate_blocks(state: _ScanState, event: JournalEvent) -> bool:
    """Los cierres previos al canal y la tabla de sesión rechazan el evento."""
    if state.channel_seen and event.kind in _PRE_CHANNEL_CLOSERS:
        return True
    return not _session_accepts(state, event.kind)


def _session_accepts(state: _ScanState, kind: str) -> bool:
    """Tabla de transiciones del §5 para el tramo con sesión de la ejecución.

    Las declaraciones exigen sesión activa. Tras session_end solo sobreviven
    los cierres alternativos; tras plugins_end o channel_end no hay tests ni
    colección (la ruta normal es colección→tests→plugins_end→session_end).
    """
    if kind == "node_declaration":
        return state.session_started and not state.session_closed
    if _outside_session_gate(state, kind):
        return kind not in _SESSION_SCOPED
    return _accepts_scoped(state, kind)


def _outside_session_gate(state: _ScanState, kind: str) -> bool:
    """Fuera del alcance de sesión siempre pasa; sin sesión nada con alcance."""
    return kind not in _SESSION_SCOPED or not state.session_started


def _accepts_scoped(state: _ScanState, kind: str) -> bool:
    """Con sesión activa: alternativas pasan, el cierre bloquea la ventana."""
    if kind in _SESSION_ALTERNATIVES:
        return True
    if state.session_closed:
        return False
    if kind in _TEST_PHASE_KINDS or kind in _COLLECTION_KINDS:
        return not state.plugins_closed and not state.channel_seen
    return True


_HANDLERS: dict[str, Callable[[_ScanState, JournalEvent], None]] = {
    "execution_start": _on_execution_start,
    "session_start": _on_session_start,
    "options": _on_options,
    "item": _on_item,
    "collect_report": _on_collect_report,
    "deselected": _on_deselected,
    "selected": _on_selected,
    "collection_end": _on_collection_end,
    "node_declaration": _on_node_declaration,
    "test_start": _on_test_start,
    "phase_make": _on_phase_make,
    "phase_log": _on_phase_log,
    "test_end": _on_test_end,
    "plugin": _on_plugin,
    "plugins_end": _on_plugins_end,
    "session_end": _on_session_end,
    "session_end_error": _on_session_end_error,
    "internal_error": _on_internal_error,
    "interrupted": _on_interrupted,
    "channel_end": _on_channel_end,
    "execution_end": _on_execution_end,
}
