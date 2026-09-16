"""Entradas de proceso externo y artefactos del registro."""

from __future__ import annotations

from tools.wct.gate.capabilities import declares
from tools.wct.gate.checks import (
    COVERAGE_TOTAL_BASELINE,
    cognitive_command,
    coverage_total_command,
    crap_command,
    gate_wire,
)
from tools.wct.gate.mutation import gate_mutation
from tools.wct.gate.runner_docstrings import gate_docstrings
from tools.wct.gate.runner_secrets import SECRET_PATHS, gate_secrets
from tools.wct.gate.runner_support import Gate, dynamic, external

REGISTRY: dict[str, Gate] = {
    "G-WIRE": declares(gate_wire, scope=("src/example/domain", "src/example/application")),
    "G-CRAP": declares(
        dynamic("G-CRAP", "crap4py", crap_command, "crap.changed_max", optional=True),
        scope=("src",),
    ),
    "G-CC": declares(
        dynamic("G-CC", "xenon", cognitive_command, "complexity.xenon_max_*", optional=True),
        scope=("src",),
    ),
    "G-COV-TOTAL": declares(
        dynamic("G-COV-TOTAL", "pytest", coverage_total_command, COVERAGE_TOTAL_BASELINE),
        scope=("src", "tools/wct"),
    ),
    "G-DOC": declares(gate_docstrings, tools=("interrogate",), scope=("src",)),
    "G-SECRET": declares(gate_secrets, tools=("detect-secrets",), scope=SECRET_PATHS),
    "G-PROP": external("G-PROP", ["pytest", "-q", "tests/property"], scope=("tests/property",)),
    "G-TEST-RANDOM": external(
        "G-TEST-RANDOM", ["pytest", "-q", "--randomly-seed=last"], optional=True, scope=("tests",)
    ),
    # --exit-code 1: sin esa bandera jscpd sale 0 aunque encuentre clones
    # (verificado empíricamente) y el gate sería vacío. CON la bandera es
    # tolerancia cero: cualquier clon a 70+ tokens falla (el "threshold" de
    # .jscpd.json solo afecta el reporte, no el exit — también verificado).
    "G-DRY-TOK": external(
        "G-DRY-TOK",
        ["jscpd", "src", "tools", "--exit-code", "1"],
        optional=True,
        scope=("src", "tools"),
    ),
    "G-SBOM": external(
        "G-SBOM", ["cyclonedx-py", "environment", "--output-file", "build/sbom.json"], optional=True
    ),
    "G-COMMIT-MSG": external(
        "G-COMMIT-MSG", ["cz", "check", "--commit-msg-file", ".git/COMMIT_EDITMSG"], optional=True
    ),
    "G-MUT": declares(gate_mutation, tools=("mutmut",), scope=("src/example",)),
    "G-ACCEPT-MUT": external("G-ACCEPT-MUT", ["wct", "accept", "mutate"], optional=True),
    "G-REDTEAM": external("G-REDTEAM", ["wct", "selftest", "redteam"]),
}
