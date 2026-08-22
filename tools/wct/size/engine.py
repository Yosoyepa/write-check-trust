from __future__ import annotations

from pathlib import Path
import tokenize
from typing import Any

from tools.wct.config import load_config

# Tokens que no implican código en la línea donde aparecen: comentarios,
# separadores de línea y marcadores estructurales del tokenizer.
_NON_CODE_TOKENS = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
    }
)


def file_loc(path: Path) -> int:
    """Líneas con código real: sin blancos ni líneas de solo comentario.

    Los docstrings y strings multilínea cuentan: son contenido mantenido.
    La exclusión de tests y generado la decide quién llama, no el contador.
    """
    code_lines: set[int] = set()
    with path.open("rb") as stream:
        for token in tokenize.tokenize(stream.readline):
            if token.type in _NON_CODE_TOKENS:
                continue
            code_lines.update(range(token.start[0], token.end[0] + 1))
    return len(code_lines)


def oversized(root: Path) -> dict[str, Any]:
    """Archivos de source y tools por encima del presupuesto de líneas."""
    _root, policy, thresholds = load_config(root)
    limit = int(thresholds["size"]["max_file_loc"])
    candidates: list[Path] = []
    for key in ("source", "tools"):
        for directory in policy["paths"].get(key, []):
            candidates.extend((root / directory).rglob("*.py"))
    files = [
        {"file": str(path.relative_to(root)), "loc": loc}
        for path in sorted(set(candidates))
        if path.is_file() and (loc := file_loc(path)) > limit
    ]
    return {"limit": limit, "files": files}
