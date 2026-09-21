"""Handlers de apertura y colección del FSM (§5)."""

from typing import cast

from tools.wct.evidence.pytest_payloads import (
    CollectedItem,
    CollectionEnd,
    CollectionReport,
    DeselectedItem,
    ExecutionStart,
    SelectedItem,
)
from tools.wct.evidence.pytest_scan_state import _finding_scan, _ScanState
from tools.wct.evidence.pytest_types import JournalEvent


def _on_execution_start(state: _ScanState, event: JournalEvent) -> None:
    if state.started:
        _on_duplicate(state, event)
        return
    state.started = True
    state.start_payload = cast(ExecutionStart, event.payload)
    state.start_offset = event.offset


def _on_event_order(state: _ScanState, event: JournalEvent) -> None:
    nodeid = getattr(event.payload, "nodeid", None)
    state.findings.append(_finding_scan("event_order", state, nodeid, event.offset))


def _on_duplicate(state: _ScanState, event: JournalEvent) -> None:
    state.findings.append(_finding_scan("duplicate_event", state, None, event.offset))


def _on_session_start(state: _ScanState, event: JournalEvent) -> None:
    if state.session_started:
        _on_duplicate(state, event)
        return
    state.session_started = True


def _on_options(state: _ScanState, event: JournalEvent) -> None:
    if state.options_seen:
        _on_duplicate(state, event)
        return
    if state.collection_started:
        _on_event_order(state, event)
        return
    state.options_seen = True


def _on_item(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(CollectedItem, event.payload)
    if state.collection_closed:
        _on_event_order(state, event)
        return
    state.collection_started = True
    state.items.append((payload.nodeid, payload.property, event.offset))
    state._collected.add(payload.nodeid)


def _on_collect_report(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(CollectionReport, event.payload)
    if state.collection_closed:
        _on_event_order(state, event)
        return
    state.collection_started = True
    if payload.outcome != "passed":
        state.findings.append(
            _finding_scan("collection_report_nonpass", state, payload.nodeid, event.offset)
        )


def _on_deselected(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(DeselectedItem, event.payload)
    if state.collection_closed:
        _on_event_order(state, event)
        return
    if payload.nodeid not in state._collected:
        _on_event_order(state, event)
        return
    state.deselected.append((payload.nodeid, payload.property, event.offset))


def _on_selected(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(SelectedItem, event.payload)
    if state.collection_closed:
        _on_event_order(state, event)
        return
    if payload.nodeid not in state._collected:
        _on_event_order(state, event)
        return
    state.selected.append((payload.nodeid, event.offset))


def _on_collection_end(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(CollectionEnd, event.payload)
    if state.collection_closed:
        _on_duplicate(state, event)
        return
    state.collection_closed = True
    state.collection_end_offset = event.offset
    if payload.selected_count != len(state.selected) or (
        payload.deselected_count != len(state.deselected)
    ):
        state.findings.append(_finding_scan("collection_count_mismatch", state, None, event.offset))


def _on_node_declaration(state: _ScanState, event: JournalEvent) -> None:
    """Metadata del supervisor: no cambia la FSM de callbacks."""
