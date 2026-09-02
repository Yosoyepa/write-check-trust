from collections.abc import Callable
from pathlib import Path

from tools.wct.ratchet.measure import coverage_total, measurements

# lcov con contadores conocidos por archivo: LF (statements), LH (ejecutados),
# BRF (arcos de rama) y BRH (arcos tomados). Los archivos sin ramas no llevan
# BRF/BRH (patrón de los __init__.py reales).
LCOV_KNOWN = """\
SF:pkg/one.py
DA:3,1
LF:10
LH:8
BRF:3
BRH:2
end_of_record
SF:pkg/two.py
LF:5
LH:4
end_of_record
SF:pkg/three.py
LF:2
LH:2
end_of_record
"""

# Salidas congeladas del MISMO run real (pytest --cov --cov-branch
# --cov-report=term -q -m "not property"): (LH+BRH)/(LF+BRF) = 65/67 y la
# línea TOTAL oficial, que --cov-fail-under usa como fuente.
LCOV_RUN = """\
SF:src/example/domain/inventory.py
DA:3,1
LF:13
LH:13
BRF:4
BRH:4
end_of_record
SF:src/example/entrypoints/cli.py
DA:23,0
LF:48
LH:47
BRF:2
BRH:1
end_of_record
"""

TERM_REPORT = """\
Name                             Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------------
src/example/entrypoints/cli.py      17      1      2      1    89%   23
----------------------------------------------------------------------------
TOTAL                               61      1      6      1    97%
"""


def _write_lcov(root: Path, text: str) -> None:
    artifact = root / "build/coverage/lcov.info"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(text, encoding="utf-8")


def test_measurement_parses_lcov(project_factory: Callable[..., Path]) -> None:
    """La medición suma LF/LH/BRF/BRH por archivo: (8+4+2+2)/(10+5+2+3) = 80."""
    root = project_factory()
    _write_lcov(root, LCOV_KNOWN)

    assert coverage_total(root) == 80.0
    assert measurements(root)["coverage-total"] == 80.0


def test_measurement_none_without_artifact(project_factory: Callable[..., Path]) -> None:
    """Sin lcov la métrica se abstiene: la clave no aparece en measurements()."""
    root = project_factory()

    assert coverage_total(root) is None
    assert "coverage-total" not in measurements(root)


def test_measurement_abstains_when_lcov_has_no_measurable_lines(
    project_factory: Callable[..., Path],
) -> None:
    """Un lcov sin statements ni ramas medibles no produce porcentaje."""
    root = project_factory()
    _write_lcov(root, "SF:pkg/empty.py\nend_of_record\n")
    assert coverage_total(root) is None

    # Un contador malformado se ignora: sin LF medibles sigue absteniéndose.
    _write_lcov(root, "SF:pkg/broken.py\nLF:patata\nLH:1\nend_of_record\n")
    assert coverage_total(root) is None


def test_lcov_parse_agrees_with_term_total(project_factory: Callable[..., Path]) -> None:
    """El parse del lcov y la línea TOTAL del term coinciden salvo el redondeo.

    TERM_REPORT congela la línea TOTAL oficial del mismo run que produjo
    LCOV_RUN: 97% es el número que --cov-fail-under habría comparado.
    """
    root = project_factory()
    _write_lcov(root, LCOV_RUN)

    parsed = coverage_total(root)

    assert TERM_REPORT.splitlines()[-1].strip().endswith("97%")
    assert round(parsed) == 97.0
    assert abs(parsed - 97.0) < 1.0
