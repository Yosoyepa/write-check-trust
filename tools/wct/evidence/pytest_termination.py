"""Consistencia exit/termination/señal y findings de execution_end (§5)."""

from typing import cast

from tools.wct.evidence.pytest_payloads import ExecutionEnd
from tools.wct.evidence.pytest_scan_open import _on_duplicate
from tools.wct.evidence.pytest_scan_state import _finding_scan, _ScanState
from tools.wct.evidence.pytest_types import JournalEvent

_ADMISSIBLE_EXIT = (0, 1)

_EXIT_ABS_MAX = 255

_SIGNAL_MAX = 64


def _natural_exit(code: object, signal: object) -> bool:
    """Salida natural observada: exit 0..255 y sin señal."""
    return type(code) is int and 0 <= code <= _EXIT_ABS_MAX and signal is None


def _signalled_exit(code: object, signal: object) -> bool:
    """Salida por señal: señal 1..64 y exit = -señal."""
    return type(signal) is int and 1 <= signal <= _SIGNAL_MAX and code == -signal


def _absent_exit(code: object, signal: object) -> bool:
    """Salida no observable: ambos campos ausentes."""
    return code is None and signal is None


def _termination_ok(payload: ExecutionEnd) -> bool:
    """Tabla exit/termination/señal del §5."""
    termination, code, signal = payload.termination, payload.exit_code, payload.signal
    if termination == "exited":
        return _natural_exit(code, signal)
    if termination == "signal":
        return _signalled_exit(code, signal)
    if termination == "launch_error":
        return _absent_exit(code, signal)
    return (
        _natural_exit(code, signal) or _signalled_exit(code, signal) or _absent_exit(code, signal)
    )


def _on_execution_end(state: _ScanState, event: JournalEvent) -> None:
    if state.execution_end_seen:
        _on_duplicate(state, event)
        return
    state.execution_end_seen = True
    state.ended = True
    state.end_seq = event.seq
    payload = cast(ExecutionEnd, event.payload)
    state.end_payload = payload
    state.end_offset = event.offset
    state.exit_code = payload.exit_code
    state.termination = payload.termination
    _execution_end_findings(state, event, payload)


def _launch_error_with_activity(state: _ScanState, payload: ExecutionEnd) -> bool:
    """launch_error no convive con sesión, tests ni instancia abierta (§5)."""
    return payload.termination == "launch_error" and bool(
        state.session_started or state.tests or state.active is not None
    )


def _exit_disagreement(state: _ScanState) -> bool:
    """Exit observado difiere del declarado por session_end con exited."""
    session_end = state.session_end_payload
    return (
        session_end is not None
        and state.termination == "exited"
        and (state.exit_code != session_end.observed_exit)
    )


def _exit_coherence_findings(state: _ScanState, event: JournalEvent, payload: ExecutionEnd) -> None:
    """Coherencia de termination, exit y señal del §5."""
    if not _termination_ok(payload) or _launch_error_with_activity(state, payload):
        state.findings.append(_finding_scan("termination_inconsistent", state, None, event.offset))
    if state.termination == "exited" and state.exit_code not in _ADMISSIBLE_EXIT:
        state.findings.append(_finding_scan("abnormal_exit", state, None, event.offset))
    if _exit_disagreement(state):
        state.findings.append(_finding_scan("exit_disagreement", state, None, event.offset))


def _bounds_findings(state: _ScanState, event: JournalEvent, payload: ExecutionEnd) -> None:
    """Límites de log y truncamiento declarado (§5)."""
    start = state.start_payload
    if start is not None and (
        payload.log_end < start.log_start or payload.monotonic_ns < start.monotonic_ns
    ):
        state.findings.append(_finding_scan("execution_bounds", state, None, event.offset))
    if payload.log_truncated:
        state.findings.append(_finding_scan("log_truncated", state, None, event.offset))


def _execution_end_findings(state: _ScanState, event: JournalEvent, payload: ExecutionEnd) -> None:
    """Consistencia de salida, límites y divergencias del §5."""
    _exit_coherence_findings(state, event, payload)
    _bounds_findings(state, event, payload)
