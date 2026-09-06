"""Contrato del ratchet exigible (ADR-G3a-02) y regresión del escape #37/#38.

La regresión usa las funciones PRODUCTIVAS del ratchet — ``measurements``,
``baseline`` y ``compare`` — sobre el propio repo: ningún segundo umbral
hardcodeado, para que un ``ratchet record`` humano futuro no invalide la
regresión (ADR-G3a-01). El control defectuoso emparejado planta UN test
introverted en un fixture y exige que el MISMO ``check`` productivo lo
reporte: sin él, un ``measurements`` roto que siempre retornara 0 pasaría
la regresión repo-pineada.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shlex

import pytest

from tools.wct.cli import main
from tools.wct.gate.checks import coverage_total_command
from tools.wct.ratchet.engine import baseline, compare
from tools.wct.ratchet.measure import _COVERAGE_TOTAL_COMMAND, check, measurements

REPO_ROOT = Path(__file__).resolve().parents[2]

# Un test deliberadamente introverted: aserciones que no trazan a ningún SUT.
INTROVERTED_TEST = "def test_siempre_verde() -> None:\n    assert 'wct' in 'wct template'\n"

LCOV_AT_BASELINE = "SF:pkg/en_piso.py\nLF:200\nLH:149\nend_of_record\n"
LCOV_BELOW_BASELINE = "SF:pkg/por_debajo.py\nLF:200\nLH:100\nend_of_record\n"


def _write_lcov(root: Path, text: str) -> None:
    artifact = root / "build/coverage/lcov.info"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(text, encoding="utf-8")


def test_repo_introverted_ratchet_holds_baseline() -> None:
    """Regresión del escape: la medición productiva del repo no supera su baseline.

    ADR-G3a-01: el invariario vive en la suite que CI ejecuta. Usa
    ``measurements`` + ``baseline`` + ``compare`` productivos sobre el repo,
    SIN un segundo umbral 0 hardcodeado: si el humano sube el baseline con
    ``ratchet record``, este test lo sigue.
    """
    current = measurements(REPO_ROOT)["introverted-tests"]
    expected = baseline(REPO_ROOT, "introverted-tests")

    assert compare(current, expected), (
        f"introverted-tests: actual={current:g}, baseline={expected['value']}"
    )


def test_defective_control_introverted_detected(
    project_factory: Callable[..., Path],
) -> None:
    """Control negativo emparejado: UN introverted en fixture → check() lo reporta.

    Especificidad del detector: el ``check`` productivo (tolerante) compara
    la medición del fixture contra SU baseline en 0 y falla nombrando la
    métrica. Un ``measurements`` que siempre retornara 0 pasaría la
    regresión repo-pineada pero NO este control.
    """
    root = project_factory()
    (root / "tests" / "test_introverted.py").write_text(INTROVERTED_TEST, encoding="utf-8")

    failures = check(root)

    assert "introverted-tests: actual=1, baseline=0" in failures


def test_require_does_not_silence_other_ratchets(
    project_factory: Callable[..., Path],
) -> None:
    """Exigir es ADITIVO: el rojo de una métrica NO exigida sobrevive (H2).

    Reproducción del hallazgo 2: introverted-tests=1 sobre baseline 0 con
    ``required=["suppressions"]``. El modo exigible conserva TODAS las
    comparaciones del modo tolerante — el fallo de introverted-tests sigue
    en el reporte, línea por línea: exigir añade obligaciones de presencia,
    jamás filtra ni apaga rojos existentes.
    """
    root = project_factory()
    (root / "tests" / "test_introverted.py").write_text(INTROVERTED_TEST, encoding="utf-8")

    tolerant = check(root)
    report = check(root, required=["suppressions"])

    assert "introverted-tests: actual=1, baseline=0" in report.failures
    assert report.failures == tolerant, report.failures


def test_invalid_lcov_counters_block_in_require_mode(
    project_factory: Callable[..., Path],
) -> None:
    """Medición inválida bloquea (H1): un LCOV imposible no compra verde.

    Variantes del hallazgo 1: LH sobre LF (200% imposible), BRH sobre BRF,
    totales en cero y resultado fuera de [0, 100]. Cada defecto bloquea con
    UNA línea de INVÁLIDA nombrando el defecto y su registro — distinta del
    texto de ausencia y del de umbral, sin comparación de umbral sobre un
    valor imposible. Los bordes válidos (100% y 0%) NO son defecto: se miden
    y se comparan contra el baseline. El modo tolerante no hereda la
    validación (byte-compat).
    """
    root = project_factory()
    invalid = {
        "SF:pkg/imposible.py\nLF:1\nLH:2\nend_of_record\n": (
            "coverage-total: medición inválida (total 200% fuera de [0, 100])"
        ),
        "SF:pkg/diluido.py\nLF:100\nLH:0\nend_of_record\n"
        "SF:pkg/imposible.py\nLF:1\nLH:2\nend_of_record\n": (
            "coverage-total: medición inválida (LH 2 > LF 1 en pkg/imposible.py)"
        ),
        "SF:pkg/rama.py\nLF:10\nLH:5\nBRF:1\nBRH:3\nend_of_record\n": (
            "coverage-total: medición inválida (BRH 3 > BRF 1 en pkg/rama.py)"
        ),
        "SF:pkg/vacio.py\nLF:0\nLH:0\nend_of_record\n": (
            "coverage-total: medición inválida (LF+BRF == 0 en todos los registros)"
        ),
    }
    for lcov, failure in invalid.items():
        _write_lcov(root, lcov)
        report = check(root, required=["coverage-total"])
        assert report.failures == [failure], (failure, report.failures)

    _write_lcov(root, "SF:pkg/completo.py\nLF:1\nLH:1\nend_of_record\n")
    assert check(root, required=["coverage-total"]).failures == []

    _write_lcov(root, "SF:pkg/nada.py\nLF:2\nLH:0\nend_of_record\n")
    nothing = check(root, required=["coverage-total"])
    assert nothing.failures == ["coverage-total: actual=0, baseline=74.5"]

    _write_lcov(root, "SF:pkg/imposible.py\nLF:1\nLH:2\nend_of_record\n")
    assert check(root) == [], "el modo tolerante no hereda la validación (byte-compat)"


def test_malformed_counters_block_in_require_mode(
    project_factory: Callable[..., Path],
) -> None:
    r"""Contadores malformados bloquean la vía exigible (0e): la regex histórica ignora.

    ``LF:-1`` NO matchea ``\\d+``: el renglón se ignora, el registro queda
    "vacío-coherente" y el validador retornaba None — verde falso pese al
    registro corrupto. La vía exigible rechaza renglones con nombre de
    contador reconocido y valor que no es entero no-negativo, nombrando el
    contador y su SF. Variantes: ``LF:-1``, ``LF:1.5``, ``LF:`` vacío. El
    modo tolerante conserva su parser histórico (byte-compat).
    """
    root = project_factory()
    valid = "SF:pkg/ok.py\nLF:1\nLH:1\nend_of_record\n"
    invalid = {
        f"{valid}SF:pkg/bad.py\nLF:-1\nLH:-2\nend_of_record\n": "contador LF:-1 en pkg/bad.py",
        f"{valid}SF:pkg/decimal.py\nLF:1.5\nend_of_record\n": "contador LF:1.5 en pkg/decimal.py",
        f"{valid}SF:pkg/vacio.py\nLF:\nend_of_record\n": "contador LF: en pkg/vacio.py",
    }
    for lcov, defect in invalid.items():
        _write_lcov(root, lcov)
        report = check(root, required=["coverage-total"])
        assert report.failures == [f"coverage-total: medición inválida ({defect})"], (
            defect,
            report.failures,
        )

    _write_lcov(root, next(iter(invalid)))
    assert check(root) == [], "el modo tolerante conserva su parser histórico (byte-compat)"


def test_incomplete_counters_block_without_traceback(
    project_factory: Callable[..., Path],
) -> None:
    """Cubiertas sin su total bloquean SIN traceback (0g): LF ausente no es 0.

    Reproducción del 3er hallazgo: ``_record_defect`` compara con
    ``.get(..., 0)`` pero el mensaje accedía ``record['LF']``/``record['BRF']``
    — con un registro VÁLIDO que diluye el total (LF:10/LH:5) el rango no se
    dispara y el registro INCOMPLETO (``LH:1`` sin ``LF``, ``BRH:1`` sin
    ``BRF``) tomaba la rama LH>LF lanzando KeyError en vez de medición
    inválida. El exigible nombra la clave ausente con los valores presentes.
    El ancla verde — ``LF`` sin ``LH`` — prueba que la completitud NO se
    amplió: es un registro válido (0 cubiertas de N) que se mide. El modo
    tolerante mide el mismo artefacto sin heredar la validación.
    """
    root = project_factory()
    dilutes = "SF:pkg/diluye.py\nLF:10\nLH:5\nend_of_record\n"
    incomplete = {
        f"{dilutes}SF:pkg/sin_total.py\nLH:1\nend_of_record\n": (
            "coverage-total: medición inválida (LH 1 sin LF en pkg/sin_total.py)"
        ),
        f"{dilutes}SF:pkg/rama_sin_total.py\nBRH:1\nend_of_record\n": (
            "coverage-total: medición inválida (BRH 1 sin BRF en pkg/rama_sin_total.py)"
        ),
    }
    for lcov, failure in incomplete.items():
        _write_lcov(root, lcov)
        report = check(root, required=["coverage-total"])
        assert report.failures == [failure], (failure, report.failures)

    _write_lcov(
        root,
        "SF:pkg/completo.py\nLF:10\nLH:10\nend_of_record\n"
        "SF:pkg/sin_cubiertas.py\nLF:2\nend_of_record\n",
    )
    measured = check(root, required=["coverage-total"])
    assert measured.failures == [], measured.failures
    assert "medidas 1 de 1 exigibles" in measured.summary

    _write_lcov(root, next(iter(incomplete)))
    assert check(root) == ["coverage-total: actual=60, baseline=74.5"], (
        "el modo tolerante mide el artefacto mixto sin heredar la validación"
    )


def test_coverage_producer_command_matches_gate_recipe() -> None:
    """El comando productor mostrado es shell-correcto y alinea con el gate (0c/0f).

    ``shlex.split`` del comando MOSTRADO reproduce los límites de argumento
    reales: ``-m "not property"`` debe quedar como UN solo argumento — sin
    comillas, la shell lo partiría en dos y el ``-m`` recibiría ``not``. La
    comparación es contra la LISTA del builder productivo
    (``coverage_total_command``, checks.py) sin el par ``--cov-fail-under
    <piso>`` — el productor mide, no enforcement — y SIN aplanar con
    ``.split()``: aplanar escondería justamente los límites de argumento que
    este test verifica.
    """
    recipe = coverage_total_command(REPO_ROOT)
    assert recipe is not None
    floor = recipe.index("--cov-fail-under")

    producer = shlex.split(_COVERAGE_TOTAL_COMMAND)

    assert producer == recipe[:floor] + recipe[floor + 2 :]


def test_green_denominator_n_of_n_with_multiple(
    project_factory: Callable[..., Path],
) -> None:
    """Verde exigible N-de-N con N≥2: el denominador cuenta lo medido (0d).

    Dos métricas medidas y en baseline: cero bloqueos y un resumen que
    declara ``medidas 2 de 2 exigibles`` — un verde siempre dice qué midió.
    """
    root = project_factory()

    report = check(root, required=["suppressions", "debt-markers"])

    assert report.failures == [], report.failures
    assert "medidas 2 de 2 exigibles" in report.summary


def test_require_rejects_empty_unknown_and_duplicated(
    project_factory: Callable[..., Path],
) -> None:
    """Entrada validada (ADR-G3a-02 §1): vacío, desconocido y duplicado son error.

    Los duplicados NO se colapsan en silencio: un typo duplicado debe verse.
    Todo error nombra los nombres válidos del inventario.
    """
    root = project_factory()

    with pytest.raises(ValueError, match="vacío") as empty_list:
        check(root, required=[])
    assert "coverage-total" in str(empty_list.value)
    with pytest.raises(ValueError, match="vacío") as blank_token:
        check(root, required=[""])
    assert "docstring-coverage" in str(blank_token.value)

    with pytest.raises(ValueError, match="desconocido") as unknown:
        check(root, required=["metrica-inventada"])
    assert "introverted-tests" in str(unknown.value)

    with pytest.raises(ValueError, match="duplicado"):
        check(root, required=["suppressions", "suppressions"])


def test_require_blocks_missing_naming_metric_and_command(
    project_factory: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exigible ausente bloquea nombrando métrica, causa y comando (ADR §3/§4).

    coverage-total sin artefacto LCOV y docstring-coverage con interrogate
    ausente del PATH (simulado): el fallo distingue la causa y sugiere el
    comando que produce la medición.
    """
    root = project_factory()
    monkeypatch.setattr("tools.wct.ratchet.measure.shutil.which", lambda _name: None)

    report = check(root, required=["coverage-total", "docstring-coverage"])

    assert len(report.failures) == 2, report.failures
    missing = "\n".join(report.failures)
    assert "coverage-total: exigible no medida" in missing
    assert "no existe build/coverage/lcov.info" in missing
    assert "--cov-report=lcov:build/coverage/lcov.info" in missing
    assert "docstring-coverage: exigible no medida" in missing
    assert "interrogate no está instalado" in missing
    assert "interrogate src" in missing


def test_require_presence_is_not_threshold(
    project_factory: Callable[..., Path],
) -> None:
    """Presencia ≠ umbral (ADR-G3a-02 §4): dos comprobaciones independientes.

    Fronteras: presente y exactamente en el baseline (verde), presente y por
    debajo del piso (rojo por umbral, texto con actual=/baseline=), y
    ausente (rojo por presencia, texto distinto al de umbral).
    """
    root = project_factory()

    _write_lcov(root, LCOV_AT_BASELINE)
    at_baseline = check(root, required=["coverage-total"])
    assert at_baseline.failures == [], at_baseline.failures

    _write_lcov(root, LCOV_BELOW_BASELINE)
    over = check(root, required=["coverage-total"])
    assert over.failures == ["coverage-total: actual=50, baseline=74.5"], over.failures

    (root / "build/coverage/lcov.info").unlink()
    absent = check(root, required=["coverage-total"])
    assert len(absent.failures) == 1, absent.failures
    assert absent.failures[0] != over.failures[0]
    assert "exigible no medida" in absent.failures[0]


def test_require_all_uses_explicit_inventory(
    project_factory: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``all`` exige el inventario de código, no lo medido (ADR-G3a-02 §2).

    El fixture mide las 8 estáticas pero no coverage-total (sin LCOV) ni
    docstring-coverage (interrogate ausente del PATH): exigir ``all``
    bloquea por ausencia — nunca éxito por omisión — y el denominador
    declara 8 de 10.
    """
    root = project_factory()
    monkeypatch.setattr("tools.wct.ratchet.measure.shutil.which", lambda _name: None)

    report = check(root, required=["all"])

    assert len(report.failures) == 2, report.failures
    missing = "\n".join(report.failures)
    assert "coverage-total: exigible no medida" in missing
    assert "docstring-coverage: exigible no medida" in missing
    assert "medidas 8 de 10 exigibles" in report.summary


def test_require_publishes_names_and_denominator(
    project_factory: Callable[..., Path],
) -> None:
    """El exigible publica exigidas, medidas y ``medidas N de M`` (ADR §5)."""
    root = project_factory()

    report = check(root, required=["suppressions", "coverage-total"])

    assert "exigidas: suppressions, coverage-total" in report.summary
    assert "medidas: suppressions" in report.summary
    assert "medidas 1 de 2 exigibles" in report.summary


def test_without_require_output_unchanged(
    project_factory: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Sin ``--require`` la salida es byte-compatible con la actual (ADR §8)."""
    root = project_factory()
    (root / "tests" / "test_introverted.py").write_text(INTROVERTED_TEST, encoding="utf-8")
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(root))

    exit_code = main(["ratchet", "check"])
    output = capsys.readouterr().out

    failures = check(root)
    assert exit_code == bool(failures)
    expected = "\n".join(failures) if failures else "Todos los ratchets se mantienen."
    assert output == f"{expected}\n"
    assert "exigibles" not in output
