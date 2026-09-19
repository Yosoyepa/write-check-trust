"""Clases de payload frozen y enums del wire compacto (SH-P03a/1 §3).

Fachada: las clases viven en ``pytest_payload_classes`` y las tablas
derivadas en ``pytest_wire_fields``/``pytest_event_catalog``; esta
superficie se conserva para los consumidores del contrato.
"""

from tools.wct.evidence.pytest_event_catalog import EVENT_CATALOG
from tools.wct.evidence.pytest_payload_classes import (
    CHANNEL_DEFECTS,
    ORIGIN_PYTEST,
    ORIGIN_SUPERVISOR,
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
from tools.wct.evidence.pytest_wire_fields import WIRE_FIELDS

__all__ = [
    "CHANNEL_DEFECTS",
    "EVENT_CATALOG",
    "ORIGIN_PYTEST",
    "ORIGIN_SUPERVISOR",
    "OUTCOMES",
    "PHASES",
    "ROLES",
    "TERMINATIONS",
    "WIRE_FIELDS",
    "ChannelEnd",
    "CollectedItem",
    "CollectionEnd",
    "CollectionReport",
    "DeselectedItem",
    "ExecutionEnd",
    "ExecutionStart",
    "InternalError",
    "Interrupted",
    "NodeDeclaration",
    "OptionsClaim",
    "PhaseLog",
    "PhaseMake",
    "PluginClaim",
    "PluginsEnd",
    "SelectedItem",
    "SessionEnd",
    "SessionEndError",
    "SessionStart",
    "TestEnd",
    "TestStart",
]
