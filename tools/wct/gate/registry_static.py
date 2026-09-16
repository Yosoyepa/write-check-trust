"""Entradas estáticas del registro: analizadores puros y configuración."""

from __future__ import annotations

from tools.wct.gate.capabilities import declares
from tools.wct.gate.checks import (
    dead_code_command,
    gate_accept,
    gate_archmetrics,
    gate_cognitive,
    gate_debt,
    gate_dry,
    gate_dry_tpl,
    gate_introvert,
    gate_lcom,
    gate_meta_integrity,
    gate_rules_drift,
    gate_size,
    gate_suppressions,
)
from tools.wct.gate.runner_audit import gate_audit
from tools.wct.gate.runner_support import Gate, dynamic, external
from tools.wct.gate.semgrep import gate_sast_semgrep

REGISTRY: dict[str, Gate] = {
    "G-META-1": gate_meta_integrity,
    "G-RULES-DRIFT": gate_rules_drift,
    "G-SUPPRESS": declares(gate_suppressions, scope=("src", "tests")),
    "G-DEBT": declares(gate_debt, scope=("src", "tests")),
    "G-LINT": external(
        "G-LINT",
        ["ruff", "check", "--config", "governance/lint/ruff.toml", "."],
        scope=(".",),
    ),
    "G-FMT": external(
        "G-FMT",
        ["ruff", "format", "--config", "governance/lint/ruff.toml", "--check", "."],
        scope=(".",),
    ),
    "G-TYPE": external("G-TYPE", ["mypy", "tools/wct", "src"], scope=("tools/wct", "src")),
    "G-TEST": external(
        "G-TEST",
        ["pytest", "-q", "tests/unit", "tests/integration", "-m", "not property"],
        scope=("tests/unit", "tests/integration"),
    ),
    "G-ARCH": external("G-ARCH", ["lint-imports"], scope=("src/example",)),
    "G-DEPS": external(
        "G-DEPS",
        [
            "deptry",
            "src",
            "tools",
            "--known-first-party",
            "example",
            "--known-first-party",
            "tools",
        ],
        scope=("src", "tools"),
    ),
    "G-DEAD": declares(
        dynamic("G-DEAD", "vulture", dead_code_command, "dead_code.vulture_min_confidence"),
        scope=("src", "tools/wct"),
    ),
    "G-SAST-BANDIT": external("G-SAST-BANDIT", ["bandit", "-q", "-r", "src"], scope=("src",)),
    "G-SAST-SEMGREP": declares(gate_sast_semgrep, tools=("semgrep",), scope=(".",)),
    "G-AUDIT": declares(gate_audit, tools=("uv", "pip-audit")),
    "G-ARCHMETRICS": declares(gate_archmetrics, scope=("src/example",)),
    "G-DRY": declares(gate_dry, scope=("src",)),
    "G-DRY-TPL": declares(gate_dry_tpl, scope=("src", "tools")),
    "G-INTROVERT": declares(gate_introvert, scope=("tests",)),
    "G-ACCEPT": declares(gate_accept, scope=("features",)),
    "G-SIZE": declares(gate_size, scope=("src", "tools")),
    "G-COGNITIVE": declares(gate_cognitive, scope=("src",)),
    "G-LCOM": declares(gate_lcom, scope=("src", "tools")),
}
