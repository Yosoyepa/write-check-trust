from collections.abc import Callable
from pathlib import Path

from tools.wct.dry.analyzer import analyze


def test_structural_clone_ignores_names_and_literals(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    source = root / "src/example"
    source.mkdir()
    (source / "first.py").write_text(
        """def alpha(items):
    result = []
    for item in items:
        if item > 3:
            result.append(item + 1)
    return result
""",
        encoding="utf-8",
    )
    (source / "second.py").write_text(
        """def beta(values):
    kept = []
    for value in values:
        if value > 9:
            kept.append(value + 2)
    return kept
""",
        encoding="utf-8",
    )

    report = analyze(root)

    assert report["candidates"][0]["score"] == 1.0


def test_syntax_error_reported_without_aborting(project_factory: Callable[..., Path]) -> None:
    """Un archivo roto se reporta como error relativo y el análisis continúa.

    Caracterización del refactor G-DRY-TOK (parse_tree compartido): el
    mensaje llega como relpath:linea: msg en la lista de errores.
    """
    root = project_factory()
    (root / "src" / "roto.py").write_text("def broken(:\n", encoding="utf-8")

    report = analyze(root)

    assert len(report["errors"]) == 1
    assert report["errors"][0].startswith("src/roto.py:")
    assert report["units"] == 0
