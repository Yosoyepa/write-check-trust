"""Characterized IR duplicate diagnostics with cohesive pure helpers."""

import re
from typing import Any

Step = tuple[str, str, str, int, bool]


def _collect(scenario: dict[str, Any], findings: list[dict[str, Any]]) -> list[Step]:
    global_steps: list[Step] = []
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
    return global_steps


def _pair(left_step: Step, right_step: Step, findings: list[dict[str, Any]]) -> None:
    left, left_text, left_scenario, left_line, left_outline = left_step
    right, _right_text, right_scenario, right_line, right_outline = right_step
    if left_scenario == right_scenario or left != right:
        return
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


def ir_dry(ir: dict[str, Any]) -> dict[str, Any]:
    """Preserve duplicate ordering, messages and Outline suggestions."""
    findings: list[dict[str, Any]] = []
    steps: list[Step] = []
    for scenario in ir["scenarios"]:
        steps.extend(_collect(scenario, findings))
    for index, left in enumerate(steps):
        for right in steps[index + 1 :]:
            _pair(left, right, findings)
    return {"findings": findings, "count": len(findings)}
