"""Gates analizadores puros (fachada TEST-007)."""

from __future__ import annotations

from tools.wct.gate.checks_debt import (  # reexport fachada TEST-007
    COVERAGE_TOTAL_BASELINE,
    _result,
    coverage_diff_command,
    coverage_total_command,
    crap_command,
    dead_code_command,
    gate_debt,
    gate_meta_integrity,
    gate_rules_drift,
    gate_suppressions,
)
from tools.wct.gate.checks_quality import (  # reexport fachada TEST-007
    XENON_FLAGS,
    XENON_KEYS,
    cognitive_command,
    gate_cognitive,
    gate_dry_tpl,
    gate_lcom,
    gate_wire,
)
from tools.wct.gate.checks_scanners import (  # reexport fachada TEST-007
    gate_accept,
    gate_archmetrics,
    gate_dry,
    gate_introvert,
    gate_size,
)

__all__ = [
    "COVERAGE_TOTAL_BASELINE",
    "XENON_FLAGS",
    "XENON_KEYS",
    "_result",
    "cognitive_command",
    "coverage_diff_command",
    "coverage_total_command",
    "crap_command",
    "dead_code_command",
    "gate_accept",
    "gate_archmetrics",
    "gate_cognitive",
    "gate_debt",
    "gate_dry",
    "gate_dry_tpl",
    "gate_introvert",
    "gate_lcom",
    "gate_meta_integrity",
    "gate_rules_drift",
    "gate_size",
    "gate_suppressions",
    "gate_wire",
]
