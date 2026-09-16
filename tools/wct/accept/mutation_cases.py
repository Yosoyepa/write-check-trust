"""Stable historical example-cell operators with a numeric-zero correction."""

from decimal import Decimal
import json
import re
from typing import Any


def _changed(value: str) -> str:
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return "1" if Decimal(value) == 0 else "0"
    return value + "__mutated"


def mutations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate each cell once, preserving scenario, row and field order."""
    generated: list[dict[str, Any]] = []
    for scenario_index, scenario in enumerate(ir["scenarios"]):
        for row_index, row in enumerate(scenario.get("examples", [])):
            for key, value in row.items():
                changed = _changed(value)
                clone = json.loads(json.dumps(ir))
                clone["scenarios"][scenario_index]["examples"][row_index][key] = changed
                generated.append(
                    {
                        "scenario": scenario["name"],
                        "row": row_index,
                        "field": key,
                        "from": value,
                        "to": changed,
                        "ir": clone,
                    }
                )
    return generated
