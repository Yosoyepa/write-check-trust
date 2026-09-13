"""Independent wire literals and mutations of the AC1 receipt contract."""

import errno
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.wct.accept.receipt import validate_receipt

GOLDEN = (
    b'{"schema_version":1,"attempt_id":"attempt","ir_sha256":"'
    b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
    b'"exit":0,"cases":[{"scenario":0,"status":"pass"}],"errors":[]}'
)


IDENTITY = {"attempt_id": "attempt", "ir_sha256": "a" * 64, "scenario_count": 1}


def test_literal_receipt_and_valid_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "receipt.json"
    path.write_bytes(GOLDEN)
    assert validate_receipt(path, exit_code=0, **IDENTITY) == ("pass", "all scenarios passed")
    payload = json.loads(GOLDEN)
    payload["exit"] = 1
    payload["cases"][0]["status"] = "mismatch"
    path.write_text(json.dumps(payload))
    assert validate_receipt(path, exit_code=1, **IDENTITY) == ("mismatch", "semantic mismatch")


@pytest.mark.parametrize(
    ("field", "value", "cause"),
    [
        ("schema_version", True, ("identity", "schema_version")),
        ("schema_version", 2, ("identity", "schema_version")),
        ("attempt_id", "old", ("identity", "attempt_id")),
        ("ir_sha256", "b" * 64, ("identity", "ir_sha256")),
        ("exit", False, ("identity", "exit")),
        ("exit", 1, ("identity", "exit")),
        ("cases", [], ()),
        ("cases", [{"scenario": True, "status": "pass"}], ()),
        ("cases", [{"scenario": 0, "status": "unknown"}], ()),
        ("errors", [""], ()),
        ("errors", ["teardown failed"], ()),
        ("extra", 1, ()),
    ],
)
def test_corrupt_receipt_is_invalid(tmp_path: Path, field: str, value, cause) -> None:
    path = tmp_path / "receipt.json"
    payload = json.loads(GOLDEN)
    payload[field] = value
    path.write_text(json.dumps(payload))
    status, reason = validate_receipt(path, exit_code=0, **IDENTITY)
    assert status == "invalid"
    assert reason
    assert all(word in reason.lower() for word in cause)


@pytest.mark.parametrize(
    "raw",
    [
        GOLDEN.replace(b'"schema_version":1', b'"schema_version":1,"schema_version":1'),
        b'{"x":NaN}',
        b"\xff",
        b"[]",
        b"{",
    ],
)
def test_invalid_wire_never_passes(tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "receipt.json"
    path.write_bytes(raw)
    assert validate_receipt(path, exit_code=0, **IDENTITY)[0] == "invalid"


def test_absent_directory_and_symlink_receipts(tmp_path: Path) -> None:
    absent = tmp_path / "absent"
    assert validate_receipt(absent, exit_code=0, **IDENTITY)[0] == "invalid"
    assert validate_receipt(tmp_path, exit_code=0, **IDENTITY)[0] == "invalid"
    real = tmp_path / "real"
    real.write_bytes(GOLDEN)
    absent.symlink_to(real)
    assert validate_receipt(absent, exit_code=0, **IDENTITY)[0] == "invalid"


def test_receipt_exact_byte_limit_and_one_byte_excess(tmp_path: Path) -> None:
    """Whitespace is legal JSON: size, not syntax, distinguishes the boundary."""
    path = tmp_path / "bounded.json"
    exact = GOLDEN + b" " * (1_048_576 - len(GOLDEN))
    path.write_bytes(exact)
    assert validate_receipt(path, exit_code=0, **IDENTITY) == ("pass", "all scenarios passed")
    path.write_bytes(exact + b" ")
    assert validate_receipt(path, exit_code=0, **IDENTITY) == (
        "invalid",
        "invalid receipt: receipt exceeds byte limit",
    )


@pytest.mark.parametrize(
    "field", ["schema_version", "attempt_id", "ir_sha256", "exit", "cases", "errors"]
)
def test_each_missing_top_level_key_is_invalid(tmp_path: Path, field: str) -> None:
    path = tmp_path / "missing-key.json"
    document = json.loads(GOLDEN)
    del document[field]
    path.write_text(json.dumps(document), encoding="utf-8")
    assert validate_receipt(path, exit_code=0, **IDENTITY) == (
        "invalid",
        "invalid receipt: receipt keys",
    )


@pytest.mark.parametrize(
    "raw",
    [
        GOLDEN.replace(b'"scenario":0', b'"scenario":0,"scenario":0'),
        GOLDEN.replace(b'"status":"pass"', b'"status":"pass","status":"pass"'),
    ],
)
def test_duplicate_nested_keys_are_rejected_before_disposition(tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "duplicate-nested.json"
    path.write_bytes(raw)
    assert validate_receipt(path, exit_code=0, **IDENTITY) == (
        "invalid",
        "invalid receipt: duplicate receipt key",
    )


@pytest.mark.parametrize(
    ("cases", "reason"),
    [
        ([{"scenario": 0, "status": "pass"}] * 2, "case index/duplicate"),
        ([{"scenario": -1, "status": "pass"}], "case inventory"),
        ([{"scenario": 1, "status": "pass"}], "case inventory"),
        ([{"scenario": 0.0, "status": "pass"}], "case index/duplicate"),
        ([{"scenario": "0", "status": "pass"}], "case index/duplicate"),
        ([{"scenario": 0}], "case keys"),
        ([{"status": "pass"}], "case keys"),
        ([{"scenario": 0, "status": "pass", "extra": 0}], "case keys"),
        ([None], "case keys"),
        ({"scenario": 0, "status": "pass"}, "cases must be a list"),
        ([{"scenario": 0, "status": True}], "case status"),
        ([{"scenario": 0, "status": None}], "case status"),
    ],
)
def test_case_shapes_and_identity_are_not_coerced(tmp_path: Path, cases, reason: str) -> None:
    path = tmp_path / "cases.json"
    document = json.loads(GOLDEN)
    document["cases"] = cases
    path.write_text(json.dumps(document), encoding="utf-8")
    assert validate_receipt(path, exit_code=0, **IDENTITY) == (
        "invalid",
        f"invalid receipt: {reason}",
    )


@pytest.mark.parametrize("errors", [None, {}, "failure", [True], [0], [None]])
def test_error_container_and_members_have_exact_types(tmp_path: Path, errors) -> None:
    path = tmp_path / "errors.json"
    document = json.loads(GOLDEN)
    document["errors"] = errors
    path.write_text(json.dumps(document), encoding="utf-8")
    assert validate_receipt(path, exit_code=0, **IDENTITY) == (
        "invalid",
        "invalid receipt: errors must contain nonempty strings",
    )


@pytest.mark.parametrize(
    ("status", "code"), [("pass", 1), ("mismatch", 0), ("mismatch", 2), ("mismatch", -9)]
)
def test_receipt_matching_process_exit_still_requires_valid_disposition(
    tmp_path: Path, status: str, code: int
) -> None:
    path = tmp_path / "disposition.json"
    document = json.loads(GOLDEN)
    document["exit"] = code
    document["cases"][0]["status"] = status
    path.write_text(json.dumps(document), encoding="utf-8")
    assert validate_receipt(path, exit_code=code, **IDENTITY) == (
        "invalid",
        "invalid receipt: receipt exit/status contradiction",
    )


@pytest.mark.parametrize(
    ("statuses", "errors"),
    [(["mismatch", "error"], []), (["mismatch", "pass"], ["teardown failed"])],
)
def test_mismatch_does_not_hide_another_error(tmp_path: Path, statuses, errors) -> None:
    path = tmp_path / "mixed.json"
    document = json.loads(GOLDEN)
    document.update(
        exit=1,
        cases=[{"scenario": index, "status": status} for index, status in enumerate(statuses)],
        errors=errors,
    )
    path.write_text(json.dumps(document), encoding="utf-8")
    assert validate_receipt(
        path, attempt_id="attempt", ir_sha256="a" * 64, exit_code=1, scenario_count=2
    ) == ("invalid", "invalid receipt: runner errors")


@pytest.mark.parametrize("mismatch", [False, True])
def test_valid_two_scenarios_accept_permuted_identity_order(tmp_path: Path, mismatch: bool) -> None:
    """Identity is a complete set, not an implicit requirement to sort the wire."""
    path = tmp_path / "two.json"
    document = json.loads(GOLDEN)
    code = 1 if mismatch else 0
    document.update(
        exit=code,
        cases=[
            {"scenario": 1, "status": "pass"},
            {"scenario": 0, "status": "mismatch" if mismatch else "pass"},
        ],
    )
    path.write_text(json.dumps(document), encoding="utf-8")
    expected = ("mismatch", "semantic mismatch") if mismatch else ("pass", "all scenarios passed")
    assert (
        validate_receipt(
            path, attempt_id="attempt", ir_sha256="a" * 64, exit_code=code, scenario_count=2
        )
        == expected
    )


def test_fifo_receipt_is_rejected_without_waiting_for_a_writer(tmp_path: Path) -> None:
    """A bounded child protects the suite if nonblocking receipt open regresses."""
    path = tmp_path / "receipt.fifo"
    os.mkfifo(path)
    command = [
        sys.executable,
        "-c",
        "import json,sys; from pathlib import Path; "
        "from tools.wct.accept.receipt import validate_receipt; "
        "print(json.dumps(validate_receipt(Path(sys.argv[1]), "
        "attempt_id='attempt', ir_sha256='a'*64, exit_code=0, scenario_count=1)))",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == ["invalid", "invalid receipt: receipt is not regular"]
    observed = validate_receipt(path, exit_code=0, **IDENTITY)
    assert json.loads(completed.stdout) == list(observed)


@pytest.mark.parametrize("valid", [True, False])
def test_receipt_descriptor_closes_after_parse_or_error(
    tmp_path: Path, monkeypatch, valid: bool
) -> None:
    path = tmp_path / "closed.json"
    path.write_bytes(GOLDEN if valid else b"{")
    original = os.open
    descriptors = []

    def observe_open(*args, **kwargs):
        descriptor = original(*args, **kwargs)
        descriptors.append(descriptor)
        return descriptor

    monkeypatch.setattr(os, "open", observe_open)
    status, reason = validate_receipt(path, exit_code=0, **IDENTITY)
    assert status == ("pass" if valid else "invalid")
    assert reason
    assert len(descriptors) == 1
    with pytest.raises(OSError, match="Bad file descriptor") as caught:
        os.fstat(descriptors[0])
    assert caught.value.errno == errno.EBADF


@pytest.mark.parametrize("second", ["unknown", "pass__mutated", "MISMATCH"])
def test_mismatch_cannot_hide_an_unknown_case_status(tmp_path: Path, second: str) -> None:
    path = tmp_path / "unknown-with-mismatch.json"
    document = json.loads(GOLDEN)
    document.update(
        exit=1,
        cases=[{"scenario": 0, "status": "mismatch"}, {"scenario": 1, "status": second}],
    )
    path.write_text(json.dumps(document), encoding="utf-8")
    status, reason = validate_receipt(
        path, attempt_id="attempt", ir_sha256="a" * 64, exit_code=1, scenario_count=2
    )
    assert status == "invalid"
    assert "case status" in reason.lower()


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_json_constant_preserves_its_cause(tmp_path: Path, constant: str) -> None:
    path = tmp_path / "constant.json"
    path.write_text('{"value":' + constant + "}", encoding="utf-8")
    status, reason = validate_receipt(path, exit_code=0, **IDENTITY)
    assert status == "invalid"
    assert "constant" in reason.lower()
    assert constant in reason


def test_oversized_receipt_is_rejected_without_reading_entire_file(tmp_path: Path) -> None:
    """An isolated allocation probe distinguishes bounded IO from reading all."""
    path = tmp_path / "oversized.json"
    # Eight MiB is a safe fixture, not an attempt to exhaust host memory.
    with path.open("wb") as stream:
        for _ in range(8):
            stream.write(b" " * (1024 * 1024))
    assert path.stat().st_size == 8 * 1024 * 1024
    expected = ("invalid", "invalid receipt: receipt exceeds byte limit")
    assert validate_receipt(path, exit_code=0, **IDENTITY) == expected
    root = Path(__file__).resolve().parents[2]
    script = (
        "import json,sys,tracemalloc; from pathlib import Path; "
        "import tools.wct.accept.receipt as subject; "
        "path=Path(sys.argv[1]); tracemalloc.start(); "
        "result=subject.validate_receipt(path,attempt_id='attempt',"
        "ir_sha256='a'*64,exit_code=0,scenario_count=1); "
        "peak=tracemalloc.get_traced_memory()[1]; tracemalloc.stop(); "
        "print(json.dumps({'result':result,'peak':peak,"
        "'source':str(Path(subject.__file__).resolve())}))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(root), str(root / "src")))
    completed = subprocess.run(
        [sys.executable, "-c", script, str(path)],
        cwd=root,
        env=env,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert completed.returncode == 0, completed.stderr
    observed = json.loads(completed.stdout)
    assert observed["source"] == str(root / "tools/wct/accept/receipt.py")
    assert observed["result"] == list(expected)
    # Diagnostic separation: ~1 MiB bounded read vs 8 MiB unbounded read.
    # This generous margin is not a new product limit or a pin on read-ahead.
    assert observed["peak"] < 4 * 1024 * 1024, observed
