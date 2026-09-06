"""Contrato del workflow quality.yml (G3a-2).

La suite pinea lo que la CI ejecuta: el productor de cobertura sigue la
receta productiva (sin property, TEST-008), el consumidor exigible corre
inmediatamente después con su comando COMPLETO y de forma incondicional
—sin `if` ni `continue-on-error`—, y los property conservan una ejecución
propia. Las aserciones estructurales que pasan sobre el workflow real
llevan controles defectuosos derivados de pasos REALES que demuestran que
detectan el defecto que vigilan (incluidas las mutaciones de la revisión
pre-bless: consumidor sustituido por eco, desactivado, condicionado a
``failure()``).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import re
import shlex
from typing import Any

import yaml

from tools.wct.ratchet.measure import (
    _COVERAGE_TOTAL_COMMAND,
    LCOV_ARTIFACT,
    REQUIRED_INVENTORY,
    check,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "quality.yml"
PRODUCER = "Generate branch coverage"
CONSUMER = "Require measured ratchets"
PROPERTY_STEP = "Run property tests separately"

# LCOVs válidos a ambos lados del baseline coverage-total del fixture (74.5).
LCOV_BELOW_BASELINE = "SF:pkg/debajo.py\nLF:200\nLH:100\nend_of_record\n"
LCOV_OVER_BASELINE = "SF:pkg/encima.py\nLF:100\nLH:90\nend_of_record\n"


def _document() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps() -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = _document()["jobs"]["commit-gates"]["steps"]
    return steps


def _job() -> dict[str, Any]:
    job: dict[str, Any] = _document()["jobs"]["commit-gates"]
    return job


def _named(steps: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return next(step for step in steps if step.get("name") == name)


def _positions(steps: list[dict[str, Any]]) -> dict[str, int]:
    return {step["name"]: index for index, step in enumerate(steps) if "name" in step}


def _is_bare_run_step(step: dict[str, Any]) -> bool:
    """True si el paso es exactamente ``{name, run}`` — nada más.

    Allowlist terminal (hallazgo MAYOR de la tercera verificación):
    cualquier clave extra rompe el contrato — ``if`` desactiva o
    condiciona (``failure()`` ejecuta SOLO tras fallos), un
    ``continue-on-error`` perdona, un ``shell`` neutralizador hace
    triunfar el comando sin ejecutarlo, y ``env``/``working-directory``/
    ``timeout-minutes`` son superficie no contratada. El diff aprobado
    define los tres pasos como nombre y comando, exactamente.
    """
    return set(step) == {"name", "run"}


def _job_executes_normally(job: dict[str, Any]) -> bool:
    """True si el job corre incondicional y con su shell de confianza.

    Nivel job (hallazgo MAYOR-1 de la segunda verificación): ``if``
    desactiva el job entero —consumidor incluido—, ``continue-on-error``
    perdona el fallo de TODO el job, un ``defaults.run.shell`` custom
    puede hacer que cada ``run`` triunfe sin ejecutar nada, un
    ``strategy.matrix`` vacío salta el job completo, y un ``needs`` hacia
    un job que no corre lo salta en cascada (MINOR-B de la ronda 4).
    """
    if "if" in job or "needs" in job or "strategy" in job or job.get("continue-on-error"):
        return False
    return "shell" not in job.get("defaults", {}).get("run", {})


def _produced_artifact(run: str) -> Path:
    """Ruta del LCOV que un comando de cobertura declara producir."""
    target = re.search(r"--cov-report=lcov:([^ ]+)", run)
    assert target is not None, f"el comando no declara un destino lcov: {run}"
    return Path(target.group(1))


def _required_names(run: str) -> list[str]:
    """Nombres que un comando ``--require`` exige, parseados con shlex."""
    tokens = shlex.split(run)
    return tokens[tokens.index("--require") + 1].split(",")


def _write_lcov(root: Path, text: str) -> None:
    artifact = root / LCOV_ARTIFACT
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(text, encoding="utf-8")


def test_coverage_step_matches_productive_recipe() -> None:
    """El productor del workflow ES la receta productiva, lanzador aparte.

    El comando de CI lleva el prefijo ``uv run`` que la constante productiva
    no tiene: lanzador y argumentos se comparan por separado, token a token
    vía shlex, y ``"not property"`` sobrevive como un único token citado
    (un ``.split()`` ingenuo que lo aplanara no puede igualar la receta).
    """
    tokens = shlex.split(_named(_steps(), PRODUCER)["run"])

    assert tokens[:2] == ["uv", "run"]
    assert tokens[2:] == shlex.split(_COVERAGE_TOTAL_COMMAND)


def test_required_ratchets_step_follows_producer() -> None:
    """El consumidor exigible existe, va tras el productor y no se perdona.

    La frescura del artefacto es el orden de pasos del job: productor y
    consumidor en la MISMA corrida, ADYACENTES — sin restauración
    intermedia (un paso forjador insertado entre ambos no cabe: ronda 4
    del verifier). El comando se pina COMPLETO con shlex — un eco que
    repita los nombres exigidos sin ejecutar WCT no puede pasar
    (hallazgo 1 de la revisión pre-bless) — y la lista se valida contra
    el inventario productivo: CI solo puede exigir ratchets que existen.
    """
    steps = _steps()
    positions = _positions(steps)
    consumer = _named(steps, CONSUMER)
    names = _required_names(consumer["run"])

    assert positions[CONSUMER] == positions[PRODUCER] + 1
    assert shlex.split(consumer["run"]) == [
        "uv",
        "run",
        "wct",
        "ratchet",
        "check",
        "--require",
        "coverage-total,docstring-coverage",
    ]
    assert names == ["coverage-total", "docstring-coverage"]
    assert set(names) <= set(REQUIRED_INVENTORY)
    assert _is_bare_run_step(consumer)


def test_property_tests_run_separately() -> None:
    """Property pierde su lugar en coverage y gana un paso propio (R03).

    G-TEST (commit) solo corre unit+integration sin property: sin este
    paso, la batería property dejaría de ejecutarse en CI. El paso existe
    POR la exclusión de la receta productiva — si esa marca cambiara, este
    test lo delata junto con T1.
    """
    steps = _steps()
    positions = _positions(steps)

    tokens = shlex.split(_named(steps, PROPERTY_STEP)["run"])
    assert tokens[:2] == ["uv", "run"]
    assert tokens[2:] == ["pytest", "-q", "tests/property"]
    assert positions[PROPERTY_STEP] > positions[CONSUMER]

    recipe = shlex.split(_COVERAGE_TOTAL_COMMAND)
    coverage = shlex.split(_named(steps, PRODUCER)["run"])
    marker = recipe[recipe.index("-m") + 1]
    assert coverage[coverage.index("-m") + 1] == marker


def test_contracted_steps_execute_normally() -> None:
    """Los pasos del contrato son exactamente {name, run} (escenario 3).

    Allowlist terminal (hallazgo MAYOR de la tercera verificación): el
    diff aprobado define productor, consumidor y property como nombre y
    comando, NADA más. Así un productor fallido detiene el job ANTES del
    consumidor, el consumidor no queda desactivado (``if: false``), ni
    condicionado a fallos ajenos (``failure()``), ni perdonado
    (``continue-on-error``), ni neutralizado por un ``shell`` que triunfa
    sin ejecutar. La identidad del productor es productiva — es el paso
    que escribe el artefacto del ratchet. Sin intérprete de expresiones
    de Actions: cualquier clave extra rompe el contrato, no hace falta
    interpretarla.
    """
    producer = _named(_steps(), PRODUCER)

    assert _produced_artifact(producer["run"]) == LCOV_ARTIFACT
    assert _is_bare_run_step(producer)
    assert _is_bare_run_step(_named(_steps(), CONSUMER))
    assert _is_bare_run_step(_named(_steps(), PROPERTY_STEP))


def test_commit_gates_job_executes_normally() -> None:
    """El job commit-gates corre en push/PR, sin perdón ni shell neutralizado.

    La vigilancia de nivel paso no ve el nivel job: `if: false` aquí
    desactiva TODO el job —consumidor exigible incluido—, un
    `continue-on-error` aquí perdona el fallo entero, y un
    `defaults.run.shell` custom puede triunfar cada `run` sin ejecutar
    nada (hallazgo MAYOR-1 de la segunda verificación, misma clase que
    los hallazgos humanos, un nivel arriba).
    """
    document = _document()
    job = document["jobs"]["commit-gates"]
    consumer = _named(job["steps"], CONSUMER)

    assert set(_required_names(consumer["run"])) <= set(REQUIRED_INVENTORY)
    assert _job_executes_normally(job)
    assert "defaults" not in document, "defaults a nivel workflow hereda a todos los jobs"
    triggers = document.get("on") or document.get(True)
    assert {"pull_request", "push"} <= set(triggers)


def test_defective_step_mutations_are_detected() -> None:
    """Control defectuoso: las mutaciones de la revisión pre-bless se rechazan.

    Todas derivadas de pasos REALES del workflow: el eco repite los
    nombres exigidos sin ejecutar WCT (burlaba la verificación de
    nombres — hallazgo 1), ``if: false`` desactiva y ``failure()``
    condiciona a fallos ajenos (burlaban la vigilancia de perdones —
    hallazgo 2), el productor perdonado sobrevive a su propio fallo, y
    el ``shell`` neutralizador del paso hace triunfar el comando pineado
    sin ejecutarlo (MAYOR de la tercera verificación). La allowlist
    ``{name, run}`` las rechaza a todas — y a cualquiera que venga.
    """
    producer = _named(_steps(), PRODUCER)
    consumer = _named(_steps(), CONSUMER)
    contracted = shlex.split(consumer["run"])

    assert set(_required_names(consumer["run"])) <= set(REQUIRED_INVENTORY)
    echoed = {**consumer, "run": "uv run echo --require coverage-total,docstring-coverage"}
    assert _required_names(echoed["run"]) == ["coverage-total", "docstring-coverage"]
    assert shlex.split(echoed["run"]) != contracted

    assert not _is_bare_run_step({**consumer, "if": "${{ false }}"})
    assert not _is_bare_run_step({**consumer, "if": "${{ failure() }}"})
    assert not _is_bare_run_step({**consumer, "shell": "/bin/true {0}"})
    assert not _is_bare_run_step({**producer, "continue-on-error": True})
    assert not _is_bare_run_step({**producer, "if": "${{ always() }}"})

    positions = _positions(_steps())
    real_steps = _steps()
    forged = [
        *real_steps[: positions[PRODUCER] + 1],
        {"name": "Forge green lcov", "run": "echo fake > build/coverage/lcov.info"},
        *real_steps[positions[PRODUCER] + 1 :],
    ]
    forged_positions = _positions(forged)
    assert forged_positions[CONSUMER] != forged_positions[PRODUCER] + 1


def test_defective_job_mutations_are_detected() -> None:
    """Control defectuoso de nivel job: el perímetro no termina en los pasos.

    Mutaciones del job REAL (MAYOR-1 de la segunda verificación): job
    desactivado, job que se perdona su fallo entero, y shell de confianza
    sustituido por uno que siempre triunfa. Si alguna pasara el predicado
    del contrato, la vigilancia de nivel paso quedaría huérfana.
    """
    job = _job()
    consumer = _named(job["steps"], CONSUMER)

    assert set(_required_names(consumer["run"])) <= set(REQUIRED_INVENTORY)
    assert not _job_executes_normally({**job, "if": "${{ false }}"})
    assert not _job_executes_normally({**job, "continue-on-error": True})
    assert not _job_executes_normally({**job, "needs": ["decoy"]})
    assert not _job_executes_normally({**job, "strategy": {"matrix": {"x": []}}})
    assert not _job_executes_normally({**job, "defaults": {"run": {"shell": "/bin/true {0}"}}})


def test_consumer_reads_artifact_the_producer_writes() -> None:
    """Cableado de la cadena: el destino del productor es la ruta del ratchet.

    El consumidor ``wct ratchet check`` lee ``LCOV_ARTIFACT`` por defecto:
    si el productor escribiera otra ruta, el exigible consumiría otro
    artefacto (o ninguno) y el paso pasaría a medir sin fuente.
    """
    run = _named(_steps(), PRODUCER)["run"]

    assert _produced_artifact(run) == LCOV_ARTIFACT


def test_defective_artifact_path_is_detected() -> None:
    """Control defectuoso: un productor que escriba en otra parte se detecta.

    Mutación mínima del paso REAL: solo cambia el destino del lcov — si el
    productor del workflow llegara a escribir otro artefacto, el cableado
    de la cadena lo delata.
    """
    real = _named(_steps(), PRODUCER)["run"]

    assert _produced_artifact(real) == LCOV_ARTIFACT
    defective = real.replace(f"lcov:{LCOV_ARTIFACT.as_posix()}", "lcov:build/otro.info")
    assert _produced_artifact(defective) != LCOV_ARTIFACT


def test_chain_blocks_when_artifact_below_baseline(
    project_factory: Callable[..., Path],
) -> None:
    """Escenario 5, fila «por debajo del baseline»: válido no es suficiente.

    El LCOV es válido (la invalidación ya es matriz de G3a-1 en
    test_ratchet_check), pero su medición no mantiene el ratchet: el
    consumidor exigible falla nombrando la métrica y el piso.
    """
    root = project_factory()
    _write_lcov(root, LCOV_BELOW_BASELINE)

    failures = check(root, required=["coverage-total"]).failures

    assert failures == ["coverage-total: actual=50, baseline=74.5"]


def test_chain_passes_when_artifact_over_baseline(
    project_factory: Callable[..., Path],
) -> None:
    """Escenario 5, fila «sobre el baseline»: la cadena deja pasar el verde."""
    root = project_factory()
    _write_lcov(root, LCOV_OVER_BASELINE)

    assert check(root, required=["coverage-total"]).failures == []
