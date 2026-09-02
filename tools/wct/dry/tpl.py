"""Detección de clones de plantilla AST (G-DRY-TPL).

Segunda pasada de DRY que anonimiza nombres e identificadores junto con
constantes literales (map a '_') antes del fingerprint de Jaccard.
Detecta código copiado de plantillas o boilerplate con variables renombradas.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
from typing import Any

from tools.wct.config import load_config


@dataclass(frozen=True)
class TemplateUnit:
    """Función con estructura y literales completamente anonimizados."""

    file: str
    name: str
    start: int
    end: int
    lines: int
    nodes: int
    fingerprints: frozenset[str]


class TemplateNormalizer(ast.NodeTransformer):
    """Anonimiza todo nombre, argumento, atributo y constante literal a '_'."""

    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(id="_", ctx=node.ctx), node)

    def visit_arg(self, node: ast.arg) -> ast.AST:
        return ast.copy_location(ast.arg(arg="_", annotation=None), node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        return ast.copy_location(
            ast.Attribute(value=self.visit(node.value), attr="_", ctx=node.ctx), node
        )

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        return ast.copy_location(ast.Constant(value="_"), node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        transformed = self.generic_visit(node)
        if not isinstance(transformed, ast.FunctionDef):
            raise TypeError("FunctionDef normalization changed node type")
        transformed.name = "_"
        return transformed

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        transformed = self.generic_visit(node)
        if not isinstance(transformed, ast.AsyncFunctionDef):
            raise TypeError("AsyncFunctionDef normalization changed node type")
        transformed.name = "_"
        return transformed


def _unit(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> TemplateUnit:
    normalized = (
        TemplateNormalizer().visit(ast.fix_missing_locations(ast.parse(ast.unparse(node)))).body[0]
    )
    dumps = [
        ast.dump(child, annotate_fields=False, include_attributes=False)
        for child in ast.walk(normalized)
    ]
    fingerprints = frozenset(
        hashlib.sha1(val.encode(), usedforsecurity=False).hexdigest() for val in dumps
    )
    return TemplateUnit(
        path.relative_to(root).as_posix(),
        node.name,
        node.lineno,
        node.end_lineno or node.lineno,
        (node.end_lineno or node.lineno) - node.lineno + 1,
        len(dumps),
        fingerprints,
    )


def _is_test_file(path: Path, root: Path, test_dirs: list[str]) -> bool:
    rel = path.relative_to(root)
    if any(part in test_dirs for part in rel.parts):
        return True
    return rel.name.startswith("test_") or rel.name.endswith("_test.py")


def _collect_units(
    paths: list[Path],
    root: Path,
    test_dirs: list[str],
    min_lines: int,
    min_nodes: int,
) -> tuple[list[TemplateUnit], list[str]]:
    units: list[TemplateUnit] = []
    errors: list[str] = []
    for path in sorted(set(paths)):
        if not path.is_file() or _is_test_file(path, root, test_dirs):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(root)}:{exc.lineno}: {exc.msg}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                item = _unit(path, root, node)
                if item.lines >= min_lines and item.nodes >= min_nodes:
                    units.append(item)
    return units, errors


def _find_candidates(units: list[TemplateUnit], threshold: float) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, left in enumerate(units):
        for right in units[index + 1 :]:
            union = left.fingerprints | right.fingerprints
            score = len(left.fingerprints & right.fingerprints) / len(union) if union else 0.0
            if score >= threshold:
                candidates.append(
                    {
                        "score": round(score, 4),
                        "left": {k: v for k, v in asdict(left).items() if k != "fingerprints"},
                        "right": {k: v for k, v in asdict(right).items() if k != "fingerprints"},
                    }
                )
    return sorted(candidates, key=lambda c: c["score"], reverse=True)


def analyze_template(
    root: Path,
    paths: list[Path] | None = None,
    threshold: float | None = None,
) -> dict[str, Any]:
    """Analiza clones estructurales con normalización agresiva de plantilla.

    Los umbrales (template_threshold, min_lines, min_nodes) provienen de
    governance/thresholds.yaml; una clave ausente es un ValueError que la
    nombra, nunca un default silencioso (ADR-B-01 §3).
    """
    _root, policy, thresholds = load_config(root)
    dry = thresholds.get("dry", {})
    try:
        min_lines = int(dry["min_lines"])
        min_nodes = int(dry["min_nodes"])
        if threshold is None:
            threshold = float(dry["template_threshold"])
    except KeyError as exc:
        raise ValueError(f"thresholds.yaml: falta la clave dry.{exc.args[0]}") from exc
    test_dirs: list[str] = policy.get("paths", {}).get("tests", ["tests"])
    if paths is None:
        paths = []
        for key in ("source", "tools"):
            for directory in policy.get("paths", {}).get(key, []):
                paths.extend((root / directory).rglob("*.py"))

    units, errors = _collect_units(paths, root, test_dirs, min_lines, min_nodes)
    candidates = _find_candidates(units, threshold)

    return {
        "candidates": candidates,
        "errors": errors,
        "units": len(units),
    }
