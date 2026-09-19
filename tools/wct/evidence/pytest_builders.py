"""Constructores de payloads desde el vector del wire (§3)."""

from collections.abc import Callable

from tools.wct.evidence.pytest_payload_classes import (
    OUTCOMES,
    PHASES,
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
from tools.wct.evidence.pytest_payloads import CHANNEL_DEFECTS, TERMINATIONS
from tools.wct.evidence.pytest_wire_composites import _argv, _cwd, _exception_type, _utc, _xfail
from tools.wct.evidence.pytest_wire_values import (
    _b,
    _enum,
    _h,
    _int_in,
    _member,
    _opt_h,
    _opt_s,
    _s,
    _u,
)


def _build_execution_start(f: dict[str, object]) -> ExecutionStart:
    """Cinco valores en el wire; role/digests se rellenan desde la cabecera."""
    return ExecutionStart(
        role="",
        argv=_argv(f["argv"]),
        cwd=_cwd(f["cwd"]),
        log_start=_u(f["log_start"]),
        monotonic_ns=_u(f["monotonic_ns"]),
        utc=_utc(f["utc"]),
        input_sha256="",
        context_sha256="",
        recipe_sha256="",
    )


def _build_execution_end(f: dict[str, object]) -> ExecutionEnd:
    """Exit -255..255 o None, terminación del §5 y señal 1..64 o None."""
    exit_code = f["exit_code"]
    signal = f["signal"]
    return ExecutionEnd(
        exit_code=None if exit_code is None else _int_in(exit_code, -255, 255),
        termination=_member(f["termination"], TERMINATIONS),
        signal=None if signal is None else _int_in(signal, 1, 64),
        log_end=_u(f["log_end"]),
        log_sha256=_h(f["log_sha256"]),
        monotonic_ns=_u(f["monotonic_ns"]),
        utc=_utc(f["utc"]),
        log_truncated=_b(f["log_truncated"]),
    )


def _build_channel_end(f: dict[str, object]) -> ChannelEnd:
    """eof/cola/hash con defecto del conjunto cerrado de canal."""
    defect = f["defect"]
    return ChannelEnd(
        eof=_b(f["eof"]),
        tail_bytes=_u(f["tail_bytes"]),
        tail_sha256=_opt_h(f["tail_sha256"]),
        defect=None if defect is None else _member(defect, CHANNEL_DEFECTS),
    )


def _build_phase_make(f: dict[str, object]) -> PhaseMake:
    """Enums lógicos de fase/resultado con excepción raw y xfail preservados."""
    return PhaseMake(
        nodeid=str(f["nodeid"]),
        phase=_enum(f["phase"], PHASES),
        outcome=_enum(f["outcome"], OUTCOMES),
        exception_present=_b(f["exception_present"]),
        exception_type=_exception_type(f["exception_present"], f["exception_type"]),
        wasxfail=_b(f["wasxfail"]),
        xfail=_xfail(f["xfail"]),
    )


_BUILDERS: dict[type, Callable[[dict[str, object]], object]] = {
    NodeDeclaration: lambda f: NodeDeclaration(index=_u(f["index"]), nodeid=_s(f["nodeid"])),
    ExecutionStart: _build_execution_start,
    ChannelEnd: _build_channel_end,
    ExecutionEnd: _build_execution_end,
    SessionStart: lambda f: SessionStart(
        pytest_version=_s(f["pytest_version"], min_len=1),
        pluggy_version=_s(f["pluggy_version"], min_len=1),
        observer_version=_s(f["observer_version"], min_len=1),
        runtime_profile_sha256=_h(f["runtime_profile_sha256"]),
    ),
    PluginClaim: lambda f: PluginClaim(
        name=_s(f["name"], min_len=1),
        module=_s(f["module"], min_len=1),
        distribution=_opt_s(f["distribution"]),
        version=_opt_s(f["version"]),
        source_sha256=_opt_h(f["source_sha256"]),
        qualified=_b(f["qualified"]),
    ),
    PluginsEnd: lambda f: PluginsEnd(count=_u(f["count"])),
    OptionsClaim: lambda f: OptionsClaim(
        effective_sha256=_h(f["effective_sha256"]), profile_match=_b(f["profile_match"])
    ),
    CollectedItem: lambda f: CollectedItem(nodeid=str(f["nodeid"]), property=_b(f["property"])),
    CollectionReport: lambda f: CollectionReport(
        nodeid=str(f["nodeid"]), outcome=_enum(f["outcome"], OUTCOMES)
    ),
    DeselectedItem: lambda f: DeselectedItem(nodeid=str(f["nodeid"]), property=_b(f["property"])),
    SelectedItem: lambda f: SelectedItem(nodeid=str(f["nodeid"])),
    CollectionEnd: lambda f: CollectionEnd(
        selected_count=_u(f["selected_count"]),
        deselected_count=_u(f["deselected_count"]),
    ),
    TestStart: lambda f: TestStart(nodeid=str(f["nodeid"])),
    PhaseMake: _build_phase_make,
    PhaseLog: lambda f: PhaseLog(
        nodeid=str(f["nodeid"]),
        phase=_enum(f["phase"], PHASES),
        outcome=_enum(f["outcome"], OUTCOMES),
        wasxfail=_b(f["wasxfail"]),
    ),
    TestEnd: lambda f: TestEnd(nodeid=str(f["nodeid"])),
    InternalError: lambda f: InternalError(exception_type=_s(f["exception_type"], min_len=1)),
    Interrupted: lambda f: Interrupted(exception_type=_s(f["exception_type"], min_len=1)),
    SessionEnd: lambda f: SessionEnd(
        argument_exit=_int_in(f["argument_exit"], 0, 255),
        observed_exit=_int_in(f["observed_exit"], 0, 255),
    ),
    SessionEndError: lambda f: SessionEndError(exception_type=_s(f["exception_type"], min_len=1)),
}
