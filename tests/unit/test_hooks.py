from pathlib import Path

from tools.wct.hooks.guard import pre_tool_use


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
