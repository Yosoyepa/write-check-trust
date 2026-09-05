from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from tools.wct.config import load_config
from tools.wct.gate.capabilities import gate_info
from tools.wct.gate.runner import REGISTRY, TIERS
from tools.wct.rules.engine import rule_documents


def _capabilities() -> list[dict[str, Any]]:
    """Perfil de capacidades por gate, derivado del constructor (ADR-D-01).

    La presencia se mide aquí y ahora (shutil.which en tiempo de report):
    el perfil responde "si corro full en este entorno, qué no se verifica
    y por qué" (O-006) sin duplicar lo que cada gate ya declara.
    """
    capabilities: list[dict[str, Any]] = []
    for gate_id, gate in REGISTRY.items():
        info = gate_info(gate)
        tools = list(info.tools) if info else []
        scope = list(info.scope) if info else []
        capabilities.append(
            {
                "gate": gate_id,
                "tools": tools,
                "present": all(shutil.which(tool) for tool in tools),
                "scope": scope,
                "tiers": [tier for tier, gates in TIERS.items() if gate_id in gates],
            }
        )
    return capabilities


def overview(root: Path) -> dict[str, Any]:
    _root, policy, _thresholds = load_config(root)
    automated: list[str] = []
    human: list[str] = []
    unknown: list[str] = []
    for document in rule_documents(root):
        for rule in document.get("rules", []):
            checks = set(rule.get("verified_by", []))
            if checks == {"human"}:
                human.append(rule["id"])
            elif checks - ({"human"} | set(REGISTRY)):
                unknown.append(rule["id"])
            else:
                automated.append(rule["id"])
    return {
        "profile": policy["profile"],
        "mode": policy["mode"],
        "rules": {"automated": automated, "human_only": human, "unknown": unknown},
        "tiers": TIERS,
        "disabled_gates": policy.get("gates", {}).get("disabled", []),
        "optional_tools": policy.get("gates", {}).get("optional_tools", []),
        "capabilities": _capabilities(),
    }
