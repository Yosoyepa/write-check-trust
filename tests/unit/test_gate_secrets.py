"""Tests for G-SECRET parsing of detect-secrets --slim output."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.gate.runner import gate_secrets
from tools.wct.model import Status


def test_secrets_finding_without_line_number_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """--slim omits line_number; the gate must not crash on it."""
    document = json.dumps(
        {"results": {"src/config.py": [{"type": "Keyword", "hashed_secret": "x"}]}}
    )

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout=document, stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/detect-secrets")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_secrets(tmp_path)

    assert result.status is Status.FAIL
    assert "src/config.py:?: posible Keyword" in result.details


def test_secrets_finding_with_line_number_is_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    document = json.dumps({"results": {"src/config.py": [{"type": "Keyword", "line_number": 12}]}})

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        # Los artefactos regenerados por las propias herramientas no se
        # escanean: fingerprints del manifiesto (generated/) y SHAs de
        # procedencia que escribe ``wct ratchet record`` (baselines/).
        assert "--exclude-files" in command
        assert "^(governance/generated|governance/baselines)/" in command
        return subprocess.CompletedProcess(command, 0, stdout=document, stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/detect-secrets")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_secrets(tmp_path)

    assert result.status is Status.FAIL
    assert "src/config.py:12: posible Keyword" in result.details


def test_secrets_empty_stdout_means_no_findings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """With every finding audited in the baseline, detect-secrets prints nothing."""

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/detect-secrets")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_secrets(tmp_path)

    assert result.status is Status.PASS


def test_secrets_excludes_findings_already_audited_in_baseline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Triaged findings in .secrets.baseline do not block the gate.

    The baseline is read WITHOUT rewriting it (G-META-1 protects it).
    """
    document = json.dumps(
        {"results": {"src/config.py": [{"type": "Keyword", "hashed_secret": "dead"}]}}
    )
    (tmp_path / ".secrets.baseline").write_text(
        json.dumps({"results": {"src/config.py": [{"type": "Keyword", "hashed_secret": "dead"}]}}),
        encoding="utf-8",
    )

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        assert "--baseline" not in command
        return subprocess.CompletedProcess(command, 0, stdout=document, stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/detect-secrets")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_secrets(tmp_path)

    assert result.status is Status.PASS


def test_secrets_reports_findings_missing_from_baseline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    document = json.dumps(
        {"results": {"src/config.py": [{"type": "Keyword", "hashed_secret": "live"}]}}
    )
    (tmp_path / ".secrets.baseline").write_text(
        json.dumps({"results": {"src/config.py": [{"type": "Keyword", "hashed_secret": "dead"}]}}),
        encoding="utf-8",
    )

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout=document, stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/detect-secrets")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_secrets(tmp_path)

    assert result.status is Status.FAIL
    assert any("config.py" in line for line in result.details)


@pytest.mark.integration
def test_secrets_ignores_ratchet_baselines_but_scans_src(tmp_path: Path) -> None:
    """Repro del falso positivo por CLASE del incidente PR #32, sin fakes.

    ``wct ratchet record`` escribe SHAs de procedencia en
    governance/baselines/*.json: hex de alta entropía por diseño, igual que
    los fingerprints de governance/generated/. La exclusión es de clase de
    artefacto, no un agujero general: el MISMO hex plantado en src/ tiene
    que seguir disparando el gate. Corre con detect-secrets real (grupo
    quality, declarado en pyproject.toml), como test_ruff_profile.py corre
    ruff real: sin skipif, que erizaría el ratchet de supresiones.
    """
    # sha256 del string vacío: 64 chars hex con entropía sobre el límite 3.0.
    # Vive en tests/, fuera de SECRET_PATHS: el G-SECRET del repo no escanea
    # su propio instrumento.
    high_entropy_hex = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    # Todos los caminos que gate_secrets pasa a detect-secrets deben existir
    # y estar trackeados: detect-secrets enumera directorios vía git ls-files
    # (patrón documentado en tools/wct/selftest/fixtures_tools.py).
    tree = {
        "governance/baselines/dry.json": json.dumps({"commit": high_entropy_hex}),
        "src/config.py": f'COMMIT = "{high_entropy_hex}"\n',
        "src/example/__init__.py": "",
        "tools/wct/__init__.py": "",
        "governance/policy.yaml": "schema_version: 1\n",
        ".claude/settings.json": "{}\n",
        "skills/README.md": "",
        "plugins/README.md": "",
        ".github/workflows/ci.yaml": "",
        "pyproject.toml": "[project]\nname = 'victim'\n",
        ".pre-commit-config.yaml": "repos: []\n",
    }
    for relative, content in tree.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    for command in (("git", "init", "-q"), ("git", "add", "-A")):
        subprocess.run(command, cwd=tmp_path, check=True, capture_output=True)

    result = gate_secrets(tmp_path)

    assert result.status is Status.FAIL
    assert any("src/config.py" in line for line in result.details)
    assert not any("baselines" in line for line in result.details)
