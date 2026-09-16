"""Real pytest campaigns distinguish semantic mismatches from runner defects."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from types import SimpleNamespace

import pytest

from tools.wct.accept.pipeline import generate, parse_feature, run_mutations
from tools.wct.accept.pytest_receipt import _Recorder, pytest_configure
from tools.wct.accept.semantic import SemanticMismatch, SemanticMismatchError


class PassingReports:
    """Supply ordinary passing reports through pytest's real hook dispatch."""

    @pytest.hookimpl
    def pytest_runtest_makereport(self, item, call):
        """Return a report independently of the receipt observer."""
        return pytest.TestReport(
            nodeid=item.nodeid,
            location=("test_real.py", 0, item.name),
            keywords={},
            outcome="passed",
            longrepr=None,
            when=call.when,
        )


def _active_environment(root, monkeypatch):
    ir = _ir(root)
    second = copy.deepcopy(ir["scenarios"][0])
    second["name"] = "other"
    ir["scenarios"].append(second)
    raw = json.dumps(ir).encode()
    source = root / "input.json"
    source.write_bytes(raw)
    receipt = root / "receipt.json"
    for key, value in {
        "WCT_ACCEPT_IR": str(source),
        "WCT_ACCEPT_RECEIPT": str(receipt),
        "WCT_ACCEPT_ATTEMPT_ID": "configured-attempt",
        "WCT_ACCEPT_IR_SHA256": hashlib.sha256(raw).hexdigest(),
        "WCT_ACCEPT_PHASE": "baseline",
    }.items():
        monkeypatch.setenv(key, value)
    return receipt, hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("missing", [False, True])
def test_active_configuration_dispatches_receipt_with_exact_catalog(tmp_path, monkeypatch, missing):
    """Configured observer records phases and missing expected cases as error."""
    receipt, digest = _active_environment(tmp_path, monkeypatch)
    manager = pytest.PytestPluginManager()
    manager.register(PassingReports())
    pytest_configure(SimpleNamespace(pluginmanager=manager))
    names = ["test_001_units"] if missing else ["test_001_units", "test_002_other"]
    items = [SimpleNamespace(name=name, nodeid=f"test_real.py::{name}") for name in names]
    session = SimpleNamespace(items=items, exitstatus=0)
    manager.hook.pytest_collection_finish(session=session)
    for item in items:
        for phase in ("setup", "call", "teardown"):
            call = pytest.CallInfo.from_call(lambda: None, when=phase)
            report = manager.hook.pytest_runtest_makereport(item=item, call=call)
            assert report.outcome == "passed"
    manager.hook.pytest_sessionfinish(session=session, exitstatus=0)
    assert json.loads(receipt.read_text()) == {
        "schema_version": 1,
        "attempt_id": "configured-attempt",
        "ir_sha256": digest,
        "exit": 0,
        "cases": [
            {"scenario": 0, "status": "pass"},
            {"scenario": 1, "status": "error" if missing else "pass"},
        ],
        "errors": [
            "collection names differ from generated inventory",
            "incomplete or erroneous scenario phases",
        ]
        if missing
        else [],
    }
    events = json.loads(receipt.with_suffix(".events.json").read_text())
    assert events[0] == {"collection": [item.nodeid for item in items]}
    assert [(event["nodeid"], event["phase"], event["status"]) for event in events[1:]] == [
        (item.nodeid, phase, "pass") for item in items for phase in ("setup", "call", "teardown")
    ]


def test_active_configuration_rejects_wrong_hash_with_cause(tmp_path, monkeypatch):
    """Digest disagreement has a meaningful cause before observer execution."""
    receipt, digest = _active_environment(tmp_path, monkeypatch)
    wrong = ("1" if digest[0] == "0" else "0") + digest[1:]
    monkeypatch.setenv("WCT_ACCEPT_IR_SHA256", wrong)
    manager = pytest.PytestPluginManager()
    with pytest.raises(ValueError, match=r"(?i)hash.*mismatch"):
        pytest_configure(SimpleNamespace(pluginmanager=manager))
    assert not receipt.exists()
    assert not receipt.with_suffix(".events.json").exists()


@pytest.fixture
def pytest_project(tmp_path, monkeypatch):
    """Isolate pytest configuration and plugins without hiding the AC1 plugin."""
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.delenv("PYTEST_PLUGINS", raising=False)
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path))
    return tmp_path


def _ir(root):
    feature = root / "case.feature"
    feature.write_text(
        "Feature: stock\nScenario Outline: units\n"
        '  Given inventory contains "<stock>" units\n'
        '  When I reserve "<quantity>" units\n'
        '  Then "<remaining>" units remain\n'
        "  Examples:\n    | stock | quantity | remaining |\n"
        "    | 10 | 3 | 7 |\n    | 5 | 5 | 0 |\n",
        encoding="utf-8",
    )
    return parse_feature(feature)


def _command(root, target):
    return [
        sys.executable,
        "-m",
        "pytest",
        str(target),
        "-q",
        "-c",
        str(root / "pytest.ini"),
        "--confcutdir",
        str(root),
    ]


def _subject(root, body):
    target = root / "test_subject.py"
    target.write_text(textwrap.dedent(body), encoding="utf-8")
    return target


def _receipts(report):
    receipts = []
    for path in Path(report["evidence_dir"]).rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "attempt_id" in data and "cases" in data:
            receipts.append(data)
    return receipts


def test_example_campaign_uses_real_pytest_and_kills_six(pytest_project):
    """Baseline and six value mutants run the real example use case."""
    ir = _ir(pytest_project)
    target = generate(ir, pytest_project / "test_generated.py")
    report = run_mutations(ir, _command(pytest_project, target))
    assert report["schema_version"] == 1
    assert report["baseline"]["status"] == "pass"
    assert report["baseline"]["exit"] == 0
    assert (
        report["planned"],
        report["killed"],
        report["survived"],
        report["errors"],
        report["not_run"],
    ) == (6, 6, 0, 0, 0)
    assert [item["exit"] for item in report["results"]] == [1] * 6
    assert [item["status"] for item in report["results"]] == ["killed"] * 6
    receipts = _receipts(report)
    assert len(receipts) == 7
    assert sum(receipt["cases"] == [{"scenario": 0, "status": "pass"}] for receipt in receipts) == 1
    assert all(receipt["errors"] == [] for receipt in receipts)


def test_unknown_handler_fails_baseline_without_mutants(pytest_project):
    """The missing P02-style handler is not six successful kills."""
    ir = _ir(pytest_project)
    ir["scenarios"][0]["steps"][0]["text"] = 'el repositorio temporal "<stock>"'
    target = generate(ir, pytest_project / "test_generated.py")
    report = run_mutations(ir, _command(pytest_project, target))
    assert report["baseline"]["status"] == "invalid"
    assert report["baseline"]["exit"] == 1
    assert report["baseline"]["reason"]
    assert (report["killed"], report["survived"], report["errors"], report["not_run"]) == (
        0,
        0,
        0,
        6,
    )
    assert all(item["status"] == "not_run" and item["exit"] is None for item in report["results"])
    assert len(_receipts(report)) == 1


@pytest.mark.parametrize("variant", ["extra", "missing"])
def test_pytest_collection_must_match_generated_names(pytest_project, variant):
    """An otherwise green collection with wrong inventory is invalid."""
    body = "def test_001_units():\n    pass\n"
    if variant == "extra":
        body += "\ndef test_unrelated():\n    pass\n"
    else:
        body = "def test_unrelated():\n    pass\n"
    target = _subject(pytest_project, body)
    report = run_mutations(_ir(pytest_project), _command(pytest_project, target))
    assert report["baseline"]["status"] == "invalid"
    assert report["baseline"]["reason"]
    assert report["killed"] == 0
    assert report["not_run"] == 6
    receipts = _receipts(report)
    assert len(receipts) == 1
    assert receipts[0]["errors"]


@pytest.mark.parametrize(
    ("fault", "exit_code"),
    [
        ("skip", 0),
        ("xfail", 0),
        ("assertion", 1),
        ("import", 2),
        ("setup", 1),
        ("teardown", 1),
        ("internal", 3),
    ],
)
def test_fault_after_sane_baseline_is_never_a_kill(pytest_project, fault, exit_code):
    """Even a typed mismatch plus teardown failure invalidates its attempt."""
    imports = "import os\nimport pytest\n"
    conditional = 'os.environ["WCT_ACCEPT_PHASE"] == "mutation"'
    body = "def test_001_units():\n    pass\n"
    if fault in {"skip", "xfail", "assertion"}:
        action = {
            "skip": 'pytest.skip("controlled skip")',
            "xfail": 'pytest.xfail("controlled xfail")',
            "assertion": 'raise AssertionError("not a semantic mismatch")',
        }[fault]
        body = f"def test_001_units():\n    if {conditional}:\n        {action}\n"
    elif fault == "import":
        imports += f"if {conditional}:\n    import ac1_missing_dependency_for_control\n"
    elif fault == "setup":
        imports += (
            f"@pytest.fixture(autouse=True)\ndef broken_setup():\n"
            f"    if {conditional}:\n        raise RuntimeError('setup failed')\n"
        )
    elif fault == "teardown":
        imports += (
            "@pytest.fixture(autouse=True)\ndef broken_teardown():\n"
            f"    yield\n    if {conditional}:\n"
            "        raise RuntimeError('teardown failed')\n"
        )
        body = (
            f"def test_001_units():\n    if {conditional}:\n"
            "        from tools.wct.accept.semantic import SemanticMismatch\n"
            "        raise SemanticMismatch('observed disagreement')\n"
        )
    else:
        (pytest_project / "conftest.py").write_text(
            "import os\ndef pytest_collection_finish(session):\n"
            f"    if {conditional}:\n        raise RuntimeError('internal failure')\n",
            encoding="utf-8",
        )
    target = _subject(pytest_project, imports + body)
    report = run_mutations(_ir(pytest_project), _command(pytest_project, target))
    assert report["baseline"]["status"] == "pass"
    assert report["baseline"]["exit"] == 0
    assert (
        report["planned"],
        report["killed"],
        report["survived"],
        report["errors"],
        report["not_run"],
    ) == (6, 0, 0, 1, 5)
    assert report["results"][0]["status"] == "error"
    assert report["results"][0]["exit"] == exit_code
    assert report["results"][0]["reason"]
    assert all(item["status"] == "not_run" for item in report["results"][1:])


def _configured_plugins(configure):
    manager = pytest.PytestPluginManager()
    before = manager.get_plugins()
    configure(SimpleNamespace(pluginmanager=manager))
    return before, manager.get_plugins(), manager.get_plugin("wct-accept-receipt-observer")


def test_pytest_plugin_is_inactive_without_protocol(pytest_project, monkeypatch):
    """Loading the plugin alone leaves an ordinary pytest run untouched."""
    target = _subject(pytest_project, "def test_ordinary_name():\n    assert 2 + 2 == 4\n")
    env = {key: value for key, value in os.environ.items() if not key.startswith("WCT_ACCEPT_")}
    completed = subprocess.run(
        [*_command(pytest_project, target), "-p", "tools.wct.accept.pytest_receipt"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "1 passed" in completed.stdout
    assert list(pytest_project.glob("*.json")) == []
    for key in list(os.environ):
        if key.startswith("WCT_ACCEPT_"):
            monkeypatch.delenv(key)
    before, registered, observer = _configured_plugins(pytest_configure)
    assert registered == before
    assert observer is None


def _direct_recorder(root, monkeypatch, recorder_type):

    raw = json.dumps(_ir(root)).encode()
    ir_path = root / "input.json"
    ir_path.write_bytes(raw)
    receipt_path = root / "receipt.json"
    for key, value in {
        "WCT_ACCEPT_IR": str(ir_path),
        "WCT_ACCEPT_RECEIPT": str(receipt_path),
        "WCT_ACCEPT_ATTEMPT_ID": "direct-attempt",
        "WCT_ACCEPT_IR_SHA256": hashlib.sha256(raw).hexdigest(),
        "WCT_ACCEPT_PHASE": "baseline",
    }.items():
        monkeypatch.setenv(key, value)
    recorder = recorder_type()
    item = SimpleNamespace(name="test_001_units", nodeid="test_real.py::test_001_units")
    recorder.pytest_collection_finish(SimpleNamespace(items=[item]))
    return recorder, item, receipt_path


def _phase(recorder, item, phase, observation=("passed", None, False)):
    outcome, error, wasxfail = observation

    def body():
        if error is not None:
            raise error

    call = pytest.CallInfo.from_call(body, when=phase)
    report = pytest.TestReport(
        nodeid=item.nodeid,
        location=("test_real.py", 0, item.name),
        keywords={},
        outcome=outcome,
        longrepr=None,
        when=phase,
    )
    if wasxfail:
        report.wasxfail = "controlled xfail"
    wrapper = recorder.pytest_runtest_makereport(item, call)
    next(wrapper)
    with pytest.raises(StopIteration) as finished:
        wrapper.send(report)
    assert finished.value.value is report


def _finish(recorder, code):
    wrapper = recorder.pytest_sessionfinish(SimpleNamespace(exitstatus=code))
    next(wrapper)
    with pytest.raises(StopIteration):
        wrapper.send(None)


@pytest.mark.parametrize(
    "observation",
    [
        ("call", "passed", "none", False, "pass"),
        ("call", "failed", "semantic", False, "mismatch"),
        ("call", "failed", "assertion", False, "error"),
        ("call", "passed", "assertion", False, "error"),
        ("call", "skipped", "none", False, "error"),
        ("call", "passed", "none", True, "error"),
        ("setup", "failed", "semantic", False, "error"),
        ("teardown", "failed", "semantic", False, "error"),
        ("teardown", "skipped", "none", True, "error"),
    ],
)
def test_hook_protocol_observes_raw_phase_and_writes_receipt(
    pytest_project, monkeypatch, observation
):
    phase, outcome, kind, wasxfail, expected = observation
    recorder, item, path = _direct_recorder(pytest_project, monkeypatch, _Recorder)
    errors = {
        "none": None,
        "semantic": SemanticMismatch("different result"),
        "assertion": AssertionError("broken test"),
    }
    for current in ("setup", "call", "teardown"):
        if current == phase:
            _phase(recorder, item, current, (outcome, errors[kind], wasxfail))
        else:
            _phase(recorder, item, current)
    code = 0 if expected == "pass" else 1
    _finish(recorder, code)
    receipt = json.loads(path.read_text())
    assert receipt == {
        "schema_version": 1,
        "attempt_id": "direct-attempt",
        "ir_sha256": os.environ["WCT_ACCEPT_IR_SHA256"],
        "exit": code,
        "cases": [{"scenario": 0, "status": expected}],
        "errors": ["incomplete or erroneous scenario phases"] if expected == "error" else [],
    }
    events = json.loads(path.with_suffix(".events.json").read_text())
    assert events[0] == {"collection": [item.nodeid]}
    assert [event["phase"] for event in events[1:]] == ["setup", "call", "teardown"]
    target = next(event for event in events[1:] if event["phase"] == phase)
    assert (target["outcome"], target["wasxfail"], target["status"]) == (
        outcome,
        wasxfail,
        expected,
    )
    assert (
        target["exception"]
        == {"none": None, "semantic": "SemanticMismatchError", "assertion": "AssertionError"}[kind]
    )


@pytest.mark.parametrize("fault", ["duplicate", "missing", "collection", "internal", "extra"])
def test_hook_receipt_preserves_protocol_faults(pytest_project, monkeypatch, fault):
    recorder, item, path = _direct_recorder(pytest_project, monkeypatch, _Recorder)
    _phase(recorder, item, "setup")
    if fault != "missing":
        _phase(recorder, item, "call")
    _phase(recorder, item, "teardown")
    if fault == "duplicate":
        _phase(recorder, item, "call")
    elif fault == "collection":
        recorder.pytest_collectreport(
            pytest.CollectReport(
                nodeid="broken", outcome="failed", longrepr="import failed", result=[]
            )
        )
    elif fault == "internal":
        recorder.pytest_internalerror(SimpleNamespace(typename="RuntimeError"))
    elif fault == "extra":
        recorder.pytest_collection_finish(
            SimpleNamespace(items=[item, SimpleNamespace(name="extra", nodeid="extra.py::extra")])
        )
    _finish(recorder, 1)
    receipt = json.loads(path.read_text())
    expected_errors = {
        "duplicate": [f"duplicate phase: {item.nodeid}/call"],
        "missing": ["incomplete or erroneous scenario phases"],
        "collection": ["collection failed: broken"],
        "internal": ["pytest internal error: RuntimeError"],
        "extra": ["collection names differ from generated inventory"],
    }
    assert receipt["errors"] == expected_errors[fault]
    assert receipt["cases"] == [
        {"scenario": 0, "status": "error" if fault == "missing" else "pass"}
    ]


def test_semantic_alias_is_the_same_assertion_type():
    assert SemanticMismatch is SemanticMismatchError
    assert issubclass(SemanticMismatch, AssertionError)
    assert type(SemanticMismatch("observed")).__name__ == "SemanticMismatchError"
