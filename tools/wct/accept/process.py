"""Bounded acceptance subprocess transport with persisted partial output."""

from contextlib import suppress
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
from typing import Any, BinaryIO, cast

OUTPUT_LIMIT = 1024 * 1024


def _terminate(process: subprocess.Popen[bytes]) -> None:
    with suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGKILL)
    process.wait(timeout=1)


def _read(selector: selectors.BaseSelector, buffers: dict[str, bytearray], remaining: int) -> str:
    for key, _events in selector.select(timeout=0.05):
        chunk = os.read(key.fd, min(65536, remaining + 1))
        if not chunk:
            selector.unregister(key.fileobj)
            continue
        buffers[key.data].extend(chunk[:remaining])
        remaining -= len(chunk)
        if remaining < 0:
            return "output limit exceeded"
    return ""


def _observe(
    process: subprocess.Popen[bytes], buffers: dict[str, bytearray], deadline: float
) -> str:
    with selectors.DefaultSelector() as selector:
        selector.register(cast("BinaryIO", process.stdout), selectors.EVENT_READ, "stdout")
        selector.register(cast("BinaryIO", process.stderr), selectors.EVENT_READ, "stderr")
        while selector.get_map() or process.poll() is None:
            if time.monotonic() >= deadline:
                return "timeout"
            remaining = OUTPUT_LIMIT - sum(len(value) for value in buffers.values())
            reason = _read(selector, buffers, remaining)
            if reason:
                return reason
    return ""


def _execute(
    command: list[str], env: dict[str, str], buffers: dict[str, bytearray], seconds: float
) -> tuple[int | None, str]:
    if seconds <= 0:
        return None, "campaign timeout"
    process = subprocess.Popen(
        command,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        reason = _observe(process, buffers, time.monotonic() + seconds)
        if reason:
            _terminate(process)
        return process.wait(timeout=1), reason
    finally:
        if process.poll() is None:
            _terminate(process)
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def run_process(
    command: list[str], env: dict[str, str], directory: Path, seconds: float
) -> dict[str, Any]:
    """Run without shell; persist bounded logs and the real exit or launch error."""
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    started = time.monotonic()
    try:
        code, reason = _execute(command, env, buffers, seconds)
    except (OSError, ValueError, IndexError, subprocess.SubprocessError) as error:
        code, reason = None, f"process error: {error}"
    for name, payload in buffers.items():
        (directory / f"{name}.log").write_bytes(payload)
    return {"exit": code, "reason": reason, "duration": time.monotonic() - started}
