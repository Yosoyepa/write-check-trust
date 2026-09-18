"""Contratos wire del journal compacto (SH-P03a/1): framing, payloads y límites.

Los bytes esperados son literales independientes del SUT: la cabecera canónica
se transcribe del contrato y los journals negativos se construyen con un
serializador propio del test, nunca llamando al decoder. Los bordes de
inventarios se aislan con constantes internas reducidas vía monkeypatch.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields as dataclass_fields
import hashlib
import json

import pytest

from tools.wct.evidence import (
    pytest_payloads as pp,
    pytest_schema as ps,
    pytest_sequence as pseq,
    pytest_types as pt,
)
from tools.wct.evidence.pytest_observation import decode_pytest_journal, reconcile_pytest

RUN_ID = "0" * 32
OTHER_RUN_ID = "1" * 32
D64 = "a" * 64
TAIL_EMPTY = hashlib.sha256(b"").hexdigest()


def _executions() -> tuple[pt.ExecutionExpectation, ...]:
    """Las dos expectativas normativas en orden."""
    return (
        pt.ExecutionExpectation("collection-1", "collection", D64, D64, D64),
        pt.ExecutionExpectation("producer-1", "producer", D64, D64, D64),
    )


HEADER_LITERAL = (
    '{"executions":[["collection-1","collection","'
    + D64
    + '","'
    + D64
    + '","'
    + D64
    + '"],["producer-1","producer","'
    + D64
    + '","'
    + D64
    + '","'
    + D64
    + '"]],"record_type":"wct-pytest-journal","run_id":"'
    + RUN_ID
    + '","schema_version":1}\n'
)


def _dump(value: object) -> bytes:
    """Serialización canónica del wire, escrita en el test y no en el SUT."""
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    ).encode("utf-8")


def _header(**overrides: object) -> dict[str, object]:
    header: dict[str, object] = {
        "schema_version": 1,
        "record_type": "wct-pytest-journal",
        "run_id": RUN_ID,
        "executions": [
            ["collection-1", "collection", D64, D64, D64],
            ["producer-1", "producer", D64, D64, D64],
        ],
    }
    header.update(overrides)
    return header


def _wire_header(**overrides: object) -> bytes:
    return _dump(_header(**overrides)) + b"\n"


def _event(seq: int, ex: int, local: int | None, code: int, payload: list[object]) -> bytes:
    return _dump([seq, ex, local, code, payload]) + b"\n"


def _decode_kwargs(
    data: bytes, *, run_id: str = RUN_ID, max_bytes: int | None = None
) -> dict[str, object]:
    """Argumentos canónicos del decoder para los bytes del test."""
    return {
        "data": data,
        "run_id": run_id,
        "executions": _executions(),
        "max_bytes": max(len(data), 1) if max_bytes is None else max_bytes,
    }


def _minimal_journal() -> bytes:
    """Cabecera más cuatro eventos válidos de la ejecución de colección."""
    return _wire_header() + b"".join(
        [
            _event(1, 0, None, 1, [["python", "-m", "pytest"], "/r", 0, 1, _UTC]),
            _event(2, 0, 1, 4, ["9.1.1", "1.6.0", "wct-pytest-observer/1", D64]),
            _event(3, 0, 2, 7, [D64, True]),
            _event(4, 0, None, 0, [0, "t"]),
        ]
    )


_UTC = "2026-09-08T00:00:00.000000+00:00"

VALUE_TYPES = [
    ("ExecutionExpectation", pt.ExecutionExpectation),
    ("JournalEvent", pt.JournalEvent),
    ("ProtocolFinding", pt.ProtocolFinding),
    ("JournalObservation", pt.JournalObservation),
    ("XfailObservation", pt.XfailObservation),
    ("PhaseObservation", pt.PhaseObservation),
    ("TestObservation", pt.TestObservation),
    ("ExecutionObservation", pt.ExecutionObservation),
    ("PytestObservation", pt.PytestObservation),
]


@pytest.mark.parametrize(("name", "kind"), VALUE_TYPES, ids=[name for name, _ in VALUE_TYPES])
def test_value_types_are_frozen_with_normative_fields(name: str, kind: type) -> None:
    """Cada tipo de valor es frozen y conserva el orden normativo de campos."""
    expected_fields = {
        "ExecutionExpectation": (
            "execution_id",
            "role",
            "input_sha256",
            "context_sha256",
            "recipe_sha256",
        ),
        "JournalEvent": (
            "seq",
            "execution_id",
            "origin",
            "local_seq",
            "kind",
            "payload",
            "offset",
            "end_offset",
        ),
        "ProtocolFinding": ("code", "execution_id", "nodeid", "phase", "offset"),
        "JournalObservation": (
            "run_id",
            "executions",
            "events",
            "findings",
            "consumed_bytes",
            "tail_sha256",
            "max_bytes",
        ),
        "XfailObservation": ("run", "strict", "raises_present"),
        "PhaseObservation": (
            "nodeid",
            "phase",
            "outcome",
            "exception_present",
            "exception_type",
            "wasxfail",
            "xfail",
            "disposition",
        ),
        "TestObservation": (
            "nodeid",
            "start_seq",
            "phases",
            "terminal",
            "pass_eligible",
            "call_disposition",
        ),
        "ExecutionObservation": (
            "execution_id",
            "role",
            "items",
            "selected",
            "deselected_property",
            "tests",
            "exit_code",
            "termination",
            "protocol_complete",
            "findings",
        ),
        "PytestObservation": (
            "executions",
            "identities",
            "preflight_identities",
            "property_findings",
            "findings",
            "provenance",
        ),
    }[name]

    assert getattr(pt, name) is kind
    assert kind.__dataclass_params__.frozen is True
    assert tuple(field.name for field in dataclass_fields(kind)) == expected_fields


def test_frozen_is_behavioral_on_a_real_value() -> None:
    """El frozen no es nominal: asignar sobre una instancia real falla."""
    expectation = pt.ExecutionExpectation("collection-1", "collection", D64, D64, D64)

    with pytest.raises(FrozenInstanceError):
        expectation.role = "producer"


def test_observation_error_is_plain_exception_with_code_and_field() -> None:
    """ObservationError es excepción normal con code/field, no frozen."""
    error = pt.ObservationError("invalid_reference", "max_bytes")

    assert isinstance(error, Exception)
    assert (error.code, error.field) == ("invalid_reference", "max_bytes")
    with pytest.raises(pt.ObservationError) as raised:
        raise error
    assert raised.value.code == "invalid_reference"


def test_event_catalog_is_the_closed_table_of_the_contract() -> None:
    """Los 21 códigos 0..20 mapean exactos a origen/kind/clase, sin alias."""
    expected = {
        0: ("supervisor", "node_declaration", pp.NodeDeclaration),
        1: ("supervisor", "execution_start", pp.ExecutionStart),
        2: ("supervisor", "channel_end", pp.ChannelEnd),
        3: ("supervisor", "execution_end", pp.ExecutionEnd),
        4: ("pytest", "session_start", pp.SessionStart),
        5: ("pytest", "plugin", pp.PluginClaim),
        6: ("pytest", "plugins_end", pp.PluginsEnd),
        7: ("pytest", "options", pp.OptionsClaim),
        8: ("pytest", "item", pp.CollectedItem),
        9: ("pytest", "collect_report", pp.CollectionReport),
        10: ("pytest", "deselected", pp.DeselectedItem),
        11: ("pytest", "selected", pp.SelectedItem),
        12: ("pytest", "collection_end", pp.CollectionEnd),
        13: ("pytest", "test_start", pp.TestStart),
        14: ("pytest", "phase_make", pp.PhaseMake),
        15: ("pytest", "phase_log", pp.PhaseLog),
        16: ("pytest", "test_end", pp.TestEnd),
        17: ("pytest", "internal_error", pp.InternalError),
        18: ("pytest", "interrupted", pp.Interrupted),
        19: ("pytest", "session_end", pp.SessionEnd),
        20: ("pytest", "session_end_error", pp.SessionEndError),
    }
    catalog = {code: (origin, kind, cls) for code, origin, kind, cls in ps.EVENT_CATALOG}
    assert catalog == expected
    assert sorted(catalog) == list(range(21))


def test_wire_fields_arity_per_class() -> None:
    """La aridad del vector payload es contrato: ExecutionStart viaja con 5."""
    assert len(pp.WIRE_FIELDS[pp.ExecutionStart]) == 5
    assert tuple(pp.WIRE_FIELDS[pp.PhaseMake]) == (
        "nodeid",
        "phase",
        "outcome",
        "exception_present",
        "exception_type",
        "wasxfail",
        "xfail",
    )
    for kind, names in pp.WIRE_FIELDS.items():
        assert len(names) <= len(dataclass_fields(kind))
        assert kind in {cls for _c, _o, _k, cls in ps.EVENT_CATALOG}


def test_canonical_header_matches_the_literal_of_the_contract() -> None:
    """La cabecera canónica reconstruible es byte-igual al literal aprobado."""
    assert ps.canonical_header(RUN_ID, _executions()) == HEADER_LITERAL.encode("utf-8")


def test_decode_preserves_offsets_tail_and_canonical_framing() -> None:
    """Journal válido: offsets semiabiertos por línea con LF, tail None."""
    data = _minimal_journal()
    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.consumed_bytes == len(data)
    assert observation.tail_sha256 is None
    assert observation.findings == ()
    assert observation.max_bytes == len(data)
    assert [event.seq for event in observation.events] == [1, 2, 3, 4]
    boundaries = []
    position = len(HEADER_LITERAL)
    for line in data[position:].splitlines(keepends=True):
        boundaries.append((position, position + len(line)))
        position += len(line)
    assert [(event.offset, event.end_offset) for event in observation.events] == boundaries
    first = observation.events[0]
    assert (first.origin, first.kind) == ("supervisor", "execution_start")
    assert first.payload.role == "collection"
    assert first.payload.argv == ("python", "-m", "pytest")
    assert first.payload.input_sha256 == D64
    assert observation.events[3].payload.nodeid == "t"


def test_decode_header_only_eof_invents_no_execution() -> None:
    """EOF justo tras la cabecera: se consume y no fabrica eventos."""
    data = _wire_header()
    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert observation.findings == ()
    assert observation.consumed_bytes == len(data)
    assert observation.tail_sha256 is None


def test_decode_empty_data_returns_empty_observation() -> None:
    """Data vacío: sin eventos ni findings, consumido 0, cola nula."""
    observation = decode_pytest_journal(**_decode_kwargs(b""))

    assert observation.events == ()
    assert observation.findings == ()
    assert observation.consumed_bytes == 0
    assert observation.tail_sha256 is None


@pytest.mark.parametrize(
    ("data", "code"),
    [
        (_wire_header()[:-1], "truncated_line"),
        (b'{"record_type":"wct-pytest-journal","schema_version":1', "truncated_line"),
        (b'{"record_type":"wct-pytest-journal\xff","schema_version":1}\n', "invalid_encoding"),
        (b'{"record_type":"wct-pytest-journal","schema_version":1}\n', "invalid_field"),
        (_wire_header(schema_version=True), "invalid_field"),
        (_wire_header(record_type="other"), "unknown_schema"),
        (
            b'{"record_type":"wct-pytest-journal","run_id":"zz","schema_version":1}\n',
            "invalid_field",
        ),
        (
            b'{"schema_version":1,"record_type":"wct-pytest-journal",'
            b'"record_type":"wct-pytest-journal"}\n',
            "invalid_json",
        ),
        (b'{"schema_version":1.5,"record_type":"wct-pytest-journal"}\n', "invalid_json"),
        (b'{"record_type":"wct-pytest-journal","schema_version":1,"x":1}\n', "unknown_field"),
        (_wire_header(schema_version=2), "unknown_schema"),
        (_wire_header(executions=[["collection-1", "collection", D64, D64, D64]]), "invalid_field"),
        (
            _wire_header(
                executions=[["x", "y", "z", D64, D64], ["producer-1", "producer", D64, D64, D64]]
            ),
            "invalid_field",
        ),
        (_wire_header(run_id=OTHER_RUN_ID), "foreign_reference"),
        (
            _wire_header(
                executions=[
                    ["producer-1", "producer", D64, D64, D64],
                    ["collection-1", "collection", D64, D64, D64],
                ]
            ),
            "foreign_reference",
        ),
        (
            _wire_header(
                executions=[
                    ["collection-1", "collection", "b" * 64, D64, D64],
                    ["producer-1", "producer", D64, D64, D64],
                ]
            ),
            "foreign_reference",
        ),
    ],
)
def test_header_defects_stop_with_finding_at_zero(data: bytes, code: str | None) -> None:
    """Defecto de cabecera: sin eventos, consumido 0, finding en offset 0."""
    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert observation.consumed_bytes == 0
    assert observation.tail_sha256 == hashlib.sha256(data).hexdigest()
    if code is None:
        assert observation.findings == ()
    else:
        assert len(observation.findings) == 1
        finding = observation.findings[0]
        assert (finding.code, finding.offset) == (code, 0)
        assert finding.execution_id is None


def test_noncanonical_header_is_rejected() -> None:
    """JSON válido con espaciado no canónico: noncanonical_json."""
    data = b'{"schema_version": 1, "record_type": "wct-pytest-journal"}\n'

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.findings[0].code == "noncanonical_json"
    assert observation.findings[0].offset == 0


def test_deep_nesting_and_duplicate_nested_keys_are_invalid_json() -> None:
    """Profundidad >8 y claves duplicadas anidadas caen en invalid_json."""
    deep = {
        "schema_version": 1,
        "record_type": "wct-pytest-journal",
        "run_id": RUN_ID,
        "executions": [[[[[[[[["x"]]]]]]]]],
    }
    nested_dup = b'{"schema_version":1,"record_type":{"a":1,"a":2}}\n'

    for data in (_dump(deep) + b"\n", nested_dup):
        observation = decode_pytest_journal(**_decode_kwargs(data))
        assert observation.findings[0].code == "invalid_json"
        assert observation.findings[0].offset == 0


def test_line_defect_preserves_prefix_with_exact_offset_and_tail() -> None:
    """Defecto en línea 5: se conservan las cuatro líneas previas con offsets."""
    good = _minimal_journal()
    broken = good + _dump([5, 0, 3, 8, [0, False]])[:-1] + b"5\n"
    prefix_len = len(good)

    observation = decode_pytest_journal(**_decode_kwargs(broken))

    assert len(observation.events) == 4
    assert observation.consumed_bytes == prefix_len
    assert observation.tail_sha256 == hashlib.sha256(broken[prefix_len:]).hexdigest()
    finding = observation.findings[0]
    assert finding.code == "invalid_json"
    assert finding.offset == prefix_len
    assert finding.execution_id is None


def test_control_characters_inside_strings_are_invalid_encoding() -> None:
    """C0/DEL dentro de valores string es invalid_encoding tras parsear."""
    data = (
        b'{"executions":[["collection-1","collection","'
        + D64.encode()
        + b'","'
        + D64.encode()
        + b'","'
        + D64.encode()
        + b'"],["producer-1","producer","'
        + D64.encode()
        + b'","'
        + D64.encode()
        + b'","'
        + D64.encode()
        + b'"]],"record_type":"wct-pytest-journal","run_id":"'
        + RUN_ID.encode()
        + b'","schema_version":1}\n'
    ).replace(b"wct-pytest-journal", b"wct-pytest-jo\\u0007urnal")

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.findings[0].code == "invalid_encoding"
    assert observation.findings[0].offset == 0


@pytest.mark.parametrize(
    ("line", "code"),
    [
        (_event(5, 0, 3, 99, []), "unknown_event"),
        (_event(5, 0, 3, 8, [0, False, True]), "invalid_field"),
        (_event(5, 0, 3, 8, [0]), "invalid_field"),
        (_event(True, 0, 3, 8, [0, False]), "invalid_field"),
        (_event(5, 0, 3, True, [0, False]), "unknown_event"),
        (_event(5, 0, 3, 8, [0, 1]), "invalid_field"),
        (_event(5, 2, 3, 8, [0, False]), "foreign_reference"),
        (_event(5, 0, 3, 8, [7, False]), "foreign_reference"),
        (_event(6, 0, 3, 8, [0, False]), "sequence_error"),
        (_event(4, 0, 3, 4, ["9", "1", "o", D64]), "sequence_error"),
        (_event(5, 0, 5, 7, [D64, True]), "sequence_error"),
        (_event(5, 0, None, 7, [D64, True]), "sequence_error"),
        (_event(5, 0, 3, 1, [["python"], "/r", 0, 1, _UTC]), "sequence_error"),
        (_event(5, 0, 3, 14, [0, 3, 0, False, None, False, None]), "invalid_field"),
        (_event(5, 0, 3, 14, [0, 0, 5, False, None, False, None]), "invalid_field"),
        (_event(5, 0, 3, 14, [0, 0, 0, False, "", False, None]), "invalid_field"),
        (_event(5, 0, 3, 14, [0, 0, 0, True, None, False, None]), "invalid_field"),
        (_event(5, 0, 3, 14, [0, 0, 0, False, None, False, [True, False]]), "invalid_field"),
        (_event(5, 0, 3, 2, [True, 0, "no-hash"]), "invalid_field"),
        (_event(5, 0, 3, 2, [True, 0, None, "weird"]), "invalid_field"),
        (_event(5, 0, 3, 6, [True]), "invalid_field"),
        (_event(5, 0, 3, 3, [300, "exited", None, 0, D64, 1, _UTC, False]), "invalid_field"),
        (_event(5, 0, 3, 3, [0, "unobserved", None, 0, D64, 1, _UTC, False]), "invalid_field"),
        (_event(5, 0, 3, 8, [0, False, None]), "invalid_field"),
        (_dump({"seq": 5}) + b"\n", "invalid_field"),
        (_dump([5, 0, 3, 8, [0, False]]) + b" \n", "noncanonical_json"),
    ],
)
def test_line_defects_are_classified_by_precedence(line: bytes, code: str) -> None:
    """Cada defecto de línea produce su código sin incorporar la línea."""
    data = _minimal_journal() + line

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert len(observation.events) == 4
    assert len(observation.findings) == 1
    assert observation.findings[0].code == code
    assert observation.findings[0].offset == len(_minimal_journal())


def test_float_in_payload_is_invalid_json() -> None:
    """Un float en el wire se rechaza a nivel JSON, antes del payload."""
    data = _minimal_journal() + b"[5,0,3,6,[0.5]]\n"

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.findings[0].code == "invalid_json"
    assert len(observation.events) == 4


def test_declaration_table_rules() -> None:
    """Índices contiguos desde 0 y strings únicos; repetir es invalid_field."""
    base = _wire_header() + _event(1, 0, None, 1, [["python"], "/r", 0, 1, _UTC])
    cases = [
        (base + _event(2, 0, None, 0, [0, "t"]) + _event(3, 0, None, 0, [0, "u"]), 2),
        (base + _event(2, 0, None, 0, [0, "t"]) + _event(3, 0, None, 0, [1, "t"]), 2),
        (base + _event(2, 0, None, 0, [4, "t"]), 1),
    ]

    for data, accepted in cases:
        observation = decode_pytest_journal(**_decode_kwargs(data))
        assert len(observation.events) == accepted
        assert observation.findings[0].code == "invalid_field"

    ok = decode_pytest_journal(
        **_decode_kwargs(base + _event(2, 0, None, 0, [0, "t"]) + _event(3, 0, 1, 13, [0]))
    )
    assert ok.events[-1].payload.nodeid == "t"


def test_local_seq_out_of_range_is_invalid_field() -> None:
    """§4: local_seq bool, 0 o fuera de rango es invalid_field, no sequence_error."""
    for local in (True, 0, 2**63):
        data = _wire_header() + _event(1, 0, local, 4, ["9", "1", "o", D64])

        observation = decode_pytest_journal(**_decode_kwargs(data))

        assert observation.findings[0].code == "invalid_field", local


def reconcile_like(observation: object, *, expected: tuple[object, ...]) -> object:
    """Reconcilia con los argumentos canónicos de identidades del test."""
    return reconcile_pytest(observation, expected=expected, property_ids=())


def _header_bytes(value: object) -> bytes:
    """Serializa un objeto arbitrario como primera línea del journal."""
    return _dump(value) + b"\n"


def test_header_structure_subbranches_are_invalid_field() -> None:
    """§4: cabecera no-objeto, executions mal formados y tipos no string."""
    cases = [
        (_header_bytes([1, 2]), "invalid_field"),
        (
            _header_bytes(
                {
                    "schema_version": 1,
                    "record_type": "wct-pytest-journal",
                    "run_id": RUN_ID,
                    "executions": [["collection-1", "collection", D64, D64, D64], "x"],
                }
            ),
            "invalid_field",
        ),
        (
            _header_bytes(
                {
                    "schema_version": 1,
                    "record_type": "wct-pytest-journal",
                    "run_id": RUN_ID,
                    "executions": [
                        ["collection-1", 2, D64, D64, D64],
                        ["producer-1", "producer", D64, D64, D64],
                    ],
                }
            ),
            "invalid_field",
        ),
        (
            _header_bytes(
                {
                    "schema_version": 1,
                    "record_type": 7,
                    "run_id": RUN_ID,
                    "executions": [],
                }
            ),
            "invalid_field",
        ),
        (
            _header_bytes(
                {
                    "schema_version": 1,
                    "record_type": "wct-pytest-journal",
                    "run_id": 7,
                    "executions": [],
                }
            ),
            "invalid_field",
        ),
    ]
    for data, code in cases:
        observation = decode_pytest_journal(**_decode_kwargs(data))
        assert observation.findings[0].code == code, data


def test_public_argument_type_and_value_errors() -> None:
    """§2: errores de tipo público son TypeError; de valor, ObservationError."""
    bad_role = (
        pt.ExecutionExpectation("collection-1", "producer", D64, D64, D64),
        pt.ExecutionExpectation("producer-1", "producer", D64, D64, D64),
    )
    bad_digest = (
        pt.ExecutionExpectation("collection-1", "collection", "z" * 64, D64, D64),
        pt.ExecutionExpectation("producer-1", "producer", D64, D64, D64),
    )
    with pytest.raises(TypeError):
        decode_pytest_journal(
            _minimal_journal(), run_id=7, executions=_executions(), max_bytes=4096
        )
    with pytest.raises(TypeError):
        decode_pytest_journal(
            _minimal_journal(), run_id=RUN_ID, executions=list(_executions()), max_bytes=4096
        )
    with pytest.raises(TypeError):
        decode_pytest_journal(
            _minimal_journal(), run_id=RUN_ID, executions=_executions()[:1], max_bytes=4096
        )
    with pytest.raises(pt.ObservationError) as role_error:
        decode_pytest_journal(
            _minimal_journal(), run_id=RUN_ID, executions=bad_role, max_bytes=4096
        )
    assert role_error.value.field == "executions[0].role"
    with pytest.raises(pt.ObservationError) as digest_error:
        decode_pytest_journal(
            _minimal_journal(), run_id=RUN_ID, executions=bad_digest, max_bytes=4096
        )
    assert digest_error.value.field == "executions[0].input_sha256"


def test_identity_arguments_type_and_value_errors() -> None:
    """§2: expected con no-string, C0 o duplicados lanza el error del contrato."""
    base = decode_pytest_journal(**_decode_kwargs(_minimal_journal()))
    with pytest.raises(TypeError):
        reconcile_like(base, expected=("t", 7))
    with pytest.raises(pt.ObservationError) as raised:
        reconcile_like(base, expected=("\x01t",))
    assert (raised.value.code, raised.value.field) == ("invalid_reference", "expected")
    with pytest.raises(pt.ObservationError) as duplicate:
        reconcile_like(base, expected=("t", "t"))
    assert (duplicate.value.code, duplicate.value.field) == ("invalid_reference", "expected")
    with pytest.raises(pt.ObservationError) as oversized:
        reconcile_like(base, expected=("t" * 4097,))
    assert (oversized.value.code, oversized.value.field) == ("invalid_reference", "expected")


def test_payload_validate_rejects_bad_nested_values() -> None:
    """§2/§3: utc inválido, cwd relativa y surrogate en nodeid son invalid_observation."""
    bad_utc = pp.ExecutionStart(
        "collection",
        ("python",),
        "/r",
        D64,
        D64,
        D64,
        0,
        1,
        "2026-02-30T00:00:00.000000+00:00",
    )
    bad_tz = pp.ExecutionStart(
        "collection",
        ("python",),
        "/r",
        D64,
        D64,
        D64,
        0,
        1,
        "2026-09-10T00:00:00.000000+05:00",
    )
    bad_cwd = pp.ExecutionStart("collection", ("python",), "relativa", D64, D64, D64, 0, 1, _UTC)
    bad_cwd_type = pp.ExecutionStart("collection", ("python",), 7, D64, D64, D64, 0, 1, _UTC)
    surrogate = pp.CollectedItem("t\ud800", False)
    for payload, field in (
        (bad_utc, "utc"),
        (bad_tz, "utc"),
        (bad_cwd, "cwd"),
        (bad_cwd_type, "cwd"),
        (surrogate, "nodeid"),
    ):
        with pytest.raises(pt.ObservationError) as raised:
            ps.validate_payload(payload)
        assert (raised.value.code, raised.value.field) == ("invalid_observation", field)


def test_payload_validate_unknown_class_and_phase_coherence() -> None:
    """§2: clase sin esquema pasa como dato; fases incoherentes se rechazan."""
    ps.validate_payload(object())

    incoherent = pp.PhaseMake(
        nodeid="t",
        phase="setup",
        outcome="passed",
        exception_present=True,
        exception_type=None,
        wasxfail=False,
        xfail=None,
    )
    with pytest.raises(pt.ObservationError) as raised:
        ps.validate_payload(incoherent)
    assert (raised.value.code, raised.value.field) == ("invalid_observation", "exception_type")


@pytest.mark.parametrize(
    ("argv", "cwd"),
    [
        pytest.param([], "/r", id="argv-vacio"),
        pytest.param("no-lista", "/r", id="argv-no-lista"),
        pytest.param(["python"], "relativa", id="cwd-relativa"),
        pytest.param(["python"], "/a/../b", id="cwd-con-dotdot"),
        pytest.param(["python"], 7, id="cwd-no-string"),
    ],
)
def test_wire_argv_and_cwd_reject_invalid_shapes(argv: object, cwd: object) -> None:
    """§3: argv no vacío lista de strings y cwd absoluta POSIX sin . o .."""
    data = _wire_header() + _event(1, 0, None, 1, [argv, cwd, 0, 1, _UTC])

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.findings[0].code == "invalid_field"


@pytest.mark.parametrize(
    "utc",
    [
        pytest.param("10-09-2026 00:00:00", id="sin-formato"),
        pytest.param("2026-02-30T00:00:00.000000+00:00", id="fecha-invalida"),
    ],
)
def test_wire_utc_rejects_invalid_marks(utc: str) -> None:
    """§3: utc exige formato exacto y fecha válida por stdlib, sin leer reloj."""
    data = _wire_header() + _event(1, 0, None, 1, [["python"], "/r", 0, 1, utc])

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.findings[0].code == "invalid_field"


# --- Regresivos R5 restaurados por C1-01 (límites reales, precedencia §4
# y topes de inventario). Verbatim del candidato R5; los tests nuevos de
# R6 se conservan sin cambios. ---


def test_empty_nodeid_declaration_only_serves_collection_report() -> None:
    """La declaración vacía (collector raíz) existe; item vacío sigue inválido."""
    base = _wire_header() + _event(1, 0, None, 1, [["python"], "/r", 0, 1, _UTC])
    declared = base + _event(2, 0, None, 0, [0, ""])
    report_ok = decode_pytest_journal(**_decode_kwargs(declared + _event(3, 0, 1, 9, [0, 0])))
    item_empty = decode_pytest_journal(**_decode_kwargs(declared + _event(3, 0, 1, 8, [0, False])))

    assert report_ok.findings == ()
    assert report_ok.events[-1].payload.nodeid == ""
    assert item_empty.findings[0].code == "invalid_field"


def test_execution_start_reconstruction_and_validation() -> None:
    """role/digests se reconstruyen de la cabecera; argv a tupla; cwd/utc."""
    bad_cwd = _wire_header() + _event(1, 0, None, 1, [["python"], "rel/path", 0, 1, _UTC])
    dot_cwd = _wire_header() + _event(1, 0, None, 1, [["python"], "/r/..", 0, 1, _UTC])
    empty_argv = _wire_header() + _event(1, 0, None, 1, [[], "/r", 0, 1, _UTC])
    bad_utc = _wire_header() + _event(
        1, 0, None, 1, [["python"], "/r", 0, 1, "2026-13-40T00:00:00.000000+00:00"]
    )
    good = decode_pytest_journal(**_decode_kwargs(_minimal_journal())).events[0].payload

    assert good.cwd == "/r"
    assert good.log_start == 0
    assert good.monotonic_ns == 1
    assert good.utc == _UTC
    for data in (bad_cwd, dot_cwd, empty_argv, bad_utc):
        assert decode_pytest_journal(**_decode_kwargs(data)).findings[0].code == "invalid_field"


def test_exception_and_xfail_coherence() -> None:
    """exception_present false exige None; xfail null o tres bools exactos."""
    base = (
        _wire_header()
        + _event(1, 0, None, 1, [["python"], "/r", 0, 1, _UTC])
        + _event(2, 0, None, 0, [0, "t"])
        + _event(3, 0, 1, 13, [0])
    )
    ok = decode_pytest_journal(
        **_decode_kwargs(base + _event(4, 0, 2, 14, [0, 0, 0, False, None, False, None]))
    )
    assert ok.events[-1].payload.exception_type is None
    assert ok.events[-1].payload.xfail is None

    present_without_type = decode_pytest_journal(
        **_decode_kwargs(base + _event(4, 0, 2, 14, [0, 0, 0, True, None, False, None]))
    )
    absent_with_type = decode_pytest_journal(
        **_decode_kwargs(base + _event(4, 0, 2, 14, [0, 0, 0, False, "ValueError", False, None]))
    )
    for broken in (present_without_type, absent_with_type):
        assert broken.findings[0].code == "invalid_field"

    with_xfail = decode_pytest_journal(
        **_decode_kwargs(
            base + _event(4, 0, 2, 14, [0, 1, 1, False, None, True, [True, False, True]])
        )
    )
    assert with_xfail.events[-1].payload.xfail == pt.XfailObservation(True, False, True)


def test_line_and_nodeid_byte_boundaries() -> None:
    """Línea de 64KiB exacta pasa; +1 es limit_exceeded; nodo 4096/+1."""
    pad = "x" * 4096
    declaration_4096 = _event(1, 0, None, 0, [0, pad])
    observation = decode_pytest_journal(**_decode_kwargs(_wire_header() + declaration_4096))
    assert observation.findings == ()
    assert observation.events[0].payload.nodeid == pad

    over = decode_pytest_journal(
        **_decode_kwargs(_wire_header() + _event(1, 0, None, 0, [0, pad + "x"]))
    )
    assert over.findings[0].code == "invalid_field"

    exact_line = _line_of_64kib()
    assert len(exact_line) == 65536
    exact = decode_pytest_journal(**_decode_kwargs(_wire_header() + declaration_4096 + exact_line))
    assert exact.findings == ()

    over_line = _line_of_64kib(extra=1)
    assert len(over_line) == 65537
    over = decode_pytest_journal(**_decode_kwargs(_wire_header() + declaration_4096 + over_line))
    assert over.findings[0].code == "limit_exceeded"
    assert over.consumed_bytes == len(_wire_header()) + len(declaration_4096)


def _line_of_64kib(*, extra: int = 0) -> bytes:
    """Línea de ejecución arrancada con longitud exacta de 65536+extra bytes.

    Cada string del wire respeta el tope de 4096 bytes: el grosor se reparte
    entre entradas de argv de 4096 y el cwd, no en un único string gigante.
    """

    def render(entries: list[str], cwd: str) -> bytes:
        return _event(2, 0, None, 1, [entries, cwd, 0, 1, _UTC])

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


def test_inventory_limits_isolated_with_reduced_constants(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bordes de inventario con constante interna reducida: exacto pasa, +1 no."""
    monkeypatch.setattr(pseq, "MAX_INVENTORY_ENTRIES", 1)
    declared = _wire_header() + _event(1, 0, None, 0, [0, "t"])
    item = _event(2, 0, 1, 8, [0, False])
    data = declared + item

    exact = decode_pytest_journal(**_decode_kwargs(data))
    assert [event.kind for event in exact.events] == ["node_declaration", "item"]

    over = decode_pytest_journal(**_decode_kwargs(data + _event(3, 0, 2, 8, [0, False])))
    assert len(over.events) == 2
    assert over.findings[0].code == "limit_exceeded"


def test_declaration_limit_isolated_with_reduced_constant(monkeypatch: pytest.MonkeyPatch) -> None:
    """El tope de declaraciones también se observa como limit_exceeded."""
    monkeypatch.setattr(pseq, "MAX_DECLARATIONS", 1)
    data = _wire_header() + _event(1, 0, None, 0, [0, "t"])

    assert decode_pytest_journal(**_decode_kwargs(data)).findings == ()
    over = decode_pytest_journal(**_decode_kwargs(data + _event(2, 0, None, 0, [1, "u"])))
    assert over.findings[0].code == "limit_exceeded"


def test_two_mebibyte_journal_decodes_at_absolute_limit() -> None:
    """Data literal de 2MiB relleno con plugins válidos: decodifica completo."""
    head = _wire_header()
    target = 2 * 1024 * 1024
    lines: list[bytes] = []
    used = len(head)
    seq = 0
    while True:
        seq += 1
        minimal = _event(seq, 0, seq, 5, [f"p{seq:06d}", "m", None, None, None, True])
        if used + len(minimal) > target - 4096:
            break
        lines.append(minimal)
        used += len(minimal)
    gap = target - used - len(minimal)
    assert 0 <= gap < 4096
    final = _event(seq, 0, seq, 5, [f"p{seq:06d}", "m" * (1 + gap), None, None, None, True])
    lines.append(final)
    data = head + b"".join(lines)

    assert len(data) == target
    observation = decode_pytest_journal(**_decode_kwargs(data, max_bytes=target))

    assert observation.consumed_bytes == target
    assert observation.tail_sha256 is None
    assert observation.findings == ()
    assert observation.events[-1].kind == "plugin"


def test_execution_start_field_order_matches_the_contract() -> None:
    """§3: role,argv,cwd,input_sha256,context_sha256,recipe_sha256,log_start,monotonic_ns,utc."""
    start = pp.ExecutionStart("collection", ("python",), "/r", D64, D64, D64, 0, 1, _UTC)

    assert [item.name for item in dataclass_fields(pp.ExecutionStart)] == [
        "role",
        "argv",
        "cwd",
        "input_sha256",
        "context_sha256",
        "recipe_sha256",
        "log_start",
        "monotonic_ns",
        "utc",
    ]
    assert (start.role, start.argv, start.cwd) == ("collection", ("python",), "/r")
    assert (start.input_sha256, start.log_start, start.utc) == (D64, 0, _UTC)


def test_deep_json_beyond_interpreter_limit_returns_invalid_json_prefix() -> None:
    """R03-04: 1200 arrays anidados no escapan como RecursionError (§4)."""
    deep_line = b"[" * 1200 + b"0" + b"]" * 1200 + b"\n"
    data = _wire_header() + deep_line

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert observation.consumed_bytes == len(_wire_header())
    assert (observation.findings[0].code, observation.findings[0].offset) == (
        "invalid_json",
        len(_wire_header()),
    )
    assert observation.tail_sha256 == hashlib.sha256(deep_line).hexdigest()


@pytest.mark.parametrize(
    ("suffix", "code"),
    [
        pytest.param(b"[" + b" " * 65536, "limit_exceeded", id="oversized"),
        pytest.param(b"\xff", "invalid_encoding", id="bad-utf8"),
        pytest.param(b"[29,1,15,19,[0,0]]", "truncated_line", id="whole-json"),
        pytest.param(b"[brok", "truncated_line", id="broken-json"),
    ],
)
def test_no_final_lf_yields_the_first_normative_cause(suffix: bytes, code: str) -> None:
    """R03-09: §4 ordena límite→UTF-8→LF→JSON; el LF ausente no tapa la causa."""
    data = _wire_header() + suffix

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert (observation.findings[0].code, observation.findings[0].offset) == (
        code,
        len(_wire_header()),
    )


def test_oversized_header_is_limit_exceeded() -> None:
    """§3: la cabecera también consume el tope de 64KiB por línea."""
    data = b'{"schema_version":1' + b" " * 65520 + b"}\n"

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert observation.consumed_bytes == 0
    assert (observation.findings[0].code, observation.findings[0].offset) == ("limit_exceeded", 0)


def test_collected_nodeids_respect_the_contract_limit(request: pytest.FixtureRequest) -> None:
    """R1-03: ningún nodeid coleccionado excede 4096 bytes; el decoder lo impone."""
    oversized = _wire_header() + _event(1, 0, None, 0, [0, "x" * 4097])
    observation = decode_pytest_journal(**_decode_kwargs(oversized))

    assert observation.findings[0].code == "invalid_field"
    longest = max(len(item.nodeid.encode("utf-8")) for item in request.session.items)
    assert longest <= 4096


@pytest.mark.parametrize(
    ("header", "code"),
    [
        pytest.param(b"[" + b" " * 65536, "limit_exceeded", id="too-long"),
        pytest.param(b"\xff", "invalid_encoding", id="bad-utf8"),
    ],
)
def test_header_without_lf_keeps_the_line_precedence(header: bytes, code: str) -> None:
    """R1-05: límite y UTF-8 preceden al LF ausente también en la cabecera (§4)."""
    observation = decode_pytest_journal(**_decode_kwargs(header))

    assert observation.events == ()
    assert observation.consumed_bytes == 0
    assert (observation.findings[0].code, observation.findings[0].offset) == (code, 0)


def test_payload_value_defect_precedes_foreign_execution_index() -> None:
    """R1-06: §4 valida aridad/campos del payload antes del execution_index."""
    bad_start = _dump([1, 9, None, 1, [["python"], "/r", False, 1, _UTC]]) + b"\n"
    data = _wire_header() + bad_start

    observation = decode_pytest_journal(**_decode_kwargs(data))

    assert observation.events == ()
    assert (observation.findings[0].code, observation.findings[0].offset) == (
        "invalid_field",
        len(_wire_header()),
    )


def _inventory_journal(count: int) -> bytes:
    """Journal de colección con count pares item/selected (frontera real §2)."""
    body = [
        _event(1, 0, None, 1, [["python"], "/r", 0, 1, _UTC]),
        _event(2, 0, 1, 4, ["9", "1", "o", D64]),
        _event(3, 0, 2, 7, [D64, True]),
        _event(4, 0, None, 0, [0, "t"]),
    ]
    seq, local = 5, 3
    for _ in range(count):
        body.append(_event(seq, 0, local, 8, [0, False]))
        seq += 1
        local += 1
        body.append(_event(seq, 0, local, 11, [0]))
        seq += 1
        local += 1
    body.append(_event(seq, 0, local, 12, [count, 0]))
    return _wire_header() + b"".join(body)


@pytest.mark.parametrize(
    ("count", "code"),
    [
        pytest.param(10_000, None, id="exacto"),
        pytest.param(10_001, "limit_exceeded", id="excedido"),
    ],
)
def test_wire_inventory_cap_at_the_real_boundary(count: int, code: str | None) -> None:
    """R2-02: el tope de §2 se observa en el wire sin monkeypatch, 10 001 falla."""
    data = _inventory_journal(count)

    observation = decode_pytest_journal(**_decode_kwargs(data, max_bytes=len(data)))

    if code is None:
        assert observation.findings == ()
        assert len(observation.events) == 4 + 2 * count + 1
    else:
        assert observation.findings[0].code == "limit_exceeded"
        assert observation.consumed_bytes < len(data)
