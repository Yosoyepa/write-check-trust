"""Esquema completo de payloads aportados manualmente (§2)."""

from collections.abc import Callable

from tools.wct.evidence.pytest_payload_predicates import (
    _is_argv,
    _is_bool,
    _is_broad_text,
    _is_cwd,
    _is_digest,
    _is_text,
    _is_u,
    _is_utc,
    _is_xfail,
    _member_of,
    _optional,
    _within,
)
from tools.wct.evidence.pytest_payloads import (
    CHANNEL_DEFECTS,
    OUTCOMES,
    PHASES,
    ROLES,
    TERMINATIONS,
    ChannelEnd,
    CollectedItem,
    CollectionEnd,
    CollectionReport,
    DeselectedItem,
    ExecutionEnd,
    ExecutionStart,
    InternalError,
    Interrupted,
    NodeDeclaration,
    OptionsClaim,
    PhaseLog,
    PhaseMake,
    PluginClaim,
    PluginsEnd,
    SelectedItem,
    SessionEnd,
    SessionEndError,
    SessionStart,
    TestEnd,
    TestStart,
)
from tools.wct.evidence.pytest_types import ObservationError

_PAYLOAD_CHECKS: dict[type, tuple[tuple[str, Callable[[object], bool]], ...]] = {
    NodeDeclaration: (("index", _is_u), ("nodeid", _is_broad_text)),
    ExecutionStart: (
        ("role", _member_of(ROLES)),
        ("argv", _is_argv),
        ("cwd", _is_cwd),
        ("input_sha256", _is_digest),
        ("context_sha256", _is_digest),
        ("recipe_sha256", _is_digest),
        ("log_start", _is_u),
        ("monotonic_ns", _is_u),
        ("utc", _is_utc),
    ),
    ChannelEnd: (
        ("eof", _is_bool),
        ("tail_bytes", _is_u),
        ("tail_sha256", _optional(_is_digest)),
        ("defect", _optional(_member_of(CHANNEL_DEFECTS))),
    ),
    ExecutionEnd: (
        ("exit_code", _optional(_within(-255, 255))),
        ("termination", _member_of(TERMINATIONS)),
        ("signal", _optional(_within(1, 64))),
        ("log_end", _is_u),
        ("log_sha256", _is_digest),
        ("monotonic_ns", _is_u),
        ("utc", _is_utc),
        ("log_truncated", _is_bool),
    ),
    SessionStart: (
        ("pytest_version", _is_text),
        ("pluggy_version", _is_text),
        ("observer_version", _is_text),
        ("runtime_profile_sha256", _is_digest),
    ),
    PluginClaim: (
        ("name", _is_text),
        ("module", _is_text),
        ("distribution", _optional(_is_text)),
        ("version", _optional(_is_text)),
        ("source_sha256", _optional(_is_digest)),
        ("qualified", _is_bool),
    ),
    PluginsEnd: (("count", _is_u),),
    OptionsClaim: (("effective_sha256", _is_digest), ("profile_match", _is_bool)),
    CollectedItem: (("nodeid", _is_text), ("property", _is_bool)),
    CollectionReport: (("nodeid", _is_broad_text), ("outcome", _member_of(OUTCOMES))),
    DeselectedItem: (("nodeid", _is_text), ("property", _is_bool)),
    SelectedItem: (("nodeid", _is_text),),
    CollectionEnd: (("selected_count", _is_u), ("deselected_count", _is_u)),
    TestStart: (("nodeid", _is_text),),
    PhaseMake: (
        ("nodeid", _is_text),
        ("phase", _member_of(PHASES)),
        ("outcome", _member_of(OUTCOMES)),
        ("exception_present", _is_bool),
        ("exception_type", _optional(_is_text)),
        ("wasxfail", _is_bool),
        ("xfail", _is_xfail),
    ),
    PhaseLog: (
        ("nodeid", _is_text),
        ("phase", _member_of(PHASES)),
        ("outcome", _member_of(OUTCOMES)),
        ("wasxfail", _is_bool),
    ),
    TestEnd: (("nodeid", _is_text),),
    InternalError: (("exception_type", _is_text),),
    Interrupted: (("exception_type", _is_text),),
    SessionEnd: (("argument_exit", _within(0, 255)), ("observed_exit", _within(0, 255))),
    SessionEndError: (("exception_type", _is_text),),
}


def validate_payload(payload: object) -> None:
    """Esquema completo de un payload de observation manual (§2).

    Tipos exactos, enums, rangos y tuplas que el decoder garantiza por
    construcción; cualquier desvío es invalid_observation con el campo.
    """
    checks = _PAYLOAD_CHECKS.get(type(payload))
    if checks is None:
        return
    for name, check in checks:
        if not check(getattr(payload, name)):
            raise ObservationError("invalid_observation", name)
    if _exception_mismatch(payload):
        raise ObservationError("invalid_observation", "exception_type")


def _exception_mismatch(payload: object) -> bool:
    """En un phase_make, exception_type presente iff exception_present."""
    return type(payload) is PhaseMake and payload.exception_present != (
        payload.exception_type is not None
    )
