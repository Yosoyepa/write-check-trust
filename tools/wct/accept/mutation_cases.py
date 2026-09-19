"""Stable historical and explicit typed acceptance-cell operators."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
import json
import re
from typing import Any

from tools.wct.accept.mutation_policy import validate_policy


def _changed(value: str) -> str:
    """Apply the exact historical scalar transformation."""
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return "1" if Decimal(value) == 0 else "0"
    return value + "__mutated"


def _typed_changed(value: str, declared_type: str) -> str:
    """Apply the explicit transformation already validated for one cell."""
    if declared_type == "bool":
        return "false" if value == "true" else "true"
    return value + "__typed"


def _changes(ir: dict[str, Any]) -> Iterator[tuple[int, int, str, str, str]]:
    """Yield selected coordinates and values while preserving the historical order."""
    if "mutation_policy" in ir:
        for cell in validate_policy(ir, ir["mutation_policy"]):
            scenario_index = cell["scenario"]
            row_index = cell["row"]
            field = cell["field"]
            value = ir["scenarios"][scenario_index]["examples"][row_index][field]
            yield scenario_index, row_index, field, value, _typed_changed(value, cell["type"])
        return
    for scenario_index, scenario in enumerate(ir["scenarios"]):
        for row_index, row in enumerate(scenario.get("examples", [])):
            for field, value in row.items():
                yield scenario_index, row_index, field, value, _changed(value)


def mutations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate selected cells once, preserving scenario, row, and field order.

    The absence of ``mutation_policy`` keeps the historical operator exactly.
    Any present value is validated before an explicit typed mutation is emitted.
    """
    generated: list[dict[str, Any]] = []
    for scenario_index, row_index, field, value, changed in _changes(ir):
        scenario = ir["scenarios"][scenario_index]
        clone = json.loads(json.dumps(ir))
        clone["scenarios"][scenario_index]["examples"][row_index][field] = changed
        generated.append(
            {
                "scenario": scenario["name"],
                "row": row_index,
                "field": field,
                "from": value,
                "to": changed,
                "ir": clone,
            }
        )
    return generated
