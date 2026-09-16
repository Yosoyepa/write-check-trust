"""Characterized Gherkin parsing, deliberately retaining issue35 limitations."""

from pathlib import Path
import re
from typing import Any

from tools.wct.config import ConfigError, find_root

STEP = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.+?)\s*$")

# TODO(owner=yosoyepa, issue=#35): Narrative remains unsupported under Feature.


def _name(line: str) -> str:
    return line.split(":", 1)[1].strip()


class _Parser:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.feature = ""
        self.background: list[dict[str, Any]] = []
        self.scenarios: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.headers: list[str] = []
        self.in_examples = False

    def _scenario(self, line: str, number: int) -> None:
        self.current = {
            "name": _name(line),
            "line": number,
            "outline": line.startswith("Scenario Outline:"),
            "steps": [],
            "examples": [],
        }
        self.scenarios.append(self.current)
        self.in_examples = False

    def _examples(self, number: int) -> None:
        if self.current is None or self.current.get("name") == "Background":
            raise ValueError(f"{self.path}:{number}: Examples fuera de Scenario Outline")
        self.in_examples = True
        self.headers = []

    def _header(self, line: str, number: int) -> bool:
        if line.startswith("Feature:"):
            self.feature = _name(line)
        elif line.startswith("Background:"):
            self.current = {
                "name": "Background",
                "line": number,
                "steps": self.background,
                "examples": [],
            }
            self.in_examples = False
        elif line.startswith(("Scenario:", "Scenario Outline:")):
            self._scenario(line, number)
        elif line.startswith("Examples:"):
            self._examples(number)
        else:
            return False
        return True

    def _row(self, line: str, number: int) -> None:
        values = [value.strip() for value in line.strip("|").split("|")]
        if not self.headers:
            self.headers = values
            return
        if len(values) != len(self.headers):
            raise ValueError(f"{self.path}:{number}: fila Examples de longitud incorrecta")
        if self.current is None:
            raise ValueError(f"{self.path}:{number}: fila Examples sin escenario")
        self.current["examples"].append(dict(zip(self.headers, values, strict=True)))

    def _target(self) -> list[dict[str, Any]] | None:
        if self.current is None:
            return None
        if self.current.get("name") == "Background":
            return self.background
        steps: list[dict[str, Any]] = self.current["steps"]
        return steps

    def _step(self, raw: str, number: int) -> None:
        match = STEP.match(raw)
        if match is None:
            raise ValueError(f"{self.path}:{number}: sintaxis Gherkin no soportada: {raw.strip()}")
        target = self._target()
        if target is None:
            raise ValueError(f"{self.path}:{number}: step fuera de scenario")
        target.append({"keyword": match.group(1), "text": match.group(2), "line": number})

    def consume(self, raw: str, number: int) -> None:
        line = raw.strip()
        if not line or line.startswith(("#", "@")):
            return
        if self._header(line, number):
            return
        if self.in_examples and line.startswith("|"):
            self._row(line, number)
        else:
            self._step(raw, number)

    def result(self) -> dict[str, Any]:
        if not self.feature or not self.scenarios:
            raise ValueError(f"{self.path}: Feature y al menos un Scenario son obligatorios")
        return {
            "schema_version": 1,
            "feature": self.feature,
            "source": _relative_source(self.path),
            "background": self.background,
            "scenarios": self.scenarios,
        }


def parse_feature(path: Path) -> dict[str, Any]:
    """Parse the historical dialect without broadening accepted syntax."""
    parser = _Parser(path)
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parser.consume(raw, number)
    return parser.result()


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
