"""Entradas derivadas del registro: alias y compuestos sobre el mapa base."""

from __future__ import annotations

from tools.wct.gate.checks import gate_archmetrics, gate_debt, gate_rules_drift
from tools.wct.gate.runner_support import Gate, alias, external


def derived(base: dict[str, Gate]) -> dict[str, Gate]:
    """Entradas derivadas: alias y compuestos sobre el mapa base."""
    return {
        "G-ARCH-CYCLE": alias("G-ARCH-CYCLE", gate_archmetrics),
        "G-CVE": alias("G-CVE", base["G-AUDIT"]),
        "G-HOOKS-WIRED": external("G-HOOKS-WIRED", ["wct", "doctor"], optional=False),
        "G-IMPORT-ORDER": alias("G-IMPORT-ORDER", base["G-LINT"]),
        "G-RULES-SYNC": alias("G-RULES-SYNC", gate_rules_drift),
        "G-SAST": alias("G-SAST", base["G-SAST-BANDIT"]),
        "G-TEST-FAST": alias("G-TEST-FAST", base["G-TEST"]),
        "G-TODO": alias("G-TODO", gate_debt),
    }
