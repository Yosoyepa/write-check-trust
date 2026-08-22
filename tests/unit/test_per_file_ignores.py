from collections.abc import Callable
from pathlib import Path

from tools.wct.ratchet.engine import ignores_count, ignores_findings

RUFF_TOML = """[lint]
exclude = ["build"]

[lint.per-file-ignores]
# Los tests usan assert a propósito y sin docstring por caso.
"tests/**" = ["S101", "D103"]
"src/legacy.py" = ["C901"]
# TODO(owner=yosoyepa, issue=#12): particionar este analizador.
"tools/wct/big.py" = ["C901", "PLR0912"]
# TODO: refactor pendiente
"tools/wct/other.py" = ["PLR0915"]

[lint.mccabe]
max-complexity = 10
"""


def _with_profile(root: Path, content: str) -> Path:
    directory = root / "governance/lint"
    directory.mkdir(parents=True)
    profile = directory / "ruff.toml"
    profile.write_text(content, encoding="utf-8")
    return root


def test_entry_without_comment_is_a_finding(project_factory: Callable[..., Path]) -> None:
    root = _with_profile(project_factory(), RUFF_TOML)

    findings = ignores_findings(root)

    assert any("src/legacy.py" in finding for finding in findings)
    assert any("sin justificación" in finding for finding in findings)


def test_justified_permanent_entry_is_not_a_finding(
    project_factory: Callable[..., Path],
) -> None:
    root = _with_profile(project_factory(), RUFF_TOML)

    findings = ignores_findings(root)

    assert not any("tests/**" in finding for finding in findings)


def test_debt_marker_requires_owner_and_issue(project_factory: Callable[..., Path]) -> None:
    root = _with_profile(project_factory(), RUFF_TOML)

    findings = ignores_findings(root)

    assert any("tools/wct/other.py" in finding for finding in findings)
    assert any("owner" in finding for finding in findings)
    assert not any("tools/wct/big.py" in finding for finding in findings)


def test_count_sums_listed_codes(project_factory: Callable[..., Path]) -> None:
    root = _with_profile(project_factory(), RUFF_TOML)

    assert ignores_count(root) == 6


def test_missing_profile_is_not_an_error(project_factory: Callable[..., Path]) -> None:
    root = project_factory()

    assert ignores_findings(root) == []
    assert ignores_count(root) == 0


def test_short_comment_below_minimum_is_a_finding(
    project_factory: Callable[..., Path],
) -> None:
    content = '[lint.per-file-ignores]\n"src/x.py" = ["S101"]  # ok\n'
    root = _with_profile(project_factory(), content)

    findings = ignores_findings(root)

    assert len(findings) == 1


def test_findings_name_the_profile_and_line(project_factory: Callable[..., Path]) -> None:
    root = _with_profile(project_factory(), RUFF_TOML)

    findings = ignores_findings(root)

    assert any(finding.startswith("governance/lint/ruff.toml:7:") for finding in findings)
