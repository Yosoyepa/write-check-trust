"""Veredicto no vacío de la mutación de aceptación (SPEC-A1-02, TEST-010).

Cero mutaciones ejecutadas es sin-datos, no éxito: el veredicto debe
fallar citando TEST-010 en vez de aprobar en silencio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.wct.accept.pipeline import accept_verdict, parse_feature

_OUTLINE = """Feature: stock
Scenario Outline: reserva
  Given inventory contains "<units>" units
Examples:
  | units |
  | 3     |
"""


def _ir(tmp_path: Path, body: str) -> dict[str, Any]:
    """IR real producido por el parser, no un doble hecho a mano."""
    feature = tmp_path / "verdict.feature"
    feature.write_text(body, encoding="utf-8")
    return parse_feature(feature)


def _report(killed: int, survived: int) -> dict[str, Any]:
    """Reporte con la estructura exacta de run_mutations.

    run_mutations registra un resultado por mutación ejecutada y cada uno
    es killed o survived: ``killed + survived`` ES el total de mutaciones
    ejecutadas (equivalente a ``len(results) == 0``).
    """
    results = [{"status": "killed"}] * killed + [{"status": "survived"}] * survived
    return {"results": results, "killed": killed, "survived": survived}


def test_zero_mutations_fails(tmp_path: Path) -> None:
    """Un escenario sin Examples ejecuta 0 mutaciones: no puede aprobar."""
    ir = _ir(
        tmp_path,
        'Feature: vacuo\nScenario: sin parametros\n  Given un paso "1"\n',
    )

    failed, messages = accept_verdict(ir, _report(killed=0, survived=0))

    assert failed
    assert any("TEST-010" in message for message in messages)
    assert any("sin parametros" in message for message in messages)


def test_zero_executed_still_fails_without_vacuous_names(tmp_path: Path) -> None:
    """El fallo depende de las ejecutadas, no de la lista de vacuos.

    Un reporte incongruente con el IR (0 ejecutadas pese a tener Examples)
    igual falla citando TEST-010, pero sin nombrar escenarios.
    """
    failed, messages = accept_verdict(_ir(tmp_path, _OUTLINE), _report(killed=0, survived=0))

    assert failed
    assert any("TEST-010" in message for message in messages)
    assert all("escenarios sin Examples" not in message for message in messages)


def test_survivors_still_fail(tmp_path: Path) -> None:
    """Regresión: con trabajo ejecutado, los sobrevivientes siguen fallando."""
    failed, messages = accept_verdict(_ir(tmp_path, _OUTLINE), _report(killed=1, survived=2))

    assert failed
    assert messages == []


def test_clean_scenario_passes(tmp_path: Path) -> None:
    """El caso sano no se rompe: ejecutadas > 0 y 0 sobrevivientes pasa."""
    failed, _messages = accept_verdict(_ir(tmp_path, _OUTLINE), _report(killed=2, survived=0))

    assert not failed


def test_vacuous_scenario_listed_as_warning(tmp_path: Path) -> None:
    """Feature mixto: el vacuo se advierte en el reporte y no bloquea solo."""
    ir = _ir(
        tmp_path,
        _OUTLINE + 'Scenario: fijo\n  Given un paso "1"\n',
    )
    report = _report(killed=1, survived=0)

    failed, _messages = accept_verdict(ir, report)

    assert not failed
    assert report["vacuous"] == ["fijo"]
