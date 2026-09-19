"""Contratos de fases y disposición nativa (SH-P03a/1 §5-§6).

Cada test construye un journal completo con dos ejecuciones y observa la
salida de reconcile_pytest. Los expected son literales del contrato: la
pareja make/log por instancia, las ocho reglas de disposición y el orden
setup→call→teardown, sin fabricar fases ni confundir terminal con PASS.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from tools.wct.evidence.pytest_observation import decode_pytest_journal, reconcile_pytest
from tools.wct.evidence.pytest_types import ExecutionExpectation, JournalObservation

RUN_ID = "0" * 32
D64 = "a" * 64
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
UTC = "2026-09-08T00:00:00.000000+00:00"
UTC2 = "2026-09-08T00:00:00.000001+00:00"


def _executions() -> tuple[ExecutionExpectation, ...]:
    return (
        ExecutionExpectation("collection-1", "collection", D64, D64, D64),
        ExecutionExpectation("producer-1", "producer", D64, D64, D64),
    )


def _dump(value: object) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
        ).encode("utf-8")
        + b"\n"
    )


class Builder:
    """Constructor de journals canónicos con seq/local_seq automáticos."""

    def __init__(self) -> None:
        self.seq = 0
        self.local = {0: 0, 1: 0}
        self.lines: list[bytes] = []

    def sup(self, ex: int, code: int, payload: list[object]) -> None:
        self.seq += 1
        self.lines.append(_dump([self.seq, ex, None, code, payload]))

    def ev(self, ex: int, code: int, payload: list[object]) -> None:
        self.seq += 1
        self.local[ex] += 1
        self.lines.append(_dump([self.seq, ex, self.local[ex], code, payload]))

    def bytes(self) -> bytes:
        return _header() + b"".join(self.lines)


def _header() -> bytes:
    return _dump(
        {
            "schema_version": 1,
            "record_type": "wct-pytest-journal",
            "run_id": RUN_ID,
            "executions": [
                ["collection-1", "collection", D64, D64, D64],
                ["producer-1", "producer", D64, D64, D64],
            ],
        }
    )


def _start(b: Builder, ex: int) -> None:
    b.sup(ex, 1, [["python", "-m", "pytest"], "/r", 0, 1, UTC])


def _close(b: Builder, ex: int, *, exit_code: int = 0) -> None:
    b.ev(ex, 6, [0])
    b.ev(ex, 19, [exit_code, exit_code])
    b.sup(ex, 2, [True, 0, None, None])
    b.sup(ex, 3, [exit_code, "exited", None, 0, EMPTY_SHA, 2, UTC2, False])


def _session_head(b: Builder, ex: int, *, declare: bool = True) -> None:
    b.ev(ex, 4, ["9.1.1", "1.6.0", "wct-pytest-observer/1", D64])
    b.ev(ex, 7, [D64, True])
    if declare:
        b.sup(ex, 0, [0, "t"])
    b.ev(ex, 8, [0, False])
    b.ev(ex, 11, [0])
    b.ev(ex, 12, [1, 0])


def _phase(b: Builder, ex: int, phase: int, outcome: int, **opts: object) -> None:
    kind = opts.get("kind")
    if kind != "log":
        b.ev(
            ex,
            14,
            [
                0,
                phase,
                outcome,
                opts.get("present", False),
                None,
                opts.get("wasxfail", False),
                opts.get("xfail"),
            ],
        )
    else:
        b.ev(ex, 15, [0, phase, outcome, opts.get("wasxfail", False)])


def _test_block(b: Builder, ex: int, phases: list[tuple[int, int]], **opts: object) -> None:
    if opts.get("start", True):
        b.ev(ex, 13, [0])
    for phase, outcome in phases:
        _phase(b, ex, phase, outcome)
        if opts.get("logs", True):
            _phase(b, ex, phase, outcome, kind="log")
    if opts.get("end", True):
        b.ev(ex, 16, [0])


def _base_journal(phases: list[tuple[int, int]] | None = None, *, exit_code: int = 0) -> bytes:
    """Colección íntegra más un productor con un test de tres fases dadas."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    _test_block(b, 1, phases if phases is not None else [(0, 0), (1, 0), (2, 0)])
    _close(b, 1, exit_code=exit_code)
    return b.bytes()


def _decoded(data: bytes) -> JournalObservation:
    """Decodifica el journal del test con los argumentos canónicos."""
    return decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )


def _producer(result: object) -> object:
    return result.executions[1]


def _codes(result: object) -> list[str]:
    return [finding.code for finding in result.findings]


def test_passing_test_is_terminal_pass_eligible_and_complete() -> None:
    """Control válido: tres passed, terminal, pass_eligible, sin findings."""
    result = reconcile_pytest(_decoded(_base_journal()), expected=("t",), property_ids=())
    producer = _producer(result)

    assert producer.protocol_complete is True
    assert producer.exit_code == 0
    assert producer.termination == "exited"
    assert len(producer.tests) == 1
    test = producer.tests[0]
    assert (test.nodeid, test.start_seq) == ("t", 18)
    assert test.terminal is True
    assert test.pass_eligible is True
    assert test.call_disposition == "observed"
    assert [phase.disposition for phase in test.phases] == ["passed"] * 3
    assert result.findings == ()
    assert result.identities.status == "match"
    assert result.preflight_identities.status == "match"
    assert result.provenance == "caller-supplied-unverified"


@pytest.mark.parametrize(
    ("phases", "exit_code", "dispositions", "disposition"),
    [
        ([(0, 0), (1, 1), (2, 0)], 1, ["passed", "failed", "passed"], "observed"),
        ([(0, 1), (2, 0)], 1, ["failed", "passed"], "not_scheduled"),
        ([(0, 2), (2, 0)], 0, ["skipped", "passed"], "not_scheduled"),
        ([(0, 0), (1, 0), (2, 1)], 1, ["passed", "passed", "failed"], "observed"),
        ([(0, 0), (1, 2), (2, 0)], 0, ["passed", "skipped", "passed"], "observed"),
    ],
)
def test_failed_terminal_preserved_with_native_disposition(
    phases: list[tuple[int, int]],
    exit_code: int,
    dispositions: list[str],
    disposition: str,
) -> None:
    """Fallo nativo visible: terminal True pero pass_eligible False."""
    result = reconcile_pytest(
        _decoded(_base_journal(phases, exit_code=exit_code)), expected=("t",), property_ids=()
    )
    producer = _producer(result)
    test = producer.tests[0]

    assert producer.protocol_complete is True
    assert producer.exit_code == exit_code
    assert test.terminal is True
    assert test.pass_eligible is False
    assert test.call_disposition == disposition
    assert [phase.disposition for phase in test.phases] == dispositions
    assert _codes(result) == []


def test_xfail_family_dispositions() -> None:
    """xfail/xpass según §6, sin reevaluar markers ni clasificar por tipo."""
    xfail = [True, False, True]
    strict = [True, True, True]
    scenarios = [
        (
            "xfail-call",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 2, False, None, True, xfail]),
                (15, [0, 1, 2, True]),
                (14, [0, 2, 0, False, None, False, None]),
                (15, [0, 2, 0, False]),
            ],
            0,
            ["passed", "xfail", "passed"],
            True,
        ),
        (
            "xfail-explicit-setup",
            [
                (14, [0, 0, 2, False, None, True, xfail]),
                (15, [0, 0, 2, True]),
                (14, [0, 2, 0, False, None, False, None]),
                (15, [0, 2, 0, False]),
            ],
            0,
            ["xfail", "passed"],
            True,
        ),
        (
            "xpass",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 0, False, None, True, None]),
                (15, [0, 1, 0, True]),
                (14, [0, 2, 0, False, None, False, None]),
                (15, [0, 2, 0, False]),
            ],
            0,
            ["passed", "xpass", "passed"],
            True,
        ),
        (
            "xpass-and-teardown-xfail",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 0, False, None, True, None]),
                (15, [0, 1, 0, True]),
                (14, [0, 2, 2, False, None, True, xfail]),
                (15, [0, 2, 2, True]),
            ],
            0,
            ["passed", "xpass", "xfail"],
            True,
        ),
        (
            "xpass-strict",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 1, False, None, False, strict]),
                (15, [0, 1, 1, False]),
                (14, [0, 2, 0, False, None, False, None]),
                (15, [0, 2, 0, False]),
            ],
            1,
            ["passed", "xpass_strict", "passed"],
            True,
        ),
        (
            "raises-mismatch-stays-failed",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 1, True, "TypeError", False, strict]),
                (15, [0, 1, 1, False]),
                (14, [0, 2, 0, False, None, False, None]),
                (15, [0, 2, 0, False]),
            ],
            1,
            ["passed", "failed", "passed"],
            True,
        ),
        (
            "xfail-teardown-after-xpass-call",
            [
                (14, [0, 0, 0, False, None, False, None]),
                (15, [0, 0, 0, False]),
                (14, [0, 1, 0, False, None, True, xfail]),
                (15, [0, 1, 0, True]),
                (14, [0, 2, 2, False, None, True, xfail]),
                (15, [0, 2, 2, True]),
            ],
            0,
            ["passed", "xpass", "xfail"],
            True,
        ),
    ]
    for name, events, exit_code, dispositions, terminal in scenarios:
        b = Builder()
        _start(b, 0)
        _session_head(b, 0)
        _close(b, 0, exit_code=0)
        _start(b, 1)
        _session_head(b, 1, declare=False)
        b.ev(1, 13, [0])
        for code, payload in events:
            b.ev(1, code, payload)
        b.ev(1, 16, [0])
        _close(b, 1, exit_code=exit_code)

        result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
        test = _producer(result).tests[0]
        assert [phase.disposition for phase in test.phases] == dispositions, name
        assert test.terminal is terminal, name
        assert test.pass_eligible is False, name


def test_passed_with_raw_exception_is_inconsistent() -> None:
    """Passed + exception_present → inconsistent con report_inconsistent."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 1, 0, True, "AssertionError", False, None])
    b.ev(1, 15, [0, 1, 0, False])
    b.ev(1, 14, [0, 0, 0, False, None, False, None])
    b.ev(1, 15, [0, 0, 0, False])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.pass_eligible is False
    assert [phase.disposition for phase in test.phases] == ["inconsistent", "passed", "passed"]
    assert "report_inconsistent" in _codes(result)


def test_xpass_outside_call_is_inconsistent() -> None:
    """Passed + wasxfail en setup/teardown → inconsistent (regla 3)."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 0, 0, False, None, True, None])
    b.ev(1, 15, [0, 0, 0, True])
    b.ev(1, 14, [0, 1, 0, False, None, False, None])
    b.ev(1, 15, [0, 1, 0, False])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.phases[0].disposition == "inconsistent"
    assert "report_inconsistent" in _codes(result)


def _pair_scenario_events(scenario: str) -> list[tuple[int, list[object]]]:
    """Eventos de fase del escenario literal pedido por la tabla."""
    events: list[tuple[int, list[object]]] = []
    if scenario == "make_without_log":
        events.append((14, [0, 0, 0, False, None, False, None]))
        events.append((14, [0, 1, 0, False, None, False, None]))
        events.append((15, [0, 1, 0, False]))
        events.append((14, [0, 2, 0, False, None, False, None]))
        events.append((15, [0, 2, 0, False]))
    elif scenario == "log_without_make":
        events.append((15, [0, 0, 0, False]))
    elif scenario == "outcome_mismatch":
        events.append((14, [0, 0, 0, False, None, False, None]))
        events.append((15, [0, 0, 1, False]))
    elif scenario == "wasxfail_mismatch":
        events.append((14, [0, 0, 0, False, None, False, None]))
        events.append((15, [0, 0, 0, True]))
    elif scenario == "duplicate_make":
        events.append((14, [0, 0, 0, False, None, False, None]))
        events.append((15, [0, 0, 0, False]))
        events.append((14, [0, 0, 1, False, None, False, None]))
        events.append((15, [0, 0, 1, False]))
    else:
        events.append((14, [0, 0, 0, False, None, False, None]))
        events.append((15, [0, 0, 0, False]))
        events.append((14, [0, 1, 0, False, None, False, None]))
        events.append((15, [0, 1, 0, False]))
        events.append((15, [0, 1, 0, False]))
    return events


def _pair_tail_events(scenario: str) -> list[tuple[int, int]]:
    """Fases restantes del bloque tras el evento defectuoso del escenario."""
    if scenario == "make_without_log":
        return []
    if scenario == "duplicate_log":
        return [(2, 0)]
    return [(1, 0), (2, 0)]


@pytest.mark.parametrize(
    ("scenario", "codes"),
    [
        ("make_without_log", ["report_pair_mismatch"]),
        ("log_without_make", ["report_pair_mismatch"]),
        ("outcome_mismatch", ["report_pair_mismatch"]),
        ("wasxfail_mismatch", ["report_pair_mismatch"]),
        ("duplicate_make", ["duplicate_phase", "duplicate_phase", "report_pair_mismatch"]),
        ("duplicate_log", ["duplicate_phase", "report_pair_mismatch"]),
    ],
)
def test_pair_cardinality_and_coherence(scenario: str, codes: list[str]) -> None:
    """La pareja (execution, start_seq, phase) es 1-a-1 y coherente."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    for code, payload in _pair_scenario_events(scenario):
        b.ev(1, code, payload)
    _test_block(b, 1, _pair_tail_events(scenario), start=False, end=False)
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.pass_eligible is False
    assert sorted(_codes(result)) == codes
    if scenario == "make_without_log":
        assert len(test.phases) == 3
    if scenario == "log_without_make":
        assert len(test.phases) == 2


def test_phase_order_inversions() -> None:
    """Invertir setup→call→teardown agrega phase_order."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 14, [0, 0, 0, False, None, False, None])
    b.ev(1, 15, [0, 0, 0, False])
    b.ev(1, 14, [0, 1, 0, False, None, False, None])
    b.ev(1, 15, [0, 1, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())

    assert "phase_order" in _codes(result)
    assert _producer(result).tests[0].terminal is False


def test_call_after_nonpass_setup_is_unexpected() -> None:
    """Call presente tras setup no-PASS → unexpected_phase, sin inventar fases."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 0, 1, False, None, False, None])
    b.ev(1, 15, [0, 0, 1, False])
    b.ev(1, 14, [0, 1, 0, False, None, False, None])
    b.ev(1, 15, [0, 1, 0, False])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=1)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert "unexpected_phase" in _codes(result)
    assert [phase.phase for phase in test.phases] == ["setup", "call", "teardown"]
    assert test.call_disposition == "observed"


def test_missing_required_phases() -> None:
    """Sin teardown o sin call tras setup passed → missing_phase y no terminal."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    _test_block(b, 1, [(0, 0), (1, 0)], end=False)
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert "missing_phase" in _codes(result)
    assert test.terminal is False
    assert test.call_disposition == "observed"


def test_call_disposition_missing_without_setup_make() -> None:
    """Sin make de setup, call_disposition es missing, no not_scheduled."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.call_disposition == "missing"
    assert "missing_phase" in _codes(result)


def test_missing_test_end_and_overlapping_start() -> None:
    """test_start solapado deja la instancia previa incompleta (missing_test_end)."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 0, 0, False, None, False, None])
    b.ev(1, 15, [0, 0, 0, False])
    b.ev(1, 13, [0])
    _test_block(b, 1, [(0, 0), (1, 0), (2, 0)], start=False)
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    producer = _producer(result)

    assert len(producer.tests) == 2
    assert producer.tests[0].terminal is False
    assert producer.tests[1].terminal is True
    assert "missing_test_end" in _codes(result)


def test_two_complete_instances_same_nodeid() -> None:
    """Dos instancias completas del mismo nodeid: start_seq distinto, sin dedup."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    _test_block(b, 1, [(0, 0), (1, 0), (2, 0)], end=False)
    b.ev(1, 16, [0])
    _test_block(b, 1, [(0, 0), (1, 0), (2, 0)], end=False)
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    producer = _producer(result)

    assert [test.start_seq for test in producer.tests] == [18, 26]
    assert all(test.terminal for test in producer.tests)
    assert all(test.pass_eligible for test in producer.tests)
    assert "duplicate_phase" not in _codes(result)
    assert "test_order" not in _codes(result)
    assert result.identities.status == "invalid"
    assert any(
        finding.code == "duplicate_identity" and finding.inventory == "executed"
        for finding in result.identities.findings
    )


def test_orphan_phase_and_foreign_test_end() -> None:
    """Fases fuera de una instancia activa o test_end ajeno → test_order."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 14, [0, 0, 0, False, None, False, None])
    b.ev(1, 13, [0])
    _test_block(b, 1, [(0, 0), (1, 0), (2, 0)], start=False)
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())

    assert _codes(result).count("test_order") >= 1


def test_log_before_make_invalidates_the_pair() -> None:
    """R03-02: make antes de log; el intercambio invalida pareja y terminal."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    _phase(b, 1, 0, 0, kind="log")
    _phase(b, 1, 0, 0)
    _test_block(b, 1, [(1, 0), (2, 0)], start=False, end=False)
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.pass_eligible is False
    assert sorted(_codes(result)) == ["report_pair_mismatch"]


def test_call_make_before_setup_log_is_phase_order() -> None:
    """R03-02: el orden setup→call→teardown rige cada evento de fase."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    _phase(b, 1, 0, 0)
    _phase(b, 1, 1, 0)
    _phase(b, 1, 0, 0, kind="log")
    _phase(b, 1, 1, 0, kind="log")
    _phase(b, 1, 2, 0)
    _phase(b, 1, 2, 0, kind="log")
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.pass_eligible is False
    assert sorted(_codes(result)) == ["phase_order"]


def test_phase_repetition_after_later_phase_is_phase_order_too() -> None:
    """R03-02: reentrar a setup tras call es inversión y también duplicado."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    _phase(b, 1, 0, 0)
    _phase(b, 1, 0, 0, kind="log")
    _phase(b, 1, 1, 0)
    _phase(b, 1, 1, 0, kind="log")
    _phase(b, 1, 0, 0)
    _phase(b, 1, 0, 0, kind="log")
    _phase(b, 1, 2, 0)
    _phase(b, 1, 2, 0, kind="log")
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert test.terminal is False
    assert test.pass_eligible is False
    assert sorted(_codes(result)) == [
        "duplicate_phase",
        "duplicate_phase",
        "phase_order",
        "report_pair_mismatch",
    ]


def test_passed_call_with_strict_xfail_is_inconsistent() -> None:
    """Regla 7: passed en call con xfail estricto es inconsistente."""
    b = Builder()
    _start(b, 0)
    _session_head(b, 0)
    _close(b, 0, exit_code=0)
    _start(b, 1)
    _session_head(b, 1, declare=False)
    b.ev(1, 13, [0])
    b.ev(1, 14, [0, 0, 0, False, None, False, [True, True, True]])
    b.ev(1, 15, [0, 0, 0, False])
    b.ev(1, 14, [0, 1, 0, False, None, False, [True, True, True]])
    b.ev(1, 15, [0, 1, 0, True])
    b.ev(1, 14, [0, 2, 0, False, None, False, None])
    b.ev(1, 15, [0, 2, 0, False])
    b.ev(1, 16, [0])
    _close(b, 1, exit_code=0)

    result = reconcile_pytest(_decoded(b.bytes()), expected=("t",), property_ids=())
    test = _producer(result).tests[0]

    assert [phase.disposition for phase in test.phases] == [
        "passed",
        "inconsistent",
        "passed",
    ]
    assert test.terminal is False
    assert test.pass_eligible is False
    assert "report_inconsistent" in [finding.code for finding in result.findings]
