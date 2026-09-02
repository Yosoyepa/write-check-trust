"""La selección de tests que corre cada mutante excluye property (TEST-008, ADR-A1-01)."""

from __future__ import annotations

from pathlib import Path
import tomllib

from tools.wct.config import load_config


def test_mutation_selection_excludes_property() -> None:
    """Mutmut corre la selección por mutante: property ahí es costo y contaminación."""
    root, _policy, _thresholds = load_config(Path(__file__).resolve().parents[2])

    document = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    selection = document["tool"]["mutmut"]["pytest_add_cli_args_test_selection"]

    assert selection, "selección de mutación vacía: el contrato no puede verificarse"
    assert not [entry for entry in selection if entry.startswith("tests/property/")]
