"""API pública de observación pytest (SH-P03a/1): decode y reconcile (§2).

La validación de argumentos vive en ``pytest_api_args``, la del objeto
observación en ``pytest_observation_validate``/``_events``/``_event``,
el barrido FSM en ``pytest_scan_*`` y ``pytest_termination``. Esta
fachada compone decode+reconcile y ordena los findings del §7.
"""

from tools.wct.evidence.identities import IdentityComparison
from tools.wct.evidence.pytest_api_args import (
    _identity_args,
    _validate_executions,
    _validate_max_bytes,
    _validate_run_id,
)
from tools.wct.evidence.pytest_inventory import (
    NON_BLOCKING_CODES,
    PROPERTY_FINDING_CODES,
    identity_comparisons,
    property_findings,
    selection_findings,
)
from tools.wct.evidence.pytest_observation_validate import _validate_observation
from tools.wct.evidence.pytest_scan_dispatch import feed_scan
from tools.wct.evidence.pytest_scan_state import _ScanState, inventory_of
from tools.wct.evidence.pytest_scan_totals import (
    _cross_execution_bounds,
    _execution_order,
    finish_scan,
)
from tools.wct.evidence.pytest_schema import decode_journal
from tools.wct.evidence.pytest_termination import _ADMISSIBLE_EXIT
from tools.wct.evidence.pytest_types import (
    PROVENANCE,
    ExecutionExpectation,
    ExecutionObservation,
    JournalObservation,
    ObservationError,
    ProtocolFinding,
    PytestObservation,
)


def decode_pytest_journal(
    data: bytes, *, run_id: str, executions: tuple[ExecutionExpectation, ...], max_bytes: int
) -> JournalObservation:
    """Decodifica el journal compacto y conserva prefijo, defectos y offsets.

    Args:
        data: bytes del journal, con cabecera y registros canónicos.
        run_id: lowerhex32 declarado por el caller.
        executions: exactamente collection-1 y producer-1, en orden.
        max_bytes: límite caller-declared en 1..2MiB; no acredita ledgers.

    Returns:
        El prefijo válido con eventos, findings, offsets y hash de cola.

    Raises:
        TypeError: si un argumento público no tiene el tipo exacto.
        ObservationError: si un valor público es inválido o data excede
            max_bytes antes de parsear.
    """
    if type(data) is not bytes:
        raise TypeError("data: deben ser bytes exactos")
    checked_data = data
    checked = (
        _validate_run_id(run_id),
        _validate_executions(executions),
        _validate_max_bytes(max_bytes),
    )
    if len(checked_data) > checked[2]:
        raise ObservationError("limit_exceeded", "data")
    return decode_journal(
        checked_data, run_id=checked[0], executions=checked[1], max_bytes=checked[2]
    )


def _sort_key(finding: ProtocolFinding, *, decoder: bool, rank: int) -> tuple[object, ...]:
    """Orden determinista del §7: decoder, ejecución, offset, código, identidad."""
    offset_key = (1, 0) if finding.offset is None else (0, finding.offset)
    nodeid_key = (0, "") if finding.nodeid is None else (1, finding.nodeid)
    phase_key = (0, "") if finding.phase is None else (1, finding.phase)
    return (0 if decoder else 1, rank, offset_key, finding.code, nodeid_key, phase_key)


def _dedupe(ordered: list[tuple[ProtocolFinding, bool, int]]) -> tuple[ProtocolFinding, ...]:
    """Elimina repetidos exactos conservando la primera aparición."""
    unique: list[ProtocolFinding] = []
    for finding, _flag, _rank in ordered:
        if not unique or unique[-1] != finding:
            unique.append(finding)
    return tuple(unique)


def _merge(
    decoder: tuple[ProtocolFinding, ...], groups: list[list[ProtocolFinding]], ranks: list[int]
) -> tuple[ProtocolFinding, ...]:
    """Unión ordenada y sin duplicados exactos de todos los findings."""
    entries = [(finding, True, 0) for finding in decoder]
    for group, rank in zip(groups, ranks, strict=True):
        entries.extend((finding, False, rank) for finding in group)
    ordered = sorted(entries, key=lambda item: _sort_key(item[0], decoder=item[1], rank=item[2]))
    return _dedupe(ordered)


def _session_phase_ok(state: _ScanState) -> bool:
    """Apertura y sesión activa cerradas sin error de sesión."""
    return (
        state.started and state.session_started and state.session_closed and not state.session_error
    )


def _closers_present(state: _ScanState) -> bool:
    """Apertura, sesión, canal y cierre de proceso presentes y sin diagnóstico."""
    return (
        _session_phase_ok(state)
        and state.channel_seen
        and state.execution_end_seen
        and not state.diagnostics
    )


def _structural_findings(state: _ScanState) -> bool:
    """Algún finding propio de la ejecución excede los no bloqueantes."""
    return any(finding.code not in NON_BLOCKING_CODES for finding in state.findings)


def _decoder_blocks(decoder: tuple[ProtocolFinding, ...], execution_id: str) -> bool:
    """Un finding de decoder afecta a esta ejecución o no está atribuido."""
    return any(finding.execution_id in (None, execution_id) for finding in decoder)


def scan_protocol_complete(state: _ScanState, decoder: tuple[ProtocolFinding, ...]) -> bool:
    """Cierres íntegros, sin hallazgos estructurales y exit admisible."""
    if not _closers_present(state):
        return False
    if _structural_findings(state):
        return False
    if _decoder_blocks(decoder, state.execution_id):
        return False
    return state.termination == "exited" and state.exit_code in _ADMISSIBLE_EXIT


def execution_view(
    state: _ScanState, decoder: tuple[ProtocolFinding, ...], rank: int
) -> ExecutionObservation:
    """ExecutionObservation con todos los findings de su ejecución."""
    return ExecutionObservation(
        execution_id=state.execution_id,
        role=state.role,
        items=tuple(nodeid for nodeid, _flag, _offset in state.items),
        selected=tuple(nodeid for nodeid, _offset in state.selected),
        deselected_property=tuple(nodeid for nodeid, _flag, _offset in state.deselected),
        tests=tuple(state.tests),
        exit_code=state.exit_code,
        termination=state.termination,
        protocol_complete=scan_protocol_complete(state, decoder),
        findings=_merge((), [state.findings], [rank]),
    )


def _reconcile_scans(checked: JournalObservation) -> list[_ScanState]:
    """Barrido FSM y cierre de cada ejecución esperada, en orden."""
    scans = [
        _ScanState(expectation=item, execution_id=item.execution_id, role=item.role)
        for item in checked.executions
    ]
    for scan in scans:
        for event in checked.events:
            if event.execution_id == scan.execution_id:
                feed_scan(scan, event)
        finish_scan(scan)
    return scans


def _append_inventory_findings(scans: list[_ScanState], property_tuple: tuple[str, ...]) -> None:
    """Hallazgos de selección y property del §7 por ejecución."""
    for scan in scans:
        scan.findings.extend(selection_findings(inventory_of(scan), scan.execution_id))
        scan.findings.extend(
            property_findings(inventory_of(scan), scan.execution_id, property_tuple)
        )


def _identity_outcome(
    scans: list[_ScanState], expected_tuple: tuple[str, ...]
) -> tuple[IdentityComparison, IdentityComparison]:
    """Preflight y final de P01 a partir de la selección y terminales observadas."""
    return identity_comparisons(
        expected_tuple,
        tuple(nodeid for nodeid, _offset in scans[0].selected),
        tuple(nodeid for nodeid, _offset in scans[1].selected),
        tuple(test.nodeid for test in scans[1].tests if test.terminal),
    )


def _property_findings_of(scans: list[_ScanState]) -> list[ProtocolFinding]:
    """Los findings de property de todas las ejecuciones, sin ordenar."""
    return [
        finding
        for scan in scans
        for finding in scan.findings
        if finding.code in PROPERTY_FINDING_CODES
    ]


def reconcile_pytest(
    observation: JournalObservation, *, expected: tuple[str, ...], property_ids: tuple[str, ...]
) -> PytestObservation:
    """Reconcilia el prefijo decodificado con expectativas explícitas.

    Args:
        observation: salida de ``decode_pytest_journal`` o construida a mano;
            se valida su esquema antes de usarla.
        expected: obligaciones declaradas de tests normales.
        property_ids: identidades property que deben aparecer deseleccionadas.

    Returns:
        Ejecuciones observadas, identidades P01, findings ordenados y
        ``provenance`` igual a ``caller-supplied-unverified``.

    Raises:
        TypeError: si ``observation`` no es JournalObservation o los
            inventarios del caller no son tuplas de strings.
        ObservationError: si la observación manual es incoherente o los
            valores públicos del caller son inválidos.
    """
    expected_tuple = _identity_args(expected, "expected")
    property_tuple = _identity_args(property_ids, "property_ids")
    if set(expected_tuple) & set(property_tuple):
        raise ObservationError("invalid_reference", "property_ids")
    checked = _validate_observation(observation)
    scans = _reconcile_scans(checked)
    ranks = {scan.execution_id: rank for rank, scan in enumerate(scans)}
    _cross_execution_bounds(scans)
    _execution_order(scans)
    _append_inventory_findings(scans, property_tuple)
    preflight, final = _identity_outcome(scans, expected_tuple)
    executions = tuple(
        execution_view(scan, checked.findings, ranks[scan.execution_id]) for scan in scans
    )
    all_findings = [scan.findings for scan in scans]
    return PytestObservation(
        executions=executions,
        identities=final,
        preflight_identities=preflight,
        property_findings=_merge((), [_property_findings_of(scans)], [0]),
        findings=_merge(
            checked.findings, all_findings, [ranks[scan.execution_id] for scan in scans]
        ),
        provenance=PROVENANCE,
    )
