"""Golden y mapa literal de casos SH-P03a/1 (§8-§9) y binding del feature.

El golden aprobado viaja byte a byte como literal de este módulo (30 líneas,
1938 bytes, SHA-256 verificado en un test): la suite no depende de una ruta
temporal ni regenera los bytes con el SUT. Cada ID del contrato es un caso de
``test_observation_case`` con expected literales independientes del SUT.
"""

from __future__ import annotations

from collections.abc import Callable
import dataclasses
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path

import pytest

from tools.wct.accept.pipeline import ir_dry, parse_feature
from tools.wct.evidence import pytest_inventory as pinv, pytest_sequence as pseq
from tools.wct.evidence.pytest_observation import decode_pytest_journal, reconcile_pytest
from tools.wct.evidence.pytest_payloads import ExecutionStart, NodeDeclaration, SessionStart
from tools.wct.evidence.pytest_types import (
    ExecutionExpectation,
    JournalEvent,
    JournalObservation,
    ObservationError,
    ProtocolFinding,
)

RUN_ID = "0" * 32
OTHER_RUN_ID = "1" * 32
D64 = "a" * 64
UTC = "2026-09-08T00:00:00.000000+00:00"
UTC2 = "2026-09-08T00:00:00.000001+00:00"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
GOLDEN_SHA256 = "52eed49e69f6d98da227347396eaa42a57d0c854e93cd662c75d9e76173a6730"
FEATURE = Path(__file__).parents[2] / "features" / "wct-pytest-observation-001.feature"

GOLDEN_LINES: tuple[bytes, ...] = (
    b'{"executions":[["collection-1","collection","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],["producer-1","producer","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]],"record_type":"wct-pytest-journal","run_id":"00000000000000000000000000000000","schema_version":1}\n',
    b'[1,0,null,1,[["python","-m","pytest"],"/r",0,1,"2026-09-08T00:00:00.000000+00:00"]]\n',
    b'[2,0,1,4,["9.1.1","1.6.0","wct-pytest-observer/1","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]]\n',
    b'[3,0,2,7,["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",true]]\n',
    b'[4,0,null,0,[0,"t"]]\n',
    b"[5,0,3,8,[0,false]]\n",
    b"[6,0,4,11,[0]]\n",
    b"[7,0,5,12,[1,0]]\n",
    b"[8,0,6,6,[0]]\n",
    b"[9,0,7,19,[0,0]]\n",
    b"[10,0,null,2,[true,0,null,null]]\n",
    b'[11,0,null,3,[0,"exited",null,0,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",2,"2026-09-08T00:00:00.000001+00:00",false]]\n',
    b'[12,1,null,1,[["python","-m","pytest"],"/r",0,1,"2026-09-08T00:00:00.000000+00:00"]]\n',
    b'[13,1,1,4,["9.1.1","1.6.0","wct-pytest-observer/1","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]]\n',
    b'[14,1,2,7,["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",true]]\n',
    b"[15,1,3,8,[0,false]]\n",
    b"[16,1,4,11,[0]]\n",
    b"[17,1,5,12,[1,0]]\n",
    b"[18,1,6,13,[0]]\n",
    b"[19,1,7,14,[0,0,0,false,null,false,null]]\n",
    b"[20,1,8,15,[0,0,0,false]]\n",
    b"[21,1,9,14,[0,1,0,false,null,false,null]]\n",
    b"[22,1,10,15,[0,1,0,false]]\n",
    b"[23,1,11,14,[0,2,0,false,null,false,null]]\n",
    b"[24,1,12,15,[0,2,0,false]]\n",
    b"[25,1,13,16,[0]]\n",
    b"[26,1,14,6,[0]]\n",
    b"[27,1,15,19,[0,0]]\n",
    b"[28,1,null,2,[true,0,null,null]]\n",
    b'[29,1,null,3,[0,"exited",null,0,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",2,"2026-09-08T00:00:00.000001+00:00",false]]\n',
)

GOLDEN = b"".join(GOLDEN_LINES)

EXPECTED_ROWS = [
    ("PA01", "protocol_complete", "true"),
    ("PA02", "decoder_prefix_preserved", "true"),
    ("PA03", "framing_defect_visible", "true"),
    ("PA04", "phase_defect_visible", "true"),
    ("PA05", "failed_terminal_preserved", "true"),
    ("PA06", "identity_substitution_detected", "true"),
    ("PA07", "property_mismatch_detected", "true"),
    ("PA08", "exit_not_replaced", "true"),
    ("PA09", "exact_boundary_allowed", "true"),
    ("PA10", "over_boundary_rejected", "true"),
    ("PA11", "provenance", "caller-supplied-unverified"),
    ("PA12", "invalid_argument_rejected", "true"),
]


def _executions() -> tuple[ExecutionExpectation, ...]:
    return (
        ExecutionExpectation("collection-1", "collection", D64, D64, D64),
        ExecutionExpectation("producer-1", "producer", D64, D64, D64),
    )


def _dump(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _line(seq: int, ex: int, local: int | None, code: int, payload: list[object]) -> bytes:
    return _dump([seq, ex, local, code, payload])


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


class Journal:
    """Constructor de journals canónicos con seq/local_seq automáticos."""

    def __init__(self) -> None:
        self.seq = 0
        self.local: dict[int, int] = {0: 0, 1: 0}
        self.lines: list[bytes] = []

    def sup(self, ex: int, code: int, payload: list[object]) -> None:
        self.seq += 1
        self.lines.append(_dump([self.seq, ex, None, code, payload]))

    def ev(self, ex: int, code: int, payload: list[object]) -> None:
        self.seq += 1
        self.local[ex] += 1
        self.lines.append(_dump([self.seq, ex, self.local[ex], code, payload]))

    def start(self, ex: int) -> None:
        self.sup(ex, 1, [["python", "-m", "pytest"], "/r", 0, 1, UTC])

    def session(self, ex: int, *, profile_match: bool = True) -> None:
        self.ev(ex, 4, ["9.1.1", "1.6.0", "wct-pytest-observer/1", D64])
        self.ev(ex, 7, [D64, profile_match])

    def declare(self, index: int, nodeid: str) -> None:
        self.sup(0, 0, [index, nodeid])

    def item(self, ex: int, index: int, *, is_property: bool = False) -> None:
        self.ev(ex, 8, [index, is_property])

    def deselect(self, ex: int, index: int, *, is_property: bool = True) -> None:
        self.ev(ex, 10, [index, is_property])

    def select(self, ex: int, index: int) -> None:
        self.ev(ex, 11, [index])

    def collect_end(self, ex: int, *, selected: int, deselected: int = 0) -> None:
        self.ev(ex, 12, [selected, deselected])

    def plugin_claim(
        self, ex: int, name: str, *, qualified: bool = True, version: str | None = "1.0"
    ) -> None:
        self.ev(ex, 5, [name, "mod", "dist", version, None, qualified])

    def plugins_end(self, ex: int, *, count: int = 0) -> None:
        self.ev(ex, 6, [count])

    def session_end(self, ex: int, *, argument: int = 0, observed: int = 0) -> None:
        self.ev(ex, 19, [argument, observed])

    def channel(self, ex: int, *, tail: tuple[object, ...] | None = None) -> None:
        self.sup(ex, 2, list(tail) if tail is not None else [True, 0, None, None])

    def execution_end(self, ex: int, **options: object) -> None:
        exit_code: int | None = options.get("exit_code", 0)
        termination: str = options.get("termination", "exited")
        signal: int | None = options.get("signal")
        log_start: int = options.get("log_start", 0)
        truncated: bool = options.get("truncated", False)
        self.sup(
            ex,
            3,
            [exit_code, termination, signal, log_start, EMPTY_SHA, 2, UTC2, truncated],
        )

    def test_start(self, ex: int, *, index: int = 0) -> None:
        self.ev(ex, 13, [index])

    def test_end(self, ex: int, *, index: int = 0) -> None:
        self.ev(ex, 16, [index])

    def diagnostic(self, ex: int, code: int) -> None:
        self.ev(ex, code, ["RuntimeError"])

    def phases(
        self, ex: int, index: int, entries: list[tuple[int, int]], **options: object
    ) -> None:
        """Emite pares make/log de fase con las variantes literales pedidas."""
        present: dict[int, bool] | None = options.get("present")
        wasxfail: dict[int, bool] | None = options.get("wasxfail")
        xfail: list[bool] | None = options.get("xfail")
        log_outcome: dict[int, int] | None = options.get("log_outcome")
        log_wasxfail: dict[int, bool] | None = options.get("log_wasxfail")
        skip_logs: set[int] | None = options.get("skip_logs")
        skip_makes: set[int] | None = options.get("skip_makes")
        extra_make: set[int] | None = options.get("extra_make")
        extra_log: set[int] | None = options.get("extra_log")
        for phase, outcome in entries:
            if skip_makes and phase in skip_makes:
                self.ev(ex, 15, [index, phase, outcome, False])
                continue
            raw_present = (present or {}).get(phase, False)
            self.ev(
                ex,
                14,
                [
                    index,
                    phase,
                    outcome,
                    raw_present,
                    "AssertionError" if raw_present else None,
                    (wasxfail or {}).get(phase, False),
                    xfail,
                ],
            )
            if skip_logs and phase in skip_logs:
                continue
            log_flag = (log_wasxfail or {}).get(phase, (wasxfail or {}).get(phase, False))
            self.ev(ex, 15, [index, phase, (log_outcome or {}).get(phase, outcome), log_flag])
        for _phase in extra_make or set():
            self.ev(ex, 14, [index, _phase, 0, False, None, False, None])
        for _phase in extra_log or set():
            self.ev(ex, 15, [index, 0, 0, False])

    def bytes(self) -> bytes:
        return _header() + b"".join(self.lines)


def _collection(j: Journal, **spec: object) -> None:
    """Colección completa de la ejecución 0 con variantes por parámetro."""
    nodeids: tuple[str, ...] = spec.get("nodeids", ("t",))
    flags: tuple[bool, ...] = spec.get("flags", (False,))
    deselects: tuple[int, ...] = spec.get("deselects", ())
    selected: tuple[int, ...] = spec.get("selected", (0,))
    end_counts: tuple[int, int] = spec.get("end_counts", (1, 0))
    plugins: list[tuple[str, dict[str, object]]] | None = spec.get("plugins")
    j.start(0)
    j.session(0)
    if spec.get("declare", True):
        for position, nodeid in enumerate(nodeids):
            j.declare(position, nodeid)
    item_indexes: tuple[int, ...] = spec.get("items", tuple(range(len(nodeids))))
    for index in item_indexes:
        flag = flags[index] if index < len(flags) else False
        j.item(0, index, is_property=flag)
    for index in deselects:
        flag = flags[index] if index < len(flags) else False
        j.deselect(0, index, is_property=flag)
    for index in selected:
        j.select(0, index)
    j.collect_end(0, selected=end_counts[0], deselected=end_counts[1])
    _collection_plugins(j, spec, plugins)
    j.plugins_end(0, count=len(plugins or []))
    _collection_close(j, spec)


def _collection_plugins(
    j: Journal,
    spec: dict[str, object],
    plugins: list[tuple[str, dict[str, object]]] | None,
) -> None:
    """Claims de plugin a mitad de sesión, tal cual lleguen."""
    mid_session = spec.get("mid_session")
    if callable(mid_session):
        mid_session(j)
    for name, extra in plugins or []:
        j.ev(
            0,
            5,
            [
                name,
                extra.get("module", "mod"),
                extra.get("dist", "dist"),
                extra.get("version", "1.0"),
                extra.get("sha", None),
                extra.get("qualified", True),
            ],
        )


def _collection_close(j: Journal, spec: dict[str, object]) -> None:
    """Cierres de sesión, canal y fin de ejecución con sus variantes."""
    end_payload: dict[str, object] | None = spec.get("end_payload")
    if spec.get("session_close", True) and not spec.get("session_error", False):
        j.session_end(
            0,
            argument=end_payload.get("argument", 0) if end_payload else 0,
            observed=end_payload.get("observed", 0) if end_payload else 0,
        )
    if spec.get("session_error", False):
        j.ev(0, 20, ["KeyboardInterrupt"])
    j.channel(0, tail=spec.get("channel"))
    options: dict[str, object] = end_payload or {}
    if spec.get("execution_close", True):
        j.sup(
            0,
            3,
            [
                options.get("exit_code", 0),
                options.get("termination", "exited"),
                options.get("signal"),
                options.get("log_start", 0),
                EMPTY_SHA,
                2,
                UTC2,
                options.get("truncated", False),
            ],
        )


def _producer_pass(j: Journal, **spec: object) -> None:
    """Productor completo con tests passed y cierres íntegros."""
    nodeid_count: int = spec.get("nodeid_count", 1)
    tests: int = spec.get("tests", 1)
    deselects: tuple[int, ...] = spec.get("deselects", ())
    end_counts: tuple[int, int] = spec.get("end_counts", (1, 0))
    selected: tuple[int, ...] = spec.get("selected", (0,))
    phase_entries: list[tuple[int, int]] | None = spec.get("phase_entries")
    phase_kw: dict[str, object] | None = spec.get("phase_kw")
    j.start(1)
    j.session(1)
    for index in range(nodeid_count):
        j.item(1, index)
    for index in deselects:
        j.deselect(1, index)
    for index in selected:
        j.select(1, index)
    j.collect_end(1, selected=end_counts[0], deselected=end_counts[1])
    for _number in range(tests):
        if spec.get("start_events", True):
            j.test_start(1)
        j.phases(
            1,
            0,
            phase_entries or [(0, 0), (1, 0), (2, 0)],
            **(phase_kw or {}),
        )
        j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)


def _standard() -> bytes:
    """Journal íntegro de control: colección más un test t passed."""
    j = Journal()
    _collection(j)
    _producer_pass(j)
    return j.bytes()


def _phases_run(
    entries: list[tuple[int, int]],
    *,
    exit_code: int = 0,
    phase_kw: dict[str, object] | None = None,
) -> bytes:
    """Productor con fases arbitrarias y colección íntegra previa."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, entries, **(phase_kw or {}))
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1, argument=exit_code, observed=exit_code)
    j.channel(1)
    j.execution_end(1, exit_code=exit_code)
    return j.bytes()


def _golden_offsets() -> list[int]:
    starts, position = [], 0
    for line in GOLDEN.splitlines(keepends=True):
        starts.append(position)
        position += len(line)
    return starts


def _decode_golden() -> JournalObservation:
    return decode_pytest_journal(GOLDEN, run_id=RUN_ID, executions=_executions(), max_bytes=1938)


@dataclass(frozen=True)
class Case:
    """Caso literal del mapa §9 con sus expectativas independientes."""

    id: str
    data: bytes | None = None
    run_id: str = RUN_ID
    max_bytes: int | None = None
    executions: tuple[ExecutionExpectation, ...] | None = None
    expected: tuple[str, ...] = ("t",)
    property_ids: tuple[str, ...] = ()
    patch: tuple[str, int] | None = None
    decode_raises: tuple[str, str] | None = None
    type_error_arg: str | None = None
    reconcile_raises: tuple[str, str] | None = None
    manual: Callable[[JournalObservation], JournalObservation] | None = None
    consumed: int | None = None
    tail_none: bool | None = None
    event_count: int | None = None
    decoder_finding: tuple[str, int] | None = None
    codes_include: tuple[str, ...] = ()
    codes_exclude: tuple[str, ...] = ()
    complete: tuple[bool, bool] | None = None
    exit_codes: tuple[int | None, int | None] | None = None
    termination: str | None = None
    start_seqs: tuple[int, ...] | None = None
    terminals: tuple[str, ...] | None = None
    eligible_all: bool | None = None
    dispositions: tuple[str, ...] | None = None
    call_disposition: str | None = None
    identity: str | None = None
    preflight: str | None = None
    identity_codes: tuple[str, ...] | None = None
    property_codes: tuple[str, ...] | None = None
    assert_that: Callable[[JournalObservation, object], None] | None = None
    findings_exact: tuple[tuple[str, str | None, str | None, int | None], ...] | None = None
    property_findings_exact: tuple[tuple[str, str | None, str | None, int | None], ...] | None = (
        None
    )


def test_golden_bytes_are_the_approved_literal() -> None:
    """El literal incrustado es byte-igual al golden aprobado (1938 bytes)."""
    assert len(GOLDEN) == 1938
    assert hashlib.sha256(GOLDEN).hexdigest() == GOLDEN_SHA256
    assert len(GOLDEN_LINES) == 30
    assert GOLDEN.endswith(b"\n")
    observation = decode_pytest_journal(
        GOLDEN, run_id=RUN_ID, executions=_executions(), max_bytes=1938
    )
    assert observation.consumed_bytes == len(GOLDEN)


def test_golden_offsets_match_the_contract() -> None:
    """Primer evento [573,657), último end_offset 1938, líneas contiguas."""
    offsets = _golden_offsets()
    assert offsets[1] == 573
    assert offsets[1] + len(GOLDEN_LINES[1]) == 657
    assert offsets[-1] + len(GOLDEN_LINES[-1]) == 1938
    assert offsets[0] + len(GOLDEN_LINES[0]) == offsets[1]
    observation = decode_pytest_journal(
        GOLDEN, run_id=RUN_ID, executions=_executions(), max_bytes=1938
    )
    assert [(event.offset, event.end_offset) for event in observation.events] == [
        (offsets[n], offsets[n] + len(line)) for n, line in enumerate(GOLDEN_LINES[1:], start=1)
    ]


def _check_golden_offsets(observation: JournalObservation, _result: object) -> None:
    """Offsets reales de las 29 líneas y start_seq 18 del único test."""
    offsets = _golden_offsets()
    assert (observation.events[0].offset, observation.events[0].end_offset) == (
        573,
        657,
    )
    assert observation.events[-1].end_offset == 1938
    for index, event in enumerate(observation.events):
        line = index + 1
        assert event.offset == offsets[line]
        assert event.end_offset == offsets[line] + len(GOLDEN_LINES[line])
    assert observation.events[17].kind == "test_start"
    assert observation.events[17].seq == 18


def _check_unicode_offsets(observation: JournalObservation, _result: object) -> None:
    """Tras la declaración de é, cada línea posterior corre un byte, no uno."""
    offsets = _golden_offsets()
    for index, event in enumerate(observation.events):
        line = index + 1
        start_shift = 1 if line >= 5 else 0
        end_shift = 1 if line >= 4 else 0
        assert event.offset == offsets[line] + start_shift
        assert event.end_offset == offsets[line] + len(GOLDEN_LINES[line]) + end_shift


def _unicode_variant() -> bytes:
    """Sustituye el único literal t de la declaración por é (un byte más)."""
    return GOLDEN.replace(b'[0,"t"]', b'[0,"\xc3\xa9"]')


def _permuted_nodeids() -> bytes:
    """Control válido con declaraciones opacas en otro orden y dos tests."""
    j = Journal()
    _collection(j, nodeids=("u", "t"), selected=(0, 1), end_counts=(2, 0))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 1)
    j.select(1, 0)
    j.select(1, 1)
    j.collect_end(1, selected=2)
    for index in (0, 1):
        j.test_start(1, index=index)
        j.phases(1, index, [(0, 0), (1, 0), (2, 0)])
        j.test_end(1, index=index)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _plugin_journal(name: str, *, qualified: bool, version: str | None = "1.0") -> bytes:
    """Run válido con un claim de plugin preservado tal cual."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugin_claim(1, name, qualified=qualified, version=version)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1, count=1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _claim_check(
    name: str, qualified: bool, version: str | None
) -> Callable[[JournalObservation, object], None]:
    """El claim viaja intacto y el provenance no cambia (se afirma aparte)."""

    def check(observation: JournalObservation, result: object) -> None:
        claims = [event.payload for event in observation.events if event.kind == "plugin"]
        assert claims
        assert claims[-1].name == name
        assert claims[-1].qualified is qualified
        assert claims[-1].version == version
        assert result.provenance == "caller-supplied-unverified"

    return check


def _options_claim_false() -> bytes:
    """Claim de opciones con profile_match=False, conservado tal cual."""
    j = Journal()
    j.start(0)
    j.session(0, profile_match=False)
    j.declare(0, "t")
    j.item(0, 0)
    j.select(0, 0)
    j.collect_end(0, selected=1)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    j.start(1)
    j.session(1, profile_match=False)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _opaque_context() -> bytes:
    j = Journal()
    _collection(j)
    j.sup(1, 1, [["pythön", "-k^^", "--x=ñ"], "/ópaque/µ-cwd", 0, 1, UTC])
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _opaque_context_check(observation: JournalObservation, _result: object) -> None:
    """argv/cwd opacos se conservan verbatim, sin normalización."""
    starts = [event.payload for event in observation.events if event.kind == "execution_start"]
    assert starts[1].cwd == "/ópaque/µ-cwd"
    assert starts[1].argv == ("pythön", "-k^^", "--x=ñ")


def _golden_with(line_number: int, replacement: bytes | None = None) -> bytes:
    """Variante del golden: sustituye, elimina (None) o añade al final."""
    lines = list(GOLDEN_LINES)
    if replacement is None:
        del lines[line_number]
    else:
        lines[line_number] = replacement
    return b"".join(lines)


def _utf8_broken() -> bytes:
    """Byte inválido de UTF-8 dentro de la línea del item (línea 6)."""
    position = _golden_offsets()[6] + 10
    return GOLDEN[:position] + b"\xff" + GOLDEN[position + 1 :]


def _incoherent(observation: JournalObservation) -> JournalObservation:
    """Evento manual imposible: execution_start con payload de otra clase."""
    events = list(observation.events)
    events[0] = dataclasses.replace(events[0], payload=SessionStart("9", "1", "o", D64))
    return dataclasses.replace(observation, events=tuple(events))


def _event_with_offset(
    observation: JournalObservation, index: int, **changes: int
) -> JournalObservation:
    events = list(observation.events)
    events[index] = dataclasses.replace(events[index], **changes)
    return dataclasses.replace(observation, events=tuple(events))


def _two_nodes_run() -> bytes:
    """Colección y productor con t y u, ambos seleccionados y passed."""
    j = Journal()
    _collection(j, nodeids=("t", "u"), selected=(0, 1), end_counts=(2, 0))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 1)
    j.select(1, 0)
    j.select(1, 1)
    j.collect_end(1, selected=2)
    for index in (0, 1):
        j.test_start(1, index=index)
        j.phases(1, index, [(0, 0), (1, 0), (2, 0)])
        j.test_end(1, index=index)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa01_cases() -> list[Case]:
    return [
        Case(
            "PA01-golden",
            data=GOLDEN,
            max_bytes=1938,
            complete=(True, True),
            exit_codes=(0, 0),
            identity="match",
            preflight="match",
            start_seqs=(18,),
            terminals=("t",),
            eligible_all=True,
            call_disposition="observed",
            dispositions=("passed", "passed", "passed"),
        ),
        Case(
            "PA01-permuted-opaque-nodeids",
            data=_permuted_nodeids(),
            expected=("u", "t"),
            complete=(True, True),
            identity="match",
            preflight="match",
        ),
        Case(
            "PA01-golden-offsets",
            data=GOLDEN,
            max_bytes=1938,
            complete=(True, True),
            assert_that=_check_golden_offsets,
        ),
        Case(
            "PA01-unicode-byte-offsets",
            data=_unicode_variant(),
            max_bytes=1939,
            expected=("é",),
            complete=(True, True),
            terminals=("é",),
            assert_that=_check_unicode_offsets,
        ),
        Case(
            "PA01-valid-control",
            data=_standard(),
            complete=(True, True),
            identity="match",
            preflight="match",
            eligible_all=True,
        ),
    ]


def _pa02_cases() -> list[Case]:
    duplicate_root = (
        GOLDEN_LINES[0][:-1]
        + b',"run_id":"'
        + RUN_ID.encode()
        + b'"}\n'
        + b"".join(GOLDEN_LINES[1:])
    )
    noncanonical = (
        b'{"executions": [["collection-1", "collection", "'
        + D64.encode()
        + b'", "'
        + D64.encode()
        + b'", "'
        + D64.encode()
        + b'"]], "record_type": "wct-pytest-journal", "run_id": "'
        + RUN_ID.encode()
        + b'", "schema_version": 1}\n'
    )
    return [
        Case(
            "PA02-invalid-utf8",
            data=_utf8_broken(),
            decoder_finding=("invalid_encoding", _golden_offsets()[6]),
            consumed=_golden_offsets()[6],
            event_count=5,
            tail_none=False,
        ),
        Case(
            "PA02-invalid-json",
            data=_golden_with(7, b"[7,0,5,12\n"),
            decoder_finding=("invalid_json", _golden_offsets()[7]),
            consumed=_golden_offsets()[7],
            event_count=6,
            tail_none=False,
        ),
        Case(
            "PA02-duplicate-root-key",
            data=duplicate_root,
            decoder_finding=("invalid_json", 0),
            consumed=0,
            event_count=0,
            codes_include=("missing_execution",),
        ),
        Case(
            "PA02-duplicate-nested-key",
            data=b'{"record_type":{"a":1,"a":2},"schema_version":1}\n',
            decoder_finding=("invalid_json", 0),
            consumed=0,
            event_count=0,
        ),
        Case(
            "PA02-noncanonical",
            data=noncanonical,
            decoder_finding=("noncanonical_json", 0),
            consumed=0,
            event_count=0,
        ),
        Case(
            "PA02-no-final-lf",
            data=GOLDEN[:-1],
            decoder_finding=("truncated_line", _golden_offsets()[29]),
            consumed=_golden_offsets()[29],
            event_count=28,
            tail_none=False,
        ),
        Case(
            "PA02-empty", data=b"", consumed=0, event_count=0, codes_include=("missing_execution",)
        ),
        Case(
            "PA02-valid-control",
            data=GOLDEN,
            max_bytes=1938,
            consumed=1938,
            tail_none=True,
            event_count=29,
        ),
    ]


def _pa03_build() -> dict[str, object]:
    """Journals de variantes PA03, construidos una sola vez por caso."""
    gap = (
        _header()
        + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
        + _line(3, 0, 1, 4, ["9", "1", "o", D64])
    )
    local_gap = (
        _header()
        + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
        + _line(2, 0, 3, 4, ["9", "1", "o", D64])
    )
    repeat = (
        _header()
        + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
        + _line(1, 0, 1, 4, ["9", "1", "o", D64])
    )
    sup_local = _header() + _line(1, 0, 1, 1, [["python"], "/r", 0, 1, UTC])
    depth = _dump(
        {
            "schema_version": 1,
            "record_type": "wct-pytest-journal",
            "run_id": RUN_ID,
            "executions": [[[[[[[[["x"]]]]]]]]],
        }
    )
    missing_ref = Journal()
    missing_ref.start(0)
    missing_ref.session(0)
    missing_ref.item(0, 3)
    missing_offset = len(_header()) + sum(len(line) for line in missing_ref.lines[:3])
    swapped_header = _dump(
        {
            "schema_version": 1,
            "record_type": "wct-pytest-journal",
            "run_id": RUN_ID,
            "executions": [
                ["producer-1", "producer", D64, D64, D64],
                ["collection-1", "collection", D64, D64, D64],
            ],
        }
    )
    float_line = (
        _header() + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC]) + _line(2, 0, 1, 6, [0.5])
    )
    bool_int = Journal()
    _collection(bool_int)
    bool_offset = len(_header()) + sum(len(line) for line in bool_int.lines[:6])
    bool_int.lines[6] = _line(7, 0, 4, 6, [True])
    return {
        "gap": gap,
        "local_gap": local_gap,
        "repeat": repeat,
        "sup_local": sup_local,
        "depth": depth,
        "missing_ref": missing_ref.bytes(),
        "missing_offset": missing_offset,
        "swapped_header": swapped_header,
        "float_line": float_line,
        "bool_int": _header() + b"".join(bool_int.lines),
        "bool_offset": bool_offset,
    }


def _pa03_header_cases() -> list[Case]:
    """Casos PA03 de cabecera y referencias de ejecución."""
    b = _pa03_build()
    return [
        Case(
            "PA03-schema",
            data=_dump(
                {
                    "schema_version": 2,
                    "record_type": "wct-pytest-journal",
                    "run_id": RUN_ID,
                    "executions": [],
                }
            ),
            decoder_finding=("unknown_schema", 0),
            consumed=0,
            event_count=0,
        ),
        Case(
            "PA03-event-code",
            data=_golden_with(8, _line(8, 0, 6, 99, [0])),
            decoder_finding=("unknown_event", _golden_offsets()[8]),
            event_count=7,
        ),
        Case(
            "PA03-extra-field",
            data=_dump(
                {
                    "schema_version": 1,
                    "record_type": "wct-pytest-journal",
                    "run_id": RUN_ID,
                    "executions": [],
                    "x": 1,
                }
            ),
            decoder_finding=("unknown_field", 0),
        ),
        Case(
            "PA03-missing-field",
            data=_dump({"schema_version": 1, "run_id": RUN_ID, "executions": []}),
            decoder_finding=("invalid_field", 0),
        ),
        Case(
            "PA03-global-seq-gap",
            data=b["gap"],
            decoder_finding=(
                "sequence_error",
                len(_header()) + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])),
            ),
            event_count=1,
        ),
        Case(
            "PA03-local-seq-gap",
            data=b["local_gap"],
            decoder_finding=(
                "sequence_error",
                len(_header()) + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])),
            ),
            event_count=1,
        ),
        Case(
            "PA03-seq-repeat",
            data=b["repeat"],
            decoder_finding=(
                "sequence_error",
                len(_header()) + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])),
            ),
            event_count=1,
        ),
        Case(
            "PA03-foreign-run",
            data=GOLDEN,
            run_id=OTHER_RUN_ID,
            decoder_finding=("foreign_reference", 0),
            consumed=0,
            event_count=0,
        ),
        Case(
            "PA03-supervisor-local-seq",
            data=b["sup_local"],
            decoder_finding=("sequence_error", len(_header())),
            event_count=0,
        ),
        Case(
            "PA03-header-execution-order",
            data=b["swapped_header"],
            decoder_finding=("foreign_reference", 0),
            event_count=0,
        ),
        Case(
            "PA03-float",
            data=b["float_line"],
            decoder_finding=(
                "invalid_json",
                len(_header()) + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])),
            ),
            event_count=1,
        ),
        Case("PA03-depth", data=b["depth"], decoder_finding=("invalid_json", 0), event_count=0),
        Case("PA03-valid-control", data=_standard(), complete=(True, True), event_count=29),
    ]


def _pa03_line_cases() -> list[Case]:
    """Casos PA03 de referencias de nodo y vectores payload."""
    b = _pa03_build()
    return [
        Case(
            "PA03-foreign-execution",
            data=_standard() + _line(30, 2, 1, 8, [0, False]),
            decoder_finding=("foreign_reference", len(_standard())),
            event_count=29,
            tail_none=False,
        ),
        Case(
            "PA03-reference-digest",
            data=GOLDEN,
            executions=(
                ExecutionExpectation("collection-1", "collection", "b" * 64, D64, D64),
                ExecutionExpectation("producer-1", "producer", D64, D64, D64),
            ),
            decoder_finding=("foreign_reference", 0),
            event_count=0,
        ),
        Case(
            "PA03-node-reference-missing",
            data=b["missing_ref"],
            decoder_finding=("foreign_reference", b["missing_offset"]),
            event_count=3,
        ),
        Case(
            "PA03-node-declaration-repeat-index",
            data=_header()
            + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
            + _line(2, 0, None, 0, [0, "t"])
            + _line(3, 0, None, 0, [0, "u"]),
            decoder_finding=(
                "invalid_field",
                len(_header())
                + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC]))
                + len(_line(2, 0, None, 0, [0, "t"])),
            ),
            event_count=2,
        ),
        Case(
            "PA03-node-declaration-repeat-string",
            data=_header()
            + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
            + _line(2, 0, None, 0, [0, "t"])
            + _line(3, 0, None, 0, [1, "t"]),
            decoder_finding=(
                "invalid_field",
                len(_header())
                + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC]))
                + len(_line(2, 0, None, 0, [0, "t"])),
            ),
            event_count=2,
        ),
        Case(
            "PA03-node-before-declaration",
            data=_header()
            + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
            + _line(2, 0, 1, 4, ["9", "1", "o", D64])
            + _line(3, 0, 2, 7, [D64, True])
            + _line(4, 0, 3, 8, [0, False]),
            decoder_finding=(
                "foreign_reference",
                len(_header())
                + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC]))
                + len(_line(2, 0, 1, 4, ["9", "1", "o", D64]))
                + len(_line(3, 0, 2, 7, [D64, True])),
            ),
            event_count=3,
        ),
        Case(
            "PA03-bool-int",
            data=b["bool_int"],
            decoder_finding=("invalid_field", b["bool_offset"]),
            event_count=6,
        ),
    ]


def _pa04_run(
    entries: list[tuple[int, int]],
    *,
    kw: dict[str, object] | None = None,
    end: bool = True,
    exit_code: int = 1,
) -> bytes:
    """Productor PA04 con fases arbitrarias, defecto de fallo y exit 1."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, entries, **(kw or {}))
    if end:
        j.test_end(1)
    j.plugins_end(1)
    j.session_end(1, argument=exit_code, observed=exit_code)
    j.channel(1)
    j.execution_end(1, exit_code=exit_code)
    return j.bytes()


def _pa04_pair_cases() -> list[Case]:
    """Casos PA04 de pareja make/log."""
    return [
        Case(
            "PA04-no-make",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"skip_makes": {0}}),
            codes_include=("report_pair_mismatch",),
            complete=(True, False),
        ),
        Case(
            "PA04-no-log",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"skip_logs": {0}}),
            codes_include=("report_pair_mismatch",),
            complete=(True, False),
        ),
        Case(
            "PA04-no-log-preserves-make",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"skip_logs": {0}}),
            dispositions=("passed", "passed", "passed"),
            codes_include=("report_pair_mismatch",),
        ),
        Case(
            "PA04-pair-outcome",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"log_outcome": {0: 1}}),
            codes_include=("report_pair_mismatch",),
        ),
        Case(
            "PA04-pair-wasxfail",
            data=_pa04_run(
                [(0, 0), (1, 0), (2, 0)], kw={"wasxfail": {1: True}, "log_wasxfail": {1: False}}
            ),
            codes_include=("report_pair_mismatch",),
        ),
    ]


def _pa04_overlap_journal() -> bytes:
    """Dos instancias solapadas: la primera queda incompleta."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0)])
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa04_raw_exception_journal() -> bytes:
    """Passed + excepción raw conservada: inconsistent en la fase de call."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0)])
    j.ev(1, 14, [0, 1, 0, True, "AssertionError", False, None])
    j.ev(1, 15, [0, 1, 0, False])
    j.phases(1, 0, [(2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa04_order_cases() -> list[Case]:
    """Casos PA04 de orden, duplicación y fases faltantes."""
    return [
        Case(
            "PA04-phase-order",
            data=_pa04_run([(2, 0), (0, 0), (1, 0)]),
            codes_include=("phase_order",),
        ),
        Case(
            "PA04-duplicate-phase",
            data=_pa04_run([(0, 0), (1, 0), (1, 0), (2, 0)]),
            codes_include=("duplicate_phase", "report_pair_mismatch"),
        ),
        Case(
            "PA04-same-instance-duplicate-make",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"extra_make": {0}}),
            codes_include=("duplicate_phase", "report_pair_mismatch"),
        ),
        Case(
            "PA04-same-instance-duplicate-log",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], kw={"extra_log": {0}}),
            codes_include=("duplicate_phase", "report_pair_mismatch"),
        ),
        Case(
            "PA04-no-teardown",
            data=_pa04_run([(0, 0), (1, 0)]),
            codes_include=("missing_phase",),
            complete=(True, False),
        ),
        Case(
            "PA04-no-test-end",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)], end=False),
            codes_include=("missing_test_end",),
            start_seqs=(18,),
        ),
        Case(
            "PA04-call-after-nonpass-setup",
            data=_pa04_run([(0, 1), (1, 0), (2, 0)]),
            codes_include=("unexpected_phase",),
        ),
        Case(
            "PA04-overlap",
            data=_pa04_overlap_journal(),
            codes_include=("missing_test_end",),
            start_seqs=(18, 21),
        ),
        Case(
            "PA04-collection-has-phases",
            data=_pa04_collection_phases(),
            codes_include=("event_order",),
        ),
        Case(
            "PA04-passed-raw-exception",
            data=_pa04_raw_exception_journal(),
            codes_include=("report_inconsistent",),
            dispositions=("passed", "inconsistent", "passed"),
        ),
        Case(
            "PA04-valid-control",
            data=_pa04_run([(0, 0), (1, 0), (2, 0)]),
            complete=(True, True),
            eligible_all=True,
        ),
    ]


def _pa04_collection_phases() -> bytes:
    """Test dentro del rol de colección: evento fuera de su máquina."""
    j = Journal()
    _collection(
        j,
        mid_session=lambda b: (
            b.test_start(0),
            b.phases(0, 0, [(0, 0), (1, 0), (2, 0)]),
            b.test_end(0),
        ),
    )
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa04_cases() -> list[Case]:
    return [*_pa04_pair_cases(), *_pa04_order_cases()]


def _pa05_cases() -> list[Case]:
    specs: list[tuple[object, ...]] = [
        (
            "PA05-call-failed",
            [(0, 0), (1, 1), (2, 0)],
            1,
            ("passed", "failed", "passed"),
            {"present": {1: True}},
            "observed",
        ),
        ("PA05-setup-failed", [(0, 1), (2, 0)], 1, ("failed", "passed"), {}, "not_scheduled"),
        (
            "PA05-teardown-failed",
            [(0, 0), (1, 0), (2, 1)],
            1,
            ("passed", "passed", "failed"),
            {},
            "observed",
        ),
        ("PA05-setup-skipped", [(0, 2), (2, 0)], 0, ("skipped", "passed"), {}, "not_scheduled"),
        (
            "PA05-call-skipped",
            [(0, 0), (1, 2), (2, 0)],
            0,
            ("passed", "skipped", "passed"),
            {},
            "observed",
        ),
        (
            "PA05-xfail",
            [(0, 0), (1, 2), (2, 0)],
            0,
            ("passed", "xfail", "passed"),
            {"wasxfail": {1: True}, "xfail": [True, False, True]},
            "observed",
        ),
        (
            "PA05-xfail-explicit-setup",
            [(0, 2), (2, 0)],
            0,
            ("xfail", "passed"),
            {"wasxfail": {0: True}, "xfail": [True, False, True]},
            "not_scheduled",
        ),
        (
            "PA05-xfail-teardown",
            [(0, 0), (1, 0), (2, 2)],
            0,
            ("passed", "xpass", "xfail"),
            {"wasxfail": {1: True, 2: True}, "xfail": [True, False, True]},
            "observed",
        ),
        (
            "PA05-xpass",
            [(0, 0), (1, 0), (2, 0)],
            0,
            ("passed", "xpass", "passed"),
            {"wasxfail": {1: True}},
            "observed",
        ),
        (
            "PA05-xpass-strict",
            [(0, 0), (1, 1), (2, 0)],
            1,
            ("passed", "xpass_strict", "passed"),
            {"xfail": [True, True, True]},
            "observed",
        ),
        (
            "PA05-inactive-marker",
            [(0, 0), (1, 1), (2, 0)],
            1,
            ("passed", "failed", "passed"),
            {"present": {1: True}, "xfail": [True, True, True]},
            "observed",
        ),
        (
            "PA05-raises-mismatch",
            [(0, 0), (1, 1), (2, 0)],
            1,
            ("passed", "failed", "passed"),
            {"present": {1: True}},
            "observed",
        ),
        (
            "PA05-valid-control",
            [(0, 0), (1, 0), (2, 0)],
            0,
            ("passed", "passed", "passed"),
            {},
            "observed",
        ),
    ]
    rows: list[Case] = []
    for case_id, entries, exit_code, dispositions, kw, call in specs:
        rows.append(
            Case(
                case_id,
                data=_phases_run(entries, exit_code=exit_code, phase_kw=kw),
                dispositions=dispositions,
                call_disposition=call,
                terminals=("t",),
                eligible_all=case_id == "PA05-valid-control",
                complete=(True, True),
            )
        )
    return rows


def _pa06_journal_replaced() -> Journal:
    """Selección del productor con otro nodeid a igual cardinalidad."""
    j = Journal()
    _collection(j, nodeids=("t", "u"), selected=(1,), end_counts=(1, 0), items=(1,))
    j.start(1)
    j.session(1)
    j.item(1, 1)
    j.select(1, 1)
    j.collect_end(1, selected=1)
    j.test_start(1, index=1)
    j.phases(1, 1, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_duplicate_item() -> Journal:
    """Item duplicado en el productor sin segunda selección."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_duplicate_selected() -> Journal:
    """Selección duplicada: P01 denuncia duplicate_identity en collected."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=2)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_duplicate_terminal() -> Journal:
    """Doble test_end: el segundo queda huérfano como test_order."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_silent_drop() -> Journal:
    """Item recolectado que nunca se selecciona: drop silencioso visible."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.collect_end(1, selected=0)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_diverge() -> Journal:
    """Colección selecciona t y u; el productor solo u."""
    j = Journal()
    _collection(j, nodeids=("t", "u"), selected=(0, 1), end_counts=(2, 0))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 1)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_journal_twice() -> Journal:
    """Dos instancias completas del mismo nodeid, sin deduplicación."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    for _round in range(2):
        j.test_start(1)
        j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
        j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa06_cases() -> list[Case]:
    replaced = _pa06_journal_replaced()
    duplicated_item = _pa06_journal_duplicate_item()
    duplicated_selected = _pa06_journal_duplicate_selected()
    duplicate_terminal = _pa06_journal_duplicate_terminal()
    silent = _pa06_journal_silent_drop()
    diverge = _pa06_journal_diverge()
    twice = _pa06_journal_twice()
    return [
        Case(
            "PA06-same-count-replacement",
            data=replaced.bytes(),
            identity="mismatch",
            preflight="mismatch",
            terminals=("u",),
            complete=(True, True),
            codes_exclude=("selection_mismatch", "test_order"),
        ),
        Case(
            "PA06-duplicate-item",
            data=duplicated_item.bytes(),
            codes_include=("selection_mismatch",),
            complete=(True, True),
            findings_exact=(
                (
                    "selection_mismatch",
                    "producer-1",
                    None,
                    _offset_of_code(duplicated_item, 12, ex=1),
                ),
            ),
        ),
        Case(
            "PA06-duplicate-selected",
            data=duplicated_selected.bytes(),
            identity="invalid",
            identity_codes=("duplicate_identity",),
            codes_include=("selection_mismatch",),
        ),
        Case(
            "PA06-duplicate-terminal",
            data=duplicate_terminal.bytes(),
            codes_include=("test_order",),
            identity="mismatch",
            terminals=(),
        ),
        Case(
            "PA06-silent-drop",
            data=silent.bytes(),
            codes_include=("selection_mismatch",),
            identity="mismatch",
        ),
        Case(
            "PA06-collection-producer-diverge",
            data=diverge.bytes(),
            preflight="mismatch",
            complete=(True, True),
        ),
        Case(
            "PA06-empty-expected",
            data=_standard(),
            expected=(),
            identity="empty",
            identity_codes=("empty_expected", "unexpected_identity", "unexpected_identity"),
        ),
        Case(
            "PA06-two-complete-instances-same-nodeid",
            data=twice.bytes(),
            start_seqs=(18, 26),
            terminals=("t", "t"),
            eligible_all=True,
            identity="invalid",
            identity_codes=("duplicate_identity",),
            codes_exclude=("duplicate_phase", "test_order"),
        ),
        Case(
            "PA06-valid-control",
            data=_standard(),
            identity="match",
            preflight="match",
            findings_exact=(),
        ),
    ]


def _pa07_property_journal(
    producer: Callable[[Journal], None],
    *,
    selected: int,
    deselected: int,
    extra_declares: tuple[str, ...] = (),
) -> Journal:
    """Journal del run con property p deseleccionada y variante en el productor."""
    j = Journal()
    nodes = ("t", "p", *extra_declares)
    _collection(
        j,
        nodeids=nodes,
        flags=(False, True, True, True),
        deselects=(1,),
        selected=(0,),
        end_counts=(1, 1),
    )
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 1, is_property=True)
    producer(j)
    j.collect_end(1, selected=selected, deselected=deselected)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j


def _pa07_property_run(
    producer: Callable[[Journal], None],
    *,
    selected: int,
    deselected: int,
    extra_declares: tuple[str, ...] = (),
) -> bytes:
    """Run con property p deseleccionada y variante aplicada al productor."""
    return _pa07_property_journal(
        producer, selected=selected, deselected=deselected, extra_declares=extra_declares
    ).bytes()


def _pa07_ok(j: Journal) -> None:
    j.deselect(1, 1)
    j.select(1, 0)


def _pa07_normal_deselected(j: Journal) -> None:
    j.item(1, 2)
    j.deselect(1, 2, is_property=False)
    j.select(1, 0)


def _pa07_property_selected(j: Journal) -> None:
    j.deselect(1, 1)
    j.select(1, 1)
    j.select(1, 0)


def _pa07_missing_property(_j: Journal) -> None:
    return None


def _pa07_property_extra(j: Journal) -> None:
    j.item(1, 2, is_property=True)
    j.deselect(1, 2)
    j.select(1, 0)


def _pa07_duplicate_property(j: Journal) -> None:
    j.deselect(1, 1)
    j.deselect(1, 1)
    j.select(1, 0)


def _pa07_marker_change(j: Journal) -> None:
    j.deselect(1, 1, is_property=False)
    j.select(1, 0)


def _pa07_cases() -> list[Case]:
    valid = _pa07_property_journal(_pa07_ok, selected=1, deselected=1)
    normal = _pa07_property_journal(
        _pa07_normal_deselected, selected=1, deselected=1, extra_declares=("n",)
    )
    selected = _pa07_property_journal(_pa07_property_selected, selected=2, deselected=1)
    extra = _pa07_property_journal(
        _pa07_property_extra, selected=1, deselected=1, extra_declares=("q",)
    )
    duplicate = _pa07_property_journal(_pa07_duplicate_property, selected=1, deselected=2)
    marker = _pa07_property_journal(_pa07_marker_change, selected=1, deselected=1)
    return [
        Case(
            "PA07-valid-property",
            data=valid.bytes(),
            property_ids=("p",),
            property_codes=(),
            identity="match",
            preflight="match",
            complete=(True, True),
            codes_exclude=("selection_mismatch",),
            findings_exact=(),
            property_findings_exact=(),
        ),
        Case(
            "PA07-normal-deselected",
            data=normal.bytes(),
            property_ids=("p",),
            property_codes=("unauthorized_deselection", "missing_property"),
            findings_exact=(
                ("selection_mismatch", "collection-1", None, _offset_of_code(normal, 12, ex=0)),
                (
                    "unauthorized_deselection",
                    "producer-1",
                    "n",
                    _offset_of_code(normal, 10, ex=1, item=2),
                ),
                ("selection_mismatch", "producer-1", None, _offset_of_code(normal, 12, ex=1)),
                ("missing_property", "producer-1", "p", None),
            ),
            property_findings_exact=(
                (
                    "unauthorized_deselection",
                    "producer-1",
                    "n",
                    _offset_of_code(normal, 10, ex=1, item=2),
                ),
                ("missing_property", "producer-1", "p", None),
            ),
        ),
        Case(
            "PA07-property-selected",
            data=selected.bytes(),
            property_ids=("p",),
            property_codes=("unauthorized_selection",),
            identity="mismatch",
            findings_exact=(
                (
                    "unauthorized_selection",
                    "producer-1",
                    "p",
                    _offset_of_code(selected, 11, ex=1, item=1),
                ),
                ("selection_mismatch", "producer-1", None, _offset_of_code(selected, 12, ex=1)),
            ),
            property_findings_exact=(
                (
                    "unauthorized_selection",
                    "producer-1",
                    "p",
                    _offset_of_code(selected, 11, ex=1, item=1),
                ),
            ),
        ),
        Case(
            "PA07-property-missing",
            data=_pa07_property_run(_pa07_missing_property, selected=1, deselected=0),
            property_ids=("p",),
            property_codes=("missing_property",),
            codes_include=("selection_mismatch",),
        ),
        Case(
            "PA07-property-extra",
            data=extra.bytes(),
            property_ids=("p",),
            property_codes=("unexpected_property", "missing_property"),
            findings_exact=(
                ("selection_mismatch", "collection-1", None, _offset_of_code(extra, 12, ex=0)),
                (
                    "unexpected_property",
                    "producer-1",
                    "q",
                    _offset_of_code(extra, 10, ex=1, item=2),
                ),
                ("selection_mismatch", "producer-1", None, _offset_of_code(extra, 12, ex=1)),
                ("missing_property", "producer-1", "p", None),
            ),
            property_findings_exact=(
                (
                    "unexpected_property",
                    "producer-1",
                    "q",
                    _offset_of_code(extra, 10, ex=1, item=2),
                ),
                ("missing_property", "producer-1", "p", None),
            ),
        ),
        Case(
            "PA07-property-duplicate",
            data=duplicate.bytes(),
            property_ids=("p",),
            property_codes=("duplicate_property",),
            findings_exact=(
                ("selection_mismatch", "producer-1", None, _offset_of_code(duplicate, 12, ex=1)),
                ("duplicate_property", "producer-1", "p", None),
            ),
            property_findings_exact=(("duplicate_property", "producer-1", "p", None),),
        ),
        Case(
            "PA07-property-marker-change",
            data=marker.bytes(),
            property_ids=("p",),
            property_codes=("property_marker_changed", "unauthorized_deselection"),
            findings_exact=(
                (
                    "property_marker_changed",
                    "producer-1",
                    "p",
                    _offset_of_code(marker, 10, ex=1, item=1),
                ),
                (
                    "unauthorized_deselection",
                    "producer-1",
                    "p",
                    _offset_of_code(marker, 10, ex=1, item=1),
                ),
            ),
            property_findings_exact=(
                (
                    "property_marker_changed",
                    "producer-1",
                    "p",
                    _offset_of_code(marker, 10, ex=1, item=1),
                ),
                (
                    "unauthorized_deselection",
                    "producer-1",
                    "p",
                    _offset_of_code(marker, 10, ex=1, item=1),
                ),
            ),
        ),
        Case(
            "PA07-valid-control",
            data=_standard(),
            property_ids=(),
            property_codes=(),
            findings_exact=(),
        ),
    ]


def _pa08_collection_run(
    *,
    session_close: bool = True,
    end: dict[str, object] | None = None,
    channel: tuple[object, ...] | None = None,
    mid: Callable[[Journal], None] | None = None,
    session_error: bool = False,
) -> bytes:
    """Colección con variantes de cierre y productor íntegro detrás."""
    j = Journal()
    _collection(
        j,
        session_close=session_close,
        end_payload=end,
        channel=channel,
        mid_session=mid,
        session_error=session_error,
    )
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa08_exit_cases() -> list[Case]:
    """Salida, terminación y límites de ejecución (§5)."""
    return [
        Case(
            "PA08-exit-zero-no-session-end",
            data=_pa08_collection_run(session_close=False),
            codes_include=("missing_session_end",),
            exit_codes=(0, 0),
            codes_exclude=("exit_disagreement",),
            complete=(False, True),
        ),
        Case(
            "PA08-exit-disagrees",
            data=_pa08_collection_run(end={"observed": 1}),
            codes_include=("exit_disagreement",),
            exit_codes=(0, 0),
            complete=(False, True),
        ),
        Case(
            "PA08-hook-argument-changed",
            data=_pa08_collection_run(end={"argument": 1}),
            codes_exclude=("exit_disagreement",),
            exit_codes=(0, 0),
            complete=(True, True),
        ),
        Case(
            "PA08-signal-valid",
            data=_pa08_collection_run(end={"termination": "signal", "signal": 5, "exit_code": -5}),
            termination="signal",
            codes_exclude=("termination_inconsistent",),
            complete=(False, True),
        ),
        Case(
            "PA08-signal-mismatch",
            data=_pa08_collection_run(end={"termination": "signal"}),
            codes_include=("termination_inconsistent",),
            termination="signal",
        ),
        Case(
            "PA08-launch-error",
            data=_pa08_collection_run(end={"termination": "launch_error", "exit_code": None}),
            termination="launch_error",
            codes_include=("termination_inconsistent",),
            complete=(False, True),
            exit_codes=(None, 0),
        ),
        Case(
            "PA08-timeout-null",
            data=_pa08_collection_run(end={"termination": "timeout", "exit_code": None}),
            termination="timeout",
            codes_exclude=("termination_inconsistent",),
            complete=(False, True),
        ),
        Case(
            "PA08-timeout-signalled",
            data=_pa08_collection_run(end={"termination": "timeout", "exit_code": -9, "signal": 9}),
            termination="timeout",
            codes_exclude=("termination_inconsistent",),
            complete=(False, True),
        ),
        Case(
            "PA08-bounds",
            data=_pa08_collection_run(end={"log_start": 5}),
            codes_include=("execution_bounds",),
            complete=(True, False),
        ),
        Case(
            "PA08-log-truncated",
            data=_pa08_collection_run(end={"truncated": True}),
            codes_include=("log_truncated",),
            complete=(False, True),
        ),
        Case(
            "PA08-valid-control",
            data=_standard(),
            complete=(True, True),
            codes_exclude=("exit_disagreement", "termination_inconsistent"),
        ),
    ]


def _pa08_diagnostic_cases() -> list[Case]:
    """Diagnósticos, canal y orden entre ejecuciones (§5)."""
    return [
        Case(
            "PA08-internal-error",
            data=_pa08_collection_run(mid=lambda b: b.diagnostic(0, 17)),
            codes_include=("internal_error",),
            complete=(False, True),
        ),
        Case(
            "PA08-interrupted",
            data=_pa08_collection_run(mid=lambda b: b.diagnostic(0, 18)),
            codes_include=("interrupted",),
            complete=(False, True),
        ),
        Case(
            "PA08-session-end-error",
            data=_pa08_collection_run(session_error=True),
            codes_include=("session_end_error",),
            codes_exclude=("duplicate_event",),
            complete=(False, True),
        ),
        Case(
            "PA08-channel-tail",
            data=_pa08_collection_run(
                channel=(False, 3, hashlib.sha256(b"tail").hexdigest(), "truncated_channel")
            ),
            codes_include=("channel_defect",),
            codes_exclude=("channel_inconsistent",),
            complete=(False, True),
        ),
        Case(
            "PA08-channel-inconsistent",
            data=_pa08_collection_run(channel=(True, 3, None, "truncated_channel")),
            codes_include=("channel_inconsistent", "channel_defect"),
            complete=(False, True),
        ),
        Case(
            "PA08-producer-before-collection-end",
            data=_pa08_before_collection_end(),
            codes_include=("execution_order",),
        ),
        Case(
            "PA08-duplicate-start",
            data=_pa08_duplicate_start(),
            codes_include=("missing_test_end",),
            start_seqs=(18, 21),
        ),
        Case(
            "PA08-after-execution-end",
            data=_pa08_after_execution_end(),
            codes_include=("event_order",),
        ),
    ]


def _pa08_before_collection_end() -> bytes:
    """El productor arranca antes del execution_end de la colección."""
    j = Journal()
    _collection(j, execution_close=False)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    j.sup(0, 3, [0, "exited", None, 0, EMPTY_SHA, 2, UTC2, False])
    return j.bytes()


def _pa08_after_execution_end() -> bytes:
    """Evento de la colección tras su execution_end: event_order."""
    j = Journal()
    _collection(j)
    j.ev(0, 8, [0, False])
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa08_duplicate_start() -> bytes:
    """Dos test_start solapados: la primera instancia queda incompleta."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0)])
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa08_cases() -> list[Case]:
    return [*_pa08_exit_cases(), *_pa08_diagnostic_cases()]


def _line_of_64kib(*, extra: int = 0) -> bytes:
    """Línea exacta de 65536+extra bytes repartidos en strings ≤4096."""

    def render(entries: list[str], cwd: str) -> bytes:
        return _line(2, 0, None, 1, [entries, cwd, 0, 1, UTC])

    entries = ["y" * 4096]
    target = 65536 + extra
    while len(render([*entries, "y" * 4096], "/r")) <= target:
        entries.append("y" * 4096)
    deficit = target - len(render(entries, "/r"))
    cwd_width = min(deficit, 4094)
    remaining = deficit - cwd_width
    cwd = "/" + "r" * (1 + cwd_width)
    if remaining > 0:
        entries[-1] = "y" * (4096 - remaining)
    line = render(entries, cwd)
    assert len(line) == target
    return line


def _pa09_nodeid_exact() -> tuple[bytes, str]:
    """Journal válido cuyo nodeid mide exactamente 4096 bytes."""
    pad = "x" * 4096
    j = Journal()
    _collection(j, nodeids=(pad,), selected=(0,), end_counts=(1, 0))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes(), pad


def _property_only_two() -> bytes:
    """Dos propiedades recolectadas y deseleccionadas, sin tests normales."""
    j = Journal()
    j.start(0)
    j.session(0)
    for index, nodeid in enumerate(("p1", "p2")):
        j.declare(index, nodeid)
    j.item(0, 0, is_property=True)
    j.item(0, 1, is_property=True)
    j.deselect(0, 0)
    j.deselect(0, 1)
    j.collect_end(0, selected=0, deselected=2)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    j.start(1)
    j.session(1)
    j.item(1, 0, is_property=True)
    j.item(1, 1, is_property=True)
    j.deselect(1, 0)
    j.deselect(1, 1)
    j.collect_end(1, selected=0, deselected=2)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def _pa09_cases() -> list[Case]:
    big, pad = _pa09_nodeid_exact()
    exact_64k = _header() + _line(1, 0, None, 0, [0, pad]) + _line_of_64kib()
    two = _two_nodes_run()
    return [
        Case("PA09-line-exact", data=exact_64k, event_count=2),
        Case(
            "PA09-journal-exact",
            data=GOLDEN,
            max_bytes=1938,
            consumed=1938,
            tail_none=True,
            complete=(True, True),
        ),
        Case(
            "PA09-nodeid-exact", data=big, expected=(pad,), identity="match", complete=(True, True)
        ),
        Case(
            "PA09-items-exact",
            data=two,
            expected=("t", "u"),
            patch=("MAX_INVENTORY_ENTRIES", 2),
            identity="match",
            complete=(True, True),
        ),
        Case(
            "PA09-selected-exact",
            data=two,
            expected=("t", "u"),
            patch=("MAX_INVENTORY_ENTRIES", 2),
            identity="match",
        ),
        Case(
            "PA09-deselected-exact",
            data=_property_only_two(),
            property_ids=("p1", "p2"),
            expected=(),
            identity="empty",
            patch=("MAX_INVENTORY_ENTRIES", 2),
            property_codes=(),
        ),
        Case(
            "PA09-test-start-exact",
            data=two,
            expected=("t", "u"),
            patch=("MAX_INVENTORY_ENTRIES", 2),
            start_seqs=(23, 31),
            identity="match",
        ),
        Case(
            "PA09-phase-make-exact",
            data=_standard(),
            patch=("MAX_INVENTORY_ENTRIES", 1),
            complete=(True, True),
        ),
        Case(
            "PA09-phase-log-exact",
            data=_standard(),
            patch=("MAX_INVENTORY_ENTRIES", 1),
            complete=(True, True),
        ),
        Case(
            "PA09-test-end-exact",
            data=two,
            expected=("t", "u"),
            patch=("MAX_INVENTORY_ENTRIES", 2),
            terminals=("t", "u"),
        ),
        Case(
            "PA09-expected-exact",
            data=_standard(),
            expected=tuple(f"n{i:05d}" for i in range(10_000)),
            identity="mismatch",
        ),
        Case(
            "PA09-property-ids-exact",
            data=_standard(),
            property_ids=tuple(f"p{i:05d}" for i in range(10_000)),
        ),
        Case("PA09-valid-control", data=_standard(), complete=(True, True)),
    ]


def _pa10_cases() -> list[Case]:
    pad = "x" * 4096
    over_node = (
        _header()
        + _line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])
        + _line(2, 0, None, 0, [0, pad + "x"])
    )
    over_line = _header() + _line(1, 0, None, 0, [0, pad]) + _line_of_64kib(extra=1)
    items_data, items_offset, items_count = _third_item_bundle()
    selects_data, sel_offset, sel_count = _third_select_bundle()
    property_extra, de_offset, de_count = _property_extra_bundle()
    three_tests, ts_offset, ts_count = _three_tests_bundle()
    extra_make, make_offset, make_count = _extra_make_bundle()
    extra_log, log_offset, log_count = _extra_log_bundle()
    extra_end, te_offset, te_count = _extra_test_end_bundle()
    return [
        Case(
            "PA10-line-plus-one",
            data=over_line,
            decoder_finding=(
                "limit_exceeded",
                len(_header()) + len(_line(1, 0, None, 0, [0, pad])),
            ),
            event_count=1,
        ),
        Case(
            "PA10-journal-plus-one",
            data=GOLDEN,
            max_bytes=1937,
            decode_raises=("limit_exceeded", "data"),
        ),
        Case(
            "PA10-nodeid-plus-one",
            data=over_node,
            decoder_finding=(
                "invalid_field",
                len(_header()) + len(_line(1, 0, None, 1, [["python"], "/r", 0, 1, UTC])),
            ),
            event_count=1,
        ),
        Case(
            "PA10-items-plus-one",
            data=items_data,
            patch=("MAX_INVENTORY_ENTRIES", 2),
            decoder_finding=("limit_exceeded", items_offset),
            event_count=items_count,
        ),
        Case(
            "PA10-selected-plus-one",
            data=selects_data,
            patch=("MAX_INVENTORY_ENTRIES", 2),
            decoder_finding=("limit_exceeded", sel_offset),
            event_count=sel_count,
        ),
        Case(
            "PA10-deselected-plus-one",
            data=property_extra,
            patch=("MAX_INVENTORY_ENTRIES", 2),
            decoder_finding=("limit_exceeded", de_offset),
            event_count=de_count,
        ),
        Case(
            "PA10-test-start-plus-one",
            data=three_tests,
            patch=("MAX_INVENTORY_ENTRIES", 2),
            decoder_finding=("limit_exceeded", ts_offset),
            event_count=ts_count,
        ),
        Case(
            "PA10-phase-make-plus-one",
            data=extra_make,
            patch=("MAX_INVENTORY_ENTRIES", 1),
            decoder_finding=("limit_exceeded", make_offset),
            event_count=make_count,
        ),
        Case(
            "PA10-phase-log-plus-one",
            data=extra_log,
            patch=("MAX_INVENTORY_ENTRIES", 1),
            decoder_finding=("limit_exceeded", log_offset),
            event_count=log_count,
        ),
        Case(
            "PA10-test-end-plus-one",
            data=extra_end,
            patch=("MAX_INVENTORY_ENTRIES", 2),
            decoder_finding=("limit_exceeded", te_offset),
            event_count=te_count,
        ),
        Case(
            "PA10-expected-plus-one",
            data=_standard(),
            expected=tuple(f"n{i:05d}" for i in range(10_001)),
            reconcile_raises=("limit_exceeded", "expected"),
        ),
        Case(
            "PA10-property-ids-plus-one",
            data=_standard(),
            property_ids=tuple(f"p{i:05d}" for i in range(10_001)),
            reconcile_raises=("limit_exceeded", "property_ids"),
        ),
        Case("PA10-valid-control", data=GOLDEN, max_bytes=1938, consumed=1938),
    ]


def _two_nodes_prefix(j: Journal, *, nodes: tuple[str, ...]) -> None:
    """Colección válida bajo tope 2: dos items y dos selecciones."""
    j.start(0)
    j.session(0)
    for index, nodeid in enumerate(nodes):
        j.declare(index, nodeid)
    for index in range(2):
        j.item(0, index)
    for index in range(2):
        j.select(0, index)
    j.collect_end(0, selected=2)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)


def _offset_of(lines: list[bytes], index: int) -> int:
    """Byte de inicio de la línea index, calculado desde el propio test."""
    return len(_header()) + sum(len(line) for line in lines[:index])


def _offset_of_code(
    j: Journal, code: int, *, ex: int | None = None, item: int | None = None, nth: int = 1
) -> int:
    """Offset del propio test para la n-ésima línea construida con ese event_code.

    Filtra opcionalmente por ejecución (`ex`) y por el primer elemento del
    vector (`item`, el índice referido por el evento). No consulta al SUT:
    lee las líneas que el test acaba de construir.
    """
    seen = 0
    for index, line in enumerate(j.lines):
        row = json.loads(line)
        if row[3] != code or (ex is not None and row[1] != ex):
            continue
        if item is not None and row[4][0] != item:
            continue
        seen += 1
        if seen == nth:
            return _offset_of(j.lines, index)
    raise AssertionError(f"event_code {code} ex={ex} item={item} nth={nth} ausente")


def _third_item_bundle() -> tuple[bytes, int, int]:
    """Tercer item (de nodo declarado) excede el tope 2 en la colección."""
    j = Journal()
    j.start(0)
    j.session(0)
    for index, nodeid in enumerate(("t", "u", "v")):
        j.declare(index, nodeid)
    for index in range(3):
        j.item(0, index)
    j.select(0, 0)
    j.collect_end(0, selected=1)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    third_item = 8
    return j.bytes(), _offset_of(j.lines, third_item), third_item


def _third_select_bundle() -> tuple[bytes, int, int]:
    """Tercera selección (de nodo declarado) excede el tope 2."""
    j = Journal()
    _two_nodes_prefix(j, nodes=("t", "u", "v"))
    j.start(1)
    j.session(1)
    for index in range(2):
        j.item(1, index)
    for index in range(3):
        j.select(1, index)
    j.collect_end(1, selected=3)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    third_select = 15 + 5 + 2
    return j.bytes(), _offset_of(j.lines, third_select), third_select


def _property_extra_bundle() -> tuple[bytes, int, int]:
    """Tercera deselección excede el tope reducido a 2."""
    j = Journal()
    j.start(0)
    j.session(0)
    for index, nodeid in enumerate(("t", "p1", "p2", "p3")):
        j.declare(index, nodeid)
    j.item(0, 0)
    for index in range(1, 4):
        j.deselect(0, index)
    j.select(0, 0)
    j.collect_end(0, selected=1, deselected=3)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    third_deselect = 7 + 3
    return j.bytes(), _offset_of(j.lines, third_deselect), third_deselect


def _nth_seq(j: Journal, code: int, n: int) -> int:
    """Seq de la n-ésima aparición de un event_code en el journal del builder."""
    seen = 0
    for line in j.lines:
        row = json.loads(line)
        if row[3] == code:
            seen += 1
            if seen == n:
                return row[0]
    raise AssertionError(f"event code {code} #{n} ausente")


def _three_tests_bundle() -> tuple[bytes, int, int]:
    """Dos tests válidos y un tercer test_start que excede el tope 2."""
    j = Journal()
    _two_nodes_prefix(j, nodes=("t", "u", "v"))
    j.start(1)
    j.session(1)
    for index in range(2):
        j.item(1, index)
        j.select(1, index)
    j.collect_end(1, selected=2)
    for index in range(3):
        j.test_start(1, index=index)
        j.phases(1, index, [(0, 0), (1, 0), (2, 0)])
        j.test_end(1, index=index)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    third_start = _nth_seq(j, 13, 3)
    return j.bytes(), _offset_of(j.lines, third_start - 1), third_start - 1


def _extra_test_end_bundle() -> tuple[bytes, int, int]:
    """Dos instancias y un tercer test_end que excede el tope 2."""
    j = Journal()
    _two_nodes_prefix(j, nodes=("t", "u"))
    j.start(1)
    j.session(1)
    for index in range(2):
        j.item(1, index)
        j.select(1, index)
    j.collect_end(1, selected=2)
    for index in range(2):
        j.test_start(1, index=index)
        j.phases(1, index, [(0, 0), (1, 0), (2, 0)])
        j.test_end(1, index=index)
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    third_end = _nth_seq(j, 16, 3)
    return j.bytes(), _offset_of(j.lines, third_end - 1), third_end - 1


def _extra_make_bundle() -> tuple[bytes, int, int]:
    """Segundo make de setup con tope reducido a 1 por fase."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)], extra_make={0})
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    second_make = _nth_seq(j, 14, 4)
    return j.bytes(), _offset_of(j.lines, second_make - 1), second_make - 1


def _extra_log_bundle() -> tuple[bytes, int, int]:
    """Segundo log de setup con tope reducido a 1 por fase."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)], extra_log={0})
    j.test_end(1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    second_log = _nth_seq(j, 15, 4)
    return j.bytes(), _offset_of(j.lines, second_log - 1), second_log - 1


def _many_property_ids() -> tuple[str, ...]:
    return tuple(f"p{i:05d}" for i in range(10_000))


def _pa11_cases() -> list[Case]:
    return [
        Case(
            "PA11-plugin-claim-false",
            data=_plugin_journal("cov", qualified=False),
            complete=(True, True),
            property_codes=(),
            assert_that=_claim_check("cov", False, "1.0"),
        ),
        Case(
            "PA11-plugin-claim-true",
            data=_plugin_journal("cov", qualified=True),
            complete=(True, True),
            assert_that=_claim_check("cov", True, "1.0"),
        ),
        Case(
            "PA11-unknown-version-claim",
            data=_plugin_journal("cov", qualified=True, version=None),
            complete=(True, True),
            assert_that=_claim_check("cov", True, None),
        ),
        Case(
            "PA11-options-claim-false",
            data=_options_claim_false(),
            complete=(True, True),
            assert_that=_check_options_claim_false,
        ),
        Case(
            "PA11-opaque-context",
            data=_opaque_context(),
            complete=(True, True),
            assert_that=_opaque_context_check,
        ),
        Case("PA11-valid-control", data=_standard(), complete=(True, True)),
    ]


def _check_options_claim_false(observation: JournalObservation, _result: object) -> None:
    """profile_match=False viaja tal cual; no se convierte en verificación."""
    claim = next(event.payload for event in observation.events if event.kind == "options")
    assert claim.profile_match is False


def _incoherent(observation: JournalObservation) -> JournalObservation:
    """Evento manual imposible: execution_start con payload de otra clase."""
    events = list(observation.events)
    events[0] = dataclasses.replace(events[0], payload=SessionStart("9", "1", "o", D64))
    return dataclasses.replace(observation, events=tuple(events))


def _event_with_offset(
    observation: JournalObservation, index: int, **changes: int
) -> JournalObservation:
    events = list(observation.events)
    events[index] = dataclasses.replace(events[index], **changes)
    return dataclasses.replace(observation, events=tuple(events))


def _pa12_cases() -> list[Case]:
    golden = _decode_golden()
    finding_only = dataclasses.replace(
        golden,
        events=(),
        consumed_bytes=len(GOLDEN_LINES[0]),
        findings=(ProtocolFinding("invalid_json", None, None, None, 100),),
    )
    last_end = dataclasses.replace(golden, max_bytes=4096, consumed_bytes=1939)
    return [
        Case("PA12-data-type", type_error_arg="data"),
        Case("PA12-max-bytes-type", type_error_arg="max_bytes"),
        Case(
            "PA12-max-bytes-zero",
            data=GOLDEN,
            max_bytes=0,
            decode_raises=("invalid_reference", "max_bytes"),
        ),
        Case(
            "PA12-max-bytes-over-absolute",
            data=GOLDEN,
            max_bytes=2 * 1024 * 1024 + 1,
            decode_raises=("invalid_reference", "max_bytes"),
        ),
        Case(
            "PA12-run-value",
            data=GOLDEN,
            run_id="zz",
            decode_raises=("invalid_reference", "run_id"),
        ),
        Case(
            "PA12-reference-order",
            data=GOLDEN,
            executions=(
                ExecutionExpectation("producer-1", "producer", D64, D64, D64),
                ExecutionExpectation("collection-1", "collection", D64, D64, D64),
            ),
            decode_raises=("invalid_expectations", "executions[0].execution_id"),
        ),
        Case(
            "PA12-reference-duplicate",
            data=GOLDEN,
            executions=(
                ExecutionExpectation("collection-1", "collection", D64, D64, D64),
                ExecutionExpectation("collection-1", "collection", D64, D64, D64),
            ),
            decode_raises=("invalid_expectations", "executions[1].execution_id"),
        ),
        Case("PA12-observation-type", type_error_arg="reconcile-observation"),
        Case(
            "PA12-observation-incoherent",
            data=GOLDEN,
            manual=_incoherent,
            reconcile_raises=("invalid_observation", "events[0].payload"),
        ),
        Case("PA12-expected-list", expected=["t"], type_error_arg="expected"),
        Case(
            "PA12-expected-duplicate",
            data=GOLDEN,
            expected=("t", "t"),
            reconcile_raises=("invalid_reference", "expected"),
        ),
        Case(
            "PA12-expected-property-overlap",
            data=GOLDEN,
            expected=("p",),
            property_ids=("p",),
            reconcile_raises=("invalid_reference", "property_ids"),
        ),
        Case("PA12-property-list", property_ids=["p"], type_error_arg="property_ids"),
        Case(
            "PA12-property-duplicate",
            data=GOLDEN,
            property_ids=("p", "p"),
            reconcile_raises=("invalid_reference", "property_ids"),
        ),
        Case(
            "PA12-offset-negative",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 0, offset=-1),
            reconcile_raises=("invalid_observation", "events[0].offset"),
        ),
        Case(
            "PA12-offset-bool",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 0, offset=True),
            reconcile_raises=("invalid_observation", "events[0].offset"),
        ),
        Case(
            "PA12-end-before-offset",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 0, end_offset=o.events[0].offset),
            reconcile_raises=("invalid_observation", "events[0].offset"),
        ),
        Case(
            "PA12-offset-overlap",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 1, offset=o.events[1].offset - 1),
            reconcile_raises=("invalid_observation", "events[1].offset"),
        ),
        Case(
            "PA12-offset-gap",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 1, offset=o.events[1].offset + 1),
            reconcile_raises=("invalid_observation", "events[1].offset"),
        ),
        Case(
            "PA12-offset-wrong-header",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, 0, offset=0),
            reconcile_raises=("invalid_observation", "events[0].offset"),
        ),
        Case(
            "PA12-end-over-consumed",
            data=GOLDEN,
            manual=lambda o: _event_with_offset(o, -1, end_offset=o.consumed_bytes + 1),
            reconcile_raises=("invalid_observation", "events[28].offset"),
        ),
        Case(
            "PA12-consumed-over-max",
            data=GOLDEN,
            manual=lambda o: dataclasses.replace(o, consumed_bytes=2000),
            reconcile_raises=("invalid_observation", "consumed_bytes"),
        ),
        Case(
            "PA12-last-end-mismatch",
            data=GOLDEN,
            manual=lambda _o: last_end,
            reconcile_raises=("invalid_observation", "consumed_bytes"),
        ),
        Case(
            "PA12-decoder-finding-offset-mismatch",
            data=GOLDEN,
            manual=lambda _o: finding_only,
            reconcile_raises=("invalid_observation", "findings"),
        ),
        Case(
            "PA12-valid-control",
            data=GOLDEN,
            max_bytes=1938,
            complete=(True, True),
            identity="match",
        ),
    ]


def _build_cases() -> list[Case]:
    rows: list[Case] = []
    for factory in (
        _pa01_cases,
        _pa02_cases,
        _pa03_header_cases,
        _pa03_line_cases,
        _pa04_pair_cases,
        _pa04_order_cases,
        _pa05_cases,
        _pa06_cases,
        _pa07_cases,
        _pa08_exit_cases,
        _pa08_diagnostic_cases,
        _pa09_cases,
        _pa10_cases,
        _pa11_cases,
        _pa12_cases,
    ):
        rows.extend(factory())
    identifiers = [case.id for case in rows]
    assert len(identifiers) == len(set(identifiers))
    return rows


CASES: list[Case] = _build_cases()


def _assert_feature_rows(ir: object) -> None:
    """Binding completo: Feature, Outline, pasos, headers, filas y celdas."""
    assert ir["feature"] == "Reconciliacion pura de observaciones pytest"
    assert len(ir["scenarios"]) == 1
    scenario = ir["scenarios"][0]
    assert scenario["name"] == "Distinguir observaciones y defectos del protocolo"
    assert scenario["outline"] is True
    assert [(step["keyword"], step["text"]) for step in scenario["steps"]] == [
        ("Given", 'el journal literal del caso "<case>"'),
        ("When", "reconcilio sus observaciones con expectativas revisadas"),
        ("Then", 'el campo "<field>" tiene el valor literal "<expected>"'),
    ]
    rows = scenario["examples"]
    assert list(rows[0]) == ["case", "field", "expected"]
    assert [(row["case"], row["field"], row["expected"]) for row in rows] == EXPECTED_ROWS


def test_feature_block_binds_to_the_contract() -> None:
    """Positivo de binding: el bloque P03a es la tabla literal de doce filas."""
    ir = parse_feature(FEATURE)

    _assert_feature_rows(ir)
    assert ir_dry(ir)["findings"] == []


def _variant_path(tmp_path: Path, transform: Callable[[str], str]) -> Path:
    """Variante de solo lectura del feature con un campo alterado."""
    variant = tmp_path / "variante.feature"
    variant.write_text(transform(FEATURE.read_text(encoding="utf-8")), encoding="utf-8")
    return variant


def _reject_variant(tmp_path: Path, transform: Callable[[str], str]) -> None:
    """Un campo alterado debe romper el binding, no pasar silenciosamente."""
    with pytest.raises((ValueError, AssertionError, KeyError)):
        _assert_feature_rows(parse_feature(_variant_path(tmp_path, transform)))


def test_binding_rejects_altered_feature_name(tmp_path: Path) -> None:
    """Negativo de binding: renombrar la Feature rompe el contrato."""
    _reject_variant(
        tmp_path, lambda text: text.replace("Feature: Reconciliacion pura", "Feature: Otra cosa")
    )


def test_binding_rejects_altered_outline_name(tmp_path: Path) -> None:
    """Negativo de binding: renombrar el Outline rompe el contrato."""
    _reject_variant(tmp_path, lambda text: text.replace("Distinguir observaciones", "Otra cosa"))


def test_binding_rejects_altered_step_text(tmp_path: Path) -> None:
    """Negativo de binding: alterar el texto de un paso rompe el contrato."""
    _reject_variant(
        tmp_path, lambda text: text.replace("reconcilio sus observaciones", "reconcilio otra cosa")
    )


def test_binding_rejects_renamed_header(tmp_path: Path) -> None:
    """Negativo de binding: renombrar el header case rompe el contrato."""
    _reject_variant(tmp_path, lambda text: text.replace("| case |", "| caso |"))


def test_binding_rejects_duplicated_row(tmp_path: Path) -> None:
    """Negativo de binding: una fila PA01 duplicada rompe la unicidad."""
    _reject_variant(
        tmp_path,
        lambda text: text.replace(
            "      | PA01 | protocol_complete | true |\n",
            "      | PA01 | protocol_complete | true |\n"
            "      | PA01 | protocol_complete | true |\n",
        ),
    )


def test_binding_rejects_dropped_row(tmp_path: Path) -> None:
    """Negativo de binding: perder una fila rompe la cardinalidad."""
    _reject_variant(
        tmp_path, lambda text: text.replace("      | PA03 | framing_defect_visible | true |\n", "")
    )


def test_binding_rejects_altered_cell(tmp_path: Path) -> None:
    """Negativo de binding: cambiar la celda literal de PA11 rompe el contrato."""
    _reject_variant(tmp_path, lambda text: text.replace("caller-supplied-unverified", "accredited"))


def _typed_arguments(case: Case) -> dict[str, object]:
    return {
        "data": case.data if case.data is not None else GOLDEN,
        "run_id": case.run_id,
        "executions": _executions(),
        "max_bytes": case.max_bytes if case.max_bytes is not None else 1938,
    }


def _assert_type_error(case: Case) -> None:
    """El argumento público mal tipado se rechaza antes de cualquier cómputo."""
    if case.type_error_arg == "reconcile-observation":
        with pytest.raises(TypeError):
            reconcile_pytest(GOLDEN, expected=case.expected, property_ids=case.property_ids)
        return
    if case.type_error_arg == "expected":
        with pytest.raises(TypeError):
            reconcile_pytest(
                _decode_golden(), expected=case.expected, property_ids=case.property_ids
            )
        return
    if case.type_error_arg == "property_ids":
        with pytest.raises(TypeError):
            reconcile_pytest(
                _decode_golden(), expected=case.expected, property_ids=case.property_ids
            )
        return
    arguments = _typed_arguments(case)
    arguments[case.type_error_arg] = {
        "data": bytearray(b"x"),
        "run_id": 7,
        "executions": list(_executions()),
        "max_bytes": True,
    }[case.type_error_arg]
    with pytest.raises(TypeError):
        decode_pytest_journal(**arguments)


def _assert_decode(case: Case, observation: JournalObservation) -> None:
    """Aserciones a nivel de prefijo decodificado."""
    if case.consumed is not None:
        assert observation.consumed_bytes == case.consumed
    if case.tail_none is not None:
        assert (observation.tail_sha256 is None) is case.tail_none
    if case.event_count is not None:
        assert len(observation.events) == case.event_count
    if case.decoder_finding is not None:
        assert len(observation.findings) == 1
        assert (
            observation.findings[0].code,
            observation.findings[0].offset,
        ) == case.decoder_finding
    else:
        assert observation.findings == ()


def _assert_reconciled_codes(case: Case, result: object) -> None:
    """Códigos de findings incluidos/excluidos, propiedades e identidades.

    ``findings_exact``/``property_findings_exact`` afirman la tupla completa
    (code, execution_id, nodeid, offset) en el orden contractual del §7; los
    esperados se derivan del contrato y de la entrada construida.
    """
    codes = [item.code for item in result.findings]
    for code in case.codes_include:
        assert code in codes, (case.id, codes)
    for code in case.codes_exclude:
        assert code not in codes, (case.id, codes)
    if case.property_codes is not None:
        assert tuple(item.code for item in result.property_findings) == (case.property_codes)
    if case.findings_exact is not None:
        assert (
            tuple(
                (item.code, item.execution_id, item.nodeid, item.offset) for item in result.findings
            )
            == case.findings_exact
        )
    if case.property_findings_exact is not None:
        assert (
            tuple(
                (item.code, item.execution_id, item.nodeid, item.offset)
                for item in result.property_findings
            )
            == case.property_findings_exact
        )
    if case.identity is not None:
        assert result.identities.status == case.identity
    if case.identity_codes is not None:
        assert tuple(item.code for item in result.identities.findings) == (case.identity_codes)
    if case.preflight is not None:
        assert result.preflight_identities.status == case.preflight


def _assert_execution_views(case: Case, result: object) -> None:
    """Resúmenes de ejecución: protocolo, exit, terminación y tests."""
    collection, producer = result.executions[0], result.executions[1]
    if case.complete is not None:
        assert (collection.protocol_complete, producer.protocol_complete) == (case.complete)
    if case.exit_codes is not None:
        assert (collection.exit_code, producer.exit_code) == case.exit_codes
    if case.termination is not None:
        assert collection.termination == case.termination
    if case.start_seqs is not None:
        assert [test.start_seq for test in producer.tests] == list(case.start_seqs)
    if case.terminals is not None:
        assert tuple(test.nodeid for test in producer.tests if test.terminal) == case.terminals
    if case.eligible_all is not None and producer.tests:
        assert all(test.pass_eligible for test in producer.tests) is case.eligible_all
    if case.dispositions is not None:
        assert tuple(phase.disposition for phase in producer.tests[0].phases) == case.dispositions
    if case.call_disposition is not None:
        assert producer.tests[0].call_disposition == case.call_disposition


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_observation_case(case: Case, monkeypatch: pytest.MonkeyPatch) -> None:
    """Un ID del contrato, un caso: aserciones literales, nada derivado del SUT."""
    if case.patch is not None:
        monkeypatch.setattr(pseq, case.patch[0], case.patch[1])
    if case.type_error_arg is not None:
        _assert_type_error(case)
        return
    if case.decode_raises is not None:
        with pytest.raises(ObservationError) as raised:
            decode_pytest_journal(
                case.data,
                run_id=case.run_id,
                executions=case.executions or _executions(),
                max_bytes=case.max_bytes if case.max_bytes is not None else 1938,
            )
        assert (raised.value.code, raised.value.field) == case.decode_raises
        return
    observation = decode_pytest_journal(
        case.data,
        run_id=case.run_id,
        executions=case.executions or _executions(),
        max_bytes=case.max_bytes if case.max_bytes is not None else max(len(case.data), 1),
    )
    if case.reconcile_raises is not None:
        target = case.manual(observation) if case.manual else observation
        with pytest.raises(ObservationError) as raised:
            reconcile_pytest(target, expected=case.expected, property_ids=case.property_ids)
        assert (raised.value.code, raised.value.field) == case.reconcile_raises
        return
    if case.manual is not None:
        observation = case.manual(observation)
    result = reconcile_pytest(observation, expected=case.expected, property_ids=case.property_ids)
    _assert_decode(case, observation)
    _assert_reconciled_codes(case, result)
    _assert_execution_views(case, result)
    if case.assert_that is not None:
        case.assert_that(observation, result)
    assert result.provenance == "caller-supplied-unverified"


CONTRACT_PROPERTY_FINDING_CODES = (
    "unauthorized_deselection",
    "unauthorized_selection",
    "property_marker_changed",
    "missing_property",
    "unexpected_property",
    "duplicate_property",
)

CONTRACT_NON_BLOCKING_CODES = (
    *CONTRACT_PROPERTY_FINDING_CODES,
    "selection_mismatch",
    "unexpected_test",
)


def test_inventory_catalog_matches_the_contract_literal() -> None:
    """§7 l.470-476: transcripción literal del catálogo de findings de inventory.

    No se compara contra otra constante del andamiaje: los seis códigos
    property y los dos no bloqueantes se transcriben del contrato y el
    conjunto del módulo debe coincidir exactamente (ni alias ni extras).
    """
    assert tuple(sorted(pinv.PROPERTY_FINDING_CODES)) == tuple(
        sorted(CONTRACT_PROPERTY_FINDING_CODES)
    )
    assert frozenset(CONTRACT_NON_BLOCKING_CODES) == pinv.NON_BLOCKING_CODES


def test_inventory_catalog_effect_on_emission_and_completeness() -> None:
    """Efecto del catálogo: emisión/orden property y pertenencia no bloqueante.

    Un run con deselección legítima más selección de property produce un
    finding property y un selection_mismatch: solo el primero se emite como
    property (pertenencia) y ninguno de los dos impide el cierre del
    protocolo (clasificación no bloqueante).
    """
    j = _pa07_property_journal(_pa07_property_selected, selected=2, deselected=1)
    observation = decode_pytest_journal(
        j.bytes(), run_id=RUN_ID, executions=_executions(), max_bytes=4096
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=("p",))

    property_codes = [finding.code for finding in result.property_findings]
    assert property_codes == ["unauthorized_selection"]
    assert "selection_mismatch" not in property_codes
    assert [finding.code for finding in result.findings] == [
        "unauthorized_selection",
        "selection_mismatch",
    ]
    assert result.executions[0].protocol_complete is True
    assert result.executions[1].protocol_complete is True


def _manual_event(
    observation: JournalObservation, position: int, **changes: object
) -> JournalObservation:
    """Observación manual con un campo de JournalEvent reemplazado."""
    events = list(observation.events)
    events[position] = dataclasses.replace(events[position], **changes)
    return dataclasses.replace(observation, events=tuple(events))


def _manual_payload(
    observation: JournalObservation, position: int, **changes: object
) -> JournalObservation:
    """Observación manual con un campo del payload del evento position."""
    payload = dataclasses.replace(observation.events[position].payload, **changes)
    return _manual_event(observation, position, payload=payload)


def _raises_invalid_observation(observation: JournalObservation, field: str) -> None:
    """Reconcile debe rechazar la observación con el campo exacto nombrado."""
    with pytest.raises(ObservationError) as raised:
        reconcile_pytest(observation, expected=("t",), property_ids=())

    assert (raised.value.code, raised.value.field) == ("invalid_observation", field)


class _ForgedStart(ExecutionStart):
    """Subclase con firma idéntica: no sustituye a la clase exacta (§3)."""


def test_manual_control_golden_reconciles_clean() -> None:
    """Control causal: la observation del golden pasa la validación entera."""
    result = reconcile_pytest(_decode_golden(), expected=("t",), property_ids=())

    assert result.findings == ()
    assert result.identities.status == "match"


def test_manual_mutable_argv_is_invalid_observation() -> None:
    """R03-03: argv es tupla; una lista mutable es imposible salida del decoder."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 0, argv=["python"]),
        "events[0].payload.argv",
    )


def test_manual_bool_log_start_is_invalid_observation() -> None:
    """R03-03: bool no sustituye a int en campos U."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 0, log_start=False),
        "events[0].payload.log_start",
    )


def test_manual_invented_outcome_is_invalid_observation() -> None:
    """R03-03: outcome fuera de passed/failed/skipped nunca se clasifica passed."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 20, outcome="invented"),
        "events[20].payload.outcome",
    )


def test_manual_duplicate_seq_is_invalid_observation() -> None:
    """R03-03: el seq global es contiguo desde 1; repetirlo es imposible."""
    _raises_invalid_observation(_manual_event(_decode_golden(), 1, seq=1), "events[1].seq")


def test_manual_local_seq_gap_is_invalid_observation() -> None:
    """R03-03: local_seq por ejecución pytest es contiguo desde 1."""
    _raises_invalid_observation(
        _manual_event(_decode_golden(), 2, local_seq=5),
        "events[2].local_seq",
    )


def test_manual_run_id_of_wrong_type_is_invalid_observation() -> None:
    """R03-07: run_id no-string es invalid_observation, no TypeError interno."""
    _raises_invalid_observation(dataclasses.replace(_decode_golden(), run_id=7), "run_id")


def test_manual_unhashable_execution_id_is_invalid_observation() -> None:
    """R03-03: execution_id no-string se rechaza antes de indexar conjuntos."""
    _raises_invalid_observation(
        _manual_event(_decode_golden(), 1, execution_id=["x"]),
        "events[1].execution_id",
    )


def test_manual_subclass_payload_is_invalid_observation() -> None:
    """§3: no herencia; una subclase con campos extra no pasa por decoder."""
    original = _decode_golden().events[0].payload
    assert isinstance(original, ExecutionStart)
    _raises_invalid_observation(
        _manual_event(_decode_golden(), 0, payload=_ForgedStart(**vars(original))),
        "events[0].payload",
    )


def test_manual_decoder_finding_with_wrong_field_types_is_invalid() -> None:
    """R03-03: los campos del finding del decoder también son tipos exactos."""
    observation = dataclasses.replace(
        _decode_golden(),
        findings=(
            ProtocolFinding(
                code="invalid_json", execution_id=7, nodeid=None, phase=None, offset=1938
            ),
        ),
    )
    _raises_invalid_observation(observation, "findings")


def test_surrogate_in_expected_is_invalid_reference() -> None:
    """R03-07: surrogate en expected es invalid_reference, no UnicodeEncodeError."""
    with pytest.raises(ObservationError) as raised:
        reconcile_pytest(_decode_golden(), expected=("\ud800",), property_ids=())

    assert (raised.value.code, raised.value.field) == ("invalid_reference", "expected")


def _renumbered(order: list[int]) -> bytes:
    """Reordena registros del golden y recalcula seq/local_seq de transporte."""
    rows = [json.loads(GOLDEN_LINES[number]) for number in order]
    per_execution = [0, 0]
    for seq, row in enumerate(rows, start=1):
        row[0] = seq
        if row[3] in (0, 1, 2, 3):
            row[2] = None
        else:
            per_execution[row[1]] += 1
            row[2] = per_execution[row[1]]
    return GOLDEN_LINES[0] + b"".join(_dump(row) for row in rows)


def _event_starts(data: bytes) -> list[int]:
    """Offset inicial de cada línea de evento en un buffer con LF final."""
    starts: list[int] = []
    cursor = data.index(b"\n") + 1
    while cursor < len(data):
        starts.append(cursor)
        cursor = data.index(b"\n", cursor) + 1
    return starts


def test_fsm_control_golden_keeps_both_executions_complete() -> None:
    """Control causal: el golden intacto no produce event_order ni ausencias."""
    observation = decode_pytest_journal(
        GOLDEN, run_id=RUN_ID, executions=_executions(), max_bytes=1938
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())

    assert [finding.code for finding in result.findings] == []
    assert [execution.protocol_complete for execution in result.executions] == [True, True]


def test_fsm_events_after_execution_end_are_event_order_and_incomplete() -> None:
    """R03-01: tras execution_end la FSM está cerrada; todo lo posterior es event_order."""
    order = [*range(1, 18), 26, 27, 28, 29, *range(18, 26)]
    data = _renumbered(order)
    starts = _event_starts(data)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [finding.code for finding in result.findings].count("event_order") == 8
    assert (result.findings[0].code, result.findings[0].execution_id) == (
        "event_order",
        "producer-1",
    )
    assert result.findings[0].offset == starts[21]
    assert producer.tests == ()
    assert producer.protocol_complete is False
    assert result.executions[0].protocol_complete is True
    assert result.identities.status == "mismatch"


def test_fsm_tests_after_session_end_are_event_order_and_incomplete() -> None:
    """R03-01: la sesión cerrada no admite eventos con sesión activa."""
    order = [*range(1, 18), 27, *range(18, 27), 28, 29]
    data = _renumbered(order)
    starts = _event_starts(data)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [finding.code for finding in result.findings].count("event_order") == 9
    assert (result.findings[0].code, result.findings[0].execution_id) == (
        "event_order",
        "producer-1",
    )
    assert result.findings[0].offset == starts[18]
    assert producer.tests == ()
    assert producer.protocol_complete is False


def test_fsm_channel_after_execution_end_is_event_order_plus_absence() -> None:
    """R03-01: channel_end tras execution_end es event_order y falta su cierre."""
    data = _renumbered([*range(1, 28), 29, 28])
    starts = _event_starts(data)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [(finding.code, finding.offset) for finding in result.findings]

    assert ("event_order", starts[28]) in codes
    assert ("missing_channel_end", None) in codes
    assert (producer.termination, producer.exit_code) == ("exited", 0)
    assert producer.protocol_complete is False


def test_channel_truncated_without_tail_is_inconsistent_plus_defect() -> None:
    """R03-08: truncated_channel sin cola exige channel_inconsistent (§5)."""
    data = _golden_with(28, _line(28, 1, None, 2, [False, 0, None, "truncated_channel"]))
    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [(finding.code, finding.offset) for finding in result.findings]

    assert ("channel_defect", _golden_offsets()[28]) in codes
    assert ("channel_inconsistent", _golden_offsets()[28]) in codes
    assert producer.protocol_complete is False


def test_channel_io_error_without_tail_keeps_only_channel_defect() -> None:
    """Control §5: io_error sin cola es uno de los cuatro defectos permitidos."""
    data = _golden_with(28, _line(28, 1, None, 2, [False, 0, None, "io_error"]))
    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    codes = [finding.code for finding in result.findings]

    assert "channel_defect" in codes
    assert "channel_inconsistent" not in codes


def _renumbered_rows(rows: list[object]) -> bytes:
    """Renumeración de transporte (seq/local_seq) sobre filas ya ordenadas."""
    per_execution = [0, 0]
    for seq, row in enumerate(rows, start=1):
        row[0] = seq
        if row[3] in (0, 1, 2, 3):
            row[2] = None
        else:
            per_execution[row[1]] += 1
            row[2] = per_execution[row[1]]
    return GOLDEN_LINES[0] + b"".join(_dump(row) for row in rows)


def _renumbered(order: list[int]) -> bytes:
    """Reordena registros del golden y recalcula seq/local_seq de transporte."""
    return _renumbered_rows([json.loads(GOLDEN_LINES[number]) for number in order])


def _with_inserted_row(after_events: int, row: list[object]) -> bytes:
    """Inserta una fila nueva tras la posición dada y renumera el transporte."""
    rows = [json.loads(GOLDEN_LINES[number]) for number in range(1, 30)]
    rows.insert(after_events, row)
    return _renumbered_rows(rows)


def test_fsm_channel_end_before_tests_is_event_order_and_incomplete() -> None:
    """R1-01: channel_end no reabre la fase de tests; §5 fija tests→plugins_end."""
    data = _renumbered([*range(1, 18), 28, *range(18, 28), 29])

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]
    complete = [execution.protocol_complete for execution in result.executions]
    tests = [(test.terminal, test.pass_eligible) for test in producer.tests]

    assert codes.count("event_order") == 10
    assert complete == [True, False]
    assert tests == []


def test_fsm_plugins_end_before_tests_is_event_order_and_incomplete() -> None:
    """R1-01: tras plugins_end no hay tests; el cierre es justo antes de session_end."""
    data = _renumbered([*range(1, 18), 26, *range(18, 26), 27, 28, 29])

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]
    complete = [execution.protocol_complete for execution in result.executions]
    tests = [(test.terminal, test.pass_eligible) for test in producer.tests]

    assert codes.count("event_order") == 8
    assert complete == [True, False]
    assert tests == []


def test_fsm_declaration_after_session_end_is_event_order() -> None:
    """R1-01: las declaraciones exigen sesión activa; tras session_end es event_order."""
    data = _with_inserted_row(27, [0, 1, None, 0, [1, "u"]])

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]
    complete = [execution.protocol_complete for execution in result.executions]
    tests = [(test.terminal, test.pass_eligible) for test in producer.tests]

    assert codes.count("event_order") == 1
    assert complete == [True, False]
    assert tests == [(True, True)]


def test_control_declaration_during_session_stays_valid() -> None:
    """Control R1-01: declarar durante sesión activa sigue siendo metadata válida."""
    data = _with_inserted_row(15, [0, 1, None, 0, [1, "u"]])

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]
    complete = [execution.protocol_complete for execution in result.executions]
    tests = [(test.terminal, test.pass_eligible) for test in producer.tests]

    assert codes == []
    assert complete == [True, True]
    assert tests == [(True, True)]


def test_manual_start_digest_must_match_its_expectation() -> None:
    """R1-02: los hashes del execution_start vienen de la cabecera; no se alteran."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 0, input_sha256="b" * 64),
        "events[0].payload.input_sha256",
    )


def test_manual_start_role_must_match_its_expectation() -> None:
    """R1-02: el rol del evento y el de la expectativa coinciden por construcción."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 0, role="producer"),
        "events[0].payload.role",
    )


def test_manual_declaration_index_must_be_contiguous() -> None:
    """R1-02: la tabla de declaraciones es contigua desde 0 también a mano."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 3, index=9),
        "events[3].payload.index",
    )


def test_manual_declaration_substitution_breaks_resolution() -> None:
    """R1-02: cambiar el string declarado deja referencias sin declaración previa."""
    _raises_invalid_observation(
        _manual_payload(_decode_golden(), 3, nodeid="u"),
        "events[4].payload.nodeid",
    )


def test_manual_foreign_decoder_finding_execution_is_invalid() -> None:
    """R1-02: un finding con ejecución desconocida no puede ocultar el defecto."""
    observation = dataclasses.replace(
        _decode_golden(),
        findings=(
            ProtocolFinding(
                code="invalid_json", execution_id="foreign", nodeid=None, phase=None, offset=1938
            ),
        ),
        tail_sha256=D64,
    )
    _raises_invalid_observation(observation, "findings")


def test_start_only_execution_reports_session_and_closures_missing() -> None:
    """R1-08: con start sin sesión faltan cierre de canal y de proceso también."""
    data = _renumbered([1])

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    codes = [finding.code for finding in result.findings]

    assert codes == [
        "missing_channel_end",
        "missing_execution_end",
        "missing_session_start",
        "missing_execution",
    ]


def test_launch_error_with_session_and_tests_is_termination_inconsistent() -> None:
    """R1-07: launch_error no convive con sesión/fases legítimas; se conserva la causa."""
    data = _golden_with(
        29, _line(29, 1, None, 3, [None, "launch_error", None, 0, EMPTY_SHA, 2, UTC2, False])
    )

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]
    complete = [execution.protocol_complete for execution in result.executions]
    tests = [(test.terminal, test.pass_eligible) for test in producer.tests]

    assert "termination_inconsistent" in codes
    assert complete == [True, False]
    assert tests == [(True, True)]


_CLOSER_NAMES = {6: "P", 19: "S", 2: "C", 3: "E"}
_CLOSURE_MATRIX = [
    (execution_index, positions, order)
    for execution_index, positions in ((0, (8, 9, 10, 11)), (1, (26, 27, 28, 29)))
    for order in itertools.permutations(positions)
]


_CLOSURE_IDS = [
    f"exec{execution_index}:"
    + "-".join(_CLOSER_NAMES[json.loads(GOLDEN_LINES[source])[3]] for source in order)
    for execution_index, _positions, order in _CLOSURE_MATRIX
]


@pytest.mark.parametrize(
    ("execution_index", "positions", "order"),
    _CLOSURE_MATRIX,
    ids=_CLOSURE_IDS,
)
def test_closure_matrix_only_the_normative_order_completes(
    execution_index: int, positions: tuple[int, ...], order: tuple[int, ...]
) -> None:
    """R2-01: la única ruta que completa es plugins→session→channel→execution (§5)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 30)]
    for destination, source in zip(positions, order, strict=True):
        rows[destination - 1] = json.loads(GOLDEN_LINES[source])
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    execution = result.executions[execution_index]

    assert observation.findings == ()
    assert execution.protocol_complete is (order == positions)
    if order != positions:
        assert any(
            finding.code == "event_order" and finding.execution_id == execution.execution_id
            for finding in result.findings
        )


def test_duplicate_test_end_invalidates_the_closed_instance() -> None:
    """R2-04: test_start/test_end únicos; el duplicado quita terminal y PASS (§6)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
    rows.append(json.loads(GOLDEN_LINES[25]))
    rows.extend(json.loads(GOLDEN_LINES[n]) for n in range(26, 30))
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert any(finding.code == "test_order" for finding in result.findings)
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(False, False)]
    assert producer.protocol_complete is False
    assert result.identities.status == "mismatch"


def test_launch_error_with_session_without_tests_is_inconsistent() -> None:
    """R2-03: §5 prohíbe sesión con launch_error también sin fases (causa visible)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 30)]
    rows[10][4][:3] = [None, "launch_error", None]
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())

    assert any(
        finding.code == "termination_inconsistent" and finding.execution_id == "collection-1"
        for finding in result.findings
    )
    assert [execution.protocol_complete for execution in result.executions] == [False, True]


def test_control_launch_error_without_session_has_no_termination_cause() -> None:
    """Control R2-03: launch_error sin sesión observada no agrega esa causa (§5)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 12)]
    rows.append(json.loads(GOLDEN_LINES[12]))
    rows.append(json.loads(GOLDEN_LINES[28]))
    last = json.loads(GOLDEN_LINES[29])
    last[4][:3] = [None, "launch_error", None]
    rows.append(last)
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())

    assert all(finding.code != "termination_inconsistent" for finding in result.findings)


def _manual_inventory_observation(count: int) -> JournalObservation:
    """Observación manual con count pares item/selected y offsets reales (§2)."""
    base = _decode_golden()
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 5)]
    for _ in range(count):
        rows.append(json.loads(GOLDEN_LINES[5]))
        rows.append(json.loads(GOLDEN_LINES[6]))
    rows.append(json.loads(GOLDEN_LINES[7]))
    rows.extend(json.loads(GOLDEN_LINES[n]) for n in range(8, 30))
    rows[4 + 2 * count][4] = [count, 0]
    data = _renumbered_rows(rows)
    lines = data.splitlines(keepends=True)
    templates = (
        list(base.events[:4])
        + [event for _ in range(count) for event in base.events[4:6]]
        + [
            dataclasses.replace(
                base.events[6],
                payload=dataclasses.replace(base.events[6].payload, selected_count=count),
            )
        ]
        + list(base.events[7:])
    )
    events: list[object] = []
    offset = len(lines[0])
    for template, line in zip(templates, lines[1:], strict=True):
        wire = json.loads(line)
        events.append(
            dataclasses.replace(
                template,
                seq=wire[0],
                local_seq=wire[2],
                offset=offset,
                end_offset=offset + len(line),
            )
        )
        offset += len(line)
    return dataclasses.replace(
        base,
        events=tuple(events),
        consumed_bytes=len(data),
        max_bytes=2_097_152,
    )


def test_manual_inventory_at_the_exact_cap_reconciles() -> None:
    """Control R2-02: 10 000 entradas por inventario es la frontera exacta (§2)."""
    result = reconcile_pytest(
        _manual_inventory_observation(10_000), expected=("t",), property_ids=()
    )

    assert result.provenance == "caller-supplied-unverified"


def test_manual_inventory_over_the_cap_is_invalid_observation() -> None:
    """R2-02: 10 001 entradas manuales son imposibles del decoder (§2/§4)."""
    with pytest.raises(ObservationError) as raised:
        reconcile_pytest(_manual_inventory_observation(10_001), expected=("t",), property_ids=())

    assert raised.value.code == "invalid_observation"


def _manual_declarations_observation(count: int) -> JournalObservation:
    """Observación manual con count declaraciones contiguas y únicas (§3)."""
    events: list[object] = []
    cursor = len(GOLDEN_LINES[0])
    for index in range(count):
        length = 30
        events.append(
            JournalEvent(
                seq=index + 1,
                execution_id="collection-1",
                origin="supervisor",
                local_seq=None,
                kind="node_declaration",
                payload=NodeDeclaration(index=index, nodeid=f"n{index}"),
                offset=cursor,
                end_offset=cursor + length,
            )
        )
        cursor += length
    return dataclasses.replace(
        _decode_golden(),
        events=tuple(events),
        consumed_bytes=cursor,
        findings=(),
        tail_sha256=None,
        max_bytes=2_097_152,
    )


def test_manual_declarations_over_the_cap_are_invalid_observation() -> None:
    """R2-02: el tope de 20 000 declaraciones también rige en entrada manual (§3)."""
    with pytest.raises(ObservationError) as raised:
        reconcile_pytest(_manual_declarations_observation(20_001), expected=(), property_ids=())

    assert raised.value.code == "invalid_observation"


def test_manual_declarations_at_the_exact_cap_pass_validation() -> None:
    """Control R2-02: 20 000 declaraciones exactas validan la observación (§3)."""
    result = reconcile_pytest(
        _manual_declarations_observation(20_000), expected=(), property_ids=()
    )

    assert result.provenance == "caller-supplied-unverified"


@pytest.mark.parametrize(
    "insert_after",
    [26, 27, 28],
    ids=["tras-plugins", "tras-sesion", "tras-canal"],
)
def test_duplicate_test_end_after_a_closer_still_invalidates(insert_after: int) -> None:
    """R3-01: el rechazo temprano de un end duplicado también invalida (§6)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, insert_after + 1)]
    rows.append(json.loads(GOLDEN_LINES[25]))
    rows.extend(json.loads(GOLDEN_LINES[n]) for n in range(insert_after + 1, 30))
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(False, False)]
    assert any(
        finding.code == "event_order" and finding.nodeid == "t" for finding in result.findings
    )
    assert producer.protocol_complete is False


def test_duplicate_end_of_first_instance_invalidates_only_the_first() -> None:
    """Control §6: el end duplicado de la primera no toca la segunda instancia."""
    rows = _renumbered_rows(
        [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
        + [json.loads(GOLDEN_LINES[25])]
        + [json.loads(GOLDEN_LINES[n]) for n in range(18, 26)]
        + [json.loads(GOLDEN_LINES[n]) for n in range(26, 30)]
    )

    observation = decode_pytest_journal(
        rows, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(rows), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [
        (False, False),
        (True, True),
    ]
    assert result.identities.status == "match"


def test_duplicate_end_of_last_instance_invalidates_only_the_last() -> None:
    """Control §6: el end duplicado de la última no toca la primera instancia."""
    rows = _renumbered_rows(
        [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
        + [json.loads(GOLDEN_LINES[n]) for n in range(18, 26)]
        + [json.loads(GOLDEN_LINES[25])]
        + [json.loads(GOLDEN_LINES[n]) for n in range(26, 30)]
    )

    observation = decode_pytest_journal(
        rows, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(rows), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [
        (True, True),
        (False, False),
    ]


def test_complete_then_incomplete_same_id_keeps_first_terminal() -> None:
    """Control §6: la primera completa conserva su terminal con la segunda incompleta."""
    rows = _renumbered_rows(
        [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
        + [json.loads(GOLDEN_LINES[n]) for n in range(18, 25)]
        + [json.loads(GOLDEN_LINES[n]) for n in range(26, 30)]
    )

    observation = decode_pytest_journal(
        rows, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(rows), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [
        (True, True),
        (False, False),
    ]
    assert any(finding.code == "missing_test_end" for finding in result.findings)


@pytest.mark.parametrize(
    ("code", "name"), [(17, "internal_error"), (18, "interrupted")], ids=["17", "18"]
)
def test_diagnostics_after_channel_with_session_open_keep_the_cause(code: int, name: str) -> None:
    """Control declarado: el diagnóstico tras channel conserva causa, sin falso completo."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
    rows.append(json.loads(GOLDEN_LINES[28]))
    rows.append([0, 1, 0, code, ["RuntimeError"]])
    rows.append(json.loads(GOLDEN_LINES[29]))
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]

    assert name in codes
    assert "missing_plugins_end" in codes
    assert "missing_session_end" in codes
    assert producer.protocol_complete is False


@pytest.mark.parametrize(
    "count",
    [1, 2, 3, 4],
    ids=["plugins", "sesion", "canal", "ejecucion"],
)
def test_late_end_of_active_instance_preserves_the_previous_terminal(count: int) -> None:
    """R4-01: el end tardío de la instancia activa no invalida la anterior (§6/§7)."""
    rows = [json.loads(GOLDEN_LINES[n]) for n in range(1, 26)]
    rows += [json.loads(GOLDEN_LINES[n]) for n in range(18, 25)]
    rows += [json.loads(GOLDEN_LINES[n]) for n in range(26, 26 + count)]
    rows.append(json.loads(GOLDEN_LINES[25]))
    rows += [json.loads(GOLDEN_LINES[n]) for n in range(26 + count, 30)]
    data = _renumbered_rows(rows)

    observation = decode_pytest_journal(
        data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [test.start_seq for test in producer.tests] == [18, 26]
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [
        (True, True),
        (False, False),
    ]
    assert any(
        finding.code == "event_order" and finding.nodeid == "t" for finding in result.findings
    )
    assert any(finding.code == "missing_test_end" for finding in result.findings)
    assert result.identities.status == "match"


def test_control_only_active_late_end_never_fabricates_terminal() -> None:
    """Control R4-01: sin instancia previa, el end tardío no fabrica terminal."""
    rows = _renumbered_rows(
        [json.loads(GOLDEN_LINES[n]) for n in range(1, 25)]
        + [json.loads(GOLDEN_LINES[26]), json.loads(GOLDEN_LINES[25])]
        + [json.loads(GOLDEN_LINES[n]) for n in range(27, 30)]
    )

    observation = decode_pytest_journal(
        rows, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(rows), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(False, False)]
    assert any(finding.code == "event_order" for finding in result.findings)
    assert any(finding.code == "missing_test_end" for finding in result.findings)


def test_duplicate_end_after_execution_without_active_invalidates() -> None:
    """Control R2-04: end duplicado post-execution sin instancia activa invalida."""
    rows = _renumbered_rows(
        [json.loads(GOLDEN_LINES[n]) for n in range(1, 30)] + [json.loads(GOLDEN_LINES[25])]
    )

    observation = decode_pytest_journal(
        rows, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(rows), 1)
    )
    result = reconcile_pytest(observation, expected=("t",), property_ids=())
    producer = result.executions[1]

    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(False, False)]
    assert result.identities.status == "mismatch"


def _mini_collection(
    pre: Callable[[Journal], None] | None = None,
    post: Callable[[Journal], None] | None = None,
) -> bytes:
    """Colección mínima declarando t, con ganchos antes y después del cierre."""
    j = Journal()
    j.start(0)
    j.session(0)
    j.ev(0, 7, [D64, True])
    j.declare(0, "t")
    if pre is not None:
        pre(j)
    j.ev(0, 12, [0, 0])
    if post is not None:
        post(j)
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    return j.bytes()


def _producer_with(inject: Callable[[Journal], None]) -> bytes:
    """Colección íntegra más productor estándar con una inyección posicionada."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugins_end(1)
    inject(j)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


def test_duplicate_singleton_events_are_duplicate_event() -> None:
    """§5: duplicar execution_start/session_start/options es duplicate_event."""
    skeletons = (
        [lambda j: j.start(0), lambda j: j.start(0)],
        [lambda j: j.session(0), lambda j: j.session(0)],
        [lambda j: j.ev(0, 7, [D64, True]), lambda j: j.ev(0, 7, [D64, True])],
    )
    for first, duplicate in skeletons:
        j = Journal()
        j.start(0)
        j.session(0)
        j.ev(0, 7, [D64, True])
        first(j)
        duplicate(j)
        j.declare(0, "t")
        j.ev(0, 12, [0, 0])
        j.plugins_end(0)
        j.session_end(0)
        j.channel(0)
        j.execution_end(0)
        data = j.bytes()
        observation = decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        )
        result = reconcile_pytest(observation, expected=(), property_ids=())
        assert "duplicate_event" in [finding.code for finding in result.findings]


def test_collect_report_paths_are_visible() -> None:
    """§5: collect_report ok pasa; failed agrega causa; tardío es event_order."""
    ok = _mini_collection(pre=lambda j: j.ev(0, 9, [0, 0]))
    result_ok = reconcile_pytest(
        decode_pytest_journal(
            ok, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(ok), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "collection_report_nonpass" not in [finding.code for finding in result_ok.findings]

    failed = _mini_collection(pre=lambda j: j.ev(0, 9, [0, 1]))
    result_failed = reconcile_pytest(
        decode_pytest_journal(
            failed, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(failed), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "collection_report_nonpass" in [finding.code for finding in result_failed.findings]

    late = _mini_collection(post=lambda j: j.ev(0, 9, [0, 0]))
    result_late = reconcile_pytest(
        decode_pytest_journal(
            late, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(late), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "event_order" in [finding.code for finding in result_late.findings]


def test_options_out_of_position_is_event_order() -> None:
    """§5: options después del primer item es event_order; duplicado es duplicate."""
    j = Journal()
    j.start(0)
    j.ev(0, 4, ["9.1.1", "1.6.0", "wct-pytest-observer/1", D64])
    j.declare(0, "t")
    j.ev(0, 8, [0, False])
    j.ev(0, 7, [D64, True])
    j.ev(0, 12, [0, 0])
    j.plugins_end(0)
    j.session_end(0)
    j.channel(0)
    j.execution_end(0)
    data = j.bytes()
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "event_order" in [finding.code for finding in result.findings]


def test_selection_events_out_of_order_are_event_order() -> None:
    """§5: deselected/selected tardíos o de nodeid no recolectado son event_order."""
    unknown = _mini_collection(
        pre=lambda j: (
            j.declare(1, "u"),
            j.ev(0, 10, [1, False]),
        )
    )
    result_unknown = reconcile_pytest(
        decode_pytest_journal(
            unknown, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(unknown), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "event_order" in [finding.code for finding in result_unknown.findings]

    late_selected = _mini_collection(post=lambda j: j.ev(0, 11, [0]))
    result_late = reconcile_pytest(
        decode_pytest_journal(
            late_selected,
            run_id=RUN_ID,
            executions=_executions(),
            max_bytes=max(len(late_selected), 1),
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "event_order" in [finding.code for finding in result_late.findings]


def test_duplicate_collection_end_is_duplicate_event() -> None:
    """§5: collection_end duplicado es duplicate_event."""
    data = _mini_collection(post=lambda j: j.ev(0, 12, [0, 0]))
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "duplicate_event" in [finding.code for finding in result.findings]


def test_closer_duplicates_are_duplicate_event() -> None:
    """§5: session_end, session_end_error y channel_end duplicados son duplicate_event."""
    for inject in (
        lambda j: (j.session_end(1), j.session_end(1)),
        lambda j: (j.session_end(1), j.ev(1, 20, ["RuntimeError"])),
        lambda j: (j.channel(1), j.channel(1)),
    ):
        j = Journal()
        _collection(j)
        j.start(1)
        j.session(1)
        j.item(1, 0)
        j.select(1, 0)
        j.collect_end(1, selected=1)
        inject(j)
        j.channel(1)
        j.execution_end(1)
        data = j.bytes()
        result = reconcile_pytest(
            decode_pytest_journal(
                data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
            ),
            expected=("t",),
            property_ids=(),
        )
        assert "duplicate_event" in [finding.code for finding in result.findings]


def test_phase_in_collection_role_is_test_order() -> None:
    """§5: la colección no admite fases; phase_make en collection es test_order."""
    data = _mini_collection(pre=lambda j: j.ev(0, 14, [0, 0, 0, False, None, False, None]))
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "test_order" in [finding.code for finding in result.findings]


def test_plugin_and_diagnostic_out_of_position_are_visible() -> None:
    """§5: plugin tras plugins_end es event_order; diagnóstico tras session también."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugins_end(1)
    j.plugin_claim(1, "p")
    j.session_end(1)
    j.ev(1, 17, ["RuntimeError"])
    j.channel(1)
    j.execution_end(1)
    data = j.bytes()
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    codes = [finding.code for finding in result.findings]
    assert codes.count("event_order") == 2
    assert "internal_error" not in codes


def test_plugins_end_inventory_findings() -> None:
    """§5: conteo erróneo y nombres repetidos se conservan como findings."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugin_claim(1, "p")
    j.plugin_claim(1, "p")
    j.plugins_end(1, count=3)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    data = j.bytes()
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    codes = [finding.code for finding in result.findings]
    assert "plugin_count_mismatch" in codes
    assert "duplicate_plugin" in codes


@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        (lambda o: dataclasses.replace(o, events=list(o.events)), "events"),
        (
            lambda o: dataclasses.replace(
                o,
                findings=[o.findings[0]]
                if o.findings
                else [ProtocolFinding("invalid_json", None, None, None, 0)],
            ),
            "findings",
        ),
        (lambda o: dataclasses.replace(o, tail_sha256="no-digest"), "tail_sha256"),
        (lambda o: dataclasses.replace(o, executions=list(o.executions)), "executions"),
        (
            lambda o: dataclasses.replace(o, executions=(o.executions[0], "no-soy-expectativa")),
            "executions[1]",
        ),
        (lambda o: dataclasses.replace(o, max_bytes=0), "max_bytes"),
        (
            lambda o: dataclasses.replace(
                o,
                findings=(
                    ProtocolFinding("hallazgo-inventado", None, None, None, o.consumed_bytes),
                ),
            ),
            "findings",
        ),
        (
            lambda o: dataclasses.replace(
                o,
                findings=(ProtocolFinding("invalid_json", None, None, None, o.consumed_bytes + 1),),
            ),
            "findings",
        ),
        (
            lambda o: dataclasses.replace(o, events=(object(),)),
            "events[0]",
        ),
        (lambda o: _manual_event(o, 1, seq=-5), "events[1].seq"),
        (
            lambda o: _manual_event(
                o, 9, execution_id="collection-1", origin="supervisor", local_seq=3
            ),
            "events[9].local_seq",
        ),
        (lambda o: _manual_event(o, 2, offset=1, end_offset=2), "events[2].offset"),
    ],
)
def test_manual_observation_schema_rejections(mutate, field: str) -> None:
    """§2: el esquema de observación manual rechaza cada desvío con su campo."""
    base = _decode_golden()
    _raises_invalid_observation(mutate(base), field)


def test_duplicate_execution_end_is_duplicate_event() -> None:
    """§5: execution_end singleton duplicado es duplicate_event."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    j.execution_end(1)
    data = j.bytes()
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "duplicate_event" in [finding.code for finding in result.findings]


def test_abnormal_exit_is_visible_as_cause() -> None:
    """§5: exit fuera de 0/1 agrega abnormal_exit sin reinterpretarlo."""
    data = _golden_with(
        29, _line(29, 1, None, 3, [2, "exited", None, 0, EMPTY_SHA, 2, UTC2, False])
    )
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "abnormal_exit" in [finding.code for finding in result.findings]


def test_execution_bounds_regression_is_visible() -> None:
    """§5: log_end menor que log_start del arranque agrega execution_bounds."""
    j = Journal()
    _collection(j)
    j.sup(1, 1, [["python"], "/r", 500, 1, UTC])
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.sup(1, 3, [0, "exited", None, 400, EMPTY_SHA, 2, UTC2, False])
    data = j.bytes()
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    assert "execution_bounds" in [finding.code for finding in result.findings]


# --- C1-03: ramas de comportamiento restantes (orden tras cierres, duplicados,
# validación manual y límites de intervalo). Oráculos desde el contrato §4/§5. ---


def test_manual_non_string_origin_is_invalid_observation() -> None:
    """§3: origin no-string no consulta el catálogo ni sustituye la clase."""
    _raises_invalid_observation(_manual_event(_decode_golden(), 1, origin=7), "events[1].payload")


def test_manual_non_positive_local_seq_is_invalid_observation() -> None:
    """§3: local_seq 0 en worker es invalid_observation, no solo el hueco."""
    _raises_invalid_observation(
        _manual_event(_decode_golden(), 2, local_seq=0), "events[2].local_seq"
    )


def test_manual_event_span_beyond_line_max_is_invalid_observation() -> None:
    """§3: el intervalo del evento no puede exceder el tope de línea de 64KiB."""
    golden = _decode_golden()
    stretched = dataclasses.replace(golden, consumed_bytes=70000, max_bytes=10**6)
    target = stretched.events[1]

    _raises_invalid_observation(
        _manual_event(stretched, 1, end_offset=target.offset + 65537),
        "events[1].offset",
    )


def _producer_pre_plugins(inject: Callable[[Journal], None]) -> bytes:
    """Productor íntegro con una inyección tras collect_end y antes de plugins_end."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    inject(j)
    j.test_start(1, index=0)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=0)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    return j.bytes()


@pytest.mark.parametrize(
    "inject",
    [
        pytest.param(lambda j: j.item(1, 0), id="item"),
        pytest.param(lambda j: j.deselect(1, 0), id="deselected"),
        pytest.param(lambda j: j.select(1, 0), id="selected"),
    ],
)
def test_inventory_event_after_collection_close_is_event_order(
    inject: Callable[[Journal], None],
) -> None:
    """§5: item/deselect/selected tras collection_end no reabren la colección."""
    data = _producer_pre_plugins(inject)

    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]

    assert codes.count("event_order") == 1
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(True, True)]


def test_phase_of_other_nodeid_is_test_order_and_active_test_survives() -> None:
    """§5: fase de otro nodeid no alimenta la instancia activa de t."""
    j = Journal()
    _collection(j, nodeids=("t", "u"))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1, index=0)
    j.phases(1, 1, [(0, 0)])
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=0)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    data = j.bytes()

    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]

    assert codes.count("test_order") == 2
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(True, True)]


def test_late_duplicate_end_after_execution_end_skips_foreign_instances() -> None:
    """R4-01: el duplicado tardío de t invalida la última t, no la u cerrada antes."""
    j = Journal()
    _collection(j, nodeids=("t", "u"), selected=(0, 1), end_counts=(2, 0))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.item(1, 1)
    j.select(1, 0)
    j.select(1, 1)
    j.collect_end(1, selected=2)
    j.test_start(1, index=0)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=0)
    j.test_start(1, index=1)
    j.phases(1, 1, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=1)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    j.test_end(1, index=0)
    data = j.bytes()

    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]

    assert codes.count("event_order") == 1
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [
        (False, False),
        (True, True),
    ]
    assert result.identities.status == "mismatch"


def test_duplicate_plugins_end_is_duplicate_event() -> None:
    """§5: plugins_end es singleton; repetirlo es duplicate_event, no cierre nuevo."""
    data = _producer_with(lambda j: j.plugins_end(1))

    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    codes = [finding.code for finding in result.findings]

    assert codes.count("duplicate_event") == 1


def test_selected_of_nodeid_never_collected_is_event_order() -> None:
    """§5: select de un nodeid sin item en la ejecución es event_order."""
    j = Journal()
    _collection(j, nodeids=("t", "u"), deselects=(1,), end_counts=(1, 1))
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.select(1, 1)
    j.collect_end(1, selected=1)
    j.test_start(1, index=0)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=0)
    j.plugins_end(1)
    j.session_end(1)
    j.channel(1)
    j.execution_end(1)
    data = j.bytes()

    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    producer = result.executions[1]
    codes = [finding.code for finding in result.findings]

    assert codes.count("event_order") == 1
    assert [(test.terminal, test.pass_eligible) for test in producer.tests] == [(True, True)]


# --- Regresiones de la adjudicación de sobrevivientes (lote normativo
# scan_closers, ADJUDICACION-SOBREVIVIENTES-SCAN-CLOSERS.md). Cada oráculo
# mata los mutantes que sobrevivieron sin él; rojo verificado contra
# MUTANT_UNDER_TEST en la copia de mutación. ---


def _producer_closers(
    channel: list[object], session: list[tuple[int, list[object]]]
) -> tuple[bytes, int]:
    """Productor íntegro con cierres de sesión parametrizados y offset del evento 20."""
    j = Journal()
    _collection(j)
    j.start(1)
    j.session(1)
    j.item(1, 0)
    j.select(1, 0)
    j.collect_end(1, selected=1)
    j.test_start(1, index=0)
    j.phases(1, 0, [(0, 0), (1, 0), (2, 0)])
    j.test_end(1, index=0)
    j.plugins_end(1)
    for code, payload in session:
        if code == 19:
            j.session_end(1)
        else:
            j.ev(1, code, payload)
    j.channel(1, tail=channel)
    j.execution_end(1)
    offset = len(_header()) + sum(len(line) for line in j.lines[: len(j.lines) - 3])
    return j.bytes(), offset


@pytest.mark.parametrize(
    ("channel", "code"),
    [
        pytest.param(
            [True, 5, EMPTY_SHA, "truncated_channel"], "channel_defect", id="defecto-declarado"
        ),
        pytest.param([False, 0, None, None], "channel_inconsistent", id="inconsistente"),
    ],
)
def test_channel_findings_carry_execution_id(channel: list[object], code: str) -> None:
    """§7: los findings de canal conservan la identidad de su ejecución."""
    data, _ = _producer_closers(channel, session=[(19, [0, 0])])
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    findings = [finding for finding in result.findings if finding.code == code]

    assert findings, [finding.code for finding in result.findings]
    assert all(finding.execution_id == "producer-1" for finding in findings), [
        (finding.code, finding.execution_id) for finding in findings
    ]


def test_channel_tail_of_one_byte_requires_sha_and_defect() -> None:
    """§5: una cola de 1 byte sin digest ni defecto es channel_inconsistent."""
    data, _ = _producer_closers([True, 1, None, None], session=[(19, [0, 0])])
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )

    assert any(finding.code == "channel_inconsistent" for finding in result.findings), [
        finding.code for finding in result.findings
    ]


def test_channel_eof_with_declared_defect_and_no_tail_is_inconsistent() -> None:
    """§5: eof con defecto declarado y sin cola no pasa por coherente."""
    data, _ = _producer_closers([True, 0, None, "timeout"], session=[(19, [0, 0])])
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )

    assert any(finding.code == "channel_inconsistent" for finding in result.findings), [
        finding.code for finding in result.findings
    ]


def test_session_end_after_session_end_error_is_duplicate() -> None:
    """§5: session_end es singleton aunque session_end_error ya hubiera cerrado."""
    data, _ = _producer_closers(
        [True, 0, None, None],
        session=[(20, ["KeyboardInterrupt"]), (19, [0, 0])],
    )
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    codes = [finding.code for finding in result.findings]

    assert codes.count("duplicate_event") == 1, codes


def test_session_end_error_finding_keeps_its_offset() -> None:
    """§7: el finding session_end_error conserva el offset de su evento."""
    data, offset = _producer_closers([True, 0, None, None], session=[(20, ["KeyboardInterrupt"])])
    result = reconcile_pytest(
        decode_pytest_journal(
            data, run_id=RUN_ID, executions=_executions(), max_bytes=max(len(data), 1)
        ),
        expected=("t",),
        property_ids=(),
    )
    findings = [finding for finding in result.findings if finding.code == "session_end_error"]

    assert findings, [finding.code for finding in result.findings]
    assert all(finding.offset == offset for finding in findings), [
        (finding.code, finding.offset) for finding in findings
    ]
