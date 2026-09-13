"""AC1 observes real runner processes, separating failures from mismatches."""

from contextlib import suppress
import hashlib
import json
import os
from pathlib import Path
import select
import selectors
import signal
import subprocess
import sys
import time
import types
from typing import Any, ClassVar

import pytest

from tests.acceptance.steps import execute_scenario
from tools.wct.accept import campaign, process as process_transport
from tools.wct.accept.pipeline import accept_verdict, parse_feature, run_mutations
from tools.wct.accept.process import _terminate, run_process
from tools.wct.accept.semantic import SemanticMismatch


def example_ir() -> dict:
    """A single mutable value yields an independently known denominator one."""
    return {
        "schema_version": 1,
        "feature": "Probe",
        "source": "probe.feature",
        "background": [],
        "scenarios": [
            {"name": "probe", "line": 2, "outline": True, "steps": [], "examples": [{"value": "2"}]}
        ],
    }


def test_ac1_feature_executes_real_campaigns(tmp_path: Path, monkeypatch) -> None:

    feature = Path(__file__).parents[2] / "features/wct-acceptance-evidence-001.feature"
    ir = parse_feature(feature)
    monkeypatch.chdir(tmp_path)
    assert execute_scenario(ir, 0) is None

    reports = [
        json.loads(path.read_text()) for path in tmp_path.glob("build/tmp/wct-accept-*/report.json")
    ]
    assert len(reports) == 6
    assert sorted((r["killed"], r["errors"], r["survived"], r["not_run"]) for r in reports) == [
        (0, 0, 0, 1),
        (0, 0, 1, 0),
        (0, 1, 0, 0),
        (0, 1, 0, 0),
        (0, 1, 0, 0),
        (1, 0, 0, 0),
    ]


def test_ac1_semantic_oracle_is_not_table_binding(tmp_path: Path, monkeypatch) -> None:

    feature = Path(__file__).parents[2] / "features/wct-acceptance-evidence-001.feature"
    ir = parse_feature(feature)
    ir["scenarios"][0]["examples"] = [ir["scenarios"][0]["examples"][0]]
    ir["scenarios"][0]["examples"][0]["killed"] = "2"
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SemanticMismatch, match="campaign verdict/counts"):
        execute_scenario(ir, 0)


def test_failed_original_does_not_launch_mutants(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    ir = example_ir()
    report = run_mutations(ir, [sys.executable, "-c", "raise SystemExit(1)"])
    assert report["killed"] == 0
    assert report["not_run"] == report["planned"] == 1
    assert report["baseline"]["status"] == "invalid"
    reason = report["results"][0]["reason"]
    assert isinstance(reason, str)
    assert reason.strip()
    assert all(word in reason.lower() for word in ("attempt", "protocol"))
    assert accept_verdict(ir, report) == (
        True,
        [f"baseline invalid: {report['baseline']['reason']}"],
    )
    assert not list(Path(report["evidence_dir"]).glob("mutation-*"))


def test_unknown_fixture_mode_is_not_a_success(tmp_path: Path, monkeypatch) -> None:
    runner = Path(__file__).parents[1] / "acceptance/protocol_runner.py"
    monkeypatch.chdir(tmp_path)
    report = run_mutations(example_ir(), [sys.executable, str(runner), "pass__mutated", "pass"])
    assert report["baseline"]["status"] == "invalid"
    assert report["baseline"]["exit"] == 2
    assert report["not_run"] == 1


def test_empty_command_reports_launch_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    report = run_mutations(example_ir(), [])
    assert report["baseline"]["status"] == "invalid"
    assert report["baseline"]["exit"] is None
    assert "process error" in report["baseline"]["reason"]
    assert report["not_run"] == 1


def test_expired_prelaunch_keeps_attempt_identity_and_empty_logs(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(campaign, "CAMPAIGN_SECONDS", 0)
    command = [sys.executable, "-c", "raise SystemExit(99)"]
    report = run_mutations(example_ir(), command)
    directory = Path(report["evidence_dir"]) / "baseline"
    attempt = json.loads((directory / "attempt.json").read_text())
    assert attempt["status"] == "invalid"
    assert attempt["reason"] == "campaign timeout"
    assert attempt["exit"] is None
    assert attempt["argv"] == command
    assert attempt["cwd"] == str(tmp_path)
    assert len(attempt["attempt_id"]) == 32
    assert attempt["ir_sha256"] == hashlib.sha256((directory / "ir.json").read_bytes()).hexdigest()
    assert (directory / "stdout.log").read_bytes() == b""
    assert (directory / "stderr.log").read_bytes() == b""
    assert not (directory / "receipt.json").exists()


def test_child_temporary_directory_is_per_attempt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TMPDIR", "/deliberate-parent-sentinel-not-created")
    code = "import os; print(os.environ['TMPDIR']); raise SystemExit(1)"
    report = run_mutations(example_ir(), [sys.executable, "-c", code])
    directory = Path(report["evidence_dir"]) / "baseline"
    assert (directory / "stdout.log").read_text().strip() == str(directory)


@pytest.mark.parametrize(
    ("mode", "status"),
    [
        ("semantic", "killed"),
        ("pass", "survived"),
        ("missing_receipt", "error"),
        ("wrong_identity", "error"),
        ("mixed_error", "error"),
        ("crash", "error"),
        ("import", "error"),
        ("signal", "error"),
        ("output", "error"),
    ],
)
def test_postbaseline_process_dispositions(
    tmp_path: Path, monkeypatch, mode: str, status: str
) -> None:
    runner = Path(__file__).parents[1] / "acceptance/protocol_runner.py"
    monkeypatch.chdir(tmp_path)
    report = run_mutations(example_ir(), [sys.executable, str(runner), "pass", mode])
    assert report["baseline"]["status"] == "pass"
    assert report["results"][0]["status"] == status
    assert report["planned"] == 1
    assert report["killed"] + report["survived"] + report["errors"] + report["not_run"] == 1
    assert accept_verdict(example_ir(), report)[0] is (status != "killed")


def test_mutant_timeout_is_error_and_stops(tmp_path: Path, monkeypatch) -> None:

    runner = Path(__file__).parents[1] / "acceptance/protocol_runner.py"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(campaign, "ATTEMPT_SECONDS", 0.2)
    ir = example_ir()
    ir["scenarios"][0]["examples"].append({"value": "3"})
    report = run_mutations(ir, [sys.executable, str(runner), "pass", "timeout"])
    assert report["errors"] == report["not_run"] == 1
    assert report["results"][0]["reason"] == "timeout"
    assert report["results"][1]["status"] == "not_run"
    assert report["results"][1]["exit"] is None
    reason = report["results"][1]["reason"]
    assert isinstance(reason, str)
    assert reason.strip()
    assert all(word in reason.lower() for word in ("attempt", "protocol"))
    assert not (Path(report["evidence_dir"]) / "mutation-1").exists()
    failed, messages = accept_verdict(ir, report)
    assert failed
    assert "invalid campaign" not in messages[0].lower()
    assert "not_run" in messages[0].lower()


def _transport_child(root: Path, body: str) -> tuple[list[str], Path]:
    """Write a real child with identity outside the output byte budget."""
    pid_path = root / "child.pid"
    script = root / "child.py"
    script.write_text(
        "import os, sys, time\nfrom pathlib import Path\n"
        "Path(sys.argv[1]).write_text(str(os.getpid()))\n" + body,
        encoding="utf-8",
    )
    return [sys.executable, str(script), str(pid_path)], pid_path


def _cleanup_transport_child(pid_path: Path) -> None:
    """Reap a test-owned child if a defective transport left it behind."""
    if not pid_path.exists():
        return
    pid = int(pid_path.read_text())
    try:
        result, _status = os.waitpid(pid, os.WNOHANG)
    except ChildProcessError:
        return
    if result == 0:
        with suppress(ProcessLookupError):
            os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)


@pytest.mark.parametrize("extra", [0, 1])
def test_transport_combined_output_exact_limit_and_one_byte_excess(
    tmp_path: Path, extra: int
) -> None:
    """The literal cap applies jointly to both streams, not separately."""
    body = (
        "sys.stdout.buffer.write(b'A' * 524288)\nsys.stdout.buffer.flush()\n"
        f"sys.stderr.buffer.write(b'B' * {524288 + extra})\nsys.stderr.buffer.flush()\n"
    )
    if extra:
        body += "time.sleep(60)\n"
    command, pid_path = _transport_child(tmp_path, body)
    try:
        report = run_process(command, dict(os.environ), tmp_path, 5.0)
        stdout = (tmp_path / "stdout.log").read_bytes()
        stderr = (tmp_path / "stderr.log").read_bytes()
        assert len(stdout) + len(stderr) == 1_048_576
        assert stdout
        assert stdout == b"A" * len(stdout)
        assert stderr
        assert stderr == b"B" * len(stderr)
        assert report["exit"] == (-signal.SIGKILL if extra else 0)
        assert report["reason"] == ("output limit exceeded" if extra else "")
        assert report["duration"] >= 0
        if not extra:
            assert (len(stdout), len(stderr)) == (524288, 524288)
        with pytest.raises(ChildProcessError):
            os.waitpid(int(pid_path.read_text()), os.WNOHANG)
    finally:
        _cleanup_transport_child(pid_path)


def test_transport_timeout_preserves_partial_streams_real_exit_and_reaps(tmp_path: Path) -> None:
    """A live writer is killed, reaped, and its earlier output retained."""
    command, pid_path = _transport_child(
        tmp_path,
        "sys.stdout.buffer.write(b'before timeout stdout\\n')\nsys.stdout.buffer.flush()\n"
        "sys.stderr.buffer.write(b'before timeout stderr\\n')\nsys.stderr.buffer.flush()\n"
        "time.sleep(60)\n",
    )
    try:
        report = run_process(command, dict(os.environ), tmp_path, 2.0)
        assert report["reason"] == "timeout"
        assert report["exit"] == -signal.SIGKILL
        stdout = (tmp_path / "stdout.log").read_bytes()
        stderr = (tmp_path / "stderr.log").read_bytes()
        assert stdout == b"before timeout stdout\n"
        assert stderr == b"before timeout stderr\n"
        assert len(stdout) + len(stderr) < 1_048_576
        with pytest.raises(ChildProcessError):
            os.waitpid(int(pid_path.read_text()), os.WNOHANG)
    finally:
        _cleanup_transport_child(pid_path)


@pytest.mark.parametrize(
    ("existing", "expected"),
    [
        (
            "existing.alpha,existing.beta",
            "existing.alpha,existing.beta,tools.wct.accept.pytest_receipt",
        ),
        (
            "tools.wct.accept.pytest_receipt,existing.alpha",
            "tools.wct.accept.pytest_receipt,existing.alpha",
        ),
    ],
)
def test_campaign_preserves_child_plugin_declarations_exactly(
    tmp_path: Path, monkeypatch, existing: str, expected: str
) -> None:
    """Observe child environment transport, without pretending to import plugins."""
    runner = tmp_path / "environment_runner.py"
    runner.write_text(
        "import json, os\nfrom pathlib import Path\n"
        "ir = json.loads(Path(os.environ['WCT_ACCEPT_IR']).read_text())\n"
        "status = 'pass' if ir['scenarios'][0]['examples'][0]['value'] == '2' else 'mismatch'\n"
        "code = 0 if status == 'pass' else 1\n"
        "print(json.dumps({'plugins': os.environ.get('PYTEST_PLUGINS'),\n"
        " 'pytest_temproot': os.environ.get('PYTEST_DEBUG_TEMPROOT'),\n"
        " 'tmpdir': os.environ.get('TMPDIR')}))\n"
        "receipt = {'schema_version': 1, 'attempt_id': os.environ['WCT_ACCEPT_ATTEMPT_ID'],\n"
        " 'ir_sha256': os.environ['WCT_ACCEPT_IR_SHA256'], 'exit': code,\n"
        " 'cases': [{'scenario': 0, 'status': status}], 'errors': []}\n"
        "Path(os.environ['WCT_ACCEPT_RECEIPT']).write_text(json.dumps(receipt))\n"
        "raise SystemExit(code)\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTEST_PLUGINS", existing)
    parent_temporaries = tmp_path / "host-temporaries"
    parent_temporaries.mkdir()
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(parent_temporaries))
    monkeypatch.setenv("TMPDIR", str(parent_temporaries))
    report = run_mutations(example_ir(), [sys.executable, str(runner)])
    assert report["baseline"]["status"] == "pass"
    assert report["baseline"]["exit"] == 0
    assert (report["planned"], report["killed"], report["errors"], report["not_run"]) == (
        1,
        1,
        0,
        0,
    )
    assert report["results"][0]["exit"] == 1
    logs = sorted(Path(report["evidence_dir"]).glob("*/stdout.log"))
    assert logs == [
        Path(report["evidence_dir"]) / "baseline/stdout.log",
        Path(report["evidence_dir"]) / "mutation-0/stdout.log",
    ]
    for log in logs:
        observed = json.loads(log.read_text(encoding="utf-8"))
        assert observed == {
            "plugins": expected,
            "pytest_temproot": str(log.parent),
            "tmpdir": str(log.parent),
        }
        assert log.parent != parent_temporaries
        assert observed["plugins"].split(",").count("tools.wct.accept.pytest_receipt") == 1
    assert os.environ["PYTEST_PLUGINS"] == existing
    assert os.environ["PYTEST_DEBUG_TEMPROOT"] == str(parent_temporaries)
    assert os.environ["TMPDIR"] == str(parent_temporaries)


def test_campaign_transports_ir_bytes_as_utf8_without_ascii_escaping(
    tmp_path: Path, monkeypatch
) -> None:
    """The persisted IR keeps non-ASCII text literal and its hash travels intact."""
    runner = Path(__file__).parents[1] / "acceptance/protocol_runner.py"
    ir = example_ir()
    ir["scenarios"][0]["name"] = "Café Ñ"
    ir["scenarios"][0]["examples"][0]["value"] = "é"
    monkeypatch.chdir(tmp_path)
    report = run_mutations(ir, [sys.executable, str(runner), "pass", "pass"])
    assert report["baseline"]["status"] == "pass"
    raw = (Path(report["evidence_dir"]) / "baseline/ir.json").read_bytes()
    assert "Café Ñ".encode() in raw
    assert b"\\u00e9" not in raw
    receipt = json.loads((Path(report["evidence_dir"]) / "baseline/receipt.json").read_text())
    assert receipt["ir_sha256"] == hashlib.sha256(raw).hexdigest()


def test_report_and_results_omit_internal_ir_even_when_baseline_invalid(
    tmp_path: Path, monkeypatch
) -> None:
    """No result row transports the internal IR, even when everything is not_run."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    report = run_mutations(example_ir(), [sys.executable, "-c", "raise SystemExit(1)"])
    assert report["baseline"]["status"] == "invalid"
    assert report["not_run"] == report["planned"] == 1
    assert all("ir" not in result for result in report["results"])
    persisted = json.loads((Path(report["evidence_dir"]) / "report.json").read_text())
    assert all("ir" not in result for result in persisted["results"])


def test_zero_budget_reports_timeout_without_launching(tmp_path: Path) -> None:
    """A zero budget fails prelaunch: no process is ever started."""
    marker = tmp_path / "launched.marker"
    command = [
        sys.executable,
        "-c",
        "import sys\nfrom pathlib import Path\n"
        "Path(sys.argv[1]).write_text('launched')\nraise SystemExit(7)",
        str(marker),
    ]
    report = run_process(command, dict(os.environ), tmp_path, 0.0)
    assert report["exit"] is None
    assert report["reason"] == "campaign timeout"
    assert not marker.exists()


def test_run_process_child_receives_eof_not_parent_stdin(tmp_path: Path) -> None:
    """The transport child reads DEVNULL, never the caller's standard input."""
    harness = tmp_path / "stdin_harness.py"
    harness.write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "from tools.wct.accept.process import run_process\n"
        "logs = Path(sys.argv[1])\n"
        "logs.mkdir(parents=True, exist_ok=True)\n"
        "result = run_process(\n"
        "    [sys.executable, '-c',"
        " \"import sys; print('EOF' if sys.stdin.read() == '' else sys.stdin.read())\"],\n"
        "    {}, logs, 10.0,\n"
        ")\n"
        "print(json.dumps(result))\n",
        encoding="utf-8",
    )
    (tmp_path / "direct").mkdir()
    direct = run_process(
        [sys.executable, "-c", "print('ok')"], dict(os.environ), tmp_path / "direct", 10.0
    )
    assert direct["exit"] == 0
    assert direct["reason"] == ""
    proc = subprocess.run(
        [sys.executable, str(harness), str(tmp_path / "logs")],
        input="PARENT-STANDARD-IN\n",
        capture_output=True,
        text=True,
        timeout=60.0,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["exit"] == 0
    assert result["reason"] == ""
    assert (tmp_path / "logs" / "stdout.log").read_text() == "EOF\n"


def test_transport_reads_pending_output_after_leader_terminates(
    tmp_path: Path, monkeypatch
) -> None:
    """Output pending behind a terminated leader's EOF is still captured."""
    late_read, late_write = os.pipe()
    os.write(late_write, b"descendant-late\n")
    os.close(late_write)
    late = os.fdopen(late_read, "rb", buffering=0)
    controlled = types.SimpleNamespace(
        DefaultSelector=lambda: _PendingOutputSelector(time.monotonic() + 15.0, late),
        EVENT_READ=1,
    )
    monkeypatch.setattr(process_transport, "selectors", controlled)
    try:
        report = run_process(
            [sys.executable, "-c", "print('leader-done')"],
            dict(os.environ),
            tmp_path,
            10.0,
        )
    finally:
        late.close()
    assert report["exit"] == 0
    assert report["reason"] == ""
    assert (tmp_path / "stdout.log").read_bytes() == b"leader-done\ndescendant-late\n"


class _PendingOutputSelector:
    """Doble fiel de selector: registro real, eventos sólo para registrados.

    Modela el estado realizable «líder terminado con salida pendiente»: el
    canal del líder llega a EOF y, al retirarlo el SUT, el mismo canal queda
    registrado por la tubería propia del test con los bytes del descendiente,
    que se leen y después alcanzan su propio EOF.
    """

    def __init__(self, deadline: float, late: Any) -> None:
        self._deadline = deadline
        self._late = late
        self._registry: dict[Any, Any] = {}
        self._steps = [
            "read-leader",
            "eof-leader",
            "read-late",
            "eof-late",
            "eof-stderr",
            "end",
        ]

    def register(self, fileobj: Any, _events: Any = None, data: Any = None) -> None:
        self._registry[fileobj] = data

    def unregister(self, fileobj: Any) -> None:
        data = self._registry.pop(fileobj, None)
        if data == "stdout" and "read-late" in self._steps:
            self._registry[self._late] = "stdout"

    _TARGETS: ClassVar[dict[str, str]] = {
        "read-leader": "stdout",
        "eof-leader": "stdout",
        "read-late": "late",
        "eof-late": "late",
        "eof-stderr": "stderr",
    }
    _WAITERS: ClassVar[frozenset[str]] = frozenset({"eof-leader", "eof-late", "eof-stderr"})

    def select(self, timeout: float | None = None):
        self._requested_wait = timeout
        step = self._steps.pop(0)
        if step == "end":
            return []
        target = (
            self._late if self._TARGETS[step] == "late" else self._registered(self._TARGETS[step])
        )
        if step in self._WAITERS:
            self._wait_readable(target)
        return [(self._key(target), 1)]

    def get_map(self):
        return dict(self._registry)

    def _registered(self, data: Any) -> Any:
        return next(fileobj for fileobj, value in self._registry.items() if value == data)

    def _key(self, fileobj: Any):
        return types.SimpleNamespace(
            fd=fileobj.fileno(), fileobj=fileobj, data=self._registry[fileobj]
        )

    def _wait_readable(self, fileobj: Any) -> None:
        while not select.select([fileobj], [], [], 0.05)[0]:
            if time.monotonic() > self._deadline:
                raise TimeoutError("stream never reached readiness")

    def __enter__(self):
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def close(self) -> None:
        return None


def test_silent_attempt_duration_tracks_budget_with_controlled_clock(
    tmp_path: Path, monkeypatch
) -> None:
    """With a clock advanced by each select wait, a silent attempt never overshoots."""
    clock = {"now": 0.0}

    def fake_monotonic() -> float:
        return clock["now"]

    class FakeSelector:
        def __init__(self) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def register(self, *_args: object) -> None:
            return None

        def unregister(self, *_args: object) -> None:
            return None

        def select(self, timeout: float | None):
            clock["now"] += timeout if timeout is not None else 0.0
            return []

        def get_map(self):
            return {"still-registered": object()}

        def close(self) -> None:
            return None

    fake_selectors = types.SimpleNamespace(
        DefaultSelector=FakeSelector, EVENT_READ=selectors.EVENT_READ
    )
    monkeypatch.setattr(process_transport, "time", types.SimpleNamespace(monotonic=fake_monotonic))
    monkeypatch.setattr(process_transport, "selectors", fake_selectors)
    report = run_process([sys.executable, "-c", "pass"], dict(os.environ), tmp_path, 0.2)
    assert report["reason"] == "timeout"
    assert 0.0 <= report["duration"] <= 0.25


def test_terminate_an_already_exited_process_does_not_raise() -> None:
    """Terminating a reaped child is a no-op, not a TypeError."""
    child = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    child.wait()
    assert child.poll() is not None
    _terminate(child)


def test_duration_is_a_measurement_not_an_accumulation(tmp_path: Path, monkeypatch) -> None:
    """run_process duration is end-start under a controlled clock."""
    calls = {"count": 0}

    def fake_monotonic() -> float:
        calls["count"] += 1
        return 10.0 if calls["count"] <= 3 else 10.5

    monkeypatch.setattr(process_transport, "time", types.SimpleNamespace(monotonic=fake_monotonic))
    report = run_process([sys.executable, "-c", "pass"], dict(os.environ), tmp_path, 0.5)
    assert report["exit"] == 0
    assert report["duration"] == 0.5
