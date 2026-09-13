import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tools.wct.accept.pipeline import generate, ir_dry, mutations, parse_feature

FEATURE = """Feature: Reserve
Scenario Outline: units
  Given stock "<stock>"
  Then remaining "<remaining>"
Examples:
  | stock | remaining |
  | 3     | 3         |
"""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", "1"),
        ("00", "1"),
        ("-0", "1"),
        ("0.0", "1"),
        ("2", "0"),
        ("-2.5", "0"),
        ("+0", "+0__mutated"),
        ("0e0", "0e0__mutated"),
    ],
)
def test_numeric_zero_operator_preserves_lexical_domain(value, expected):
    ir = {"scenarios": [{"name": "S", "examples": [{"x": value}]}]}
    result = mutations(ir)
    assert result == [
        {
            "scenario": "S",
            "row": 0,
            "field": "x",
            "from": value,
            "to": expected,
            "ir": {"scenarios": [{"name": "S", "examples": [{"x": expected}]}]},
        }
    ]
    assert ir["scenarios"][0]["examples"] == [{"x": value}]


def test_generate_is_reproducible_across_roots(tmp_path: Path) -> None:
    """Dos checkouts del mismo feature producen artefactos byte-idénticos.

    El IR registraba el source como ruta ABSOLUTA: el artefacto versionado
    cambiaba según el checkout que lo regenerara (bug de PR-C, ADR-D-04).
    El source debe embeberse relativo al root del repo.
    """
    artifacts = []
    for checkout in ("checkout-a", "checkout-b"):
        root = tmp_path / checkout
        (root / "governance").mkdir(parents=True)
        (root / "governance" / "policy.yaml").write_text("schema_version: 1\n", encoding="utf-8")
        (root / "features").mkdir()
        feature = root / "features" / "example.feature"
        feature.write_text(FEATURE, encoding="utf-8")

        ir = parse_feature(feature)
        output = generate(ir, root / "tests" / "acceptance" / "generated" / "test_acceptance.py")

        assert ir["source"] == "features/example.feature"
        artifacts.append(output.read_bytes())

    assert artifacts[0] == artifacts[1]


def test_parser_builds_canonical_ir(tmp_path: Path) -> None:
    feature = tmp_path / "sample.feature"
    feature.write_text(
        """Feature: Add
Scenario Outline: numbers
  Given value "<value>"
  Then result "<result>"
Examples:
  | value | result |
  | 2     | 4      |
""",
        encoding="utf-8",
    )

    result = parse_feature(feature)

    assert result["feature"] == "Add"
    assert result["scenarios"][0]["examples"] == [{"value": "2", "result": "4"}]
    assert len(mutations(result)) == 2


def test_ir_dry_finds_repeated_step_shape(tmp_path: Path) -> None:
    feature = tmp_path / "duplicate.feature"
    feature.write_text(
        """Feature: duplicate
Scenario: one
  Given value "1"
Scenario: two
  Given value "2"
""",
        encoding="utf-8",
    )

    report = ir_dry(parse_feature(feature))

    assert report["count"] == 1
    assert report["findings"][0]["kind"] == "placeholder-variant"


def test_placeholder_variant_names_step_and_both_scenarios(tmp_path: Path) -> None:
    """The finding must say WHICH step collided with WHICH scenario where."""
    feature = tmp_path / "duplicate.feature"
    feature.write_text(
        """Feature: duplicate
Scenario: one
  Given value "1"
Scenario: two
  Given value "2"
""",
        encoding="utf-8",
    )

    report = ir_dry(parse_feature(feature))
    finding = report["findings"][0]

    assert finding["step"] == 'value "1"'
    assert finding["other_scenario"] == "one"
    assert finding["scenario"] == "two"
    assert "one" in finding["message"]
    assert "two" in finding["message"]
    assert "value" in finding["message"]


def test_placeholder_variant_names_the_outline_and_suggests_fix(tmp_path: Path) -> None:
    """Phases 24-25 of the pilot: the message must suggest the reformulation.

    When one side of the collision is a Scenario Outline, the cheapest fix is
    a new Examples column on THAT step — say so instead of "either one".
    """
    feature = tmp_path / "collide.feature"
    feature.write_text(
        """Feature: collide
Scenario: plain
  Given value "1"
Scenario Outline: tabulated
  Given value "2"
  Examples:
    | n |
    | 3 |
""",
        encoding="utf-8",
    )

    report = ir_dry(parse_feature(feature))
    finding = report["findings"][0]

    assert finding["kind"] == "placeholder-variant"
    assert "Scenario Outline 'tabulated'" in finding["message"]
    assert "columna" in finding["message"]


def test_characterize_complete_ir_and_source(tmp_path: Path) -> None:
    """Freeze line numbers, keyword identity, order and background semantics."""
    (tmp_path / "governance").mkdir()
    (tmp_path / "governance/policy.yaml").write_text("schema_version: 1\n")
    path = tmp_path / "sample.feature"
    path.write_text(
        "# comment\n@tag\nFeature: Ordered\n\nBackground:\n  Given setup\n"
        "Scenario: plain\n  When act\n  And continue\n  But stop\n"
        "Scenario Outline: matrix\n  Then value <n>\nExamples:\n"
        "  | n | text |\n  | 1 | é |\n  # retain examples\n  | 2 | two |\n"
    )
    assert parse_feature(path) == {
        "schema_version": 1,
        "feature": "Ordered",
        "source": "sample.feature",
        "background": [{"keyword": "Given", "text": "setup", "line": 6}],
        "scenarios": [
            {
                "name": "plain",
                "line": 7,
                "outline": False,
                "steps": [
                    {"keyword": "When", "text": "act", "line": 8},
                    {"keyword": "And", "text": "continue", "line": 9},
                    {"keyword": "But", "text": "stop", "line": 10},
                ],
                "examples": [],
            },
            {
                "name": "matrix",
                "line": 11,
                "outline": True,
                "steps": [{"keyword": "Then", "text": "value <n>", "line": 12}],
                "examples": [{"n": "1", "text": "é"}, {"n": "2", "text": "two"}],
            },
        ],
    }


@pytest.mark.parametrize(
    ("body", "diagnostic"),
    [
        ("Feature: F\nnarrative\nScenario: S\n", ":2: sintaxis Gherkin no soportada: narrative"),
        ("Feature: F\nGiven early\n", ":2: step fuera de scenario"),
        ("Feature: F\nExamples:\n", ":2: Examples fuera de Scenario Outline"),
        ("Feature: F\nBackground:\nExamples:\n", ":3: Examples fuera de Scenario Outline"),
        (
            "Feature: F\nScenario Outline: S\nExamples:\n| a | b |\n| 1 |\n",
            ":5: fila Examples de longitud incorrecta",
        ),
        ("Feature: F\nScenario: S\n| a |\n", ":3: sintaxis Gherkin no soportada: | a |"),
        ("Feature: F\n", ": Feature y al menos un Scenario son obligatorios"),
        ("Scenario: S\nGiven step\n", ": Feature y al menos un Scenario son obligatorios"),
    ],
)
def test_characterize_parser_diagnostics(tmp_path: Path, body: str, diagnostic: str) -> None:
    """Issue35 and malformed input retain exact historical diagnostics."""
    path = tmp_path / "bad.feature"
    path.write_text(body)
    with pytest.raises(ValueError, match=re.escape(diagnostic)) as caught:
        parse_feature(path)
    assert str(caught.value) == str(path) + diagnostic


def test_characterize_plain_examples_and_feature_replacement(tmp_path: Path) -> None:
    """Do not tighten historical accepted syntax during the mechanical move."""
    path = tmp_path / "legacy.feature"
    path.write_text("Feature: Old\nScenario: S\nExamples:\n| n |\n| 1 |\nFeature: New\nThen end\n")
    result = parse_feature(path)
    assert result["feature"] == "New"
    assert result["scenarios"] == [
        {
            "name": "S",
            "line": 2,
            "outline": False,
            "steps": [{"keyword": "Then", "text": "end", "line": 7}],
            "examples": [{"n": "1"}],
        }
    ]


def test_characterize_scenario_named_background(tmp_path: Path) -> None:
    """The old name-based special case remains visible rather than silently fixed."""
    path = tmp_path / "named.feature"
    path.write_text("Feature: F\nScenario: Background\nGiven special\n")
    result = parse_feature(path)
    assert result["background"] == [{"keyword": "Given", "text": "special", "line": 3}]
    assert result["scenarios"] == [
        {"name": "Background", "line": 2, "outline": False, "steps": [], "examples": []}
    ]
    path.write_text("Feature: F\nScenario: Background\nExamples:\n")
    with pytest.raises(ValueError, match="Examples fuera de Scenario Outline") as caught:
        parse_feature(path)
    assert str(caught.value) == f"{path}:3: Examples fuera de Scenario Outline"


def test_characterize_generation_literal(tmp_path: Path) -> None:
    """Pin independent generated bytes, including environment IR consumption."""
    ir = {
        "schema_version": 1,
        "feature": "F",
        "source": "f.feature",
        "background": [],
        "scenarios": [{"name": "Á B!", "line": 2, "outline": False, "steps": [], "examples": []}],
    }
    output = tmp_path / "nested/test_generated.py"
    assert generate(ir, output) == output
    expected = (
        "# Generated by wct accept generate. Do not edit.\n"
        "import json\nimport os\nfrom pathlib import Path\n\n"
        "from tests.acceptance.steps import execute_scenario\n\n"
        "BASE_IR = json.loads(\n"
        '    \'{"schema_version": 1, "feature": "F", "source": "f.feature", '
        '"background": [], "scenarios": [{"name": "Á B!", "line": 2, '
        '"outline": false, "steps": [], "examples": []}]}\'\n'
        ")\n\n\ndef _ir():\n"
        '    path = os.environ.get("WCT_ACCEPT_IR")\n'
        '    return json.loads(Path(path).read_text(encoding="utf-8")) if path else BASE_IR\n\n'
        "\ndef test_001_b():\n    execute_scenario(_ir(), 0)\n"
    )
    assert output.read_bytes() == expected.encode("utf-8")


def test_characterize_ir_dry_intrascenario_order(tmp_path: Path) -> None:
    """Each duplicate references the last prior occurrence, preserving findings."""
    path = tmp_path / "repeat.feature"
    path.write_text('Feature: F\nScenario: S\nGiven value "1"\nAnd value "2"\nBut value "3"\n')
    report = ir_dry(parse_feature(path))
    assert report == {
        "findings": [
            {
                "kind": "duplicate-in-scenario",
                "scenario": "S",
                "line": 4,
                "other_line": 3,
                "step": 'value "2"',
                "message": (
                    "Paso 'value \"2\"' repite la forma de la línea 3 dentro del escenario 'S'"
                ),
            },
            {
                "kind": "duplicate-in-scenario",
                "scenario": "S",
                "line": 5,
                "other_line": 4,
                "step": 'value "3"',
                "message": (
                    "Paso 'value \"3\"' repite la forma de la línea 4 dentro del escenario 'S'"
                ),
            },
        ],
        "count": 2,
    }


@pytest.mark.parametrize("kind", ["Scenario", "Scenario Outline"])
def test_colons_inside_feature_and_scenario_names_are_preserved(tmp_path: Path, kind: str) -> None:
    """Only the first colon separates the keyword from the full name."""
    path = tmp_path / "colons.feature"
    path.write_text(
        f"Feature: One: Two: Three\n{kind}: A: B: C\nGiven action\n",
        encoding="utf-8",
    )
    observed = parse_feature(path)
    assert observed["feature"] == "One: Two: Three"
    assert observed["scenarios"] == [
        {
            "name": "A: B: C",
            "line": 2,
            "outline": kind == "Scenario Outline",
            "steps": [{"keyword": "Given", "text": "action", "line": 3}],
            "examples": [],
        }
    ]


@pytest.mark.parametrize(
    ("body", "line"),
    [
        ("|x|\nFeature: F\nScenario: S\nGiven action\n", 1),
        ("Feature: F\nBackground:\n|x|\nScenario: S\nGiven action\n", 3),
    ],
)
def test_tables_outside_examples_keep_historical_rejection(
    tmp_path: Path, body: str, line: int
) -> None:
    """An uninitialized or Background parser must not consume a table header."""
    path = tmp_path / "outside.feature"
    path.write_text(body, encoding="utf-8")
    expected = f"{path}:{line}: sintaxis Gherkin no soportada: |x|"
    with pytest.raises(ValueError, match=re.escape(expected)) as caught:
        parse_feature(path)
    assert str(caught.value) == expected


def test_compact_examples_retain_x_at_both_cell_edges(tmp_path: Path) -> None:
    """Delimiter stripping may not consume data adjacent to a pipe."""
    path = tmp_path / "compact.feature"
    path.write_text(
        "Feature: F\nScenario Outline: S\nThen value <name>\nExamples:\n"
        "|name|\n|X|\n|XmiddleX|\n|plain|\n",
        encoding="utf-8",
    )
    result = parse_feature(path)
    assert result["scenarios"][0]["examples"] == [
        {"name": "X"},
        {"name": "XmiddleX"},
        {"name": "plain"},
    ]


def test_feature_outside_explicit_project_preserves_original_source(
    tmp_path: Path, monkeypatch
) -> None:
    """A genuine sibling path exercises relative-source fallback without mocks."""
    project = tmp_path / "project"
    (project / "governance").mkdir(parents=True)
    (project / "governance/policy.yaml").write_text("schema_version: 1\n", encoding="utf-8")
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(project))
    external = tmp_path / "elsewhere.feature"
    external.write_text("Feature: Outside\nScenario: S\nGiven action\n", encoding="utf-8")
    assert parse_feature(external)["source"] == str(external)
    internal = project / "inside.feature"
    internal.write_text("Feature: Inside\nScenario: S\nGiven action\n", encoding="utf-8")
    assert parse_feature(internal)["source"] == "inside.feature"


@pytest.mark.parametrize(("left", "right"), [("read file", "save record"), ("value ß", "value ss")])
def test_ir_dry_does_not_collapse_distinct_step_shapes(
    tmp_path: Path, left: str, right: str
) -> None:
    """Preserve lower-based Unicode behavior rather than imposing casefold/upper."""
    path = tmp_path / "distinct.feature"
    path.write_text(f"Feature: F\nScenario: S\nGiven {left}\nThen {right}\n", encoding="utf-8")
    assert ir_dry(parse_feature(path)) == {"findings": [], "count": 0}


def test_ir_dry_literal_placeholder_keeps_historical_normalization(tmp_path: Path) -> None:
    """A literal placeholder and numeric normalization historically collide."""
    path = tmp_path / "placeholder.feature"
    path.write_text(
        "Feature: F\nScenario: S\nGiven value 1\nThen value <value>\n", encoding="utf-8"
    )
    assert ir_dry(parse_feature(path)) == {
        "findings": [
            {
                "kind": "duplicate-in-scenario",
                "scenario": "S",
                "line": 4,
                "other_line": 3,
                "step": "value <value>",
                "message": (
                    "Paso 'value <value>' repite la forma de la línea 3 dentro del escenario 'S'"
                ),
            }
        ],
        "count": 1,
    }


def test_plain_scenario_collision_preserves_complete_diagnostic(tmp_path: Path) -> None:
    """Public findings expose exact location keys and ordinary-scenario advice."""
    path = tmp_path / "plain-collision.feature"
    path.write_text(
        'Feature: F\nScenario: first\nGiven value "1"\nScenario: second\nThen value "2"\n',
        encoding="utf-8",
    )
    assert ir_dry(parse_feature(path)) == {
        "findings": [
            {
                "kind": "placeholder-variant",
                "scenario": "second",
                "line": 5,
                "other_line": 3,
                "other_scenario": "first",
                "step": 'value "1"',
                "message": (
                    "Paso 'value \"1\"' del escenario 'first' (línea 3) colisiona con el "
                    "escenario 'second' (línea 5); parametriza uno de los dos"
                ),
            }
        ],
        "count": 1,
    }


def test_generate_writes_utf8_under_ascii_process_locale(tmp_path: Path) -> None:
    """The generated file encoding is independent of the interpreter locale."""
    root = Path(__file__).resolve().parents[2]
    ir = {"feature": "Á", "scenarios": []}
    in_process = generate(ir, tmp_path / "in-process.py")
    child_output = tmp_path / "ascii-process.py"
    script = (
        "import codecs,json,locale,sys; from pathlib import Path; "
        "import tools.wct.accept.generation as subject; "
        "subject.generate({'feature':'\\u00c1','scenarios':[]},Path(sys.argv[1])); "
        "print(json.dumps({'encoding':codecs.lookup(locale.getencoding()).name,"
        "'utf8_mode':sys.flags.utf8_mode,'source':str(Path(subject.__file__).resolve())}))"
    )
    env = dict(os.environ)
    env.update(
        LC_ALL="C",
        PYTHONUTF8="0",
        PYTHONCOERCECLOCALE="0",
        PYTHONPATH=str(root),
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(child_output)],
        cwd=root,
        env=env,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert completed.returncode == 0, completed.stderr
    provenance = json.loads(completed.stdout)
    assert provenance == {
        "encoding": "ascii",
        "utf8_mode": 0,
        "source": str(root / "tools/wct/accept/generation.py"),
    }
    observed = child_output.read_bytes()
    assert b'"feature": "\xc3\x81"' in observed
    assert observed.decode("utf-8").startswith("# Generated by wct accept generate.")
    assert observed == in_process.read_bytes()


def test_parse_reads_utf8_under_ascii_process_locale(tmp_path: Path) -> None:
    """UTF-8 feature bytes retain Unicode independently of process locale."""
    root = Path(__file__).resolve().parents[2]
    feature = tmp_path / "unicode.feature"
    feature.write_bytes(b"Feature: \xc3\x81\nScenario: \xc3\x81\nGiven value \xc3\x81\n")
    expected = parse_feature(feature)
    assert expected["feature"] == "Á"
    assert expected["scenarios"][0]["name"] == "Á"
    assert expected["scenarios"][0]["steps"] == [{"keyword": "Given", "text": "value Á", "line": 3}]
    script = (
        "import codecs,json,locale,sys; from pathlib import Path; "
        "import tools.wct.accept.parsing as subject; "
        "ir=subject.parse_feature(Path(sys.argv[1])); "
        "print(json.dumps({'encoding':codecs.lookup(locale.getencoding()).name,"
        "'utf8_mode':sys.flags.utf8_mode,'source':str(Path(subject.__file__).resolve()),"
        "'ir':ir}))"
    )
    env = dict(os.environ)
    env.update(
        LC_ALL="C",
        PYTHONUTF8="0",
        PYTHONCOERCECLOCALE="0",
        PYTHONPATH=os.pathsep.join((str(root), str(root / "src"))),
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(feature)],
        cwd=root,
        env=env,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "encoding": "ascii",
        "utf8_mode": 0,
        "source": str(root / "tools/wct/accept/parsing.py"),
        "ir": expected,
    }
