"""Cooperative pytest adapter; inactive outside an AC1 protocol attempt."""

from collections import Counter
from collections.abc import Generator
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest

from tools.wct.accept.generation import scenario_names
from tools.wct.accept.semantic import phase_status, scenario_status


class _Recorder:
    def __init__(self) -> None:
        raw = Path(os.environ["WCT_ACCEPT_IR"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != os.environ["WCT_ACCEPT_IR_SHA256"]:
            raise ValueError("AC1 original IR hash mismatch")
        self.names = scenario_names(json.loads(raw))
        self.nodes: dict[str, str] = {}
        self.phases: dict[str, dict[str, str]] = {}
        self.events: list[dict[str, Any]] = []
        self.errors: list[str] = []

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Bind the exact generated names to observed full nodeids."""
        observed = [item.name for item in session.items]
        self.events.append({"collection": [item.nodeid for item in session.items]})
        if Counter(observed) != Counter(self.names):
            self.errors.append("collection names differ from generated inventory")
        for item in session.items:
            self.nodes[item.nodeid] = item.name

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        """Collection failures and skips invalidate the attempt."""
        if not report.passed:
            self.errors.append(f"collection {report.outcome}: {report.nodeid}")

    def pytest_internalerror(self, excinfo: Any) -> None:
        """Retain pytest internal errors rather than treating them as kills."""
        self.errors.append(f"pytest internal error: {excinfo.typename}")

    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_runtest_makereport(
        self, item: pytest.Item, call: pytest.CallInfo[Any]
    ) -> Generator[None, pytest.TestReport, pytest.TestReport]:
        """Combine the raw exception with the report after other wrappers."""
        exception = call.excinfo.value if call.excinfo is not None else None
        report = yield
        status = phase_status(
            report.when, report.outcome, exception, wasxfail=hasattr(report, "wasxfail")
        )
        phases = self.phases.setdefault(item.nodeid, {})
        if report.when in phases:
            self.errors.append(f"duplicate phase: {item.nodeid}/{report.when}")
        phases[report.when] = status
        self.events.append(
            {
                "nodeid": item.nodeid,
                "phase": report.when,
                "outcome": report.outcome,
                "exception": type(exception).__name__ if exception is not None else None,
                "wasxfail": hasattr(report, "wasxfail"),
                "status": status,
            }
        )
        return report

    def _cases(self) -> list[dict[str, Any]]:
        statuses = {
            name: scenario_status(self.phases.get(nodeid, {}))
            for nodeid, name in self.nodes.items()
        }
        return [
            {"scenario": index, "status": statuses.get(name, "error")}
            for index, name in enumerate(self.names)
        ]

    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_sessionfinish(self, session: pytest.Session) -> Generator[None, Any, None]:
        """Persist minimal receipt and a separate node/phase diagnostic log."""
        yield
        cases = self._cases()
        if any(case["status"] == "error" for case in cases):
            self.errors.append("incomplete or erroneous scenario phases")
        document = {
            "schema_version": 1,
            "attempt_id": os.environ["WCT_ACCEPT_ATTEMPT_ID"],
            "ir_sha256": os.environ["WCT_ACCEPT_IR_SHA256"],
            "exit": int(session.exitstatus),
            "cases": cases,
            "errors": self.errors,
        }
        path = Path(os.environ["WCT_ACCEPT_RECEIPT"])
        path.with_suffix(".events.json").write_text(json.dumps(self.events, indent=2) + "\n")
        with path.open("x", encoding="utf-8") as stream:
            json.dump(document, stream)


def pytest_configure(config: pytest.Config) -> None:
    """Register only when the supervisor explicitly provides the protocol."""
    if "WCT_ACCEPT_IR" not in os.environ:
        return
    config.pluginmanager.register(_Recorder(), "wct-accept-receipt-observer")
