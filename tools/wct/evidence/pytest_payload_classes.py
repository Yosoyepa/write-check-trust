"""Clases de payload frozen y enums del wire compacto (SH-P03a/1 §3).

Fuente de verdad de las clases; las fachadas y tablas derivadas
reexportan o importan desde aquí.
"""

from dataclasses import dataclass

from tools.wct.evidence.pytest_types import XfailObservation

ORIGIN_SUPERVISOR = "supervisor"

ORIGIN_PYTEST = "pytest"

ROLES = ("collection", "producer")

PHASES = ("setup", "call", "teardown")

OUTCOMES = ("passed", "failed", "skipped")

TERMINATIONS = (
    "exited",
    "signal",
    "launch_error",
    "timeout",
    "cancelled",
    "io_error",
    "limit_exceeded",
)

CHANNEL_DEFECTS = ("truncated_channel", "io_error", "timeout", "cancelled", "limit_exceeded")


@dataclass(frozen=True)
class NodeDeclaration:
    """Declaración del supervisor en la tabla global de nodeids."""

    index: int
    nodeid: str


@dataclass(frozen=True)
class ExecutionStart:
    """Arranque de proceso; role y digests llegan desde la cabecera."""

    role: str
    argv: tuple[str, ...]
    cwd: str
    input_sha256: str
    context_sha256: str
    recipe_sha256: str
    log_start: int
    monotonic_ns: int
    utc: str


@dataclass(frozen=True)
class ChannelEnd:
    """Cierre de canal con cola y defecto declarados por el emisor."""

    eof: bool
    tail_bytes: int
    tail_sha256: str | None
    defect: str | None


@dataclass(frozen=True)
class ExecutionEnd:
    """Cierre de proceso con exit, terminación y límites de log."""

    exit_code: int | None
    termination: str
    signal: int | None
    log_end: int
    log_sha256: str
    monotonic_ns: int
    utc: str
    log_truncated: bool


@dataclass(frozen=True)
class SessionStart:
    """Versions y perfil declaradas por el emisor, no verificadas."""

    pytest_version: str
    pluggy_version: str
    observer_version: str
    runtime_profile_sha256: str


@dataclass(frozen=True)
class PluginClaim:
    """Claim de plugin: se conserva tal cual, incluso ``qualified=False``."""

    name: str
    module: str
    distribution: str | None
    version: str | None
    source_sha256: str | None
    qualified: bool


@dataclass(frozen=True)
class PluginsEnd:
    """Cierre del inventario de plugins con su cardinalidad declarada."""

    count: int


@dataclass(frozen=True)
class OptionsClaim:
    """Claim de opciones efectivas; no certifica configuración real."""

    effective_sha256: str
    profile_match: bool


@dataclass(frozen=True)
class CollectedItem:
    """Item recolectado con su marca property declarada."""

    nodeid: str
    property: bool


@dataclass(frozen=True)
class CollectionReport:
    """Reporte de collector; el nodeid vacío es el collector raíz."""

    nodeid: str
    outcome: str


@dataclass(frozen=True)
class DeselectedItem:
    """Item deseleccionado; debe corresponder a property_ids revisados."""

    nodeid: str
    property: bool


@dataclass(frozen=True)
class SelectedItem:
    """Item seleccionado para ejecución."""

    nodeid: str


@dataclass(frozen=True)
class CollectionEnd:
    """Cierre de colección con conteos declarados."""

    selected_count: int
    deselected_count: int


@dataclass(frozen=True)
class TestStart:
    """Apertura de instancia de test; el seq la identifica."""

    nodeid: str


@dataclass(frozen=True)
class PhaseMake:
    """Reporte de fase con excepción raw y xfail conservados."""

    nodeid: str
    phase: str
    outcome: str
    exception_present: bool
    exception_type: str | None
    wasxfail: bool
    xfail: XfailObservation | None


@dataclass(frozen=True)
class PhaseLog:
    """Log de fase; la pareja make/log se coteja por instancia."""

    nodeid: str
    phase: str
    outcome: str
    wasxfail: bool


@dataclass(frozen=True)
class TestEnd:
    """Cierre de instancia de test."""

    nodeid: str


@dataclass(frozen=True)
class InternalError:
    """Diagnóstico de error interno; marca protocolo incompleto."""

    exception_type: str


@dataclass(frozen=True)
class Interrupted:
    """Diagnóstico de interrupción; marca protocolo incompleto."""

    exception_type: str


@dataclass(frozen=True)
class SessionEnd:
    """Exit del argumento y del observador; su divergencia es dato, no cambio."""

    argument_exit: int
    observed_exit: int


@dataclass(frozen=True)
class SessionEndError:
    """Cierre de sesión por error; alternativa de session_end."""

    exception_type: str
