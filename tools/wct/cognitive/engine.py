"""Complejidad cognitiva por función (G-COGNITIVE).

Algoritmo inspirado en Campbell/SonarSource (S3776, umbral 15), con la
semántica de referencia para Python del proyecto Melevir/cognitive_complexity.
Reglas: if/for/while/except/match/ternario suman 1 + profundidad; elif suma
en la profundidad actual (la cadena plana no acumula); else suma 1 plano;
función/lambda anida sin sumar; cada secuencia de operadores lógicos suma 1;
la recursión directa suma 1. Divergencias documentadas: assert, with y las
comprehensions no incrementan.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from tools.wct.config import load_config


def _sum(nodes: ast.AST | Sequence[ast.AST], depth: int) -> int:
    if isinstance(nodes, ast.AST):
        return sum(_score(child, depth) for child in ast.iter_child_nodes(nodes))
    return sum(_score(child, depth) for child in nodes)


def _if_orelse(orelse: Sequence[ast.stmt], depth: int) -> int:
    if not orelse:
        return 0
    if len(orelse) == 1 and isinstance(orelse[0], ast.If):
        # elif: se cobra como un if en la profundidad actual; la cadena
        # plana no acumula anidación.
        return _score(orelse[0], depth)
    # rama else: suma 1 plano; su cuerpo queda un nivel más adentro
    return 1 + _sum(orelse, depth + 1)


def _if_score(node: ast.If, depth: int) -> int:
    return (
        1
        + depth
        + _score(node.test, depth)
        + _sum(node.body, depth + 1)
        + _if_orelse(node.orelse, depth)
    )


def _loop_score(
    test: ast.expr, body: Sequence[ast.stmt], orelse: Sequence[ast.stmt], depth: int
) -> int:
    score = 1 + depth + _score(test, depth) + _sum(body, depth + 1)
    if orelse:
        score += 1 + _sum(orelse, depth + 1)
    return score


def _for_score(node: ast.For | ast.AsyncFor, depth: int) -> int:
    return _loop_score(node.iter, node.body, node.orelse, depth)


def _while_score(node: ast.While, depth: int) -> int:
    return _loop_score(node.test, node.body, node.orelse, depth)


def _except_score(node: ast.ExceptHandler, depth: int) -> int:
    return 1 + depth + _sum(node.body, depth + 1)


def _match_score(node: ast.Match, depth: int) -> int:
    return 1 + depth + _score(node.subject, depth) + _sum(node.cases, depth + 1)


def _ternary_score(node: ast.IfExp, depth: int) -> int:
    return (
        1
        + depth
        + _score(node.test, depth)
        + _score(node.body, depth + 1)
        + _score(node.orelse, depth + 1)
    )


def _boolop_score(node: ast.BoolOp, _depth: int) -> int:
    """Una secuencia de operadores lógicos por nodo BoolOp del subárbol."""
    return sum(isinstance(child, ast.BoolOp) for child in ast.walk(node))


def _nesting_score(node: ast.AST, depth: int) -> int:
    """Función o lambda: anida sin sumar; su cuerpo se cobra un nivel más."""
    return _sum(node, depth + 1)


def _recurses(funcdef: ast.AST, name: str) -> bool:
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
        for node in ast.walk(funcdef)
    )


_HANDLERS: dict[type[ast.AST], Callable[[Any, int], int]] = {
    ast.If: _if_score,
    ast.For: _for_score,
    ast.AsyncFor: _for_score,
    ast.While: _while_score,
    ast.ExceptHandler: _except_score,
    ast.Match: _match_score,
    ast.IfExp: _ternary_score,
    ast.BoolOp: _boolop_score,
    ast.FunctionDef: _nesting_score,
    ast.AsyncFunctionDef: _nesting_score,
    ast.Lambda: _nesting_score,
}


def _score(node: ast.AST, depth: int) -> int:
    """Puntuación cognitiva del nodo y su subárbol a la profundidad dada."""
    handler = _HANDLERS.get(type(node))
    if handler is not None:
        return handler(node, depth)
    return _sum(node, depth)


def function_score(funcdef: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Complejidad cognitiva de una función (la recursión directa suma 1)."""
    score = sum(_score(statement, 0) for statement in funcdef.body)
    if _recurses(funcdef, funcdef.name):
        score += 1
    return score


def scan(root: Path) -> dict[str, Any]:
    """Funciones de src/ por encima del umbral cognitivo."""
    _root, policy, thresholds = load_config(root)
    limit = int(thresholds["complexity"]["max_cognitive_per_function"])
    functions: list[dict[str, Any]] = []
    for directory in policy["paths"]["source"]:
        for path in sorted((root / directory).rglob("*.py")):
            if not path.is_file():
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    score = function_score(node)
                    if score > limit:
                        functions.append(
                            {
                                "file": str(path.relative_to(root)),
                                "function": node.name,
                                "line": node.lineno,
                                "score": score,
                            }
                        )
    return {"limit": limit, "functions": functions}
