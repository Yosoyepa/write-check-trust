"""Estado del barrido FSM de una ejecución y constantes de transición (§5)."""

from dataclasses import dataclass, field

from tools.wct.evidence.pytest_disposition import PhaseEvent
from tools.wct.evidence.pytest_inventory import ExecutionInventory
from tools.wct.evidence.pytest_payloads import ExecutionEnd, ExecutionStart, SessionEnd
from tools.wct.evidence.pytest_types import ProtocolFinding, TestObservation

_SESSION_SCOPED = frozenset(
    {
        "options",
        "item",
        "collect_report",
        "deselected",
        "selected",
        "collection_end",
        "test_start",
        "phase_make",
        "phase_log",
        "test_end",
        "plugin",
        "plugins_end",
        "session_end",
        "session_end_error",
        "internal_error",
        "interrupted",
    }
)

_TAILLESS_DEFECTS = frozenset({"io_error", "timeout", "cancelled", "limit_exceeded"})

_SESSION_ALTERNATIVES = ("session_end", "session_end_error")

_TEST_PHASE_KINDS = frozenset({"test_start", "phase_make", "phase_log", "test_end"})

_PRE_CHANNEL_CLOSERS = frozenset({"plugins_end", "session_end", "session_end_error"})
_COLLECTION_KINDS = frozenset(
    {"options", "item", "collect_report", "deselected", "selected", "collection_end"}
)


@dataclass
class _ScanState:
    """Estado mutable del barrido FSM de una ejecución esperada (§5)."""

    execution_id: str
    role: str
    findings: list[ProtocolFinding] = field(default_factory=list)
    items: list[tuple[str, bool, int]] = field(default_factory=list)
    selected: list[tuple[str, int]] = field(default_factory=list)
    deselected: list[tuple[str, bool, int]] = field(default_factory=list)
    tests: list[TestObservation] = field(default_factory=list)
    started: bool = False
    ended: bool = False
    session_started: bool = False
    session_closed: bool = False
    session_error: bool = False
    options_seen: bool = False
    collection_started: bool = False
    collection_closed: bool = False
    collection_end_offset: int | None = None
    plugins_closed: bool = False
    channel_seen: bool = False
    execution_end_seen: bool = False
    diagnostics: bool = False
    exit_code: int | None = None
    termination: str = "unobserved"
    plugin_claims: list[tuple[str, int]] = field(default_factory=list)
    start_payload: ExecutionStart | None = None
    start_offset: int | None = None
    end_payload: ExecutionEnd | None = None
    end_offset: int | None = None
    session_end_payload: SessionEnd | None = None
    active: tuple[str, int, int, list[PhaseEvent]] | None = None
    _collected: set[str] = field(default_factory=set)
    _test_starts: dict[int, int] = field(default_factory=dict)
    first_seq: int | None = None
    first_offset: int | None = None
    end_seq: int | None = None


def _finding_scan(
    code: str, state: _ScanState, nodeid: str | None, offset: int | None
) -> ProtocolFinding:
    """Finding semántico del barrido con ejecución y evento causante."""
    return ProtocolFinding(
        code=code, execution_id=state.execution_id, nodeid=nodeid, phase=None, offset=offset
    )


def inventory_of(state: _ScanState) -> ExecutionInventory:
    """Inventario en orden observado para las reglas del §7."""
    return ExecutionInventory(
        items=tuple(state.items),
        selected=tuple(state.selected),
        deselected=tuple(state.deselected),
        collection_end_offset=state.collection_end_offset,
    )
