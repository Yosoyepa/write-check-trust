"""Todo módulo bajo tests/property lleva el marker property a nivel de módulo (TEST-008)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from tools.wct.config import load_config


def _marker_names(module: object) -> list[str]:
    """Nombres de los marks declarados en el pytestmark del módulo."""
    pytestmark = getattr(module, "pytestmark", None)
    marks = pytestmark if isinstance(pytestmark, list) else [pytestmark]
    return [getattr(mark, "name", "") for mark in marks]


def test_property_modules_carry_marker() -> None:
    """El marker es por módulo: uno nuevo sin él rompería el contrato inadvertidamente."""
    root, _policy, _thresholds = load_config(Path(__file__).resolve().parents[2])

    modules = sorted((root / "tests" / "property").glob("test_*.py"))
    assert modules, "tests/property sin módulos: el contrato no puede verificarse"
    for path in modules:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert "property" in _marker_names(module), f"{path.name}: falta pytestmark de módulo"
