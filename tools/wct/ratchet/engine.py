from __future__ import annotations

import json
from pathlib import Path
import re
import tokenize
from typing import Any

from tools.wct.config import load_config

SUPPRESSION = re.compile(
    r"#\s*(?:noqa|type:\s*ignore|pragma:\s*no cover|nosec|fmt:\s*off)"
    r"|@pytest\.mark\.(?:skip|xfail)",
    re.I,
)
JUSTIFIED = re.compile(r"(?:—|--|because|reason:|justification:).{12,}", re.I)
DEBT = re.compile(r"\b(?:ponytail:|TODO|FIXME|HACK|XXX)\b", re.I)
DEBT_FORMAT = re.compile(
    r"(?:TODO|FIXME|HACK|XXX)\(owner=[^,]+,\s*issue=(?:#\d+|https?://[^)]+)\):|ponytail:\s*owner=[^,]+,\s*issue=(?:#\d+|https?://\S+)",
    re.I,
)
PROFILE = "governance/lint/ruff.toml"
IGNORES_SECTION = "[lint.per-file-ignores]"
IGNORES_ENTRY = re.compile(r'^\s*"(?P<glob>[^"]+)"\s*=\s*\[(?P<rules>[^\]]*)\]')
# La detección de deuda en comentarios del perfil es case-sensitive a
# propósito: la palabra española "todo" no debe leerse como marcador.
DEBT_STRICT = re.compile(r"\b(?:ponytail:|TODO|FIXME|HACK|XXX)\b")
DEBT_STRICT_FORMAT = re.compile(
    r"(?:TODO|FIXME|HACK|XXX)\(owner=[^,]+,\s*issue=(?:#\d+|https?://[^)]+)\):"
    r"|ponytail:\s*owner=[^,]+,\s*issue=(?:#\d+|https?://\S+)"
)


def source_files(root: Path) -> list[Path]:
    _root, policy, _thresholds = load_config(root)
    selected: list[Path] = []
    for key in ("source", "tests"):
        for directory in policy["paths"].get(key, []):
            selected.extend((root / directory).rglob("*.py"))
    return sorted(path for path in selected if path.is_file())


def suppression_findings(root: Path) -> list[str]:
    _root, _policy, thresholds = load_config(root)
    minimum = int(thresholds["suppressions"]["min_justification_chars"])
    findings: list[str] = []
    for path in source_files(root):
        for number, line in _policy_lines(path):
            if SUPPRESSION.search(line) and (
                not JUSTIFIED.search(line) or len(line.split("—")[-1].strip()) < minimum
            ):
                findings.append(
                    f"{path.relative_to(root)}:{number}: supresión sin regla y justificación"
                )
    return findings


def suppression_count(root: Path) -> int:
    """Count every suppression, including justified existing ones."""
    return sum(
        bool(SUPPRESSION.search(line))
        for path in source_files(root)
        for _number, line in _policy_lines(path)
    )


def debt_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for path in source_files(root):
        for number, line in _policy_lines(path):
            if DEBT.search(line) and not DEBT_FORMAT.search(line):
                findings.append(f"{path.relative_to(root)}:{number}: deuda sin owner + issue")
    return findings


def _policy_lines(path: Path) -> list[tuple[int, str]]:
    """Return comments and pytest decorators without matching string fixtures."""
    selected: list[tuple[int, str]] = []
    with path.open("rb") as stream:
        try:
            selected.extend(
                (token.start[0], token.string)
                for token in tokenize.tokenize(stream.readline)
                if token.type == tokenize.COMMENT
            )
        except (tokenize.TokenError, IndentationError):
            return selected
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("@pytest.mark."):
            selected.append((number, line))
    return selected


def baseline(root: Path, name: str) -> dict[str, Any]:
    value = json.loads((root / "governance/baselines" / f"{name}.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"baseline {name} debe ser un objeto JSON")
    return value


def compare(current: float, base: dict[str, Any]) -> bool:
    direction = base["direction"]
    value = float(base["value"])
    return current <= value if direction == "lower_is_better" else current >= value


def per_file_ignores(root: Path) -> list[dict[str, Any]]:
    """Entries of the canonical ruff profile's [lint.per-file-ignores].

    tomllib drops comments, so the raw text is parsed: each entry carries the
    contiguous comment block above it plus any trailing comment on its line.
    """
    profile = root / PROFILE
    if not profile.is_file():
        return []
    lines = profile.read_text(encoding="utf-8").splitlines()
    entries: list[dict[str, Any]] = []
    section = ""
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]") and "=" not in stripped:
            section = stripped
            continue
        if section != IGNORES_SECTION:
            continue
        match = IGNORES_ENTRY.match(line)
        if not match:
            continue
        comment_parts: list[str] = []
        trailing = line[match.end() :]
        if "#" in trailing:
            comment_parts.append(trailing.split("#", 1)[1])
        above = index - 1
        while above >= 0 and lines[above].strip().startswith("#"):
            comment_parts.append(lines[above].strip().lstrip("#"))
            above -= 1
        entries.append(
            {
                "glob": match.group("glob"),
                "line": index + 1,
                "rules": [
                    rule.strip().strip('"')
                    for rule in match.group("rules").split(",")
                    if rule.strip()
                ],
                "comment": " ".join(part.strip() for part in comment_parts).strip(),
            }
        )
    return entries


def ignores_findings(root: Path) -> list[str]:
    """Every per-file-ignores entry needs justification; debt needs owner+issue."""
    _root, _policy, thresholds = load_config(root)
    minimum = int(thresholds["suppressions"]["min_justification_chars"])
    findings: list[str] = []
    for entry in per_file_ignores(root):
        if len(entry["comment"]) < minimum:
            findings.append(
                f"{PROFILE}:{entry['line']}: {entry['glob']}: "
                f"exención sin justificación de al menos {minimum} caracteres"
            )
            continue
        comment = str(entry["comment"])
        if DEBT_STRICT.search(comment) and not DEBT_STRICT_FORMAT.search(comment):
            findings.append(f"{PROFILE}:{entry['line']}: {entry['glob']}: deuda sin owner + issue")
    return findings


def ignores_count(root: Path) -> int:
    """Exempt rule codes across all entries ("ALL" counts as one)."""
    return sum(len(entry["rules"]) for entry in per_file_ignores(root))
