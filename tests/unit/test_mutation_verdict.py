"""Clasificación y precedencia del inventario del motor (G1a, ADR-G1-01).

La tabla de ADR-G1-01 es la única verdad del comportamiento: estos tests la
alinean estado por estado contra ``classify_inventory``, la función pura que
traduce el inventario de ``mutmut results --all true`` a un ``GateResult``.
No corren el motor — los controles con motor real viven en
``test_gate_mutation.py`` (sano, timeout, inyección) y el CLI por subprocess
en ``test_mutation_cli.py`` (RG09).
"""

from __future__ import annotations

import pytest

from tools.wct.model import Status
from tools.wct.mutate.verdict import classify_inventory

# ADR-G1-01: 1 estado aprobado, 2 defectuosos, 7 fuera del contrato de
# certificación. El vocabulario es el de mutmut 3.7.0 (__main__.py:82-104).
STATE_TABLE = [
    ("killed", Status.PASS, "clasificación del motor"),
    ("survived", Status.FAIL, "criterio de mutación incumplido"),
    ("no tests", Status.FAIL, "criterio de mutación incumplido"),
    ("timeout", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("suspicious", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("not checked", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("check was interrupted by user", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("segfault", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("skipped", Status.ERROR, "fuera del contrato de certificación WCT"),
    ("caught by type check", Status.ERROR, "fuera del contrato de certificación WCT"),
]


@pytest.mark.parametrize(("state", "expected", "cause"), STATE_TABLE)
def test_classification_table(state: str, expected: Status, cause: str) -> None:
    """Cada estado del vocabulario produce el veredicto y la causa de la tabla."""
    result = classify_inventory(f"    victim.calc.x_add__mutmut_1: {state}\n")

    assert result.status is expected
    assert cause in result.summary


def test_duplicate_identity_and_unknown_line_error() -> None:
    """Renglón inválido (ID duplicado, estado fuera de vocabulario, truncado) → ERROR.

    Un inventario malformado es evidencia inválida: el gate no puede
    certificar sobre identidades que no puede contar (RG04).
    """
    inventory = (
        "    victim.calc.x_add__mutmut_1: killed\n"
        "    victim.calc.x_add__mutmut_1: killed\n"
        "    victim.calc.x_add__mutmut_2: jubilado\n"
        "    victim.calc.x_add__mutmut_3 renglón truncado\n"
    )

    result = classify_inventory(inventory)

    assert result.status is Status.ERROR
    assert "evidencia inválida (fase clasificación)" in result.summary
    assert any("identidad duplicada" in line for line in result.details)
    assert any("estado fuera de vocabulario" in line for line in result.details)
    assert any("renglón desconocido" in line for line in result.details)


def test_empty_inventory_is_error() -> None:
    """Inventario legible y VACÍO donde se exige trabajo → ERROR fase inventario (M02)."""
    result = classify_inventory("")

    assert result.status is Status.ERROR
    assert "no acreditado (fase inventario)" in result.summary
    assert "0 mutantes" in result.summary
    assert "fase: inventario" in result.details


def test_mixed_survived_and_timeout_error_preserves_findings() -> None:
    """Survived + timeout: ERROR prioritario sin esconder las identidades FAIL (RG03).

    La precedencia ERROR>FAIL de ADR-G1-01 exige que el veredicto sea ERROR
    por los estados fuera del contrato Y que las identidades de los
    sobrevivientes sigan en details: el hallazgo de producto no desaparece
    porque el instrumento se rompiera.
    """
    inventory = (
        "    victim.billing.x_total__mutmut_1: survived\n"
        "    victim.billing.x_total__mutmut_2: survived\n"
        "    victim.countdown.x_countdown__mutmut_1: timeout\n"
        "    victim.countdown.x_countdown__mutmut_2: timeout\n"
    )

    result = classify_inventory(inventory)

    assert result.status is Status.ERROR
    assert "fuera del contrato de certificación WCT" in result.summary
    identities = [line for line in result.details if line.startswith("identidades:")]
    assert any(": survived" in line for line in identities)
    assert any(": timeout" in line for line in identities)
