"""Tipos de valor de SH-P03a/1: observaciones frozen y error público.

Solo datos: ninguna función de negocio, sin IO, sin reloj y sin pytest.
Los payloads del wire viven en ``pytest_payloads``; este módulo conserva el
resultado de la observación. ``bool`` nunca sustituye a ``int`` en estas
columnas y toda colección es tupla.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.wct.evidence.identities import IdentityComparison

PROVENANCE = "caller-supplied-unverified"


class ObservationError(Exception):
    """Error de valor público del API con código cerrado y campo nombrado.

    Attributes:
        code: uno de ``invalid_reference``, ``invalid_expectations``,
            ``invalid_observation`` o ``limit_exceeded``.
        field: el argumento público o su campo (por ejemplo
            ``executions[1].role``).
    """

    def __init__(self, code: str, field: str) -> None:
        super().__init__(f"{code}: {field}")
        self.code = code
        self.field = field


@dataclass(frozen=True)
class ExecutionExpectation:
    """Expectativa declarada por el caller para una ejecución del journal."""

    execution_id: str
    role: str
    input_sha256: str
    context_sha256: str
    recipe_sha256: str


@dataclass(frozen=True)
class JournalEvent:
    """Evento decodificado con su intervalo de bytes observado [offset, end).

    ``payload`` es una instancia exacta de una clase de ``pytest_payloads``;
    los offsets son de bytes, incluyen el LF y nunca viajan en el wire.
    """

    seq: int
    execution_id: str
    origin: str
    local_seq: int | None
    kind: str
    payload: object
    offset: int
    end_offset: int


@dataclass(frozen=True)
class ProtocolFinding:
    """Defecto puntual sin texto dinámico; offset del evento causante."""

    code: str
    execution_id: str | None
    nodeid: str | None
    phase: str | None
    offset: int | None


@dataclass(frozen=True)
class JournalObservation:
    """Prefijo decodificado del journal con sus defectos de protocolo."""

    run_id: str
    executions: tuple[ExecutionExpectation, ...]
    events: tuple[JournalEvent, ...]
    findings: tuple[ProtocolFinding, ...]
    consumed_bytes: int
    tail_sha256: str | None
    max_bytes: int


@dataclass(frozen=True)
class XfailObservation:
    """Metadatos limitados del marker xfail; nunca se reevalúa el marker."""

    run: bool
    strict: bool
    raises_present: bool


@dataclass(frozen=True)
class PhaseObservation:
    """Fase observada desde un phase_make válido, con disposición nativa."""

    nodeid: str
    phase: str
    outcome: str
    exception_present: bool
    exception_type: str | None
    wasxfail: bool
    xfail: XfailObservation | None
    disposition: str


@dataclass(frozen=True)
class TestObservation:
    """Instancia de test anclada al seq de su test_start.

    Dos instancias del mismo nodeid conservan start_seq distinto: ningún
    diccionario por nodeid oculta repeticiones.
    """

    nodeid: str
    start_seq: int
    phases: tuple[PhaseObservation, ...]
    terminal: bool
    pass_eligible: bool
    call_disposition: str


@dataclass(frozen=True)
class ExecutionObservation:
    """Observación estructural de una ejecución esperada del journal."""

    execution_id: str
    role: str
    items: tuple[str, ...]
    selected: tuple[str, ...]
    deselected_property: tuple[str, ...]
    tests: tuple[TestObservation, ...]
    exit_code: int | None
    termination: str
    protocol_complete: bool
    findings: tuple[ProtocolFinding, ...]


@dataclass(frozen=True)
class PytestObservation:
    """Reconciliación completa: ejecuciones, identidades y findings.

    ``provenance`` es siempre ``caller-supplied-unverified``: los datos
    aportados no autentican a su emisor ni elevan el protocolo a acreditado.
    """

    executions: tuple[ExecutionObservation, ...]
    identities: IdentityComparison
    preflight_identities: IdentityComparison
    property_findings: tuple[ProtocolFinding, ...]
    findings: tuple[ProtocolFinding, ...]
    provenance: str
