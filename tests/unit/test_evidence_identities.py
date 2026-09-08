"""Contratos de SH-P01 (sh-p01/1): reconciliación pura de identidades.

La tabla I01-I18 transcribe como datos literales el expected normativo de
P01-IDENTIDADES §5: no se deriva de otra llamada al SUT ni de un helper
que reproduzca su algoritmo. I19-I22 cubren la frontera de tipos, la
inmutabilidad/determinismo con orden canónico y la opacidad de las
identidades (nodeids y Unicode sin normalizar). El test de binding coteja
la tabla literal contra las filas del feature aprobado.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from tools.wct.accept.pipeline import parse_feature
from tools.wct.evidence.identities import IdentityComparison, IdentityFinding, compare_identities

CONTRACT = "sh-p01/1"
NODEID_WITH_SPACE = "tests/unit/test_x.py::test_y[a b]"
NODEID_WITH_PARAM = "tests/unit/test_x.py::test_y[a]"
UNICODE_COMPOSED = "caso-caf\u00e9"
UNICODE_DECOMPOSED = "caso-cafe\u0301"
INVENTORY_ACRONYM = {"expected": "E", "collected": "C", "executed": "X"}
CODE_ACRONYM = {
    "empty_expected": "e",
    "empty_identity": "z",
    "duplicate_identity": "d",
    "missing_identity": "m",
    "unexpected_identity": "u",
}


def _finding(inventory: str, code: str, identity: str | None) -> IdentityFinding:
    """Hallazgo esperado, literal de la tabla del contrato."""
    return IdentityFinding(inventory=inventory, code=code, identity=identity)


def _rendered_identity(identity: str | None) -> str:
    """Identidad en la convención abreviada del feature aprobado."""
    if identity is None:
        return "None"
    if identity == "" or identity != identity.strip():
        return f'"{identity}"'
    return identity


def _rendered_findings(findings: tuple[IdentityFinding, ...]) -> str:
    """Hallazgos literales en la notación abreviada del feature."""
    if not findings:
        return "ninguna"
    return "; ".join(
        f"{INVENTORY_ACRONYM[finding.inventory]}"
        f":{CODE_ACRONYM[finding.code]}:{_rendered_identity(finding.identity)}"
        for finding in findings
    )


IDENTITY_CASES: list[tuple[Any, ...]] = [
    ("I01", ("A",), ("A",), ("A",), "match", ()),
    ("I02", ("B", "A"), ("A", "B"), ("B", "A"), "match", ()),
    (
        "I03",
        ("A", "B"),
        ("A", "C"),
        ("A", "C"),
        "mismatch",
        (
            _finding("collected", "missing_identity", "B"),
            _finding("collected", "unexpected_identity", "C"),
            _finding("executed", "missing_identity", "B"),
            _finding("executed", "unexpected_identity", "C"),
        ),
    ),
    (
        "I04",
        ("A", "B"),
        ("A",),
        ("A", "B"),
        "mismatch",
        (_finding("collected", "missing_identity", "B"),),
    ),
    (
        "I05",
        ("A", "B"),
        ("A", "B"),
        ("A",),
        "mismatch",
        (_finding("executed", "missing_identity", "B"),),
    ),
    (
        "I06",
        (),
        (),
        (),
        "empty",
        (_finding("expected", "empty_expected", None),),
    ),
    (
        "I07",
        (),
        ("A",),
        ("A",),
        "empty",
        (
            _finding("expected", "empty_expected", None),
            _finding("collected", "unexpected_identity", "A"),
            _finding("executed", "unexpected_identity", "A"),
        ),
    ),
    (
        "I08",
        ("A", "A"),
        ("A",),
        ("A",),
        "invalid",
        (_finding("expected", "duplicate_identity", "A"),),
    ),
    (
        "I09",
        ("A",),
        ("A", "A"),
        ("A",),
        "invalid",
        (_finding("collected", "duplicate_identity", "A"),),
    ),
    (
        "I10",
        ("A",),
        ("A",),
        ("A", "A"),
        "invalid",
        (_finding("executed", "duplicate_identity", "A"),),
    ),
    (
        "I11",
        ("A",),
        ("A", "B"),
        ("A",),
        "mismatch",
        (_finding("collected", "unexpected_identity", "B"),),
    ),
    (
        "I12",
        ("A",),
        ("A",),
        ("A", "B"),
        "mismatch",
        (_finding("executed", "unexpected_identity", "B"),),
    ),
    (
        "I13",
        ("A",),
        ("A", ""),
        ("A",),
        "invalid",
        (_finding("collected", "empty_identity", ""),),
    ),
    (
        "I14",
        ("",),
        ("A",),
        ("A",),
        "invalid",
        (
            _finding("expected", "empty_expected", None),
            _finding("expected", "empty_identity", ""),
            _finding("collected", "unexpected_identity", "A"),
            _finding("executed", "unexpected_identity", "A"),
        ),
    ),
    (
        "I15",
        ("A",),
        ("A", "a"),
        ("A",),
        "mismatch",
        (_finding("collected", "unexpected_identity", "a"),),
    ),
    (
        "I16",
        ("A",),
        ("A",),
        (" A",),
        "mismatch",
        (
            _finding("executed", "missing_identity", "A"),
            _finding("executed", "unexpected_identity", " A"),
        ),
    ),
    (
        "I17",
        ("A", "A", "B"),
        ("A", "", "C"),
        ("A", "A", "C"),
        "invalid",
        (
            _finding("expected", "duplicate_identity", "A"),
            _finding("collected", "empty_identity", ""),
            _finding("collected", "missing_identity", "B"),
            _finding("collected", "unexpected_identity", "C"),
            _finding("executed", "duplicate_identity", "A"),
            _finding("executed", "missing_identity", "B"),
            _finding("executed", "unexpected_identity", "C"),
        ),
    ),
    (
        "I18",
        ("A",),
        ("A",),
        ("", ""),
        "invalid",
        (
            _finding("executed", "empty_identity", ""),
            _finding("executed", "missing_identity", "A"),
        ),
    ),
]


@pytest.mark.parametrize(
    ("expected", "collected", "executed", "status", "findings"),
    [pytest.param(*case[1:], id=case[0]) for case in IDENTITY_CASES],
)
def test_identity_table_row(
    expected: tuple[str, ...],
    collected: tuple[str, ...],
    executed: tuple[str, ...],
    status: str,
    findings: tuple[IdentityFinding, ...],
) -> None:
    """Cada fila del contrato produce su estado y sus hallazgos completos."""
    result = compare_identities(expected=expected, collected=collected, executed=executed)

    assert result.status == status
    assert result.findings == findings


FIELDS = ["expected", "collected", "executed"]

NON_TUPLE_CONTAINERS = [
    pytest.param("A", id="string"),
    pytest.param(["A"], id="list"),
    pytest.param({"A"}, id="set"),
    pytest.param({"A": 1}, id="dict"),
    pytest.param(iter(("A",)), id="iterator"),
    pytest.param(None, id="none"),
    pytest.param(7, id="int"),
]


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("container", NON_TUPLE_CONTAINERS)
def test_i19_non_tuple_container_raises(field: str, container: object) -> None:
    """I19: un contenedor que no es tupla se rechaza antes del reporte."""
    arguments: dict[str, object] = {
        "expected": ("A",),
        "collected": ("A",),
        "executed": ("A",),
    }
    arguments[field] = container

    with pytest.raises(TypeError):
        compare_identities(**arguments)


NON_STRING_ELEMENTS = [
    pytest.param(None, id="none"),
    pytest.param(7, id="int"),
    pytest.param(b"A", id="bytes"),
    pytest.param(["A"], id="nested-list"),
]


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("element", NON_STRING_ELEMENTS)
def test_i20_non_string_element_raises(field: str, element: object) -> None:
    """I20: un elemento no string se rechaza en cualquier inventario."""
    arguments: dict[str, object] = {
        "expected": ("A",),
        "collected": ("A",),
        "executed": ("A",),
    }
    arguments[field] = ("A", element)

    with pytest.raises(TypeError):
        compare_identities(**arguments)


def test_i21_immutable_deterministic_canonical() -> None:
    """I21: inmutabilidad, entradas intactas, determinismo y orden canónico."""
    expected = ("Z", "A", "A", "M")
    collected = (" ", "A", "M", "Z", "Q", "")
    executed = ("Z", "M", "M", "A", "K")
    inputs_snapshot = (expected, collected, executed)

    first = compare_identities(expected=expected, collected=collected, executed=executed)
    second = compare_identities(expected=expected, collected=collected, executed=executed)

    assert first == second
    assert (expected, collected, executed) == inputs_snapshot
    assert isinstance(first.findings, tuple)
    assert first == IdentityComparison(
        "invalid",
        (
            _finding("expected", "duplicate_identity", "A"),
            _finding("collected", "empty_identity", ""),
            _finding("collected", "unexpected_identity", " "),
            _finding("collected", "unexpected_identity", "Q"),
            _finding("executed", "duplicate_identity", "M"),
            _finding("executed", "unexpected_identity", "K"),
        ),
    )
    with pytest.raises(FrozenInstanceError):
        first.status = "match"
    with pytest.raises(FrozenInstanceError):
        first.findings[0].inventory = "collected"


def test_i21b_canonical_order_with_repeated_ids() -> None:
    """I21b (R1/R02): orden canónico con duplicados múltiples y entradas permutadas.

    Expected literal independiente del SUT: dos o más identidades duplicadas
    en cada inventario y múltiples missing/unexpected del mismo código. La
    permutación de las entradas no puede cambiar la salida completa.
    """
    expected = ("B", "A", "B", "A")
    collected = ("Z", "Y", "A", "B", "Z", "Y", "")
    executed = ("D", "C", "D", "C")
    literal = IdentityComparison(
        "invalid",
        (
            _finding("expected", "duplicate_identity", "A"),
            _finding("expected", "duplicate_identity", "B"),
            _finding("collected", "empty_identity", ""),
            _finding("collected", "duplicate_identity", "Y"),
            _finding("collected", "duplicate_identity", "Z"),
            _finding("collected", "unexpected_identity", "Y"),
            _finding("collected", "unexpected_identity", "Z"),
            _finding("executed", "duplicate_identity", "C"),
            _finding("executed", "duplicate_identity", "D"),
            _finding("executed", "missing_identity", "A"),
            _finding("executed", "missing_identity", "B"),
            _finding("executed", "unexpected_identity", "C"),
            _finding("executed", "unexpected_identity", "D"),
        ),
    )

    direct = compare_identities(expected=expected, collected=collected, executed=executed)
    permuted = compare_identities(
        expected=("A", "B", "A", "B"),
        collected=("", "Y", "Z", "B", "A", "Y", "Z"),
        executed=("C", "C", "D", "D"),
    )

    assert direct == literal
    assert permuted == literal


def test_i22_identity_opacity() -> None:
    """I22: igualdad exacta de strings; sin normalizar nodeids ni Unicode."""
    assert UNICODE_COMPOSED != UNICODE_DECOMPOSED

    nodeid_control = compare_identities(
        expected=(NODEID_WITH_SPACE,),
        collected=(NODEID_WITH_SPACE,),
        executed=(NODEID_WITH_SPACE,),
    )
    assert (nodeid_control.status, nodeid_control.findings) == ("match", ())

    nodeid_substituted = compare_identities(
        expected=(NODEID_WITH_SPACE,),
        collected=(NODEID_WITH_PARAM,),
        executed=(NODEID_WITH_SPACE,),
    )
    assert nodeid_substituted == IdentityComparison(
        "mismatch",
        (
            _finding("collected", "missing_identity", NODEID_WITH_SPACE),
            _finding("collected", "unexpected_identity", NODEID_WITH_PARAM),
        ),
    )

    both_retained = compare_identities(
        expected=(NODEID_WITH_SPACE, NODEID_WITH_PARAM),
        collected=(NODEID_WITH_SPACE, NODEID_WITH_PARAM),
        executed=(NODEID_WITH_PARAM, NODEID_WITH_SPACE),
    )
    assert (both_retained.status, both_retained.findings) == ("match", ())

    unicode_control = compare_identities(
        expected=(UNICODE_COMPOSED,),
        collected=(UNICODE_COMPOSED,),
        executed=(UNICODE_COMPOSED,),
    )
    assert (unicode_control.status, unicode_control.findings) == ("match", ())

    unicode_substituted = compare_identities(
        expected=(UNICODE_COMPOSED,),
        collected=(UNICODE_DECOMPOSED,),
        executed=(UNICODE_COMPOSED,),
    )
    assert unicode_substituted == IdentityComparison(
        "mismatch",
        (
            _finding("collected", "missing_identity", UNICODE_COMPOSED),
            _finding("collected", "unexpected_identity", UNICODE_DECOMPOSED),
        ),
    )


APPROVED_FEATURE = Path(__file__).parents[2] / "features" / "wct-evidence-identities-001.feature"
DUPLICATED_I01_ROW = "      | I01 | sh-p01/1 | match | ninguna |\n"
EXTRA_OUTLINE = (
    "\n  Scenario Outline: Escenario intruso\n"
    '    Given los inventarios del caso "<caso>" fijados por el contrato "<contrato>"\n'
    "    When comparo expected collected y executed con la API productiva\n"
    '    Then el estado de identidad es "<estado>"\n'
    '    And las findings completas corresponden a "<hallazgos>"\n'
    "    Examples:\n"
    "      | caso | contrato | estado | hallazgos |\n"
    "      | I01 | sh-p01/1 | match | ninguna |\n"
)


def _bound_rows(ir: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Vincula el inventario contratado tras validar cardinalidad y unicidad.

    Rechaza IRs con escenarios distintos del Scenario Outline contratado y
    filas con caso repetido, desconocido o faltante, antes de indexar por ID.

    Args:
        ir: IR producido por el parser productivo.

    Returns:
        Las filas indexadas por caso, solo si el inventario es exacto.

    Raises:
        ValueError: si el inventario de escenarios o de filas no es el
            contratado.
    """
    scenarios = ir["scenarios"]
    if len(scenarios) != 1:
        raise ValueError(f"se esperaba 1 Scenario Outline contratado, hay {len(scenarios)}")
    rows = scenarios[0]["examples"]
    cases = [row["caso"] for row in rows]
    if len(cases) != len(IDENTITY_CASES):
        raise ValueError(f"se esperaban {len(IDENTITY_CASES)} filas, hay {len(cases)}")
    if len(set(cases)) != len(cases):
        raise ValueError("fila con caso repetido en el feature")
    if set(cases) != {case[0] for case in IDENTITY_CASES}:
        raise ValueError("los casos del feature no son la tabla contratada")
    return dict(zip(cases, rows, strict=True))


def _parsed_variant(tmp_path: Path, transform: Callable[[str], str]) -> dict[str, Any]:
    """Parsea con el parser productivo una variante de solo lectura del feature."""
    variant = tmp_path / "variante.feature"
    variant.write_text(transform(APPROVED_FEATURE.read_text(encoding="utf-8")), encoding="utf-8")
    return parse_feature(variant)


def test_feature_rows_bind_to_literal_table() -> None:
    """Las filas del feature aprobado son la tabla literal, fila a fila."""
    ir = parse_feature(APPROVED_FEATURE)
    rows = _bound_rows(ir)

    assert ir["feature"] == "Reconciliacion no vacua de identidades de evidencia"
    assert len(ir["scenarios"]) == 1
    assert ir["scenarios"][0]["name"] == (
        "Cada inventario conserva sus obligaciones y sus defectos"
    )
    for case_id, _expected, _collected, _executed, status, findings in IDENTITY_CASES:
        assert rows[case_id]["contrato"] == CONTRACT
        assert rows[case_id]["estado"] == status
        assert rows[case_id]["hallazgos"] == _rendered_findings(findings)


def test_binding_rejects_duplicated_case(tmp_path: Path) -> None:
    """Negativo R1/R03: una fila I01 repetida rompe la cardinalidad contratada."""
    ir = _parsed_variant(
        tmp_path,
        lambda text: text.replace(DUPLICATED_I01_ROW, DUPLICATED_I01_ROW + DUPLICATED_I01_ROW),
    )

    with pytest.raises(ValueError, match="filas"):
        _bound_rows(ir)


def test_binding_rejects_duplicate_ids_same_cardinality(tmp_path: Path) -> None:
    """Negativo R1/R03: dos filas I01 a igual cardinalidad violan la unicidad."""
    ir = _parsed_variant(
        tmp_path,
        lambda text: text.replace(
            "      | I02 | sh-p01/1 | match | ninguna |\n", DUPLICATED_I01_ROW
        ),
    )

    with pytest.raises(ValueError, match="repetido"):
        _bound_rows(ir)


def test_binding_rejects_extra_scenario(tmp_path: Path) -> None:
    """Negativo R1/R03: un Scenario Outline extra viola el inventario contratado."""
    ir = _parsed_variant(tmp_path, lambda text: text + EXTRA_OUTLINE)

    with pytest.raises(ValueError, match="Scenario Outline"):
        _bound_rows(ir)
