"""Execute the approved typed acceptance-mutation operator feature."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any

from tools.wct.accept.mutation_policy import MutationPolicyError, load_policy
from tools.wct.accept.pipeline import mutations, parse_feature

_ROOT = Path(__file__).resolve().parents[2]
_TEMPORARY_ROOT = _ROOT / "build" / "tmp"
StepHandler = Callable[[dict[str, Any], tuple[str, ...]], None]
_LOADER_DEFECTS = frozenset(
    {"duplicate-json-key", "nan", "wrong-hash", "missing-policy-file", "invalid-utf8"}
)
_ROOT_POLICY_DEFECTS: dict[str, tuple[str, object]] = {
    "schema-bool": ("schema_version", True),
    "schema-unknown": ("schema_version", 2),
    "extra-key": ("extra", "forbidden"),
    "wrong-source": ("source", "features/wrong.feature"),
}
_CELL_POLICY_DEFECTS: dict[str, tuple[str, object]] = {
    "unknown-type": ("type", "int"),
    "unknown-column": ("field", "unknown"),
    "unknown-row": ("row", 1),
    "unknown-scenario": ("scenario", 1),
}


def execute_scenario(ir: dict[str, Any], scenario_index: int) -> None:
    """Execute every example row of the typed-operator scenario.

    Args:
        ir: Parsed feature IR dispatched by the exact feature source guard.
        scenario_index: Zero-based index of the scenario to execute.

    Raises:
        AssertionError: If the approved vocabulary, sequence, or observed result differs.
        MutationPolicyError: If an unexpected policy failure escapes an invalid-policy assertion.
    """
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
    """Dispatch one exact step from the three approved scenario vocabularies."""
    for pattern, handler in _HANDLERS:
        match = pattern.fullmatch(text)
        if match is not None:
            handler(context, match.groups())
            return
    raise AssertionError(f"unknown typed operator step: {text}")


def _given_typed_row(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Create the one-cell synthetic IR used to exercise a declared type."""
    declared_type, value = values
    if declared_type not in {"bool", "str"}:
        raise AssertionError(f"unknown typed operator type: {declared_type}")
    context["ir"] = _single_cell_ir(value)
    context["declared_type"] = declared_type


def _when_enumerate(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Attach an explicit policy only for the requested activation mode."""
    (activation,) = values
    ir = _required(context, "ir")
    if activation == "explicit":
        ir["mutation_policy"] = _policy_for(ir, _required(context, "declared_type"))
    elif activation != "absent":
        raise AssertionError(f"unknown typed operator activation: {activation}")
    context["inventory"] = mutations(ir)


def _then_result(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Compare actual product mutations against the feature's expected value and count."""
    expected, planned_text = values
    inventory = _required(context, "inventory")
    planned = _integer(planned_text, "planned cells")
    if len(inventory) != planned or not inventory or inventory[0]["to"] != expected:
        actual = inventory[0]["to"] if inventory else None
        message = (
            "typed mutation result differs: "
            f"expected {expected!r}, got {actual!r}; planned {planned}"
        )
        raise AssertionError(message)


def _given_invalid_policy(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Prepare a valid baseline IR whose policy will be made defective on demand."""
    (defect,) = values
    context["defect"] = defect
    context["ir"] = _single_cell_ir("true")


def _when_attempt_policy(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Invoke the real loader or mutator, catching only the documented policy error."""
    if values:
        raise AssertionError("invalid typed operator activation step")
    defect = _required(context, "defect")
    context["inventory"] = None
    try:
        if defect in _LOADER_DEFECTS:
            context["inventory"] = _load_defective_policy(defect)
        else:
            ir = _required(context, "ir")
            ir["mutation_policy"] = _defective_policy(ir, defect)
            context["inventory"] = mutations(ir)
    except MutationPolicyError as error:
        context["error"] = error
    else:
        context["error"] = None


def _then_policy_error(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Require the expected error class and reject any successfully produced inventory."""
    (expected,) = values
    error = _required(context, "error")
    if error is None:
        raise AssertionError("invalid policy approved inventory")
    if type(error).__name__ != expected:
        raise AssertionError(f"unexpected policy error: {type(error).__name__}")
    if context.get("inventory") is not None:
        raise AssertionError("invalid policy produced an inventory")


def _given_inventory(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Build the fixed twelve-row, three-column fixture used for independent inventory checks."""
    rows_text, columns_text = values
    rows = _integer(rows_text, "rows")
    columns = _integer(columns_text, "columns")
    if rows != 12 or columns != 3:
        raise AssertionError("unknown typed operator inventory shape")
    examples = []
    cells = []
    for row_index in range(rows):
        expected = "caller-supplied-unverified" if row_index == 10 else "true"
        examples.append(
            {"case": f"PA{row_index + 1:02d}", "field": "expected", "expected": expected}
        )
        cells.append(
            {
                "scenario": 0,
                "row": row_index,
                "field": "expected",
                "type": "str" if row_index == 10 else "bool",
            }
        )
    ir: dict[str, Any] = {
        "schema_version": 1,
        "feature": "typed inventory",
        "source": "features/typed-inventory.fixture",
        "background": [],
        "scenarios": [
            {
                "name": "typed inventory",
                "line": 1,
                "outline": True,
                "steps": [],
                "examples": examples,
            }
        ],
    }
    context["ir"] = ir
    context["policy"] = _policy_for(ir, "bool", cells)


def _when_select(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Select the supported number of columns and enumerate through the real operator."""
    eligible_text, activation = values
    if _integer(eligible_text, "eligible columns") != 1:
        raise AssertionError("unknown typed operator eligible-column count")
    ir = _required(context, "ir")
    if activation == "explicit":
        ir["mutation_policy"] = _required(context, "policy")
    elif activation != "absent":
        raise AssertionError(f"unknown typed operator activation: {activation}")
    context["baseline"] = json.loads(json.dumps(ir))
    context["inventory"] = mutations(ir)


def _then_inventory(context: dict[str, Any], values: tuple[str, ...]) -> None:
    """Verify independent identity count and that each clone changes exactly its own cell."""
    (planned_text,) = values
    planned = _integer(planned_text, "planned identities")
    inventory = _required(context, "inventory")
    baseline = _required(context, "baseline")
    identities = [(item["scenario"], item["row"], item["field"]) for item in inventory]
    if len(inventory) != planned or len(set(identities)) != len(inventory):
        raise AssertionError("typed mutation identities differ from the independent inventory")
    for item in inventory:
        expected = json.loads(json.dumps(baseline))
        expected["scenarios"][0]["examples"][item["row"]][item["field"]] = item["to"]
        original = baseline["scenarios"][0]["examples"][item["row"]][item["field"]]
        if item["from"] != original or item["ir"] != expected:
            raise AssertionError("typed mutation clone changes more than its declared cell")
    if _required(context, "ir") != baseline:
        raise AssertionError("typed mutation changed its input IR")


def _single_cell_ir(value: str) -> dict[str, Any]:
    """Return the Gherkin fixture IR whose policy controls its sole string cell."""
    return {
        "schema_version": 1,
        "feature": "typed operator fixture",
        "source": "features/typed-operator.fixture",
        "background": [],
        "scenarios": [
            {
                "name": "typed operator fixture",
                "line": 1,
                "outline": True,
                "steps": [],
                "examples": [{"expected": value}],
            }
        ],
    }


def _policy_for(
    ir: dict[str, Any], declared_type: str, cells: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Build a minimal explicit policy matching an in-memory fixture IR."""
    return {
        "schema_version": 1,
        "source": ir["source"],
        "source_sha256": "a" * 64,
        "cells": cells
        if cells is not None
        else [{"scenario": 0, "row": 0, "field": "expected", "type": declared_type}],
    }


def _load_defective_policy(defect: str) -> dict[str, Any]:
    """Use on-disk feature and sidecar fixtures for defects only the loader can observe."""
    _TEMPORARY_ROOT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=_TEMPORARY_ROOT) as directory:
        fixture = Path(directory)
        feature = fixture / "typed.feature"
        feature.write_text(
            "Feature: Typed\nScenario Outline: S\nGiven value <expected>\n"
            "Examples:\n| expected |\n| true |\n",
            encoding="utf-8",
        )
        source = parse_feature(feature)["source"]
        policy = {
            "schema_version": 1,
            "source": source,
            "source_sha256": hashlib.sha256(feature.read_bytes()).hexdigest(),
            "cells": [{"scenario": 0, "row": 0, "field": "expected", "type": "bool"}],
        }
        sidecar = fixture / "typed.mutation.json"
        if defect == "missing-policy-file":
            return load_policy(feature, sidecar)
        if defect == "invalid-utf8":
            sidecar.write_bytes(b"\xff")
        elif defect == "wrong-hash":
            policy["source_sha256"] = "b" * 64
            sidecar.write_text(json.dumps(policy), encoding="utf-8")
        else:
            encoded = json.dumps(policy, ensure_ascii=False, separators=(",", ":"))
            if defect == "duplicate-json-key":
                encoded = encoded.replace(
                    '"schema_version":1', '"schema_version":1,"schema_version":1', 1
                )
            elif defect == "nan":
                encoded = encoded.replace('"schema_version":1', '"schema_version":NaN', 1)
            else:
                raise AssertionError(f"unknown typed operator policy defect: {defect}")
            sidecar.write_text(encoded, encoding="utf-8")
        return load_policy(feature, sidecar)


def _defective_policy(ir: dict[str, Any], defect: str) -> object:
    """Derive every in-memory invalid-policy case from one otherwise valid policy."""
    if defect == "present-null":
        return None
    if defect == "present-empty":
        return {}
    policy = _policy_for(ir, "bool")
    if defect == "invalid-bool":
        ir["scenarios"][0]["examples"][0]["expected"] = "yes"
    elif defect in _ROOT_POLICY_DEFECTS:
        key, value = _ROOT_POLICY_DEFECTS[defect]
        policy[key] = value
    elif defect in _CELL_POLICY_DEFECTS:
        key, value = _CELL_POLICY_DEFECTS[defect]
        policy["cells"][0][key] = value
    elif defect == "duplicate-cell":
        policy["cells"].append(dict(policy["cells"][0]))
    elif defect == "empty-cells":
        policy["cells"] = []
    else:
        raise AssertionError(f"unknown typed operator policy defect: {defect}")
    return policy


def _required(context: dict[str, Any], key: str) -> Any:
    """Fetch prior-step state while making invalid step ordering explicit."""
    if key not in context:
        raise AssertionError("typed operator step order is invalid")
    return context[key]


def _integer(value: str, label: str) -> int:
    """Parse a feature integer or fail the vocabulary rather than silently accepting it."""
    try:
        return int(value)
    except ValueError as error:
        raise AssertionError(f"invalid typed operator {label}: {value}") from error


_HANDLERS: tuple[tuple[re.Pattern[str], StepHandler], ...] = (
    (re.compile(r'una fila con tipo "([^"]+)" y valor "(.*)"'), _given_typed_row),
    (re.compile(r'enumero con activacion "([^"]+)"'), _when_enumerate),
    (re.compile(r'obtengo "(.*)" con "([^\"]+)" celdas elegibles'), _then_result),
    (re.compile(r'una politica con defecto "([^"]+)"'), _given_invalid_policy),
    (re.compile(r"intento activar y enumerar"), _when_attempt_policy),
    (re.compile(r'obtengo error "([^"]+)" sin aprobar inventario'), _then_policy_error),
    (
        re.compile(r'un inventario original de "([^\"]+)" filas y "([^\"]+)" columnas'),
        _given_inventory,
    ),
    (re.compile(r'selecciono "([^\"]+)" columnas con activacion "([^"]+)"'), _when_select),
    (re.compile(r'hay "([^\"]+)" identidades unicas y solo cambia su celda'), _then_inventory),
)
