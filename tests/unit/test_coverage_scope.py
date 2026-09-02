"""El scope de cobertura incluye al propio harness (PR-A2): el que verifica se verifica."""

from __future__ import annotations

from pathlib import Path
import tomllib

from tools.wct.config import load_config


def test_coverage_source_includes_harness() -> None:
    """La medición cubre src y tools/wct: 61 statements del ejemplo no son el repo."""
    root, _policy, _thresholds = load_config(Path(__file__).resolve().parents[2])

    document = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    source = document["tool"]["coverage"]["run"]["source"]

    assert "src" in source, "el scope de cobertura perdió src"
    assert "tools/wct" in source, "el harness queda fuera de su propia medición"
