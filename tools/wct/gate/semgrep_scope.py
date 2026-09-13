"""Inventario exigible y normalización de rutas de G-SAST-SEMGREP (partición fachada).

E = fuentes Python exigibles: los *.py regulares de los directorios
declarados en policy.paths (source, tests, tools) que existen bajo la raíz,
normalizados como POSIX relativos a ella. Incluye rastreados, no
rastreados, ignorados por Git y módulos de unsuitable_for_test; excluye por
definición de alcance build, caches, bytecode y todo lo que escape de la
raíz. La excepción SemgrepScopeError vive aquí porque toda indeterminación
de ruta —de política, escaneada o de hallazgo— es indeterminación de
alcance.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

_SOURCE_KEYS = ("source", "tests", "tools")

# Excluidos por definición de alcance dentro de las rutas declaradas
# (addenda §1): .git, entornos virtuales y cachés. Mismo conjunto que
# `_protected` de integrity, más .git; el bytecode ya queda fuera por el
# filtro *.py. Se matchea por componente de ruta (límite de directorio),
# nunca por prefijo textual.
_IGNORED_PARTS = frozenset(
    {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
)


class SemgrepScopeError(ValueError):
    """El alcance exigible o la respuesta del instrumento es indeterminable."""


def relative_path(path: Any) -> PurePosixPath | None:
    """Ruta POSIX relativa normalizable; None si el tipo o la forma no valen."""
    if not isinstance(path, str):
        return None
    pure = PurePosixPath(path)
    if not pure.parts or pure.is_absolute() or ".." in pure.parts:
        return None
    return pure


def _relative(root: Path, raw: str) -> str:
    """Normaliza una ruta relativa POSIX bajo root; error si escapa de él."""
    pure = relative_path(raw)
    if pure is None:
        raise SemgrepScopeError(f"ruta de alcance no normalizable bajo la raíz: {raw!r}")
    resolved = (root / Path(*pure.parts)).resolve()
    if not resolved.is_relative_to(root):
        raise SemgrepScopeError(f"ruta de alcance escapa de la raíz: {raw!r}")
    return resolved.relative_to(root).as_posix()


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _scoped_dirs(policy: dict[str, Any]) -> list[str]:
    """Rutas declaradas en policy.paths source/tests/tools."""
    paths = policy.get("paths")
    if not isinstance(paths, dict):
        raise SemgrepScopeError("policy.paths debe ser un mapa para determinar el alcance")
    declared: list[str] = []
    for key in _SOURCE_KEYS:
        value = paths.get(key, [])
        if not _is_string_list(value):
            raise SemgrepScopeError(f"policy.paths.{key} debe ser una lista de rutas string")
        declared.extend(value)
    return declared


def _unique_dirs(root: Path, declared: list[str]) -> list[str]:
    """Normaliza las rutas declaradas; dos crudas que resuelven a la misma son ambiguas."""
    normalized: dict[str, str] = {}
    for raw in declared:
        name = _relative(root, raw)
        if normalized.setdefault(name, raw) != raw:
            raise SemgrepScopeError(f"ruta de política ambigua: {raw!r} y {name!r}")
    return sorted(normalized)


def _python_files(root: Path, base: Path, builds: list[Path]) -> set[str]:
    files: set[str] = set()
    for candidate in sorted(base.rglob("*.py")):
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            raise SemgrepScopeError(f"fuente declarada escapa de la raíz: {candidate}")
        if any(resolved.is_relative_to(build) for build in builds):
            continue
        relative = resolved.relative_to(root)
        if _IGNORED_PARTS & set(relative.parts):
            continue
        if candidate.is_file():
            files.add(relative.as_posix())
    return files


def _build_dirs(root: Path, policy: dict[str, Any]) -> list[Path]:
    """Directorios de construcción declarados (paths.build), resueltos bajo la raíz.

    Excluidos por definición de alcance incluso si solapan con una fuente
    declarada; la pertenencia es por límite de directorio, no por prefijo
    textual (un `builder.py` o un `build2/` vecinos siguen contando).
    """
    raw = policy["paths"].get("build", [])
    values = [raw] if isinstance(raw, str) else raw
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise SemgrepScopeError(
            "policy.paths.build debe ser una ruta string o una lista de rutas string"
        )
    builds: list[Path] = []
    for item in values:
        pure = relative_path(item)
        if pure is None:
            raise SemgrepScopeError(f"ruta de construcción no normalizable bajo la raíz: {item!r}")
        builds.append((root / Path(*pure.parts)).resolve())
    return builds


def required_sources(root: Path, policy: dict[str, Any]) -> list[str]:
    """E: fuentes Python exigibles según los directorios declarados de policy.paths.

    Recorre sólo los directorios explícitos (patrón de size/ratchet/dry), sin
    rglob desde la raíz; no consulta Git, así que las fuentes ignoradas siguen
    siendo exigibles y los módulos de unsuitable_for_test no se omiten. Un
    directorio declarado inexistente no aporta fuentes. El directorio de
    construcción (paths.build, string o lista) y los entornos virtuales y
    cachés anidados se excluyen por límite de directorio, aunque solapen con
    una fuente declarada; una fuente que escape de la raíz es ERROR.
    """
    base_root = root.resolve()
    declared = _unique_dirs(base_root, _scoped_dirs(policy))
    builds = _build_dirs(base_root, policy)
    sources: set[str] = set()
    for directory in declared:
        base = base_root / directory
        if not base.is_dir():
            continue
        sources.update(_python_files(base_root, base, builds))
    return sorted(sources)
