"""Red team del instrumento: siembra defectos y exige que el arnés los cace.

Despachador por arnés (ADR-C-01 §1) sobre la UNIÓN de
``quality/redteam/cases.yaml`` + ``cases-engine.yaml`` + ``cases-tool.yaml``
(los ausentes se toleran y se reportan):

- ``gate-engine``: importa el motor productivo del caso (misma función que su
  gate usa) y lo corre sobre el fixture que planta el defecto.
- ``gate-tool``: invoca ``REGISTRY[gate]`` sobre el fixture; herramienta
  ausente → SKIP visible con la herramienta nombrada, nunca failure.
- ``hook``: ejercita ``pre_tool_use`` real (casos F14/F15).
- ``heuristic``: reconocedores residuales declarados (ADR-C-02). F9-b fue
  redimido en la PR #31 y corre como gate-engine; F11-b en PR-D (ADR-D-02)
  y corre como gate-tool.

Un caso convertido que el motor NO caza queda en rojo: es un hallazgo del
instrumento, no se ajusta el fixture hasta que pase (ADR-C-01 §5).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
import importlib
from pathlib import Path
import shutil
import tempfile
from typing import Any

from tools.wct.config import load_yaml
from tools.wct.gate.runner import REGISTRY
from tools.wct.hooks.guard import pre_tool_use
from tools.wct.model import Status
from tools.wct.selftest.fixtures_engine import BUILDERS as ENGINE_BUILDERS

BLOCK_EXIT = 2
CASES_PER_MODE = 2
FAILURE_MODES = tuple(f"F{index}" for index in range(1, 16))
CASE_FILES = ("cases.yaml", "cases-engine.yaml", "cases-tool.yaml")
SCRATCH = Path("build/tmp")
CAUGHT, SKIPPED, FAILED = "caught", "skipped", "failed"

Builder = Callable[[Path], Path]
Engine = Callable[[Path], Any]


def meets(report: Any, expect: str) -> bool:
    """Evalúa la condición de caza del caso sobre el reporte del motor.

    Formato ``clave.anidada>=N`` para reportes dict (una lista cuenta sus
    elementos) o ``>=N`` cuando el motor retorna un escalar. Una condición sin
    comparador es inválida: retorna False y el caso queda en rojo.
    """
    key, separator, number = expect.partition(">=")
    if not separator:
        return False
    actual = _measure(_lookup(report, key.strip()))
    return float(actual) >= float(number)


def _lookup(report: Any, key: str) -> Any:
    for part in filter(None, key.split(".")):
        report = report[part]
    return report


def _measure(value: Any) -> Any:
    return len(value) if isinstance(value, (list, tuple, set)) else value


def _resolve(dotted: str) -> Engine:
    """Importa el motor productivo por ruta punteada."""
    module_name, _, attribute = dotted.rpartition(".")
    engine: Engine = getattr(importlib.import_module(module_name), attribute)
    return engine


def _builders() -> dict[str, Builder]:
    """Unión de builders engine + tool; fixtures_tools es opcional hasta que R2 aterrice."""
    merged = dict(ENGINE_BUILDERS)
    merged.update(_tool_builders())
    return merged


def _tool_builders() -> dict[str, Builder]:
    try:
        module = importlib.import_module("tools.wct.selftest.fixtures_tools")
    except ModuleNotFoundError:
        return {}
    builders: dict[str, Builder] = dict(module.BUILDERS)
    return builders


def _load_union(root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Casos de la unión de archivos; los ausentes se toleran y se reportan."""
    directory = root / "quality" / "redteam"
    cases: list[dict[str, Any]] = []
    loaded: list[str] = []
    missing: list[str] = []
    for name in CASE_FILES:
        path = directory / name
        if path.is_file():
            cases.extend(load_yaml(path).get("cases", []))
            loaded.append(name)
        else:
            missing.append(name)
    return cases, loaded, missing


def _mode_gaps(cases: list[dict[str, Any]], missing: list[str]) -> list[str]:
    """Exige >=2 casos por modo sobre la unión.

    Con archivos ausentes solo se exigen los modos que alcanzaron el par: la
    baja puede vivir en el archivo ausente, que ya se reporta por su nombre.
    Con el inventario completo se exigen los quince modos F1-F15.
    """
    counts = Counter(str(case.get("failure_mode")) for case in cases)
    required = (
        list(FAILURE_MODES)
        if not missing
        else [mode for mode in counts if counts[mode] >= CASES_PER_MODE]
    )
    return [
        f"{mode}: requiere al menos dos casos" for mode in required if counts[mode] < CASES_PER_MODE
    ]


def _reject(root: Path, checker: str, payload: str) -> bool:
    """Reconocedor residual: heurísticas declaradas y casos hook.

    Despacho por tabla: cada checker declarado (ADR-C-02 y su addendum) es
    una función pequeña; un checker sin entrada en la tabla no rechaza nada.
    """
    resolver = _CHECKERS.get(checker)
    return resolver is not None and resolver(root, payload)


def _reject_testless(_root: Path, payload: str) -> bool:
    """F2-a/F4-b: producción sin tests; solo la mutación real lo expone."""
    return "production=true" in payload and "tests=false" in payload


def _reject_hardcoded(_root: Path, payload: str) -> bool:
    """F2-b: valor hardcodeado; pytest lo aprueba por diseño."""
    return "expected fixture" in payload


def _reject_survivor(_root: Path, payload: str) -> bool:
    """F5-b: mutante superviviente, output de una corrida inexistente."""
    return int(payload.split("=", 1)[1]) > 0


def _reject_protected_write(root: Path, payload: str) -> bool:
    """F14: escritura en ruta protegida; la bloquea pre_tool_use."""
    request = {"tool_name": "Edit", "tool_input": {"file_path": str(root / payload)}}
    return pre_tool_use(root, request) == BLOCK_EXIT


def _reject_forbidden_command(root: Path, payload: str) -> bool:
    """F15: comando prohibido; lo bloquea pre_tool_use."""
    request = {"tool_name": "Bash", "tool_input": {"command": payload}}
    return pre_tool_use(root, request) == BLOCK_EXIT


_CHECKERS: dict[str, Callable[[Path, str], bool]] = {
    "testless": _reject_testless,
    "hardcoded": _reject_hardcoded,
    "survivor": _reject_survivor,
    "protected-write": _reject_protected_write,
    "forbidden-command": _reject_forbidden_command,
}


def _run_engine(
    case: dict[str, Any],
    builders: dict[str, Builder],
    scratch: Path,
) -> tuple[str, str]:
    """Corre el motor productivo del caso sobre su fixture aislado."""
    case_id = str(case.get("id"))
    builder = builders.get(case_id)
    if builder is None:
        return FAILED, f"{case_id}: sin builder para el caso"
    try:
        engine = _resolve(str(case.get("engine")))
        with tempfile.TemporaryDirectory(dir=scratch, prefix=f"redteam-{case_id}-") as directory:
            report = engine(builder(Path(directory)))
    except Exception as exc:  # un motor que crash contra el adversario es hallazgo, no skip
        return FAILED, f"{case_id}: {type(exc).__name__}: {exc}"
    if meets(report, str(case.get("expect"))):
        return CAUGHT, ""
    return FAILED, f"{case_id}: el motor no reportó el defecto ({case.get('expect')})"


def _run_tool(case: dict[str, Any], builders: dict[str, Builder]) -> tuple[str, str]:
    """Invoca la función de gate sobre el fixture; el caso caza si el gate FALLA.

    semgrep/detect-secrets enumeran archivos vía git: un fixture dentro del
    repo es invisible para ellos (untracked). El tmpdir del arnés tool vive
    fuera del árbol del repo; el de engine se queda en build/tmp (PROC-007;
    los engines no usan git).
    """
    tool = str(case.get("tool", ""))
    if shutil.which(tool) is None:
        return SKIPPED, f"herramienta ausente: {tool}"
    case_id = str(case.get("id"))
    builder = builders.get(case_id)
    if builder is None:
        return FAILED, f"{case_id}: sin builder para el caso"
    return _gate_on_fixture(case, case_id, builder)


def _gate_on_fixture(
    case: dict[str, Any],
    case_id: str,
    builder: Builder,
) -> tuple[str, str]:
    """Corre el gate del caso sobre su fixture y traduce el GateResult a veredicto."""
    gate = REGISTRY[str(case.get("gate"))]
    try:
        with tempfile.TemporaryDirectory(prefix=f"redteam-{case_id}-") as directory:
            result = gate(builder(Path(directory)))
    except Exception as exc:
        return FAILED, f"{case_id}: {type(exc).__name__}: {exc}"
    if result.status is Status.FAIL:
        return CAUGHT, ""
    return FAILED, f"{case_id}: el gate no cazó el defecto ({result.summary})"


def _reject_verdict(root: Path, case: dict[str, Any], gate: str) -> tuple[str, str]:
    """Veredicto de los arneses hook/heuristic: decide el reconocedor residual."""
    if _reject(root, str(case.get("checker")), str(case.get("payload"))):
        return CAUGHT, ""
    return FAILED, f"{case.get('id')}: dejó de ser rechazado por {gate}"


def _dispatch_case(
    root: Path,
    case: dict[str, Any],
    builders: dict[str, Builder],
    scratch: Path,
) -> tuple[str, str]:
    """Despacha un caso según su arnés; retorna (estado, detalle)."""
    gate = str(case.get("gate", ""))
    if gate not in REGISTRY:
        return FAILED, f"{case.get('id')}: gate inexistente {gate}"
    harness = str(case.get("harness", ""))
    if harness == "gate-engine":
        verdict = _run_engine(case, builders, scratch)
    elif harness == "gate-tool":
        verdict = _run_tool(case, builders)
    elif harness in {"hook", "heuristic"}:
        verdict = _reject_verdict(root, case, gate)
    else:
        return FAILED, f"{case.get('id')}: arnés desconocido {harness}"
    return verdict


def _report(
    evaluated: int,
    counts: Counter[str],
    skips: list[str],
    loaded: list[str],
    missing: list[str],
) -> None:
    """Imprime el resumen honesto por arnés (ADR-C-01 §4)."""
    absent = f"; ausentes: {', '.join(missing)}" if missing else ""
    print(f"red team: cargados {', '.join(loaded)}{absent}")
    for skip in skips:
        print(f"red team SKIP: {skip}")
    print(
        f"{sum(counts.values())}/{evaluated} rechazados · {counts['gate-engine']} gate-engine · "
        f"{counts['gate-tool']} gate-tool · {counts['hook']} hook · "
        f"{counts['heuristic']} heuristic (declarados) · {len(skips)} SKIP"
    )


def run(root: Path) -> tuple[int, list[str]]:
    """Ejecuta la unión de casos adversariales; retorna (casos evaluados, fallos)."""
    cases, loaded, missing = _load_union(root)
    if not cases:
        return 0, [f"quality/redteam: sin archivos de casos ({', '.join(CASE_FILES)})"]
    failures = _mode_gaps(cases, missing)
    builders = _builders()
    scratch = root / SCRATCH
    scratch.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    skips: list[str] = []
    for case in cases:
        state, detail = _dispatch_case(root, case, builders, scratch)
        if state == CAUGHT:
            counts[str(case.get("harness"))] += 1
        elif state == SKIPPED:
            skips.append(f"{case.get('id')}: {detail}")
        else:
            failures.append(detail)
    evaluated = len(cases) - len(skips)
    _report(evaluated, counts, skips, loaded, missing)
    return evaluated, failures
