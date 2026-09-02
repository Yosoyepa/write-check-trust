from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
from typing import Any

from tools.wct.config import load_config
from tools.wct.integrity.engine import violations
from tools.wct.rules.engine import drift

# Mapa clave→gate de los umbrales cableados por PR-B (ADR-B-02 §3). Es el
# ÚNICO elemento estático de la sección: los valores siempre se leen del
# thresholds.yaml vigente; rota solo si se cablea una clave nueva.
WIRED_THRESHOLDS: tuple[tuple[str, str], ...] = (
    ("crap.changed_max", "G-CRAP"),
    ("coverage.diff_min", "G-COV-DIFF"),
    ("dead_code.vulture_min_confidence", "G-DEAD"),
    ("complexity.xenon_max_absolute", "G-CC"),
    ("complexity.xenon_max_modules", "G-CC"),
    ("complexity.xenon_max_average", "G-CC"),
    ("dry.min_lines", "G-DRY-TPL"),
    ("dry.min_nodes", "G-DRY-TPL"),
    ("dry.template_threshold", "G-DRY-TPL"),
    ("dry.review_threshold", "G-DRY"),
    ("lcom.min_methods", "G-LCOM"),
    ("lcom.threshold", "G-LCOM"),
)

_MISSING = "AUSENTE (el gate fallará nombrándola)"


def declared_thresholds(thresholds: dict[str, Any]) -> list[tuple[bool, str]]:
    """Filas advisory 'Umbrales declarados → gates' para el YAML ya cargado.

    Cada fila muestra la clave cableada, el gate que la consume y el valor
    VIVO del thresholds.yaml recibido (ADR-B-02 §3): doctor informa, nunca
    bloquea — por eso toda fila nace en ok=True.
    """
    rows: list[tuple[bool, str]] = [
        (True, "Umbrales declarados → gates (advisory; valores de thresholds.yaml)")
    ]
    for key, gate in WIRED_THRESHOLDS:
        value: Any = thresholds
        for part in key.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        rendered = _MISSING if value is None else str(value)
        rows.append((True, f"  {gate} ← {key} = {rendered}"))
    return rows


def diagnose(root: Path) -> list[tuple[bool, str]]:
    checks: list[tuple[bool, str]] = []
    try:
        _root, policy, thresholds = load_config(root)
        checks.append((True, "governance YAML válido"))
    except Exception as exc:
        return [(False, f"configuración: {exc}")]
    checks.append(
        (sys.version_info >= (3, 11), f"Python {sys.version.split()[0]} (requiere >=3.11)")
    )
    checks.append((shutil.which("git") is not None, "git disponible"))
    checks.append((shutil.which("uv") is not None, "uv disponible"))
    checks.append((not drift(root), "reglas por proveedor sincronizadas"))
    settings = root / ".claude/settings.json"
    if settings.is_file():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            hook_map = data.get("hooks", {})
            events = set(hook_map)
            required = {
                "PreToolUse",
                "PostToolUse",
                "Stop",
                "SubagentStart",
                "SubagentStop",
                "ConfigChange",
            }
            checks.append((required <= events, f"hooks cableados ({len(events)} eventos)"))
            expected_commands = {
                "PreToolUse": "wct hook pre-tool-use",
                "PostToolUse": "wct hook post-tool-use",
                "Stop": "wct hook stop",
                "SubagentStart": "wct hook subagent-start",
                "SubagentStop": "wct hook subagent-stop",
                "ConfigChange": "wct hook config-change",
            }
            wired = all(
                expected in json.dumps(hook_map.get(event, []))
                for event, expected in expected_commands.items()
            )
            checks.append((wired, "cada evento requerido invoca su guard WCT exacto"))
        except (OSError, json.JSONDecodeError) as exc:
            checks.append((False, f".claude/settings.json inválido: {exc}"))
    else:
        checks.append((False, "falta .claude/settings.json"))
    checks.append((not violations(root), "integrity.lock coincide"))
    for tool in ("ruff", "mypy", "pytest"):
        checks.append((shutil.which(tool) is not None, f"{tool} disponible"))
    if policy.get("minimalism_mode") == "ultra":
        checks.append((False, "minimalism_mode ultra está prohibido por ADR-001"))
    checks.extend(declared_thresholds(thresholds))
    return checks
