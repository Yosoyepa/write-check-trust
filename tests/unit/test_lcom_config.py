"""lcom.min_methods y lcom.threshold declarados y consumidos (PR-B)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from tools.wct.lcom.engine import scan

REPO = Path(__file__).parents[2]

# Dos métodos: por debajo de lcom.min_methods vigente (3), no se evalúa.
TWO_METHODS = (
    "class Pair:\n"
    "    def m1(self):\n"
    "        return self.a\n"
    "    def m2(self):\n"
    "        return self.b\n"
)

# Cuatro métodos en dos grupos disjuntos: LCOM4 = 2.
TWO_GROUPS = (
    "class Split:\n"
    "    def m1(self):\n"
    "        return self.a\n"
    "    def m2(self):\n"
    "        return self.a\n"
    "    def m3(self):\n"
    "        return self.b\n"
    "    def m4(self):\n"
    "        return self.b\n"
)


def _declared(dotted: str) -> object:
    """Lee una clave puntual del thresholds.yaml real del repositorio."""
    document = yaml.safe_load((REPO / "governance" / "thresholds.yaml").read_text(encoding="utf-8"))
    value: object = document
    for part in dotted.split("."):
        assert isinstance(value, dict)
        value = value[part]
    return value


def _set_threshold(root: Path, dotted: str, value: object) -> None:
    """Reescribe el thresholds.yaml del fixture con la clave en el valor dado."""
    path = root / "governance" / "thresholds.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    section, key = dotted.split(".")
    document[section][key] = value
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def _drop_threshold(root: Path, dotted: str) -> None:
    """Elimina la clave del thresholds.yaml del fixture."""
    path = root / "governance" / "thresholds.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    section, key = dotted.split(".")
    del document[section][key]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def test_lcom_thresholds_declared_and_consumed(
    project_factory: Callable[..., Path],
) -> None:
    """Los umbrales LCOM4 viven en thresholds.yaml y scan los obedece."""
    assert _declared("lcom.min_methods") == 3
    assert _declared("lcom.threshold") == 2

    root = project_factory()
    (root / "src/cohesion.py").write_text(TWO_METHODS + "\n\n" + TWO_GROUPS, encoding="utf-8")

    with_default = scan(root)
    assert [item["class"] for item in with_default["classes"]] == ["Split"]
    assert [item["class"] for item in with_default["violators"]] == ["Split"]

    _set_threshold(root, "lcom.min_methods", 2)
    with_min_methods = scan(root)

    assert [item["class"] for item in with_min_methods["classes"]] == ["Pair", "Split"]

    _set_threshold(root, "lcom.threshold", 3)
    with_threshold = scan(root)

    assert with_threshold["violators"] == []


def test_missing_lcom_threshold_fails_naming_it(
    project_factory: Callable[..., Path],
) -> None:
    """Clave ausente: error que la nombra; nunca un default silencioso."""
    root = project_factory()
    (root / "src/cohesion.py").write_text(TWO_GROUPS, encoding="utf-8")
    _drop_threshold(root, "lcom.threshold")

    with pytest.raises(ValueError, match=r"lcom\.threshold"):
        scan(root)
