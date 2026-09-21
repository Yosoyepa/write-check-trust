"""Handlers de session_end y channel_end con su coherencia (§5)."""

from typing import cast

from tools.wct.evidence.pytest_payloads import ChannelEnd, SessionEnd
from tools.wct.evidence.pytest_scan_open import _on_duplicate
from tools.wct.evidence.pytest_scan_state import _TAILLESS_DEFECTS, _finding_scan, _ScanState
from tools.wct.evidence.pytest_scan_totals import _finding
from tools.wct.evidence.pytest_types import JournalEvent, ProtocolFinding


def _channel_findings(payload: ChannelEnd, execution_id: str, offset: int) -> list[ProtocolFinding]:
    """Coherencia de canal del §5; cada defecto declarado se conserva."""
    findings: list[ProtocolFinding] = []
    if payload.defect is not None:
        findings.append(_finding("channel_defect", execution_id, None, offset))
    if not _channel_consistent(payload):
        findings.append(_finding("channel_inconsistent", execution_id, None, offset))
    return findings


def _channel_consistent(payload: ChannelEnd) -> bool:
    """Cola, eof y defecto declarado deben ser coherentes entre sí."""
    if payload.tail_bytes > 0:
        return payload.tail_sha256 is not None and payload.defect is not None
    if not payload.eof:
        return payload.defect in _TAILLESS_DEFECTS
    return payload.defect is None and payload.tail_sha256 is None


def _on_session_end(state: _ScanState, event: JournalEvent) -> None:
    payload = cast(SessionEnd, event.payload)
    if state.session_closed:
        _on_duplicate(state, event)
        return
    state.session_closed = True
    state.session_end_payload = payload


def _on_session_end_error(state: _ScanState, event: JournalEvent) -> None:
    if state.session_closed:
        _on_duplicate(state, event)
        return
    state.session_closed = True
    state.session_error = True
    state.findings.append(_finding_scan("session_end_error", state, None, event.offset))


def _on_channel_end(state: _ScanState, event: JournalEvent) -> None:
    if state.channel_seen:
        _on_duplicate(state, event)
        return
    state.channel_seen = True
    channel = cast(ChannelEnd, event.payload)
    state.findings.extend(_channel_findings(channel, state.execution_id, event.offset))
