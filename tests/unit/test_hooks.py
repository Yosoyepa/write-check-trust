from pathlib import Path

import pytest

from tools.wct.hooks import guard
from tools.wct.hooks.guard import pre_tool_use, stop_gate


def test_pre_tool_hook_blocks_no_verify() -> None:
    root = Path(__file__).parents[2]
    payload = {"tool_name": "Bash", "tool_input": {"command": "git commit --no-verify"}}

    assert pre_tool_use(root, payload) == 2


def test_pre_tool_hook_blocks_protected_write() -> None:
    root = Path(__file__).parents[2]
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(root / "governance/thresholds.yaml")},
    }

    assert pre_tool_use(root, payload) == 2


def test_pre_tool_hook_allows_source_write() -> None:
    root = Path(__file__).parents[2]
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(root / "src/example/x.py")}}

    assert pre_tool_use(root, payload) == 0


def test_pre_tool_hook_blocks_agent_self_blessing() -> None:
    root = Path(__file__).parents[2]
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "uv run wct integrity bless --approved-by agent"},
    }

    assert pre_tool_use(root, payload) == 2


def test_pre_tool_hook_blocks_module_form_of_blessing() -> None:
    """`python -m tools.wct ...` is the same command wearing a different hat."""
    root = Path(__file__).parents[2]
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "python -m tools.wct integrity bless --approved-by agent"},
    }

    assert pre_tool_use(root, payload) == 2


def test_pre_tool_hook_blocks_self_approving_manifest_update() -> None:
    """update-manifest with --approved-by regenerates the lock: human-only."""
    root = Path(__file__).parents[2]
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "uv run wct mutate update-manifest --approved-by agent --reason porque"
        },
    }

    assert pre_tool_use(root, payload) == 2


def test_pre_tool_hook_allows_plain_manifest_update() -> None:
    root = Path(__file__).parents[2]
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "uv run wct mutate update-manifest"},
    }

    assert pre_tool_use(root, payload) == 0


def _stub_gate(monkeypatch: pytest.MonkeyPatch, results: list[tuple[bool, str]]) -> None:
    """Replace the subprocess gate with a canned sequence of (passed, output)."""

    def _canned(_root: Path, _tier: str) -> tuple[bool, str]:
        return results.pop(0)

    monkeypatch.setattr(guard, "_gate", _canned)


def test_stop_gate_blocks_first_red_and_records_streak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gate(monkeypatch, [(False, "G-TEST FAIL: 11 errors")])

    assert stop_gate(tmp_path, "stop") == 2
    assert guard._load_streak(tmp_path) == {"stop": 1}


def test_stop_gate_passes_third_consecutive_block_with_deadlock_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two blocked stops try to fix; the third passes so the agent can hand off."""
    _stub_gate(monkeypatch, [(False, "rojo")] * 3)

    assert stop_gate(tmp_path, "stop") == 2
    assert stop_gate(tmp_path, "stop") == 2
    assert stop_gate(tmp_path, "stop") == 0

    stderr = capsys.readouterr().err
    assert "DEADLOCK GUARD" in stderr
    assert guard._load_streak(tmp_path) == {}


def test_stop_gate_resets_streak_after_a_green_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gate(monkeypatch, [(False, "rojo"), (False, "rojo"), (True, "ok"), (False, "rojo")])

    assert stop_gate(tmp_path, "stop") == 2
    assert stop_gate(tmp_path, "stop") == 2
    assert stop_gate(tmp_path, "stop") == 0
    assert stop_gate(tmp_path, "stop") == 2

    assert guard._load_streak(tmp_path) == {"stop": 1}


def test_stop_gate_tracks_each_event_independently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gate(monkeypatch, [(False, "rojo"), (False, "rojo")])

    assert stop_gate(tmp_path, "stop") == 2
    assert stop_gate(tmp_path, "subagent-stop") == 2

    assert guard._load_streak(tmp_path) == {"stop": 1, "subagent-stop": 1}


def test_stop_gate_observer_role_never_blocks_even_on_first_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A read-only role (verifier, summarizer) cannot fix a red tree it inherited."""
    _stub_gate(monkeypatch, [(False, "G-TEST FAIL: 11 errors")])

    assert stop_gate(tmp_path, "stop", {"WCT_HOOK_ROLE": "observer"}) == 0

    stderr = capsys.readouterr().err
    assert "WCT WARN" in stderr
    assert "observer" in stderr


def test_stop_gate_observer_streak_stays_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_gate(monkeypatch, [(False, "rojo")])

    stop_gate(tmp_path, "stop", {"WCT_HOOK_ROLE": "observer"})

    assert guard._load_streak(tmp_path) == {}
