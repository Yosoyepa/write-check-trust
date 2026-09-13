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
from tools.wct.gate.semgrep import SemgrepScopeError, classify, gate_sast_semgrep, required_sources
from tools.wct.model import Status
from tools.wct.selftest.fixtures_tools import SEMGREP_RULES, f9_a
from tools.wct.util.git import tracked_files

FEATURE = Path(__file__).resolve().parents[2] / "features" / "wct-sast-targets-001.feature"
RULE = "governance.semgrep.wct-io-in-domain"
VICTIM = "src/a.py"
OUTLINE = "Clasificar una respuesta Semgrep por rutas normalizadas"
APPROVED_SCENARIOS = (
    OUTLINE,
    "Una fuente ignorada sigue siendo exigible",
    "Un temporal fuera de rutas declaradas no infla el denominador",
    "Un modulo no testeable sigue sujeto a seguridad",
    "El fixture adversarial usa una raiz Git propia",
    "El aislamiento Git restaura el entorno en el mismo proceso",
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
    }
    return builders.get(name, lambda: _document(scanned))()


def _expect(verdict: object, status: str, diagnostic: str) -> None:
    assert verdict.status is Status[status]
    if diagnostic == "regla y archivo":
        assert RULE in verdict.summary
        assert VICTIM in verdict.summary
    else:
        assert verdict.summary.startswith(diagnostic)


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


def test_exit_fuera_de_contrato() -> None:
    verdict = classify(["src/a.py"], _document([]), 2)

    assert verdict.status is Status.ERROR
    assert verdict.summary == "exit fuera de contrato"


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
