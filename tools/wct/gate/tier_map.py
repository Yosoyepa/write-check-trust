"""Mapa de tiers y puertas del tier commit."""

from __future__ import annotations

_COMMIT_GATES = [
    "G-META-1",
    "G-META-2",
    "G-RULES-DRIFT",
    "G-SUPPRESS",
    "G-DEBT",
    "G-LINT",
    "G-FMT",
    "G-TYPE",
    "G-TEST",
    "G-ARCH",
    "G-ARCHMETRICS",
    "G-DEPS",
    "G-DEAD",
    "G-SAST-BANDIT",
    "G-SECRET",
    "G-MUT-SITES",
    "G-ACCEPT",
    "G-SIZE",
    "G-COGNITIVE",
    "G-WIRE",
    # ADR-G3a-03 G3a-1: promoción por membresía — el control de introvertidos
    # corre en el tier que CI ya ejecuta. Al vivir en _COMMIT_GATES, full y pr
    # lo heredan: su entrada literal en full se retiró para no duplicar.
    "G-INTROVERT",
]

TIERS: dict[str, list[str]] = {
    "fast": [
        "G-META-2",
        "G-RULES-DRIFT",
        "G-SUPPRESS",
        "G-DEBT",
        "G-LINT",
        "G-FMT",
        "G-TYPE",
    ],
    "commit": list(_COMMIT_GATES),
    "full": [
        *_COMMIT_GATES,
        "G-COV-TOTAL",
        "G-MUT",
        "G-CRAP",
        "G-CC",
        "G-DRY",
        "G-DRY-TOK",
        "G-DRY-TPL",
        "G-LCOM",
        "G-SAST-SEMGREP",
        "G-AUDIT",
        "G-SBOM",
        "G-DOC",
        "G-REDTEAM",
    ],
    # Espejo local de quality.yml en PRs: todo lo que CI exige de una PR,
    # ejecutable con un solo comando antes de pushear.
    "pr": [
        *_COMMIT_GATES,
        "G-HOOKS-WIRED",
        "G-COV-TOTAL",
        "G-COV-DIFF",
        "G-PROP",
        "G-ACCEPT-MUT",
        "G-REDTEAM",
    ],
}
