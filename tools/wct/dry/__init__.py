"""Structural fuzzy duplication analysis."""

from __future__ import annotations

import ast
from pathlib import Path


def parse_tree(path: Path, root: Path) -> ast.Module | str:
    """Parsea un archivo; en SyntaxError devuelve el error relativo al root.

    Args:
        path: archivo a parsear.
        root: raíz del proyecto, para relativizar el mensaje de error.

    Returns:
        El árbol parseado, o el mensaje de error listo para la lista de
        errores del caller (``relpath:linea: msg``).
    """
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return f"{path.relative_to(root)}:{exc.lineno}: {exc.msg}"
