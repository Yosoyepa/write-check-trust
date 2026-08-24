from __future__ import annotations

import ast
from pathlib import Path

from tools.wct.gate.runner import TIERS
from tools.wct.lcom.engine import class_lcom4, scan
from tools.wct.ratchet.engine import baseline


def first_class(source: str) -> ast.ClassDef:
    """Extrae el primer nodo ClassDef del fuente."""
    return next(node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef))


def test_two_disjoint_groups_has_lcom4_two() -> None:
    source = (
        "class TwoGroups:\n"
        "    def m1(self):\n"
        "        return self.a\n"
        "    def m2(self):\n"
        "        return self.a\n"
        "    def m3(self):\n"
        "        return self.b\n"
        "    def m4(self):\n"
        "        return self.b\n"
    )

    assert class_lcom4(first_class(source)) == 2


def test_cohesive_class_has_lcom4_one() -> None:
    source = (
        "class Cohesive:\n"
        "    def m1(self):\n"
        "        return self.a\n"
        "    def m2(self):\n"
        "        return self.a + self.b\n"
        "    def m3(self):\n"
        "        return self.b\n"
    )

    assert class_lcom4(first_class(source)) == 1


def test_orchestrator_methods_calling_each_other_has_lcom4_one() -> None:
    source = (
        "class Orchestrator:\n"
        "    def run(self):\n"
        "        self.step1()\n"
        "        self.step2()\n"
        "    def step1(self):\n"
        "        pass\n"
        "    def step2(self):\n"
        "        pass\n"
    )

    assert class_lcom4(first_class(source)) == 1


def test_dataclass_and_protocol_are_excluded() -> None:
    dataclass_source = (
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Data:\n"
        "    a: int\n"
        "    b: int\n"
        "    def m1(self): return self.a\n"
        "    def m2(self): return self.b\n"
        "    def m3(self): return self.a + self.b\n"
    )
    protocol_source = (
        "from typing import Protocol\n"
        "class Port(Protocol):\n"
        "    def m1(self): ...\n"
        "    def m2(self): ...\n"
        "    def m3(self): ...\n"
    )

    assert class_lcom4(first_class(dataclass_source)) is None
    assert class_lcom4(first_class(protocol_source)) is None


def test_class_with_fewer_than_three_methods_is_excluded() -> None:
    source = (
        "class Small:\n"
        "    def m1(self):\n"
        "        return self.a\n"
        "    def m2(self):\n"
        "        return self.b\n"
    )

    assert class_lcom4(first_class(source)) is None


def test_repo_sum_matches_baseline_number() -> None:
    report = scan(Path())
    base = baseline(Path(), "lcom-classes")
    violators = [item for item in report["classes"] if item["lcom4"] >= 2]
    assert len(violators) == base["value"]


def test_lcom_gate_is_in_full_tier() -> None:
    assert "G-LCOM" in TIERS["full"]
    assert "G-LCOM" not in TIERS["commit"]
    assert "G-LCOM" not in TIERS["fast"]
