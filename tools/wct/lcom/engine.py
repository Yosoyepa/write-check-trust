"""Cálculo de cohesión LCOM4 para clases (G-LCOM).

LCOM4 mide el número de componentes conexas en el grafo de métodos
y atributos de una clase. LCOM4 = 1 indica alta cohesión; LCOM4 >= 2
indica que la clase tiene responsabilidades separadas y debe revisarse.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from tools.wct.config import load_config

_EXCLUDED_BASES = frozenset(
    {
        "NamedTuple",
        "Enum",
        "IntEnum",
        "StrEnum",
        "Flag",
        "IntFlag",
        "Protocol",
        "BaseModel",
        "Exception",
        "BaseException",
        "ValueError",
        "TypeError",
        "KeyError",
        "RuntimeError",
        "NodeTransformer",
        "NodeVisitor",
    }
)


def _decorator_name(dec: ast.AST) -> str:
    target = dec.func if isinstance(dec, ast.Call) else dec
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ""


def _base_name(base: ast.AST) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""


def _is_excluded_class(node: ast.ClassDef) -> bool:
    """Determina si la clase está excluida del cálculo de LCOM4."""
    if node.name.startswith("Test") or node.name.endswith(("Test", "Tests")):
        return True
    if any(_decorator_name(dec) == "dataclass" for dec in node.decorator_list):
        return True
    for base in node.bases:
        name = _base_name(base)
        if name in _EXCLUDED_BASES or name.endswith(("Error", "Exception")):
            return True
    return False


def _is_abstract(method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in method.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "abstractmethod":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod":
            return True
    return False


def _extract_methods(
    node: ast.ClassDef,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        item
        for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_abstract(item)
    ]


def _method_refs(
    m: ast.FunctionDef | ast.AsyncFunctionDef, method_names: set[str]
) -> tuple[set[str], set[str]]:
    self_name = m.args.args[0].arg if m.args.args else "self"
    calls: set[str] = set()
    call_targets: set[ast.AST] = set()
    for child in ast.walk(m):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and isinstance(child.func.value, ast.Name)
            and child.func.value.id == self_name
        ):
            call_targets.add(child.func)
            if child.func.attr in method_names:
                calls.add(child.func.attr)

    attrs = {
        child.attr
        for child in ast.walk(m)
        if isinstance(child, ast.Attribute)
        and child not in call_targets
        and isinstance(child.value, ast.Name)
        and child.value.id == self_name
    }
    return attrs, calls


def _connected_components(names: list[str], adj: dict[str, set[str]]) -> int:
    visited: set[str] = set()
    components = 0
    for name in names:
        if name not in visited:
            components += 1
            queue = [name]
            visited.add(name)
            while queue:
                curr = queue.pop(0)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return components


def class_lcom4(node: ast.ClassDef, min_methods: int | None = None) -> int | None:
    """Calcula LCOM4 de una clase. Retorna None si está excluida.

    min_methods None se resuelve desde governance/thresholds.yaml
    (lcom.min_methods); una clave ausente es un ValueError que la nombra,
    nunca un default silencioso (ADR-B-01 §3).
    """
    if min_methods is None:
        _root, _policy, thresholds = load_config()
        lcom = thresholds.get("lcom", {})
        try:
            min_methods = int(lcom["min_methods"])
        except KeyError as exc:
            raise ValueError(f"thresholds.yaml: falta la clave lcom.{exc.args[0]}") from exc
    if _is_excluded_class(node):
        return None
    methods = _extract_methods(node)
    if len(methods) < min_methods:
        return None

    method_names = {m.name for m in methods}
    names = [m.name for m in methods]
    attrs: dict[str, set[str]] = {}
    calls: dict[str, set[str]] = {}

    for m in methods:
        a, c = _method_refs(m, method_names)
        attrs[m.name] = a
        calls[m.name] = c

    adj: dict[str, set[str]] = {name: set() for name in names}
    for i, n1 in enumerate(names):
        for n2 in names[i + 1 :]:
            if bool(attrs[n1] & attrs[n2]) or n2 in calls[n1] or n1 in calls[n2]:
                adj[n1].add(n2)
                adj[n2].add(n1)

    return _connected_components(names, adj)


def scan(root: Path) -> dict[str, Any]:
    """Escanea src/ y tools/ en busca de métricas LCOM4.

    Los umbrales (lcom.min_methods, lcom.threshold) provienen de
    governance/thresholds.yaml del proyecto analizado; una clave ausente es
    un ValueError que la nombra (ADR-B-01 §3).
    """
    _root, policy, thresholds = load_config(root)
    lcom = thresholds.get("lcom", {})
    try:
        min_methods = int(lcom["min_methods"])
        lcom_threshold = int(lcom["threshold"])
    except KeyError as exc:
        raise ValueError(f"thresholds.yaml: falta la clave lcom.{exc.args[0]}") from exc
    candidates: list[Path] = []
    for key in ("source", "tools"):
        for directory in policy.get("paths", {}).get(key, []):
            candidates.extend((root / directory).rglob("*.py"))

    classes: list[dict[str, Any]] = []
    for path in sorted(set(candidates)):
        if not path.is_file():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        rel_file = str(path.relative_to(root))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                score = class_lcom4(node, min_methods)
                if score is not None:
                    classes.append(
                        {
                            "file": rel_file,
                            "class": node.name,
                            "line": node.lineno,
                            "lcom4": score,
                        }
                    )

    return {
        "classes": classes,
        "violators": [c for c in classes if c["lcom4"] >= lcom_threshold],
    }
