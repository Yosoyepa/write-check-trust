"""AC1 Gherkin recipes observe actual supervisor campaigns, not table equality."""

from pathlib import Path
import re
import sys
from typing import Any

from tests.acceptance.protocol_runner import MODES
from tools.wct.accept.pipeline import accept_verdict, run_mutations
from tools.wct.accept.semantic import SemanticMismatch


def _campaign(context: dict[str, Any], planned: int) -> None:
    ir = {
        "schema_version": 1,
        "feature": "AC1 inner fixture",
        "source": "deliberate-runner.feature",
        "background": [],
        "scenarios": [
            {
                "name": "probe",
                "line": 2,
                "outline": True,
                "steps": [],
                "examples": [{"value": "2"} for _ in range(planned)],
            }
        ],
    }
    runner = Path(__file__).with_name("protocol_runner.py")
    report = run_mutations(
        ir, [sys.executable, str(runner), context["baseline"], context["mutation"]]
    )
    context["report"] = report
    context["verdict"] = "fail" if accept_verdict(ir, report)[0] else "pass"


def execute_step(text: str, context: dict[str, Any]) -> bool:
    """Recognize only the approved campaign vocabulary and compare real results."""
    if match := re.fullmatch(r'un ejecutor con baseline "([^"]+)" y mutante "([^"]+)"', text):
        _modes(context, *match.groups())
    elif match := re.fullmatch(r'ejecuto una campana con "(\d+)" mutacion', text):
        _campaign(context, int(match.group(1)))
    elif match := re.fullmatch(
        r'el veredicto es "([^"]+)" con "(\d+)" killed y "(\d+)" errores', text
    ):
        _verdict(context, match.group(1), int(match.group(2)), int(match.group(3)))
    elif match := re.fullmatch(r'quedan "(\d+)" supervivientes y "(\d+)" sin ejecutar', text):
        _remaining(context, int(match.group(1)), int(match.group(2)))
    else:
        return False
    return True


def _modes(context: dict[str, Any], baseline: str, mutation: str) -> None:
    if baseline not in MODES or mutation not in MODES:
        raise ValueError("unknown campaign runner mode")
    context.update(baseline=baseline, mutation=mutation)


def _verdict(context: dict[str, Any], verdict: str, killed: int, errors: int) -> None:
    if verdict not in {"pass", "fail"}:
        raise ValueError("unknown campaign verdict")
    actual = context["verdict"], context["report"]["killed"], context["report"]["errors"]
    if actual != (verdict, killed, errors):
        raise SemanticMismatch("campaign verdict/counts differ from expected")


def _remaining(context: dict[str, Any], survived: int, not_run: int) -> None:
    actual = context["report"]["survived"], context["report"]["not_run"]
    if actual != (survived, not_run):
        raise SemanticMismatch("campaign residual counts differ from expected")
