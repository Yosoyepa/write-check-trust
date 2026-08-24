"""Analizador de inyección de dependencias y límites de capa (G-WIRE).

Detecta instanciación de infraestructura o dependencias prohibidas dentro de
domain/ y application/, imports con comodín y llamadas con efectos a nivel de
módulo en domain/.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from tools.wct.config import load_config

_TYPING_NAMES = frozenset(
    {
        "Protocol",
        "TypeVar",
        "NewType",
        "TypeAlias",
        "NamedTuple",
        "TypedDict",
        "cast",
        "overload",
        "dataclass",
        "dataclasses",
        "typing",
        "Annotated",
        "Generic",
    }
)


def _file_layer(path: Path, root: Path, layers: list[str]) -> str | None:
    """Retorna la capa de arquitectura a la que pertenece el archivo."""
    rel = path.relative_to(root)
    for part in rel.parts:
        if part in layers:
            return part
    return None


def _collect_imports_and_stars(
    tree: ast.AST, rel_file: str
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Mapea nombres locales a su origen punteado y detecta star-imports."""
    mapping: dict[str, str] = {}
    findings: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                mapping[local] = alias.name
                if "." in alias.name:
                    mapping[alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    findings.append(
                        {
                            "file": rel_file,
                            "line": node.lineno,
                            "symbol": "*",
                            "origin": mod or ".",
                            "rule": "star-import",
                        }
                    )
                else:
                    local = alias.asname or alias.name
                    full = f"{mod}.{alias.name}" if mod else alias.name
                    mapping[local] = full
    return mapping, findings


def _resolve_call(func: ast.AST, mapping: dict[str, str]) -> tuple[str, str]:
    """Resuelve el símbolo llamado y su origen calificado."""
    if isinstance(func, ast.Name):
        sym = func.id
        origin = mapping.get(sym, sym)
        return sym, origin
    if isinstance(func, ast.Attribute):
        parts: list[str] = []
        cur: ast.AST = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            parts.reverse()
            sym = ".".join(parts)
            base = parts[0]
            resolved_base = mapping.get(base, base)
            origin = ".".join([resolved_base, *parts[1:]])
            return sym, origin
    return ast.unparse(func), ast.unparse(func)


def _is_higher_layer_or_forbidden(
    origin: str,
    higher_layers: list[str],
    forbidden: list[str],
    root_pkg: str | None,
) -> str | None:
    """Determina si un origen cruza capas indebidas o usa dependencias prohibidas."""
    for hl in higher_layers:
        prefixes = [f"{hl}.", hl]
        if root_pkg:
            prefixes.extend([f"{root_pkg}.{hl}.", f"{root_pkg}.{hl}"])
        for prefix in prefixes:
            if origin == prefix or origin.startswith(f"{prefix}.") or f".{hl}." in origin:
                return "higher-layer"
    for pkg in forbidden:
        if origin == pkg or origin.startswith(f"{pkg}."):
            return "forbidden-external"
    return None


def _is_typing_or_decl(sym: str, origin: str) -> bool:
    if sym in _TYPING_NAMES or origin in _TYPING_NAMES:
        return True
    return origin.startswith("typing.") or origin.startswith("dataclasses.")


def _check_module_level_calls(
    tree: ast.Module, rel_file: str, mapping: dict[str, str]
) -> list[dict[str, Any]]:
    """Detecta llamadas ejecutadas durante la importación a nivel de módulo."""
    findings: list[dict[str, Any]] = []
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for child in ast.walk(stmt):
            if isinstance(child, ast.Call):
                sym, origin = _resolve_call(child.func, mapping)
                if not _is_typing_or_decl(sym, origin):
                    findings.append(
                        {
                            "file": rel_file,
                            "line": child.lineno,
                            "symbol": sym,
                            "origin": origin,
                            "rule": "module-level-call",
                        }
                    )
    return findings


def scan(root: Path) -> dict[str, Any]:
    """Escanea domain/ y application/ en busca de anti-patrones de cableado."""
    _root, policy, _thresholds = load_config(root)
    arch = policy.get("architecture", {})
    layers: list[str] = arch.get("layers", ["entrypoints", "adapters", "application", "domain"])
    forbidden_map: dict[str, list[str]] = arch.get("forbidden_external", {})
    root_pkg: str | None = arch.get("root_package")
    source_dirs: list[str] = policy.get("paths", {}).get("source", ["src"])

    target_layers = {"domain", "application"}
    findings: list[dict[str, Any]] = []

    for sdir in source_dirs:
        for path in sorted((root / sdir).rglob("*.py")):
            if not path.is_file():
                continue
            layer = _file_layer(path, root, layers)
            if layer not in target_layers:
                continue

            rel_file = str(path.relative_to(root))
            layer_idx = layers.index(layer)
            higher_layers = layers[:layer_idx]
            forbidden = forbidden_map.get(layer, [])

            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue

            mapping, star_findings = _collect_imports_and_stars(tree, rel_file)
            findings.extend(star_findings)

            if layer == "domain":
                findings.extend(_check_module_level_calls(tree, rel_file, mapping))

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    sym, origin = _resolve_call(node.func, mapping)
                    rule = _is_higher_layer_or_forbidden(origin, higher_layers, forbidden, root_pkg)
                    if rule:
                        findings.append(
                            {
                                "file": rel_file,
                                "line": node.lineno,
                                "symbol": sym,
                                "origin": origin,
                                "rule": rule,
                            }
                        )

    return {"findings": findings}
