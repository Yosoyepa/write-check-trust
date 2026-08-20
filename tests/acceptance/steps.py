from __future__ import annotations

import re
from typing import Any

from example.adapters import MemoryInventoryRepository
from example.application import ReserveStock
from example.domain import Inventory


def execute_scenario(ir: dict[str, Any], scenario_index: int) -> None:
    scenario = ir["scenarios"][scenario_index]
    rows = scenario.get("examples") or [{}]
    for row in rows:
        context: dict[str, Any] = {}
        for step in [*ir.get("background", []), *scenario["steps"]]:
            text = step["text"]
            for key, value in row.items():
                text = text.replace(f"<{key}>", value)
            _execute_step(text, context)


def _execute_step(text: str, context: dict[str, Any]) -> None:
    if match := re.fullmatch(r'inventory contains "(\d+)" units', text):
        repository = MemoryInventoryRepository([Inventory("book", int(match.group(1)))])
        context["repository"] = repository
        context["use_case"] = ReserveStock(repository)
        return
    if match := re.fullmatch(r'I reserve "(\d+)" units', text):
        context["result"] = context["use_case"].execute("book", int(match.group(1)))
        return
    if match := re.fullmatch(r'"(\d+)" units remain', text):
        assert context["result"].units == int(match.group(1))
        return
    raise AssertionError(f"missing acceptance step: {text}")
