"""Hotspots: churn x complejidad (Tornhill, "Your Code as a Crime Scene").

Reporte asesor, no gate: el churn absoluto castiga módulos simplemente
activos, así que ningún umbral bloquea aquí. El producto churn x
complejidad es el mejor predictor empírico de defectos publicado
("Code Red", 39 codebases: 15x) y señala DÓNDE refactorizar primero.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
from typing import Any

from tools.wct.cognitive.engine import function_score
from tools.wct.config import load_config
from tools.wct.util.git import run_git

NUMSTAT_LINE = re.compile(r"^(\d+|-)\t(\d+|-)\t(.+)$")


def _final_name(raw: str) -> str:
    """Resuelve la forma de rename de numstat (plana y con llaves)."""
    if "=>" not in raw:
        return raw
    if "{" in raw:
        before, rest = raw.split("{", 1)
        changed, after = rest.split("}", 1)
        return f"{before}{changed.split('=>', 1)[1].strip()}{after}"
    return raw.split("=>", 1)[1].strip()


def churn_from_log(text: str) -> dict[str, int]:
    """Churn por archivo: líneas añadidas + removidas acumuladas."""
    churn: dict[str, int] = {}
    for line in text.splitlines():
        match = NUMSTAT_LINE.match(line)
        if not match:
            continue
        added, removed, raw_path = match.groups()
        if added == "-" or removed == "-":
            continue
        path = _final_name(raw_path)
        churn[path] = churn.get(path, 0) + int(added) + int(removed)
    return churn


def _file_complexity(path: Path) -> int:
    """Suma de complejidad cognitiva de las funciones del archivo."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return 0
    return sum(
        function_score(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    )


def report(root: Path, days: int = 90, top: int = 10) -> dict[str, Any]:
    """Top de archivos por churn x complejidad sobre source y tools."""
    _root, policy, _thresholds = load_config(root)
    directories = sorted(
        {directory for key in ("source", "tools") for directory in policy["paths"].get(key, [])}
    )
    log = run_git(
        root,
        "log",
        "--numstat",
        "--format=",
        f"--since={days} days ago",
        "--",
        *directories,
        check=False,
    )
    files: list[dict[str, Any]] = []
    for relative, changes in churn_from_log(log.stdout).items():
        path = root / relative
        if not path.is_file() or path.suffix != ".py":
            continue
        complexity = _file_complexity(path)
        files.append(
            {
                "file": relative,
                "churn": changes,
                "complexity": complexity,
                "hotspot": changes * complexity,
            }
        )
    files.sort(key=lambda item: (-item["hotspot"], item["file"]))
    return {"days": days, "files": files[:top]}


def render(data: dict[str, Any]) -> str:
    """Tabla de texto: prioridad de refactor sugerida, no veredicto."""
    lines = [f"hotspots ({data['days']} días) — asesor, no bloqueante:"]
    for position, item in enumerate(data["files"], 1):
        lines.append(
            f"{position}. {item['file']}: churn={item['churn']} "
            f"cognitiva={item['complexity']} hotspot={item['hotspot']}"
        )
    return "\n".join(lines) if len(lines) > 1 else lines[0] + " sin datos todavía"
