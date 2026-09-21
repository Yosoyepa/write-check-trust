"""Esquema completo de una observación antes de usar datos manuales (§2)."""

from tools.wct.evidence.pytest_api_args import _DIGEST_RE, _RUN_ID_RE, _validate_expectation
from tools.wct.evidence.pytest_limits import (
    DECODER_FINDING_CODES,
    MAX_JOURNAL_BYTES,
    MIN_JOURNAL_BYTES,
)
from tools.wct.evidence.pytest_observation_events import _validate_events
from tools.wct.evidence.pytest_types import (
    ExecutionExpectation,
    JournalObservation,
    ObservationError,
    ProtocolFinding,
)

_EXECUTION_COUNT = 2


def _validate_observation(observation: object) -> JournalObservation:
    """Esquema completo de una observation antes de usar datos manuales."""
    if type(observation) is not JournalObservation:
        raise TypeError("observation: debe ser un JournalObservation")
    _validate_identity_fields(observation)
    if type(observation.events) is not tuple:
        raise ObservationError("invalid_observation", "events")
    if type(observation.findings) is not tuple or len(observation.findings) > 1:
        raise ObservationError("invalid_observation", "findings")
    for finding in observation.findings:
        _validate_decoder_finding(finding, observation)
    _validate_tail(observation)
    _validate_events(observation)
    return observation


def _validate_tail(observation: JournalObservation) -> None:
    """El tail_sha256 opcional es un string lowerhex64."""
    if observation.tail_sha256 is not None and (
        type(observation.tail_sha256) is not str
        or _DIGEST_RE.fullmatch(observation.tail_sha256) is None
    ):
        raise ObservationError("invalid_observation", "tail_sha256")


def _validate_identity_fields(observation: JournalObservation) -> None:
    """Identidad, expectativas, límites y consumo del prefijo declarado."""
    if type(observation.run_id) is not str or _RUN_ID_RE.fullmatch(observation.run_id) is None:
        raise ObservationError("invalid_observation", "run_id")
    if type(observation.executions) is not tuple or len(observation.executions) != _EXECUTION_COUNT:
        raise ObservationError("invalid_observation", "executions")
    _validate_execution_items(observation)
    _validate_byte_limits(observation)


def _validate_execution_items(observation: JournalObservation) -> None:
    """Cada expectativa es de la clase exacta y pasa el esquema del §2."""
    for position, item in enumerate(observation.executions):
        if type(item) is not ExecutionExpectation:
            raise ObservationError("invalid_observation", f"executions[{position}]")
        _validate_expectation(position, item, "invalid_observation")


def _validate_byte_limits(observation: JournalObservation) -> None:
    """max_bytes en el rango del contrato y consumo dentro de max_bytes."""
    if type(observation.max_bytes) is not int or not (
        MIN_JOURNAL_BYTES <= observation.max_bytes <= MAX_JOURNAL_BYTES
    ):
        raise ObservationError("invalid_observation", "max_bytes")
    if type(observation.consumed_bytes) is not int or not (
        0 <= observation.consumed_bytes <= observation.max_bytes
    ):
        raise ObservationError("invalid_observation", "consumed_bytes")


def _validate_decoder_finding(finding: object, observation: JournalObservation) -> None:
    """Máximo un finding de decoder, con código cerrado y campos exactos."""
    if type(finding) is not ProtocolFinding:
        raise ObservationError("invalid_observation", "findings")
    _validate_finding_fields(finding)
    _validate_finding_anchor(finding, observation)


def _validate_finding_fields(finding: ProtocolFinding) -> None:
    """Código cerrado y campos de texto opcionales bien tipados."""
    if type(finding.code) is not str or finding.code not in DECODER_FINDING_CODES:
        raise ObservationError("invalid_observation", "findings")
    for name in ("execution_id", "nodeid", "phase"):
        value = getattr(finding, name)
        if value is not None and type(value) is not str:
            raise ObservationError("invalid_observation", "findings")


def _validate_finding_anchor(finding: ProtocolFinding, observation: JournalObservation) -> None:
    """execution_id conocido y offset igual al consumo declarado."""
    if finding.execution_id is not None and finding.execution_id not in {
        item.execution_id for item in observation.executions
    }:
        raise ObservationError("invalid_observation", "findings")
    if type(finding.offset) is not int or finding.offset != observation.consumed_bytes:
        raise ObservationError("invalid_observation", "findings")
