import ast
from collections.abc import Callable
from pathlib import Path

from tools.wct.cognitive.engine import function_score, scan
from tools.wct.gate.runner import REGISTRY, TIERS
from tools.wct.model import Status


def first_function(source: str) -> ast.FunctionDef:
    """Extrae la primera función del fuente: el SUT la puntúa el assert."""
    return next(node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.FunctionDef))


def test_flat_branches_cost_one_each() -> None:
    source = (
        "def flat(a, b, c):\n"
        "    if a:\n"
        "        return 1\n"
        "    if b:\n"
        "        return 2\n"
        "    if c:\n"
        "        return 3\n"
        "    return 0\n"
    )

    assert function_score(first_function(source)) == 3


def test_nesting_multiplies_the_cost() -> None:
    source = (
        "def nested(a, b, c):\n"
        "    if a:\n"
        "        if b:\n"
        "            if c:\n"
        "                return 1\n"
        "    return 0\n"
    )

    assert function_score(first_function(source)) == 6


def test_elif_chain_stays_flat() -> None:
    source = (
        "def chain(a, b):\n"
        "    if a:\n"
        "        return 1\n"
        "    elif b:\n"
        "        return 2\n"
        "    else:\n"
        "        return 3\n"
    )

    assert function_score(first_function(source)) == 3


def test_deep_nesting_exceeds_where_same_cc_passes() -> None:
    """El caso que CC≤10 perdona y la cognitiva no: 6 niveles anidados."""
    lines = ["def deep(a):"]
    for level in range(6):
        lines.append(f"{'    ' * (level + 1)}if a > {level}:")
    lines.append("    " * 7 + "return 1")
    lines.append("    return 0")

    assert function_score(first_function("\n".join(lines) + "\n")) == 21


def test_boolean_sequences_count_once_each() -> None:
    one = "def f(a, b, c):\n    if a and b and c:\n        return 1\n"
    two = "def f(a, b, c):\n    if (a and b) or c:\n        return 1\n"

    assert function_score(first_function(one)) == 2
    assert function_score(first_function(two)) == 3


def test_ternary_loop_and_handler_increment() -> None:
    source = (
        "def mixed(items):\n"
        "    value = 1 if items else 0\n"
        "    for item in items:\n"
        "        try:\n"
        "            value += item\n"
        "        except ValueError:\n"
        "            value = 0\n"
        "    return value\n"
    )

    assert function_score(first_function(source)) == 4


def test_lambda_nests_for_its_contents() -> None:
    source = "def f(g):\n    pick = lambda x: 1 if x else 0\n    return pick(g)\n"

    assert function_score(first_function(source)) == 2


def test_recursion_adds_one() -> None:
    source = "def f(n):\n    return 1 if n <= 0 else f(n - 1)\n"

    assert function_score(first_function(source)) == 2


def test_scan_reports_only_functions_over_limit(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    lines = ["def deep(a):"]
    for level in range(6):
        lines.append(f"{'    ' * (level + 1)}if a > {level}:")
    lines.append("    " * 7 + "return 1")
    lines.append("    return 0")
    (root / "src/deep.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (root / "src/flat.py").write_text(
        "def flat(a, b):\n    if a:\n        return 1\n    if b:\n        return 2\n",
        encoding="utf-8",
    )

    report = scan(root)

    assert report["limit"] == 15
    assert [item["function"] for item in report["functions"]] == ["deep"]
    assert report["functions"][0]["score"] == 21


def test_gate_blocks_on_deep_nesting(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    (root / "src/deep.py").write_text(
        "def deep(a):\n"
        "    if a > 0:\n"
        "        if a > 1:\n"
        "            if a > 2:\n"
        "                if a > 3:\n"
        "                    if a > 4:\n"
        "                        if a > 5:\n"
        "                            return 1\n"
        "    return 0\n",
        encoding="utf-8",
    )

    result = REGISTRY["G-COGNITIVE"](root)

    assert result.status is Status.FAIL
    assert "deep" in result.summary


def test_cognitive_gate_is_in_commit_pr_and_full_tiers() -> None:
    assert "G-COGNITIVE" in TIERS["commit"]
    assert "G-COGNITIVE" in TIERS["pr"]
    assert "G-COGNITIVE" in TIERS["full"]
    assert "G-COGNITIVE" not in TIERS["fast"]
