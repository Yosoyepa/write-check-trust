"""Alcance verificable de G-SAST-SEMGREP: matriz literal y binding del Gherkin.

La matriz es independiente del feature (el feature no es su propio oráculo);
el binding ejecuta comportamiento productivo: clasificación pura de la
respuesta, E real sobre árboles plantados, fixture F9-a con raíz Git propia
y el contexto de aislamiento Git. Comprueba además que el Gherkin mantiene
exactamente los escenarios aprobados (addenda de frontera).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

from tests.conftest import git_isolated
from tools.wct.accept.parsing import parse_feature
from tools.wct.config import ConfigError, load_config
from tools.wct.gate.runner import REGISTRY
from tools.wct.gate.semgrep import SemgrepScopeError, classify, gate_sast_semgrep, required_sources
from tools.wct.model import Status
from tools.wct.selftest.fixtures_tools import SEMGREP_RULES, f9_a
from tools.wct.util.git import tracked_files

FEATURE = Path(__file__).resolve().parents[2] / "features" / "wct-sast-targets-001.feature"
RULE = "governance.semgrep.wct-io-in-domain"
VICTIM = "src/a.py"
OUTLINE = "Clasificar una respuesta Semgrep por rutas normalizadas"
OUTLINE_OMITIDAS = "Los resumenes SAST conservan las fuentes omitidas"
OUTLINE_ALCANCE = "Los errores de alcance identifican la causa del rechazo"
OUTLINE_SKIP = "La herramienta ausente produce un SKIP visible del gate"
OUTLINE_GIT = "El preflight tolera un Git no cero acotado y observa el resultado posterior"
OUTLINE_ERROR = "La rama de error expone la causa y la duracion medida"
OUTLINE_FINAL = "El retorno final expone duracion y comando informativo"
COMANDO = "semgrep --quiet --error --severity ERROR --config governance/semgrep --json"
APPROVED_SCENARIOS = (
    OUTLINE,
    "Una fuente ignorada sigue siendo exigible",
    "Un temporal fuera de rutas declaradas no infla el denominador",
    "Un modulo no testeable sigue sujeto a seguridad",
    "El fixture adversarial usa una raiz Git propia",
    "El aislamiento Git restaura el entorno en el mismo proceso",
    "La gobernanza del fixture adversarial es cargable por el lector productivo",
    OUTLINE_OMITIDAS,
    OUTLINE_ALCANCE,
    OUTLINE_SKIP,
    OUTLINE_GIT,
    OUTLINE_ERROR,
    OUTLINE_FINAL,
)


def _document(
    scanned: list[str],
    findings: list[dict[str, Any]] | None = None,
    errors: list[dict[str, str]] | None = None,
) -> str:
    return json.dumps(
        {"errors": errors or [], "paths": {"scanned": scanned}, "results": findings or []}
    )


def _finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "check_id": RULE,
        "path": VICTIM,
        "start": {"line": 3},
        "extra": {"severity": "ERROR"},
    }
    finding.update(overrides)
    return finding


def _payload(name: str, scanned: list[str]) -> str:
    builders = {
        "finding-valido": lambda: _document(scanned, findings=[_finding()]),
        "esquema-incompleto": lambda: json.dumps({"errors": [], "results": []}),
        "errores-instrumento": lambda: _document(
            scanned, errors=[{"message": "error interno del instrumento"}]
        ),
        "json-malformado": lambda: '{"errors": [',
        "scanned-no-lista": lambda: json.dumps(
            {"errors": [], "paths": {"scanned": VICTIM}, "results": []}
        ),
        "errors-no-lista": lambda: json.dumps(
            {"errors": {}, "paths": {"scanned": scanned}, "results": []}
        ),
        "mensaje-no-string": lambda: json.dumps(
            {"errors": [{"message": 42}], "paths": {"scanned": scanned}, "results": []}
        ),
        "results-no-lista": lambda: json.dumps(
            {"errors": [], "paths": {"scanned": scanned}, "results": "x"}
        ),
        "resultado-no-dict": lambda: json.dumps(
            {"errors": [], "paths": {"scanned": scanned}, "results": ["x"]}
        ),
        "ruta-con-escape": lambda: _document(scanned, findings=[_finding(path="../fuera.py")]),
        "linea-cero": lambda: _document(scanned, findings=[_finding(start={"line": 0})]),
        "linea-uno": lambda: _document(scanned, findings=[_finding(start={"line": 1})]),
    }
    return builders.get(name, lambda: _document(scanned))()


def _expect(verdict: object, status: str, diagnostic: str) -> None:
    assert verdict.status is Status[status]
    assert isinstance(verdict.details, tuple)
    if diagnostic == "regla y archivo":
        assert RULE in verdict.summary
        assert VICTIM in verdict.summary
    else:
        assert verdict.summary.startswith(diagnostic)
    if diagnostic == "error del instrumento":
        assert any("error interno del instrumento" in item for item in verdict.details)


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            (["src/a.py"], ["src/a.py"], "finding-valido", 1, "FAIL", "regla y archivo"),
            id="hallazgo",
        ),
        pytest.param(
            (
                ["src/a.py", "tools/b.py"],
                ["src/a.py", "tools/b.py"],
                "limpio-valido",
                0,
                "PASS",
                "2 fuentes analizadas",
            ),
            id="cobertura-completa",
        ),
        pytest.param(
            (["src/a.py"], [], "limpio-valido", 0, "ERROR", "0 de 1 fuentes"),
            id="cero-escaneadas",
        ),
        pytest.param(
            (
                ["src/a.py", "tools/b.py"],
                ["src/a.py"],
                "limpio-valido",
                0,
                "ERROR",
                "falta tools/b.py",
            ),
            id="omision-parcial",
        ),
        pytest.param(
            (
                ["src/a.py", "tools/b.py"],
                ["src/a.py", "tests/c.py"],
                "limpio-valido",
                0,
                "ERROR",
                "ruta distinta no compensa",
            ),
            id="extra-no-compensa",
        ),
        pytest.param(
            ([], [], "limpio-valido", 0, "PASS", "sin fuentes aplicables"), id="sin-fuentes"
        ),
        pytest.param(
            (["src/a.py"], [], "json-malformado", 0, "ERROR", "salida ilegible"),
            id="json-malformado",
        ),
        pytest.param(
            (["src/a.py"], [], "esquema-incompleto", 0, "ERROR", "esquema incompleto"),
            id="esquema-incompleto",
        ),
        pytest.param(
            (
                ["src/a.py"],
                ["src/a.py"],
                "errores-instrumento",
                0,
                "ERROR",
                "error del instrumento",
            ),
            id="errores-instrumento",
        ),
        pytest.param(
            (
                ["src/a.py"],
                ["src/a.py"],
                "limpio-valido",
                1,
                "ERROR",
                "exit sin finding explicativo",
            ),
            id="exit-sin-finding",
        ),
        pytest.param(
            (["src/a.py"], [], "scanned-no-lista", 0, "ERROR", "esquema incompleto"),
            id="scanned-no-lista",
        ),
        pytest.param(
            (["src/a.py"], [], "errors-no-lista", 0, "ERROR", "esquema incompleto"),
            id="errors-no-lista",
        ),
        pytest.param(
            (["src/a.py"], [], "mensaje-no-string", 0, "ERROR", "esquema incompleto"),
            id="mensaje-no-string",
        ),
        pytest.param(
            (["src/a.py"], [], "results-no-lista", 0, "ERROR", "esquema incompleto"),
            id="results-no-lista",
        ),
        pytest.param(
            (["src/a.py"], [], "resultado-no-dict", 0, "ERROR", "esquema incompleto"),
            id="resultado-no-dict",
        ),
        pytest.param(
            (["src/a.py"], [], "ruta-con-escape", 0, "ERROR", "esquema incompleto"),
            id="ruta-con-escape",
        ),
        pytest.param(
            (["src/a.py"], ["src/a.py"], "linea-cero", 1, "ERROR", "esquema incompleto"),
            id="linea-cero",
        ),
        pytest.param(
            (["src/a.py"], ["src/a.py"], "linea-uno", 1, "FAIL", "regla y archivo"),
            id="linea-uno",
        ),
    ],
)
def test_matriz_literal(case: tuple[list[str], list[str], str, int, str, str]) -> None:
    required, scanned, payload, exit_code, status, diagnostic = case
    verdict = classify(required, _payload(payload, scanned), exit_code)
    _expect(verdict, status, diagnostic)


def test_exit_cero_con_hallazgos_es_incoherente() -> None:
    verdict = classify(["src/a.py"], _document(["src/a.py"], findings=[_finding()]), 0)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "exit incoherente con hallazgos"
    assert verdict.details == ()


def test_exit_fuera_de_contrato() -> None:
    verdict = classify(["src/a.py"], _document([]), 2)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "exit fuera de contrato"
    assert verdict.details == ("exit observado: 2",)


def test_hallazgo_sin_regla_no_se_atribuye() -> None:
    verdict = classify(["src/a.py"], _document(["src/a.py"], findings=[_finding(check_id="")]), 1)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "esquema incompleto"


def test_linea_booleana_no_es_linea_valida() -> None:
    verdict = classify(
        ["src/a.py"], _document(["src/a.py"], findings=[_finding(start={"line": True})]), 1
    )

    assert verdict.status is Status.ERROR
    assert verdict.summary == "esquema incompleto"


def test_severidad_no_bloqueante_es_esquema() -> None:
    verdict = classify(
        ["src/a.py"],
        _document(["src/a.py"], findings=[_finding(extra={"severity": "WARNING"})]),
        1,
    )

    assert verdict.status is Status.ERROR
    assert verdict.summary == "esquema incompleto"


def test_ruta_escaneada_con_escape_es_esquema() -> None:
    verdict = classify(["src/a.py"], _document(["../a.py"]), 0)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "esquema incompleto"


def test_extra_queda_como_diagnostico_en_detalles() -> None:
    verdict = classify(["src/a.py"], _document(["src/a.py", "tests/c.py"]), 0)

    assert verdict.status is Status.PASS
    assert verdict.summary == "1 fuentes analizadas, 0 hallazgos"
    assert any("tests/c.py" in item for item in verdict.details)


def test_fail_con_omision_no_oculta_el_defecto() -> None:
    document = _document(["src/a.py"], findings=[_finding()])
    verdict = classify(["src/a.py", "tools/b.py"], document, 1)

    assert verdict.status is Status.FAIL
    assert RULE in verdict.summary
    assert "tools/b.py" in verdict.summary
    assert any(RULE in item for item in verdict.details)
    assert any("omitida: tools/b.py" in item for item in verdict.details)


def _policy(source: list[str], **extra: Any) -> dict[str, Any]:
    policy: dict[str, Any] = {"schema_version": 1, "paths": {"source": source}}
    policy.update(extra)
    return policy


def test_fuente_ignorada_por_git_sigue_siendo_exigible(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("src/a.py\n", encoding="utf-8")

    assert required_sources(tmp_path, _policy(["src"])) == ["src/a.py"]


def test_temporal_bajo_build_queda_fuera(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    temporal = tmp_path / "build" / "tmp"
    temporal.mkdir(parents=True)
    (temporal / "x.py").write_text("value = 2\n", encoding="utf-8")
    policy = _policy(["src"])
    policy["paths"]["build"] = "build"

    assert required_sources(tmp_path, policy) == ["src/a.py"]


def test_build_solapado_con_fuente_queda_fuera(tmp_path: Path) -> None:
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/inner.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 2\n", encoding="utf-8")
    policy = _policy(["tools", "src"])
    policy["paths"]["build"] = "tools"

    assert required_sources(tmp_path, policy) == ["src/a.py"]


def test_build_anidado_respeta_el_limite_de_directorio(tmp_path: Path) -> None:
    (tmp_path / "src/build").mkdir(parents=True)
    (tmp_path / "src/build/gen.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "src/builder.py").write_text("value = 2\n", encoding="utf-8")
    (tmp_path / "src/build2/pkg").mkdir(parents=True)
    (tmp_path / "src/build2/pkg/mod.py").write_text("value = 3\n", encoding="utf-8")
    policy = _policy(["src"])
    policy["paths"]["build"] = "src/build"

    assert required_sources(tmp_path, policy) == ["src/build2/pkg/mod.py", "src/builder.py"]


def test_build_en_forma_de_lista(tmp_path: Path) -> None:
    (tmp_path / "src/build").mkdir(parents=True)
    (tmp_path / "src/build/gen.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "src/a.py").write_text("value = 2\n", encoding="utf-8")
    policy = _policy(["src"])
    policy["paths"]["build"] = ["src/build"]

    assert required_sources(tmp_path, policy) == ["src/a.py"]


def test_caches_y_entornos_anidados_quedan_fuera(tmp_path: Path) -> None:
    for nested in (".venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".git"):
        (tmp_path / "src" / nested).mkdir(parents=True)
        (tmp_path / "src" / nested / "mod.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "src/a.py").write_text("value = 2\n", encoding="utf-8")

    assert required_sources(tmp_path, _policy(["src"])) == ["src/a.py"]


def test_modulo_no_testeable_sigue_sujeto_a_seguridad(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/legacy.py").write_text("value = 1\n", encoding="utf-8")
    policy = _policy(["src"], architecture={"unsuitable_for_test": ["src/legacy.py"]})

    assert required_sources(tmp_path, policy) == ["src/legacy.py"]


def test_ruta_de_policy_de_tipo_invalido_es_error(tmp_path: Path) -> None:
    with pytest.raises(SemgrepScopeError):
        required_sources(tmp_path, _policy(["src", 7]))


def test_fuente_declarada_que_escapa_es_error(tmp_path: Path) -> None:
    with pytest.raises(SemgrepScopeError):
        required_sources(tmp_path, _policy(["../afuera"]))


def test_ruta_declarada_ambigua_es_error(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    with pytest.raises(SemgrepScopeError):
        required_sources(tmp_path, _policy(["src", "./src"]))


def test_enlace_simbolico_que_escapa_es_error(
    tmp_path: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("afuera")
    (outside / "real.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/enlace.py").symlink_to(outside / "real.py")

    with pytest.raises(SemgrepScopeError):
        required_sources(tmp_path, _policy(["src"]))


def test_raiz_absorbida_por_ancestro_ajeno_es_error(tmp_path: Path) -> None:
    if shutil.which("semgrep") is None:
        pytest.skip("herramienta ausente: semgrep")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    inner = repo / "inner"
    inner.mkdir()

    result = gate_sast_semgrep(inner)

    assert result.status is Status.ERROR
    assert result.summary.startswith("candidate root absorbed by foreign Git ancestor:")


def test_raiz_git_propia_permite_analisis_sano(tmp_path: Path) -> None:
    if shutil.which("semgrep") is None:
        pytest.skip("herramienta ausente: semgrep")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    governance = tmp_path / "governance"
    (governance / "semgrep").mkdir(parents=True)
    (governance / "policy.yaml").write_text(
        "schema_version: 1\npaths:\n  source: [src]\n", encoding="utf-8"
    )
    (governance / "semgrep" / "wct-architecture.yaml").write_text(SEMGREP_RULES, encoding="utf-8")

    result = gate_sast_semgrep(tmp_path)

    assert result.status is Status.PASS
    assert result.summary == "1 fuentes analizadas, 0 hallazgos"


def test_gherkin_mantiene_los_escenarios_aprobados() -> None:
    ir = parse_feature(FEATURE)
    outline = ir["scenarios"][0]

    assert [scenario["name"] for scenario in ir["scenarios"]] == list(APPROVED_SCENARIOS)
    assert outline["outline"] is True
    assert [row["required"] for row in outline["examples"]] == [
        "src/a.py",
        "src/a.py;tools/b.py",
        "src/a.py",
        "src/a.py;tools/b.py",
        "src/a.py;tools/b.py",
        "",
        "src/a.py",
        "src/a.py",
        "src/a.py",
        "src/a.py",
    ]
    assert [row["status"] for row in outline["examples"]] == [
        "FAIL",
        "PASS",
        "ERROR",
        "ERROR",
        "ERROR",
        "PASS",
        "ERROR",
        "ERROR",
        "ERROR",
        "ERROR",
    ]


def test_binding_ejecuta_la_matriz_del_gherkin() -> None:
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE)
    steps = [step["text"] for step in outline["steps"]]

    assert steps == [
        'fuentes Python exigibles "<required>"',
        'rutas Python informadas como escaneadas "<scanned>"',
        'una respuesta "<payload>" con exit "<exit>"',
        "clasifico el resultado SAST por alcance",
        'obtengo estado "<status>" y diagnostico "<diagnostic>"',
    ]
    for row in outline["examples"]:
        required = [item for item in row["required"].split(";") if item]
        scanned = [item for item in row["scanned"].split(";") if item]
        verdict = classify(required, _payload(row["payload"], scanned), int(row["exit"]))
        _expect(verdict, row["status"], row["diagnostic"])


def test_binding_los_resumenes_conservan_las_omitidas() -> None:
    """Contrato ratificado: solo los resumenes que enumeran fuentes omitidas.

    Las rutas omitidas se conservan, ordenadas y separadas por coma y espacio.
    """
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_OMITIDAS)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        'fuentes Python exigibles para el resumen "<required>"',
        'rutas Python informadas como escaneadas para el resumen "<scanned>"',
        'una respuesta para el resumen "<payload>" con exit "<exit>"',
        "clasifico el resultado SAST para el resumen",
        'obtengo estado "<status>" y resumen exacto "<resumen>"',
    ]
    assert outline["examples"] == [
        {
            "required": "src/a.py;tools/b.py;tests/c.py",
            "scanned": "src/a.py",
            "payload": "finding-valido",
            "exit": "1",
            "status": "FAIL",
            "resumen": (
                "governance.semgrep.wct-io-in-domain src/a.py:3 (omitidas: tests/c.py, tools/b.py)"
            ),
        },
        {
            "required": "src/a.py;tools/b.py;tests/c.py",
            "scanned": "src/a.py",
            "payload": "limpio-valido",
            "exit": "0",
            "status": "ERROR",
            "resumen": "falta tests/c.py, tools/b.py",
        },
    ]
    for row in outline["examples"]:
        required = [item for item in row["required"].split(";") if item]
        scanned = [item for item in row["scanned"].split(";") if item]
        verdict = classify(required, _payload(row["payload"], scanned), int(row["exit"]))

        assert verdict.status is Status[row["status"]]
        assert verdict.summary == row["resumen"]


def _politica_de_alcance(raiz: Path, caso: str) -> dict[str, Any]:
    """Raiz y politica de alcance para cada sitio de rechazo del outline."""
    (raiz / "src").mkdir()
    (raiz / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    policy: dict[str, Any] = {"schema_version": 1, "paths": {"source": ["src"]}}
    if caso == "paths-no-mapa":
        policy["paths"] = "no-es-un-mapa"
    elif caso == "source-string":
        policy["paths"]["source"] = "src"
    elif caso == "build-mapa":
        policy["paths"]["build"] = {"a": 1}
    elif caso == "build-no-normalizable":
        policy["paths"]["build"] = ["."]
    elif caso == "declarada-no-normalizable":
        policy["paths"]["source"] = ["../afuera"]
    elif caso == "declarada-ambigua":
        policy["paths"]["source"] = ["src", "./src"]
    elif caso in {"fuente-escapa", "declarada-escapa"}:
        afuera = raiz.parent / "afuera-cierre"
        afuera.mkdir(exist_ok=True)
        if caso == "fuente-escapa":
            (raiz / "src/sub").mkdir()
            (afuera / "real.py").write_text("value = 2\n", encoding="utf-8")
            (raiz / "src/sub/enlace.py").symlink_to(afuera / "real.py")
        else:
            (afuera / "mod.py").write_text("value = 2\n", encoding="utf-8")
            (raiz / "enlace").symlink_to(afuera, target_is_directory=True)
            policy["paths"]["source"] = ["enlace"]
    return policy


def test_binding_los_errores_de_alcance_identifican_la_causa(tmp_path: Path) -> None:
    """Contrato aprobado: los errores de alcance identifican la causa del rechazo.

    Los prefijos de los ocho sitios son estables; los valores variables
    posteriores no quedan fijados.
    """
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_ALCANCE)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        'una raiz temporal con la politica de alcance "<caso>"',
        'la condicion invalida "<invalido>"',
        "determino el alcance exigible de la raiz",
        'el rechazo es de tipo "<tipo>" con prefijo "<prefijo>"',
    ]
    assert outline["examples"] == [
        {
            "caso": "paths-no-mapa",
            "invalido": "policy sin mapa paths",
            "tipo": "SemgrepScopeError",
            "prefijo": "policy.paths debe ser un mapa para determinar el alcance",
        },
        {
            "caso": "source-string",
            "invalido": "source como string no lista",
            "tipo": "SemgrepScopeError",
            "prefijo": "policy.paths.source debe ser una lista de rutas string",
        },
        {
            "caso": "build-mapa",
            "invalido": "build como mapa no lista",
            "tipo": "SemgrepScopeError",
            "prefijo": "policy.paths.build debe ser una ruta string o una lista de rutas string",
        },
        {
            "caso": "build-no-normalizable",
            "invalido": "build que no normaliza bajo la raiz",
            "tipo": "SemgrepScopeError",
            "prefijo": "ruta de construcción no normalizable bajo la raíz",
        },
        {
            "caso": "fuente-escapa",
            "invalido": "fuente cuyo enlace resuelve fuera de la raiz",
            "tipo": "SemgrepScopeError",
            "prefijo": "fuente declarada escapa de la raíz",
        },
        {
            "caso": "declarada-no-normalizable",
            "invalido": "declarada con salto de directorio",
            "tipo": "SemgrepScopeError",
            "prefijo": "ruta de alcance no normalizable bajo la raíz",
        },
        {
            "caso": "declarada-escapa",
            "invalido": "declarada que resuelve fuera de la raiz",
            "tipo": "SemgrepScopeError",
            "prefijo": "ruta de alcance escapa de la raíz",
        },
        {
            "caso": "declarada-ambigua",
            "invalido": "dos declaradas que resuelven a la misma",
            "tipo": "SemgrepScopeError",
            "prefijo": "ruta de política ambigua",
        },
    ]
    for row in outline["examples"]:
        raiz = tmp_path / row["caso"]
        raiz.mkdir()
        policy = _politica_de_alcance(raiz, row["caso"])

        with pytest.raises(SemgrepScopeError) as excinfo:
            required_sources(raiz, policy)

        assert str(excinfo.value).startswith(row["prefijo"])


def test_la_declarada_inexistente_no_aborta_las_posteriores(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 1\n", encoding="utf-8")

    assert required_sources(tmp_path, _policy(["no-existe", "src"])) == ["src/a.py"]


def test_binding_fuente_ignorada(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("src/a.py\n", encoding="utf-8")
    exigibles = required_sources(tmp_path, _policy(["src"]))

    verdict = classify(exigibles, _document([]), 0)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "0 de 1 fuentes"
    assert any("src/a.py" in item for item in verdict.details)


def test_binding_fixture_adversarial_raiz_propia(tmp_path: Path) -> None:
    if shutil.which("semgrep") is None:
        pytest.skip("herramienta ausente: semgrep")
    root = f9_a(tmp_path)
    toplevel = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert toplevel == str(root.resolve())

    result = gate_sast_semgrep(root)

    assert result.status is Status.FAIL
    assert RULE in result.summary
    assert "src/victim/domain/io.py" in result.summary


def test_fallo_de_ejecucion_del_instrumento_es_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if shutil.which("semgrep") is None:
        pytest.skip("herramienta ausente: semgrep")

    def raise_os_error(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise OSError("semgrep desapareció entre which y run")

    monkeypatch.setattr("tools.wct.gate.semgrep.subprocess.run", raise_os_error)

    result = gate_sast_semgrep(tmp_path)

    assert result.status is Status.ERROR


def test_binding_aislamiento_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in (
        ("GIT_CEILING_DIRECTORIES", "/outer/ceiling"),
        ("GIT_DIR", "/outer/git"),
        ("GIT_WORK_TREE", "/outer/worktree"),
    ):
        monkeypatch.setenv(name, value)
    plain = tmp_path / "sin-repositorio"
    plain.mkdir()

    with git_isolated(tmp_path):
        assert os.environ["GIT_CEILING_DIRECTORIES"] == str(tmp_path)
        assert tracked_files(plain) is None

    assert os.environ["GIT_CEILING_DIRECTORIES"] == "/outer/ceiling"
    assert os.environ["GIT_DIR"] == "/outer/git"
    assert os.environ["GIT_WORK_TREE"] == "/outer/worktree"


def test_binding_gobernanza_del_fixture_cargable_por_load_config(tmp_path: Path) -> None:
    """Contrato mínimo ratificado: la raíz de f9_a es cargable por load_config.

    El escenario usa filesystem y Git mediante f9_a; no requiere Semgrep.
    """
    root = f9_a(tmp_path)

    project, policy, thresholds = load_config(root)

    assert project == root
    assert isinstance(policy, dict)
    assert isinstance(thresholds, dict)


def _raiz_con_politica(raiz: Path) -> None:
    (raiz / "src").mkdir(parents=True)
    (raiz / "src/a.py").write_text("value = 1\n", encoding="utf-8")
    governance = raiz / "governance"
    governance.mkdir()
    (governance / "policy.yaml").write_text(
        "schema_version: 1\npaths:\n  source: [src]\n", encoding="utf-8"
    )


def _raiz_git_con_politica(raiz: Path) -> None:
    _raiz_con_politica(raiz)
    subprocess.run(["git", "init", "-q"], cwd=raiz, check=True, capture_output=True)


def _reloj(lecturas: list[float]) -> Any:
    pendientes = iter(lecturas)

    def monotonic() -> float:
        return next(pendientes, lecturas[-1])

    return monotonic


def _toplevel_git(raiz: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=raiz,
        text=True,
        capture_output=True,
        check=False,
    )


def _instrumento_controlado(
    monkeypatch: pytest.MonkeyPatch, respuesta: str, exit_code: int
) -> list[list[str]]:
    """Sustituye la ejecución del instrumento y preserva el resto de subprocess.run."""
    real = subprocess.run
    invocados: list[list[str]] = []

    def fake(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if argv and argv[0] == "semgrep":
            invocados.append(list(argv))
            return subprocess.CompletedProcess(argv, exit_code, stdout=respuesta, stderr="")
        return real(argv, **kwargs)

    monkeypatch.setattr("tools.wct.gate.semgrep.subprocess.run", fake)
    return invocados


def test_binding_la_herramienta_ausente_declara_skip_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D1: la detección ausente produce SKIP con identidad y resumen exacto."""
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_SKIP)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        "una raiz de proyecto con politica de alcance valida",
        'la deteccion de "semgrep" no encuentra la herramienta',
        "ejecuto el gate SAST sobre la raiz sin herramienta",
        'obtengo estado "<status>" con gate "<gate>" y resumen "<resumen>"',
    ]
    assert outline["examples"] == [
        {
            "status": "SKIP",
            "gate": "G-SAST-SEMGREP",
            "resumen": "herramienta ausente: semgrep",
        }
    ]
    monkeypatch.setattr("tools.wct.gate.semgrep.shutil.which", lambda _name: None)
    raiz = tmp_path / "raiz-sin-herramienta"
    _raiz_con_politica(raiz)

    for row in outline["examples"]:
        result = gate_sast_semgrep(raiz)

        assert result.status is Status[row["status"]]
        assert result.gate_id == row["gate"]
        assert result.summary == row["resumen"]


def test_binding_el_preflight_tolera_git_no_cero_acotado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D2: el fallo Git acotado no aborta ni oculta el resultado posterior."""
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_GIT)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        'una raiz privada sin repositorio con frontera Git "<frontera>"',
        "una politica de alcance valida con fuente declarada",
        'un instrumento acotado que responde "<payload>" con exit "<exit>"',
        "ejecuto el gate SAST sobre la raiz privada",
        'obtengo estado "<status>" y resumen "<resumen>"',
    ]
    assert outline["examples"] == [
        {
            "frontera": "ceiling",
            "payload": "limpio-valido",
            "exit": "0",
            "status": "PASS",
            "resumen": "1 fuentes analizadas, 0 hallazgos",
        },
        {
            "frontera": "ceiling",
            "payload": "limpio-valido",
            "exit": "2",
            "status": "ERROR",
            "resumen": "exit fuera de contrato",
        },
    ]
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    raiz = tmp_path / "raiz-privada"
    _raiz_con_politica(raiz)
    assert _toplevel_git(raiz).returncode != 0

    for row in outline["examples"]:
        assert row["frontera"] == "ceiling"
        _instrumento_controlado(
            monkeypatch, _payload(row["payload"], ["src/a.py"]), int(row["exit"])
        )
        result = gate_sast_semgrep(raiz)

        assert result.status is Status[row["status"]]
        assert result.summary == row["resumen"]


def test_binding_la_rama_de_error_expone_causa_y_duracion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D3 (ERROR) y D5: duración medida y causa de policy conservada."""
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_ERROR)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        "una raiz de proyecto con politica de alcance ilegible",
        'la deteccion de "semgrep" encuentra la herramienta',
        'un reloj controlado para la rama de error "<inicio>" seguido de "<fin>"',
        "ejecuto el gate SAST sobre la raiz con politica ilegible",
        'obtengo estado "<status>" con gate "<gate>" y duracion de error ms "<duracion>"',
        'el resumen empieza por "<prefijo>" y conserva la causa "<causa>"',
    ]
    assert outline["examples"] == [
        {
            "inicio": "3000.0",
            "fin": "3001.25",
            "status": "ERROR",
            "gate": "G-SAST-SEMGREP",
            "duracion": "1250",
            "prefijo": "governance/policy.yaml ilegible:",
            "causa": "causa determinista de lectura",
        }
    ]
    monkeypatch.setattr(
        "tools.wct.gate.semgrep.shutil.which", lambda _name: "/instrumento/falso/semgrep"
    )
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    raiz = tmp_path / "raiz-policy-ilegible"
    raiz.mkdir()
    assert _toplevel_git(raiz).returncode != 0

    for row in outline["examples"]:

        def _falla_al_cargar(_path: Path, causa: str = row["causa"]) -> dict[str, Any]:
            raise ConfigError(causa)

        monkeypatch.setattr("tools.wct.gate.semgrep.load_yaml", _falla_al_cargar)
        monkeypatch.setattr(
            "tools.wct.gate.semgrep.time.monotonic",
            _reloj([float(row["inicio"]), float(row["fin"])]),
        )

        result = gate_sast_semgrep(raiz)

        assert result.status is Status[row["status"]]
        assert result.gate_id == row["gate"]
        assert result.duration_ms == int(row["duracion"])
        assert result.summary.startswith(row["prefijo"])
        assert row["causa"] in result.summary


def test_binding_el_retorno_final_expone_duracion_y_comando(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D3 (retorno final) y D4: duración medida y comando informativo independiente."""
    ir = parse_feature(FEATURE)
    outline = next(scenario for scenario in ir["scenarios"] if scenario["name"] == OUTLINE_FINAL)

    assert outline["outline"] is True
    assert [step["text"] for step in outline["steps"]] == [
        "una raiz Git propia con politica de alcance valida",
        'un instrumento controlado que responde "<payload>" con exit "<exit>"',
        'un reloj controlado para el retorno final "<inicio>" seguido de "<fin>"',
        "ejecuto el gate SAST sobre la raiz Git propia",
        'obtengo estado "<status>" con gate "<gate>" y duracion final ms "<duracion>"',
        'el comando informado es "<comando>"',
    ]
    assert outline["examples"] == [
        {
            "inicio": "1000.0",
            "fin": "1002.5",
            "payload": "limpio-valido",
            "exit": "0",
            "status": "PASS",
            "gate": "G-SAST-SEMGREP",
            "duracion": "2500",
            "comando": COMANDO,
        }
    ]
    raiz = tmp_path / "raiz-git-propia"
    _raiz_git_con_politica(raiz)
    assert _toplevel_git(raiz).stdout.strip() == str(raiz.resolve())

    for row in outline["examples"]:
        invocados = _instrumento_controlado(
            monkeypatch, _payload(row["payload"], ["src/a.py"]), int(row["exit"])
        )
        monkeypatch.setattr(
            "tools.wct.gate.semgrep.time.monotonic",
            _reloj([float(row["inicio"]), float(row["fin"])]),
        )

        result = gate_sast_semgrep(raiz)

        assert result.status is Status[row["status"]]
        assert result.gate_id == row["gate"]
        assert result.summary == "1 fuentes analizadas, 0 hallazgos"
        assert result.duration_ms == int(row["duracion"])
        assert isinstance(result.details, list)
        assert result.details == []
        assert result.command == row["comando"]
        assert [" ".join(invocado) for invocado in invocados] == [row["comando"]]


def test_dispatch_registry_observa_fuente_completa_y_omision_total(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PX-REG: la entrada real del REGISTRY conserva PASS y el ERROR por omisión."""
    raiz = tmp_path / "raiz-registry"
    _raiz_git_con_politica(raiz)
    assert _toplevel_git(raiz).stdout.strip() == str(raiz.resolve())
    monkeypatch.setattr(
        "tools.wct.gate.semgrep.shutil.which", lambda _name: "/instrumento/falso/semgrep"
    )

    invocados = _instrumento_controlado(monkeypatch, _payload("limpio-valido", []), 0)
    result = REGISTRY["G-SAST-SEMGREP"](raiz)

    assert result.status is Status.ERROR
    assert result.gate_id == "G-SAST-SEMGREP"
    assert result.summary == "0 de 1 fuentes"
    assert isinstance(result.details, list)
    assert any("omitida: src/a.py" in item for item in result.details)
    assert result.command == COMANDO
    assert [" ".join(invocado) for invocado in invocados] == [COMANDO]

    invocados = _instrumento_controlado(monkeypatch, _payload("limpio-valido", ["src/a.py"]), 0)
    result = REGISTRY["G-SAST-SEMGREP"](raiz)

    assert result.status is Status.PASS
    assert result.gate_id == "G-SAST-SEMGREP"
    assert result.summary == "1 fuentes analizadas, 0 hallazgos"
    assert result.details == []
    assert result.command == COMANDO
    assert [" ".join(invocado) for invocado in invocados] == [COMANDO]
