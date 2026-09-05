from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

from tools.wct.config import ConfigError, find_root

STEP = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.+?)\s*$")

# TODO(owner=yosoyepa, issue=#35): parse_feature no soporta narrativa Gherkin
# bajo Feature: (solo #, @, keywords, filas | y steps); soportarla es trabajo
# separado de PR-F, con TDD propio y decisión sobre el flujo por el IR.


def parse_feature(path: Path) -> dict[str, Any]:
    feature = ""
    background: list[dict[str, Any]] = []
    scenarios: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_examples = False
    headers: list[str] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("@"):
            continue
        if line.startswith("Feature:"):
            feature = line.split(":", 1)[1].strip()
        elif line.startswith("Background:"):
            current = {"name": "Background", "line": number, "steps": background, "examples": []}
            in_examples = False
        elif line.startswith(("Scenario:", "Scenario Outline:")):
            current = {
                "name": line.split(":", 1)[1].strip(),
                "line": number,
                "outline": line.startswith("Scenario Outline:"),
                "steps": [],
                "examples": [],
            }
            scenarios.append(current)
            in_examples = False
        elif line.startswith("Examples:"):
            if current is None or current.get("name") == "Background":
                raise ValueError(f"{path}:{number}: Examples fuera de Scenario Outline")
            in_examples = True
            headers = []
        elif in_examples and line.startswith("|"):
            values = [value.strip() for value in line.strip("|").split("|")]
            if not headers:
                headers = values
            else:
                if len(values) != len(headers):
                    raise ValueError(f"{path}:{number}: fila Examples de longitud incorrecta")
                if current is None:
                    raise ValueError(f"{path}:{number}: fila Examples sin escenario")
                current["examples"].append(dict(zip(headers, values, strict=True)))
        else:
            match = STEP.match(raw)
            if match:
                target = (
                    background
                    if current and current.get("name") == "Background"
                    else current["steps"]
                    if current
                    else None
                )
                if target is None:
                    raise ValueError(f"{path}:{number}: step fuera de scenario")
                target.append({"keyword": match.group(1), "text": match.group(2), "line": number})
            elif line:
                raise ValueError(f"{path}:{number}: sintaxis Gherkin no soportada: {line}")
    if not feature or not scenarios:
        raise ValueError(f"{path}: Feature y al menos un Scenario son obligatorios")
    return {
        "schema_version": 1,
        "feature": feature,
        "source": _relative_source(path),
        "background": background,
        "scenarios": scenarios,
    }


def _relative_source(path: Path) -> str:
    """Ruta del feature relativa al root del repo cuando es derivable (ADR-D-04).

    El root se resuelve con ``find_root`` (marcador: governance/policy.yaml).
    Si el feature vive fuera de él, o el root no es derivable, la ruta viaja
    tal cual: el IR — y el artefacto generado que lo embebe — no debe
    depender del checkout absoluto que lo produjo.

    Args:
        path: ruta del archivo .feature tal como la pasó el caller.

    Returns:
        La ruta relativa al root (POSIX del repo) o la original absoluta.
    """
    try:
        return str(path.resolve().relative_to(find_root(path)))
    except (ConfigError, ValueError):
        return str(path)


def ir_dry(ir: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    global_steps: list[tuple[str, str, str, int, bool]] = []
    for scenario in ir["scenarios"]:
        seen: dict[str, int] = {}
        for step in scenario["steps"]:
            normalized = re.sub(
                r"(?:\d+(?:\.\d+)?|\"[^\"]*\"|'[^']*')", "<value>", step["text"].lower()
            )
            if normalized in seen:
                findings.append(
                    {
                        "kind": "duplicate-in-scenario",
                        "scenario": scenario["name"],
                        "line": step["line"],
                        "other_line": seen[normalized],
                        "step": step["text"],
                        "message": (
                            f"Paso '{step['text']}' repite la forma de la línea "
                            f"{seen[normalized]} dentro del escenario '{scenario['name']}'"
                        ),
                    }
                )
            seen[normalized] = step["line"]
            global_steps.append(
                (normalized, step["text"], scenario["name"], step["line"], scenario["outline"])
            )
    for index, (left, left_text, left_scenario, left_line, left_outline) in enumerate(global_steps):
        for right, _right_text, right_scenario, right_line, right_outline in global_steps[
            index + 1 :
        ]:
            if left_scenario != right_scenario and left == right:
                suggestion = "parametriza uno de los dos"
                if left_outline or right_outline:
                    outline = left_scenario if left_outline else right_scenario
                    suggestion = (
                        f"parametriza el paso en el Scenario Outline '{outline}' con una "
                        f"columna nueva en Examples, o reformula su texto para diferenciarlos"
                    )
                findings.append(
                    {
                        "kind": "placeholder-variant",
                        "scenario": right_scenario,
                        "line": right_line,
                        "other_line": left_line,
                        "other_scenario": left_scenario,
                        "step": left_text,
                        "message": (
                            f"Paso '{left_text}' del escenario '{left_scenario}' (línea "
                            f"{left_line}) colisiona con el escenario '{right_scenario}' "
                            f"(línea {right_line}); {suggestion}"
                        ),
                    }
                )
    return {"findings": findings, "count": len(findings)}


def generate(ir: dict[str, Any], output: Path) -> Path:
    payload = json.dumps(ir, ensure_ascii=False)
    source = "\n".join(
        [
            "# Generated by wct accept generate. Do not edit.",
            "import json",
            "import os",
            "from pathlib import Path",
            "",
            "from tests.acceptance.steps import execute_scenario",
            "",
            "BASE_IR = json.loads(",
            f"    {payload!r}",
            ")",
            "",
            "",
            "def _ir():",
            '    path = os.environ.get("WCT_ACCEPT_IR")',
            '    return json.loads(Path(path).read_text(encoding="utf-8")) if path else BASE_IR',
            "",
        ]
    )
    source += "\n"
    for index, scenario in enumerate(ir["scenarios"], 1):
        safe = re.sub(r"[^a-z0-9_]+", "_", scenario["name"].lower()).strip("_")
        source += (
            f"""\ndef test_{index:03d}_{safe}():\n    execute_scenario(_ir(), {index - 1})\n"""
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source, encoding="utf-8")
    return output


def mutations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    for scenario_index, scenario in enumerate(ir["scenarios"]):
        for row_index, row in enumerate(scenario.get("examples", [])):
            for key, value in row.items():
                changed = (
                    "0"
                    if value != "0" and re.fullmatch(r"-?\d+(?:\.\d+)?", value)
                    else value + "__mutated"
                )
                clone = json.loads(json.dumps(ir))
                clone["scenarios"][scenario_index]["examples"][row_index][key] = changed
                generated.append(
                    {
                        "scenario": scenario["name"],
                        "row": row_index,
                        "field": key,
                        "from": value,
                        "to": changed,
                        "ir": clone,
                    }
                )
    return generated


def run_mutations(ir: dict[str, Any], command: list[str]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="wct-accept-") as temp:
        for index, mutation in enumerate(mutations(ir), 1):
            path = Path(temp) / f"mutation-{index}.json"
            path.write_text(json.dumps(mutation.pop("ir")), encoding="utf-8")
            env = {**os.environ, "WCT_ACCEPT_IR": str(path)}
            completed = subprocess.run(
                command, text=True, capture_output=True, env=env, check=False
            )
            results.append(
                {
                    **mutation,
                    "status": "killed" if completed.returncode else "survived",
                    "exit": completed.returncode,
                }
            )
            if index % 10 == 0:
                print(f"accept mutation progress: {index}/{len(results)}", file=sys.stderr)
    return {
        "results": results,
        "killed": sum(item["status"] == "killed" for item in results),
        "survived": sum(item["status"] == "survived" for item in results),
    }


def accept_verdict(ir: dict[str, Any], report: dict[str, Any]) -> tuple[bool, list[str]]:
    """Decide el veredicto no vacuo de la mutación de aceptación.

    Anexa al reporte la clave aditiva ``vacuous`` (nombres de escenarios
    sin Examples) como advertencia, y exige trabajo ejecutado para
    aprobar: ``killed + survived == 0`` es sin-datos, no éxito, y falla
    citando TEST-010. Con mutaciones ejecutadas manda la semántica previa:
    sobrevivientes fallan, el caso sano pasa.

    Args:
        ir: IR del feature parseado; fuente de los escenarios.
        report: reporte de ``run_mutations``; recibe ``vacuous`` in place.

    Returns:
        (fallo, mensajes): fallo True exige exit != 0; mensajes son
        líneas accionables para stderr (vacías en el caso sano).
    """
    report["vacuous"] = [
        scenario["name"] for scenario in ir["scenarios"] if not scenario["examples"]
    ]
    if report["killed"] + report["survived"] == 0:
        messages = [
            "0 mutaciones ejecutadas: el escenario no parametriza campos "
            "variables; agrega Examples (TEST-010)"
        ]
        if report["vacuous"]:
            messages.append(f"escenarios sin Examples: {', '.join(report['vacuous'])}")
        return True, messages
    return bool(report["survived"]), []
