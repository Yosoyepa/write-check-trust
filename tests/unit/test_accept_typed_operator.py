"""TDD observable for the approved typed acceptance mutation operator."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any

import pytest

from tests.acceptance.steps import execute_scenario
from tools.wct.accept.mutation_policy import MutationPolicyError, load_policy, validate_policy
from tools.wct.accept.pipeline import generate, mutations, parse_feature

ROOT = Path(__file__).parents[2]
FEATURE = ROOT / "features/wct-typed-mutation-001.feature"


def _policy_ir() -> dict[str, Any]:
    """Build one row with a single explicitly eligible boolean cell."""
    return {
        "schema_version": 1,
        "feature": "typed fixture",
        "source": "features/typed-fixture.feature",
        "background": [],
        "scenarios": [
            {
                "name": "typed fixture",
                "line": 1,
                "outline": True,
                "steps": [],
                "examples": [{"case": "PA01", "field": "expected", "expected": "true"}],
            }
        ],
        "mutation_policy": {
            "schema_version": 1,
            "source": "features/typed-fixture.feature",
            "source_sha256": "a" * 64,
            "cells": [{"scenario": 0, "row": 0, "field": "expected", "type": "bool"}],
        },
    }


def _run_generated(ir: dict[str, Any], output: Path) -> subprocess.CompletedProcess[str]:
    """Run a generated feature with no inherited campaign protocol variables."""
    generate(ir, output)
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("WCT_ACCEPT_") and key != "MUTANT_UNDER_TEST"
    }
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(ROOT), str(ROOT / "src"), environment.get("PYTHONPATH")) if item
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-o", "addopts=", str(output)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_explicit_policy_mutates_only_the_declared_typed_cell() -> None:
    """An embedded policy changes its one boolean cell, not the full row."""
    ir = _policy_ir()

    result = mutations(ir)

    assert [
        (item["scenario"], item["row"], item["field"], item["from"], item["to"]) for item in result
    ] == [("typed fixture", 0, "expected", "true", "false")]
    assert result[0]["ir"]["scenarios"][0]["examples"] == [
        {"case": "PA01", "field": "expected", "expected": "false"}
    ]
    assert ir["scenarios"][0]["examples"] == [
        {"case": "PA01", "field": "expected", "expected": "true"}
    ]


def test_present_invalid_policy_never_falls_back_to_historical_mutations() -> None:
    """The key's presence is activation; a null policy is an error, not legacy mode."""
    ir = _policy_ir()
    ir["mutation_policy"] = None

    with pytest.raises(MutationPolicyError, match="policy"):
        mutations(ir)


def test_absent_policy_preserves_the_historical_operator() -> None:
    """Omitting the policy keeps the stable historical transformation exactly."""
    ir = _policy_ir()
    del ir["mutation_policy"]

    result = mutations(ir)

    assert result[2]["field"] == "expected"
    assert result[2]["to"] == "true__mutated"


def test_operator_feature_executes_with_a_real_generated_runner(tmp_path: Path) -> None:
    """The approved feature reaches real mutation APIs through the dispatcher."""
    completed = _run_generated(parse_feature(FEATURE), tmp_path / "test_typed_operator.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_operator_then_is_observable_and_not_an_import_failure(tmp_path: Path) -> None:
    """A deliberately wrong Then fails for the typed comparison, not import plumbing."""
    ir = parse_feature(FEATURE)
    ir["scenarios"][0]["examples"][0]["changed"] = "incorrect"

    completed = _run_generated(ir, tmp_path / "test_wrong_typed_operator.py")
    output = completed.stdout + completed.stderr

    assert completed.returncode == 1
    assert "typed mutation result differs" in output
    assert "ImportError" not in output
    assert "ModuleNotFoundError" not in output


def _loader_fixture(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    """Create a parsed feature and a sidecar object authenticated to its current bytes."""
    feature = tmp_path / "typed.feature"
    feature.write_text(
        "Feature: Typed\nScenario Outline: S\nGiven value <expected>\n"
        "Examples:\n| expected |\n| true |\n",
        encoding="utf-8",
    )
    ir = parse_feature(feature)
    return feature, {
        "schema_version": 1,
        "source": ir["source"],
        "source_sha256": hashlib.sha256(feature.read_bytes()).hexdigest(),
        "cells": [{"scenario": 0, "row": 0, "field": "expected", "type": "bool"}],
    }


@pytest.mark.parametrize(
    ("declared_type", "value", "expected"),
    [
        ("bool", "true", "false"),
        ("bool", "false", "true"),
        ("str", "", "__typed"),
        ("str", "x", "x__typed"),
        ("str", "ñ__typed", "ñ__typed__typed"),
    ],
)
def test_typed_transformations_are_literal_and_deterministic(
    declared_type: str, value: str, expected: str
) -> None:
    """Each declared type has its closed transformation and leaves the input unchanged."""
    ir = _policy_ir()
    ir["scenarios"][0]["examples"][0]["expected"] = value
    ir["mutation_policy"]["cells"][0]["type"] = declared_type
    before = json.loads(json.dumps(ir))

    first = mutations(ir)
    second = mutations(ir)

    assert first == second
    assert [(item["field"], item["from"], item["to"]) for item in first] == [
        ("expected", value, expected)
    ]
    assert ir == before


def test_validate_policy_returns_fresh_cells_in_canonical_ir_order() -> None:
    """JSON cell order cannot change mutation identity order or leak mutable policy data."""
    ir: dict[str, Any] = {
        "schema_version": 1,
        "feature": "canonical",
        "source": "features/canonical.feature",
        "background": [],
        "scenarios": [
            {
                "name": "canonical",
                "line": 1,
                "outline": True,
                "steps": [],
                "examples": [
                    {"case": "PA01", "expected": "true", "label": "x"},
                    {"case": "PA02", "expected": "false", "label": "y"},
                ],
            }
        ],
    }
    policy = {
        "schema_version": 1,
        "source": ir["source"],
        "source_sha256": "a" * 64,
        "cells": [
            {"scenario": 0, "row": 1, "field": "label", "type": "str"},
            {"scenario": 0, "row": 0, "field": "label", "type": "str"},
            {"scenario": 0, "row": 0, "field": "expected", "type": "bool"},
        ],
    }

    cells = validate_policy(ir, policy)

    assert [(cell["row"], cell["field"], cell["type"]) for cell in cells] == [
        (0, "expected", "bool"),
        (0, "label", "str"),
        (1, "label", "str"),
    ]
    cells[0]["field"] = "changed"
    assert policy["cells"][2]["field"] == "expected"


def test_explicit_mutation_clone_preserves_the_policy_and_changes_one_cell() -> None:
    """The typed clone retains metadata and differs only at its declared coordinate."""
    ir = _policy_ir()
    baseline = json.loads(json.dumps(ir))

    result = mutations(ir)

    clone = result[0]["ir"]
    expected = json.loads(json.dumps(baseline))
    expected["scenarios"][0]["examples"][0]["expected"] = "false"
    assert clone == expected
    assert clone["mutation_policy"] == baseline["mutation_policy"]


def test_absent_policy_ignores_sidecar_metadata_and_keeps_all_historical_cells() -> None:
    """A sidecar-looking value cannot activate the typed operator without the IR key."""
    ir = _policy_ir()
    del ir["mutation_policy"]
    ir["mutation_sidecar"] = {"cells": [{"field": "expected"}]}

    result = mutations(ir)

    assert [(item["field"], item["to"]) for item in result] == [
        ("case", "PA01__mutated"),
        ("field", "expected__mutated"),
        ("expected", "true__mutated"),
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", "1"),
        ("00", "1"),
        ("-0", "1"),
        ("0.0", "1"),
        ("2", "0"),
        ("-2", "0"),
        ("2.5", "0"),
        ("+0", "+0__mutated"),
        ("1e3", "1e3__mutated"),
        ("text", "text__mutated"),
    ],
)
def test_absent_policy_preserves_the_exact_historical_numeric_operator(
    value: str, expected: str
) -> None:
    """The explicit branch does not broaden or weaken the legacy Decimal/regex behavior."""
    ir = _policy_ir()
    del ir["mutation_policy"]
    ir["scenarios"][0]["examples"] = [{"expected": value}]

    result = mutations(ir)

    assert result == [
        {
            "scenario": "typed fixture",
            "row": 0,
            "field": "expected",
            "from": value,
            "to": expected,
            "ir": {
                "schema_version": 1,
                "feature": "typed fixture",
                "source": "features/typed-fixture.feature",
                "background": [],
                "scenarios": [
                    {
                        "name": "typed fixture",
                        "line": 1,
                        "outline": True,
                        "steps": [],
                        "examples": [{"expected": expected}],
                    }
                ],
            },
        }
    ]


@pytest.mark.parametrize("policy", [None, False, {}, []])
def test_every_present_nonobject_policy_is_rejected_without_historical_fallback(
    policy: object,
) -> None:
    """Presence of null, false, empty object, or list must not silently enumerate legacy cells."""
    ir = _policy_ir()
    ir["mutation_policy"] = policy
    before = json.loads(json.dumps(ir))

    with pytest.raises(MutationPolicyError):
        mutations(ir)

    assert ir == before


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("scenario", True),
        ("scenario", -1),
        ("row", 1.0),
        ("field", "missing"),
        ("type", "int"),
    ],
)
def test_validate_policy_rejects_manual_invalid_coordinates_and_types(
    key: str, value: object
) -> None:
    """Directly injected policy objects receive the same strict validation as loaded JSON."""
    ir = _policy_ir()
    policy = ir["mutation_policy"]
    policy["cells"][0][key] = value

    with pytest.raises(MutationPolicyError):
        validate_policy(ir, policy)


@pytest.mark.parametrize("declared_type", [[], {}], ids=["list", "object"])
def test_validate_policy_rejects_container_declared_types_as_policy_errors(
    declared_type: object,
) -> None:
    """Container declarations fail through the pure validator, never with TypeError."""
    ir = _policy_ir()
    policy = ir["mutation_policy"]
    policy["cells"][0]["type"] = declared_type

    with pytest.raises(MutationPolicyError, match="policy type"):
        validate_policy(ir, policy)


@pytest.mark.parametrize("declared_type", [[], {}], ids=["list", "object"])
def test_mutations_rejects_container_declared_types_as_policy_errors(
    declared_type: object,
) -> None:
    """Container declarations fail through mutation enumeration without fallback."""
    ir = _policy_ir()
    policy = ir["mutation_policy"]
    policy["cells"][0]["type"] = declared_type

    with pytest.raises(MutationPolicyError, match="policy type"):
        mutations(ir)


@pytest.mark.parametrize("declared_type", [[], {}], ids=["list", "object"])
def test_load_policy_rejects_container_declared_types_as_policy_errors(
    tmp_path: Path, declared_type: object
) -> None:
    """Container declarations decoded from JSON remain normalized policy errors."""
    feature, policy = _loader_fixture(tmp_path)
    policy["cells"][0]["type"] = declared_type
    sidecar = tmp_path / "container-type.mutation.json"
    sidecar.write_text(json.dumps(policy), encoding="utf-8")

    with pytest.raises(MutationPolicyError, match="policy type"):
        load_policy(feature, sidecar)


def test_load_policy_authenticates_feature_bytes_and_returns_a_fresh_normalized_object(
    tmp_path: Path,
) -> None:
    """Combine strict JSON, parsed-IR compatibility, and physical feature hashing."""
    feature, policy = _loader_fixture(tmp_path)
    sidecar = tmp_path / "typed.mutation.json"
    sidecar.write_text(json.dumps(policy), encoding="utf-8")

    loaded = load_policy(feature, sidecar)

    assert loaded == policy
    loaded["cells"][0]["field"] = "changed"
    assert policy["cells"][0]["field"] == "expected"
    feature.write_text(feature.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
    with pytest.raises(MutationPolicyError, match="source_sha256") as caught:
        load_policy(feature, sidecar)
    assert str(feature) in str(caught.value)
    assert str(sidecar) in str(caught.value)


@pytest.mark.parametrize(
    "raw",
    [
        b"\xff",
        b'{"schema_version":1,"schema_version":1}',
        b'{"schema_version":NaN}',
        b"[]",
    ],
)
def test_load_policy_rejects_invalid_utf8_duplicate_keys_nonfinite_values_and_nonobjects(
    tmp_path: Path, raw: bytes
) -> None:
    """The loader rejects JSON inputs before they can normalize into an approved inventory."""
    feature, _policy = _loader_fixture(tmp_path)
    sidecar = tmp_path / "invalid.mutation.json"
    sidecar.write_bytes(raw)

    with pytest.raises(MutationPolicyError) as caught:
        load_policy(feature, sidecar)

    assert str(feature) in str(caught.value)
    assert str(sidecar) in str(caught.value)


def test_dispatcher_requires_the_exact_typed_feature_source() -> None:
    """Only the approved relative source enters the local typed executor guard."""
    ir = parse_feature(FEATURE)

    execute_scenario(ir, 0)
    similar = json.loads(json.dumps(ir))
    similar["source"] = "features/wct-typed-mutation-001.feature.similar"
    with pytest.raises(AssertionError, match="missing acceptance step"):
        execute_scenario(similar, 0)


def _foreign_engine_imports(engine_modules: list[ModuleType]) -> list[str]:
    """Names of tests.*/tools.wct.evidence.* objects present in loaded engine modules.

    Recorre el espacio de nombres real de cada módulo del motor: todo valor
    importado queda como atributo (módulo, o función/clase cuyo ``__module__``
    delata su origen). Es el estado observable del SUT cargado, no su texto.
    """
    foreign: set[str] = set()
    for module in engine_modules:
        for value in vars(module).values():
            if isinstance(value, ModuleType):
                origin = value.__name__
            else:
                origin = getattr(value, "__module__", None)
            if origin and (
                origin == "tests" or origin.startswith(("tests.", "tools.wct.evidence"))
            ):
                foreign.add(origin)
    return sorted(foreign)


def test_policy_and_operator_import_no_tests_or_evidence_modules() -> None:
    """The production operator stays independent from test and evidence packages.

    O6 (VERIFICACION.md): oráculo observable sobre el SUT — los módulos del
    motor, alcanzados desde sus funciones públicas ya cargadas, no exponen
    ningún objeto importado de ``tests.*`` ni ``tools.wct.evidence.*``. La
    inspección sintáctica se conserva porque cubre imports condicionales o
    diferidos que no se ejecutan al importar el módulo.
    """
    engine_modules = [
        sys.modules[public.__module__] for public in (load_policy, validate_policy, mutations)
    ]
    foreign = _foreign_engine_imports(engine_modules)
    assert not foreign, f"the engine imports foreign packages: {foreign}"

    imported: list[str] = []
    for module in [
        ROOT / "tools/wct/accept/mutation_policy.py",
        ROOT / "tools/wct/accept/mutation_cases.py",
    ]:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.append(node.module)

    assert not [
        name
        for name in imported
        if name == "tests" or name.startswith("tests.") or name.startswith("tools.wct.evidence")
    ]


def test_approved_feature_keeps_the_phase_one_example_denominators() -> None:
    """The checked-in Gherkin contains exactly the approved 8, 18, and 2 example rows."""
    ir = parse_feature(FEATURE)

    assert ir["source"] == "features/wct-typed-mutation-001.feature"
    assert [len(scenario["examples"]) for scenario in ir["scenarios"]] == [8, 18, 2]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda _ir, policy: policy.update(schema_version=True),
        lambda _ir, policy: policy.update(source=""),
        lambda _ir, policy: policy.update(source="features/other.feature"),
        lambda _ir, policy: policy.update(source_sha256="A" * 64),
        lambda _ir, policy: policy.update(cells=[]),
        lambda _ir, policy: policy.update(cells={}),
        lambda _ir, policy: policy["cells"].__setitem__(0, []),
        lambda _ir, policy: policy["cells"].__setitem__(0, {"scenario": 0}),
        lambda _ir, policy: policy["cells"].append(dict(policy["cells"][0])),
        lambda ir, _policy: ir.update(source=None),
        lambda ir, _policy: ir["scenarios"].__setitem__(0, []),
        lambda ir, _policy: ir["scenarios"][0]["examples"].__setitem__(0, []),
        lambda ir, _policy: ir["scenarios"][0]["examples"][0].__setitem__("expected", True),
        lambda ir, policy: (
            policy["cells"][0].__setitem__("type", "bool")
            or ir["scenarios"][0]["examples"][0].__setitem__("expected", "not-a-bool")
        ),
    ],
    ids=[
        "schema-bool",
        "empty-source",
        "wrong-source",
        "bad-digest",
        "empty-cells",
        "cells-object",
        "cell-not-object",
        "cell-missing-keys",
        "duplicate-cell",
        "missing-ir-source",
        "scenario-not-object",
        "row-not-object",
        "target-not-string",
        "invalid-boolean",
    ],
)
def test_validate_policy_rejects_all_remaining_schema_and_target_shapes(mutate: Any) -> None:
    """Every strict policy branch rejects in-memory input before an inventory can be emitted."""
    ir = _policy_ir()
    policy = ir["mutation_policy"]
    mutate(ir, policy)

    with pytest.raises(MutationPolicyError):
        validate_policy(ir, policy)


def test_load_policy_wraps_a_missing_sidecar_with_both_paths(tmp_path: Path) -> None:
    """Loader I/O failures retain the feature and sidecar paths for diagnosis."""
    feature, _policy = _loader_fixture(tmp_path)
    missing = tmp_path / "missing.mutation.json"

    with pytest.raises(MutationPolicyError) as caught:
        load_policy(feature, missing)

    assert str(feature) in str(caught.value)
    assert str(missing) in str(caught.value)
