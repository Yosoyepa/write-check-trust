from __future__ import annotations

from collections.abc import Mapping
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from tools.wct.config import find_root, load_config

PROHIBITED_BASH = [
    (re.compile(r"(?:^|\s)git\s+(?:commit|push)\b[^\n]*--no-verify\b"), "bypass --no-verify"),
    (re.compile(r"(?:^|\s)git\s+reset\s+--hard\b"), "git reset --hard"),
    (
        re.compile(r"(?:^|\s)(?:rm|find)\b[^\n]*(?:governance|\.git|integrity\.lock)"),
        "borrado de control plane",
    ),
    (
        re.compile(
            r"(?:sed\s+-i|perl\s+-pi|python[^\n]*-c)[^\n]*(?:governance|integrity\.lock|thresholds\.yaml)"
        ),
        "edición indirecta de control plane",
    ),
    (
        re.compile(r"(?:^|\s)(?:uv\s+run\s+)?wct\s+integrity\s+(?:lock|bless)\b"),
        "auto-aprobación de integridad; ejecútala un humano fuera del agente",
    ),
    (
        re.compile(r"(?:^|\s)(?:uv\s+run\s+)?wct\s+ratchet\s+record\b"),
        "auto-aprobación de baseline; ejecútala un humano fuera del agente",
    ),
    (
        re.compile(
            r"(?:^|\s)(?:uv\s+run\s+)?wct\s+mutate\s+update-manifest\b[^\n]*--approved-by\b"
        ),
        "auto-aprobación de manifiesto+lock; ejecútala un humano fuera del agente",
    ),
]


def _normalize_module_invocation(command: str) -> str:
    """Rewrite `python -m tools.wct ...` (and uv-run variants) to `wct ...`.

    Module-form invocations cannot dodge the prohibited-command patterns.
    """
    return re.sub(r"(?:^|\s)(?:\S*python\S*|uv\s+run)\s+-m\s+tools\.wct\b", " wct", command)


def _read() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise TypeError("hook input debe ser un objeto JSON")
    return value


def _block(reason: str) -> int:
    print(f"WCT BLOCK: {reason}", file=sys.stderr)
    return 2


def _path_is_protected(root: Path, raw: str) -> bool:
    _root, policy, _thresholds = load_config(root)
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError:
        return False
    return any(fnmatch.fnmatch(relative, pattern) for pattern in policy["paths"]["protected"])


def pre_tool_use(root: Path, payload: dict[str, Any]) -> int:
    name = str(payload.get("tool_name", ""))
    data = payload.get("tool_input") or {}
    if name in {"Edit", "Write", "NotebookEdit"}:
        target = str(data.get("file_path") or data.get("path") or "")
        if target and _path_is_protected(root, target):
            return _block(
                f"{target} está protegido; usa `wct integrity bless` con aprobación humana"
            )
    if name in {"Bash", "exec_command", "shell"}:
        command = _normalize_module_invocation(str(data.get("command") or data.get("cmd") or ""))
        for pattern, label in PROHIBITED_BASH:
            if pattern.search(command):
                return _block(f"comando prohibido: {label}")
    return 0


def _gate(root: Path, tier: str) -> tuple[bool, str]:
    """Ejecuta un tier del gate; retorna (pasó, salida recortada)."""
    command = [sys.executable, "-m", "tools.wct", "gate", "--tier", tier, "--quiet"]
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode == 0, output[-8000:]


def _run_gate(root: Path, tier: str) -> int:
    passed, output = _gate(root, tier)
    if not passed:
        return _block(output or f"tier {tier} falló")
    return 0


MAX_CONSECUTIVE_BLOCKS = 2


def _streak_path(root: Path) -> Path:
    return root / "build" / "hooks" / "guard-streak.json"


def _load_streak(root: Path) -> dict[str, int]:
    try:
        streak = json.loads(_streak_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return streak if isinstance(streak, dict) else {}


def _save_streak(root: Path, streak: dict[str, int]) -> None:
    path = _streak_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(streak), encoding="utf-8")


def _wants_observer(environ: Mapping[str, str] | None) -> bool:
    env = os.environ if environ is None else environ
    return env.get("WCT_HOOK_ROLE", "").strip().lower() == "observer"


def stop_gate(root: Path, event: str, environ: Mapping[str, str] | None = None) -> int:
    """Gate de Stop con las dos válvulas anti-deadlock.

    - WCT_HOOK_ROLE=observer: los roles de solo lectura (verificador,
      resumidor) advierten en vez de bloquear; no pueden reparar un árbol
      rojo que no escribieron.
    - Cortacircuitos: la tercera bloqueada consecutiva del mismo evento pasa
      con advertencia para que el agente pueda entregar el handoff. Un stop
      verde resetea la racha.
    """
    passed, output = _gate(root, "commit")
    if passed:
        _save_streak(root, {})
        return 0
    summary = output or "tier commit falló"
    if _wants_observer(environ):
        print(f"WCT WARN (observer): {summary}", file=sys.stderr)
        return 0
    streak = _load_streak(root)
    if streak.get(event, 0) >= MAX_CONSECUTIVE_BLOCKS:
        _save_streak(root, {})
        print(
            "WCT WARN (DEADLOCK GUARD): stop bloqueado "
            f"{MAX_CONSECUTIVE_BLOCKS + 1} veces seguidas con el tier commit en rojo; "
            "paso para no deadlockear al agente. El árbol SIGUE rojo: "
            "decláralo así en el handoff, no lo reportes como verde.",
            file=sys.stderr,
        )
        return 0
    streak[event] = streak.get(event, 0) + 1
    _save_streak(root, streak)
    return _block(summary)


def _dispatch_unsafe(event: str) -> int:
    root = find_root()
    payload = _read()
    normalized = event.lower().replace("_", "-")
    if normalized == "pre-tool-use":
        return pre_tool_use(root, payload)
    if normalized in {"stop", "subagent-stop"}:
        return stop_gate(root, normalized)
    gate_tier = {
        "post-tool-use": "fast",
        "post-tool-batch": "fast",
        "config-change": "fast",
    }.get(normalized)
    if gate_tier:
        return _run_gate(root, gate_tier)
    if normalized in {"session-start", "subagent-start", "post-compact"}:
        rules = (
            (root / "CLAUDE.md").read_text(encoding="utf-8")
            if (root / "CLAUDE.md").is_file()
            else "Run `wct rules build`."
        )
        print(json.dumps({"hookSpecificOutput": {"additionalContext": rules[:12000]}}))
    return 0


def dispatch(event: str) -> int:
    try:
        result = _dispatch_unsafe(event)
    except Exception as exc:  # deliberate fail-closed behavior
        return _block(f"guard crash ({event}): {type(exc).__name__}: {exc}")
    return result
