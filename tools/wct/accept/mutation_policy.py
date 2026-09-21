"""Explicit, typed mutation-policy loading and validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, NoReturn, cast

from tools.wct.accept.parsing import parse_feature

_POLICY_KEYS = frozenset({"schema_version", "source", "source_sha256", "cells"})
_CELL_KEYS = frozenset({"scenario", "row", "field", "type"})
_DIGEST = re.compile(r"[0-9a-f]{64}")
_ALLOWED_TYPES = frozenset({"bool", "str"})


class MutationPolicyError(ValueError):
    """Raised when an explicit acceptance mutation policy is invalid."""


def load_policy(feature_path: Path, policy_path: Path) -> dict[str, Any]:
    """Load and authenticate a JSON policy for an unmodified feature.

    Args:
        feature_path: Feature whose original bytes and parsed IR define the policy target.
        policy_path: JSON sidecar containing the explicit mutation policy.

    Returns:
        A fresh, normalized policy object with canonically ordered cells.

    Raises:
        MutationPolicyError: If either input cannot be read, parsed, authenticated, or validated.
    """
    feature = Path(feature_path)
    policy_file = Path(policy_path)
    try:
        feature_bytes = feature.read_bytes()
        policy = cast(dict[str, Any], _decode_policy(policy_file.read_bytes()))
        ir = parse_feature(feature)
        cells = validate_policy(ir, policy)
        if policy["source_sha256"] != hashlib.sha256(feature_bytes).hexdigest():
            raise MutationPolicyError("source_sha256 does not match feature bytes")
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise MutationPolicyError(f"policy {policy_file} for feature {feature}: {error}") from error
    return {
        "schema_version": policy["schema_version"],
        "source": policy["source"],
        "source_sha256": policy["source_sha256"],
        "cells": [dict(cell) for cell in cells],
    }


def validate_policy(ir: dict[str, Any], policy: object) -> list[dict[str, Any]]:
    """Validate an embedded policy and return fresh cells in canonical IR order.

    Args:
        ir: Parsed acceptance-feature intermediate representation to target.
        policy: Object supplied under the explicit ``mutation_policy`` IR key.

    Returns:
        Independent cell dictionaries ordered by scenario, row, and original column order.

    Raises:
        MutationPolicyError: If the policy schema or any selected cell is incompatible with ``ir``.
    """
    if type(policy) is not dict:
        raise MutationPolicyError("policy must be a JSON object")
    _exact_keys(policy, _POLICY_KEYS, "policy")
    _schema_version(policy["schema_version"])
    source = policy["source"]
    if type(source) is not str or not source:
        raise MutationPolicyError("policy source must be a non-empty string")
    if source != _ir_source(ir):
        raise MutationPolicyError("policy source does not match the IR source")
    digest = policy["source_sha256"]
    if type(digest) is not str or _DIGEST.fullmatch(digest) is None:
        raise MutationPolicyError(
            "policy source_sha256 must be 64 lowercase hexadecimal characters"
        )
    cells = policy["cells"]
    if type(cells) is not list or not cells:
        raise MutationPolicyError("policy cells must be a non-empty list")

    seen: set[tuple[int, int, str]] = set()
    canonical: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
    for cell in cells:
        normalized, position = _validated_cell(ir, cell, seen)
        canonical.append((position, normalized))
    return [dict(cell) for _position, cell in sorted(canonical, key=lambda item: item[0])]


def _decode_policy(raw: bytes) -> object:
    """Decode strict UTF-8 JSON while rejecting duplicate or non-finite values."""
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_without_duplicate_keys,
        parse_constant=_reject_nonfinite_constant,
    )


def _without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object only when every key was supplied once."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MutationPolicyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> NoReturn:
    """Reject JSON extensions such as NaN and Infinity rather than normalizing them."""
    raise MutationPolicyError(f"non-finite JSON constant: {value}")


def _exact_keys(value: dict[str, Any], expected: frozenset[str], label: str) -> None:
    """Require precisely the documented object keys."""
    if set(value) != expected:
        missing = ", ".join(sorted(expected - set(value))) or "none"
        extra = ", ".join(sorted(set(value) - expected)) or "none"
        raise MutationPolicyError(f"{label} keys differ (missing: {missing}; extra: {extra})")


def _schema_version(value: object) -> None:
    """Require schema version one without accepting booleans as integers."""
    if type(value) is not int or value != 1:
        raise MutationPolicyError("schema_version must be the integer 1")


def _ir_source(ir: dict[str, Any]) -> str:
    """Return a valid IR source or explain why policy validation cannot continue."""
    source = ir.get("source")
    if type(source) is not str or not source:
        raise MutationPolicyError("IR source must be a non-empty string")
    return source


def _validated_cell(
    ir: dict[str, Any], cell: object, seen: set[tuple[int, int, str]]
) -> tuple[dict[str, Any], tuple[int, int, int]]:
    """Validate one cell and pair its copied data with a canonical sort position."""
    if type(cell) is not dict:
        raise MutationPolicyError("policy cell must be an object")
    _exact_keys(cell, _CELL_KEYS, "policy cell")
    scenario_index = cell["scenario"]
    row_index = cell["row"]
    field = cell["field"]
    declared_type = cell["type"]
    if type(scenario_index) is not int or scenario_index < 0:
        raise MutationPolicyError("policy scenario must be a non-negative integer")
    if type(row_index) is not int or row_index < 0:
        raise MutationPolicyError("policy row must be a non-negative integer")
    if type(field) is not str:
        raise MutationPolicyError("policy field must be a string")
    if type(declared_type) is not str or declared_type not in _ALLOWED_TYPES:
        raise MutationPolicyError("policy type must be exactly bool or str")
    coordinate = scenario_index, row_index, field
    if coordinate in seen:
        raise MutationPolicyError("policy contains a duplicate cell coordinate")
    _scenario, row = _target_row(ir, scenario_index, row_index)
    if field not in row:
        raise MutationPolicyError("policy field does not exist in the target row")
    value = row[field]
    if type(value) is not str:
        raise MutationPolicyError("policy target cell must contain a string")
    if declared_type == "bool" and value not in {"true", "false"}:
        raise MutationPolicyError("boolean policy target must be true or false")
    seen.add(coordinate)
    return (
        {"scenario": scenario_index, "row": row_index, "field": field, "type": declared_type},
        (scenario_index, row_index, list(row).index(field)),
    )


def _target_row(
    ir: dict[str, Any], scenario_index: int, row_index: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Find a selected row without accepting malformed IR coordinates."""
    scenarios = ir.get("scenarios")
    if type(scenarios) is not list or scenario_index >= len(scenarios):
        raise MutationPolicyError("policy scenario does not exist")
    scenario = scenarios[scenario_index]
    if type(scenario) is not dict:
        raise MutationPolicyError("IR scenario must be an object")
    examples = scenario.get("examples")
    if type(examples) is not list or row_index >= len(examples):
        raise MutationPolicyError("policy row does not exist")
    row = examples[row_index]
    if type(row) is not dict:
        raise MutationPolicyError("IR example row must be an object")
    return scenario, row
