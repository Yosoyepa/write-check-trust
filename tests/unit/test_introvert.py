from collections.abc import Callable
from pathlib import Path

from tools.wct.introvert.analyzer import analyze


def test_introverted_literal_assertion_is_flagged(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    test = root / "tests/test_bad.py"
    test.write_text("def test_bad():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    report = analyze(root, [test])

    assert report["counts"] == {"introverted": 1}


def test_assertion_derived_from_sut_is_extroverted(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    test = root / "tests/test_good.py"
    test.write_text(
        """from example.domain import calculate

def test_good():
    result = calculate()
    assert result == 4
""",
        encoding="utf-8",
    )

    report = analyze(root, [test])

    assert report["counts"] == {"extroverted": 1}
