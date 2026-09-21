"""Handlers de instancias de test, fases y plugins del FSM (§5)."""

import dataclasses
from typing import cast

from tools.wct.evidence.pytest_disposition import PhaseEvent
from tools.wct.evidence.pytest_payload_classes import TestEnd
from tools.wct.evidence.pytest_payloads import (
    PhaseLog,
    PhaseMake,
    PluginClaim,
    PluginsEnd,
    TestStart,
)
from tools.wct.evidence.pytest_phases import observe_instance
from tools.wct.evidence.pytest_scan_open import _on_duplicate, _on_event_order
from tools.wct.evidence.pytest_scan_state import _finding_scan, _ScanState
from tools.wct.evidence.pytest_types import JournalEvent


def _on_test_start(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(TestStart, event.payload)
    if state.role != "producer" or not state.collection_closed:
        _on_event_order(state, event)
        return
    if state.active is not None:
        _close_active(state, event.offset, ended=False)
    state.active = (payload.nodeid, event.seq, event.offset, [])
    state._test_starts[event.seq] = event.offset


def _phase_event(state: _ScanState, event: JournalEvent, *, is_make: bool) -> None:
    if state.role != "producer" or state.active is None:
        _on_test_order(state, event)
        return
    nodeid, _seq, _offset, events = state.active
    if not _phase_matches(event, nodeid, is_make=is_make):
        _on_test_order(state, event)
        return
    _record_phase(events, event, is_make=is_make)


def _phase_matches(event: JournalEvent, nodeid: str, *, is_make: bool) -> bool:
    """El payload de fase apunta a la instancia activa."""
    if is_make:
        return cast(PhaseMake, event.payload).nodeid == nodeid
    return cast(PhaseLog, event.payload).nodeid == nodeid


def _record_phase(events: list[PhaseEvent], event: JournalEvent, *, is_make: bool) -> None:
    """Registra la fase con los campos que cada dirección conserva."""
    if is_make:
        make = cast(PhaseMake, event.payload)
        events.append(
            PhaseEvent(
                is_make=True,
                phase=make.phase,
                outcome=make.outcome,
                wasxfail=make.wasxfail,
                exception_present=make.exception_present,
                exception_type=make.exception_type,
                xfail=make.xfail,
                offset=event.offset,
            )
        )
    else:
        log = cast(PhaseLog, event.payload)
        events.append(
            PhaseEvent(
                is_make=False,
                phase=log.phase,
                outcome=log.outcome,
                wasxfail=log.wasxfail,
                exception_present=False,
                exception_type=None,
                xfail=None,
                offset=event.offset,
            )
        )


def _on_phase_make(state: _ScanState, event: JournalEvent) -> None:
    _phase_event(state, event, is_make=True)


def _on_phase_log(state: _ScanState, event: JournalEvent) -> None:
    _phase_event(state, event, is_make=False)


def _on_test_end(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(TestEnd, event.payload)
    if state.role != "producer":
        _on_event_order(state, event)
        return
    if state.active is None or payload.nodeid != state.active[0]:
        _on_test_order(state, event)
        _invalidate_last_instance(state, payload.nodeid)
        return
    _close_active(state, None, ended=True)


def _invalidate_last_instance(state: _ScanState, nodeid: str) -> None:
    """El test_end duplicado deja no terminal la última instancia cerrada (§6).

    El terminal exige test_end único: la instancia ya cerrada deja de alimentar
    el inventario de terminales y pierde su elegibilidad PASS.
    """
    for position in range(len(state.tests) - 1, -1, -1):
        if state.tests[position].nodeid == nodeid:
            state.tests[position] = dataclasses.replace(
                state.tests[position], terminal=False, pass_eligible=False
            )
            return


def _close_active(state: _ScanState, cause_offset: int | None, *, ended: bool) -> None:
    """Cierra la instancia activa; sin end conserva missing_test_end."""
    active = state.active
    if active is None:
        return
    nodeid, start_seq, _offset, events = active
    state.active = None
    evaluation = observe_instance(state.execution_id, nodeid, start_seq, tuple(events), ended=ended)
    state.tests.append(evaluation.test)
    state.findings.extend(evaluation.findings)
    if not ended:
        state.findings.append(_finding_scan("missing_test_end", state, nodeid, cause_offset))


def _on_plugin(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(PluginClaim, event.payload)
    if state.plugins_closed:
        _on_event_order(state, event)
        return
    state.plugin_claims.append((payload.name, event.offset))


def _on_plugins_end(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(PluginsEnd, event.payload)
    if state.plugins_closed:
        _on_duplicate(state, event)
        return
    state.plugins_closed = True
    if payload.count != len(state.plugin_claims):
        state.findings.append(_finding_scan("plugin_count_mismatch", state, None, event.offset))
    seen: set[str] = set()
    for name, offset in state.plugin_claims:
        if name in seen:
            state.findings.append(_finding_scan("duplicate_plugin", state, name, offset))
        seen.add(name)


def _on_internal_error(state: _ScanState, event: JournalEvent) -> None:
    _on_diagnostic(state, event, "internal_error")


def _on_interrupted(state: _ScanState, event: JournalEvent) -> None:
    _on_diagnostic(state, event, "interrupted")


def _on_diagnostic(state: _ScanState, event: JournalEvent, code: str) -> None:
    """Diagnóstico con sesión activa; marca protocolo incompleto (§5)."""
    state.diagnostics = True
    state.findings.append(_finding_scan(code, state, None, event.offset))


def _on_test_order(state: _ScanState, event: JournalEvent) -> None:
    nodeid = getattr(event.payload, "nodeid", None)
    state.findings.append(_finding_scan("test_order", state, nodeid, event.offset))
