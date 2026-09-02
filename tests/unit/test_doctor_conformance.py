"""Sección de conformidad 'Umbrales declarados → gates' en doctor (PR-B)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from tools.wct.doctor.checks import WIRED_THRESHOLDS, diagnose

REPO = Path(__file__).parents[2]


def _declared(root: Path, dotted: str) -> Any:
    """Lee una clave puntual del thresholds.yaml del proyecto dado."""
    document = yaml.safe_load((root / "governance" / "thresholds.yaml").read_text(encoding="utf-8"))
    value: Any = document
    for part in dotted.split("."):
        value = value[part]
    return value


def _set_threshold(root: Path, dotted: str, value: object) -> None:
    """Reescribe el thresholds.yaml del fixture con la clave en el valor dado."""
    path = root / "governance" / "thresholds.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    section, key = dotted.split(".")
    document[section][key] = value
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def test_doctor_lists_wired_thresholds() -> None:
    """La sección lista >=11 pares clave→gate con los valores del YAML vigente."""
    rows = [message.strip() for _ok, message in diagnose(REPO) if " ← " in message]

    assert len(rows) >= 11
    for key, gate in WIRED_THRESHOLDS:
        assert f"{gate} ← {key} = {_declared(REPO, key)}" in rows


def test_doctor_section_is_advisory() -> None:
    """La sección nunca pone un FAIL: doctor informa, los gates bloquean."""
    rows = [(ok, message) for ok, message in diagnose(REPO) if " ← " in message]

    assert rows
    assert all(ok for ok, _message in rows)


def test_doctor_section_reads_live_yaml(project_factory: Callable[..., Path]) -> None:
    """Los valores mostrados provienen del thresholds.yaml del entorno."""
    root = project_factory()
    _set_threshold(root, "crap.changed_max", 9)
    _set_threshold(root, "lcom.threshold", 5)
    _set_threshold(root, "dry.template_threshold", 0.55)

    rows = [message.strip() for _ok, message in diagnose(root) if " ← " in message]

    assert "G-CRAP ← crap.changed_max = 9" in rows
    assert "G-LCOM ← lcom.threshold = 5" in rows
    assert "G-DRY-TPL ← dry.template_threshold = 0.55" in rows
    assert "G-CRAP ← crap.changed_max = 6" not in rows
