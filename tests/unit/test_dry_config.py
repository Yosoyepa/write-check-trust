"""dry.template_threshold y filtros de tamaño del engine de plantilla (PR-B)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from tools.wct.dry.tpl import analyze_template

REPO = Path(__file__).parents[2]

# Par con similitud de plantilla ~0.76: por debajo de 0.90 (sin clúster con el
# YAML vigente) y por encima de 0.5 (clúster con un umbral declarado menor).
NEAR_MISS_A = (
    "def process_user(user_id, count):\n"
    "    limit = 100\n"
    "    if count > limit:\n"
    "        log_warning('overflow', user_id)\n"
    "        return None\n"
    "    return count * 2\n"
)
NEAR_MISS_B = (
    "def handle_order(order_ref, amount):\n"
    "    maximum = 500\n"
    "    if amount > maximum:\n"
    "        notify_error('exceeded', order_ref)\n"
    "        return None\n"
    "    extra = amount * 3\n"
    "    audit_trace('order', extra)\n"
    "    return extra\n"
)

# Par idéntico salvo nombres/literales: clúster con el umbral vigente 0.90.
IDENTICAL_A = (
    "def process_user(user_id, count):\n"
    "    limit = 100\n"
    "    if count > limit:\n"
    "        log_warning('overflow', user_id)\n"
    "        return None\n"
    "    return count * 2\n"
)
IDENTICAL_B = (
    "def handle_order(order_ref, amount):\n"
    "    maximum = 500\n"
    "    if amount > maximum:\n"
    "        notify_error('exceeded', order_ref)\n"
    "        return None\n"
    "    return amount * 3\n"
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


def test_template_threshold_declared_and_consumed(
    project_factory: Callable[..., Path],
) -> None:
    """El umbral de plantilla vive en thresholds.yaml y el engine lo obedece."""
    assert _declared("dry.template_threshold") == 0.90

    root = project_factory()
    (root / "src/alpha.py").write_text(NEAR_MISS_A, encoding="utf-8")
    (root / "src/beta.py").write_text(NEAR_MISS_B, encoding="utf-8")

    with_default = analyze_template(root)
    assert with_default["candidates"] == []

    _set_threshold(root, "dry.template_threshold", 0.5)

    with_declared = analyze_template(root)

    assert len(with_declared["candidates"]) == 1
    assert with_declared["candidates"][0]["score"] >= 0.5


def test_min_lines_and_min_nodes_consumed_by_template_engine(
    project_factory: Callable[..., Path],
) -> None:
    """Los filtros de tamaño del engine salen del YAML, no de literales."""
    by_lines = project_factory(package="bylines")
    (by_lines / "src/alpha.py").write_text(IDENTICAL_A, encoding="utf-8")
    (by_lines / "src/beta.py").write_text(IDENTICAL_B, encoding="utf-8")
    assert len(analyze_template(by_lines)["candidates"]) == 1

    _set_threshold(by_lines, "dry.min_lines", 9)
    by_nodes = project_factory(package="bynodes")
    (by_nodes / "src/alpha.py").write_text(IDENTICAL_A, encoding="utf-8")
    (by_nodes / "src/beta.py").write_text(IDENTICAL_B, encoding="utf-8")
    _set_threshold(by_nodes, "dry.min_nodes", 50)

    assert analyze_template(by_lines)["candidates"] == []
    assert analyze_template(by_nodes)["candidates"] == []


def test_missing_dry_template_threshold_fails_naming_it(
    project_factory: Callable[..., Path],
) -> None:
    """Clave ausente: error que la nombra; nunca un default silencioso."""
    root = project_factory()
    (root / "src/alpha.py").write_text(IDENTICAL_A, encoding="utf-8")
    _drop_threshold(root, "dry.template_threshold")

    with pytest.raises(ValueError, match=r"dry\.template_threshold"):
        analyze_template(root)
