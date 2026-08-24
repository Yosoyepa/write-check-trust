from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from tools.wct.dry.tpl import analyze_template
from tools.wct.gate.runner import TIERS


def test_identical_functions_with_different_names_and_literals_form_cluster(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    f1 = (
        "def process_user(user_id, count):\n"
        "    limit = 100\n"
        "    if count > limit:\n"
        '        log_warning("overflow", user_id)\n'
        "        return None\n"
        "    return count * 2\n"
    )
    f2 = (
        "def handle_order(order_ref, amount):\n"
        "    maximum = 500\n"
        "    if amount > maximum:\n"
        '        notify_error("exceeded", order_ref)\n'
        "        return None\n"
        "    return amount * 3\n"
    )
    (root / "src/users.py").write_text(f1, encoding="utf-8")
    (root / "src/orders.py").write_text(f2, encoding="utf-8")

    report = analyze_template(root)

    assert len(report["candidates"]) == 1
    candidate = report["candidates"][0]
    assert candidate["score"] >= 0.90


def test_functions_with_different_flow_do_not_cluster(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    f1 = (
        "def compute_branch(x, y):\n"
        "    if x > 0:\n"
        "        return y + 1\n"
        "    else:\n"
        "        return y - 1\n"
    )
    f2 = (
        "def compute_loop(items, factor):\n"
        "    total = 0\n"
        "    for item in items:\n"
        "        total += item * factor\n"
        "    return total\n"
    )
    (root / "src/branch.py").write_text(f1, encoding="utf-8")
    (root / "src/loop.py").write_text(f2, encoding="utf-8")

    report = analyze_template(root)

    assert report["candidates"] == []


def test_tests_directory_is_excluded_from_template_dry(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    f1 = (
        "def helper_one(a, b):\n"
        "    limit = 10\n"
        "    if a > limit:\n"
        "        return b\n"
        "    return None\n"
    )
    (root / "tests/test_helper1.py").write_text(f1, encoding="utf-8")
    (root / "tests/test_helper2.py").write_text(f1, encoding="utf-8")

    report = analyze_template(root)

    assert report["candidates"] == []


def test_similarity_under_threshold_does_not_trigger(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    f1 = (
        "def fn_a(items, flag):\n"
        "    result = []\n"
        "    for item in items:\n"
        "        if flag and item > 0:\n"
        "            result.append(item * 2)\n"
        "    return result\n"
    )
    f2 = (
        "def fn_b(values, mode):\n"
        "    out = []\n"
        "    try:\n"
        "        for val in values:\n"
        "            out.append(val)\n"
        "    except Exception:\n"
        "        pass\n"
        "    return out\n"
    )
    (root / "src/a.py").write_text(f1, encoding="utf-8")
    (root / "src/b.py").write_text(f2, encoding="utf-8")

    report = analyze_template(root)

    assert all(c["score"] >= 0.90 for c in report["candidates"])
    assert len(report["candidates"]) == 0


def test_dry_tpl_gate_is_in_full_tier() -> None:
    assert "G-DRY-TPL" in TIERS["full"]
    assert "G-DRY-TPL" not in TIERS["commit"]
    assert "G-DRY-TPL" not in TIERS["fast"]
