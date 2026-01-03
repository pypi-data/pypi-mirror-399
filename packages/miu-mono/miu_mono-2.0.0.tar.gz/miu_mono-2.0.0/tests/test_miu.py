"""Tests for miu-mono glue package."""

from miu_mono import __version__


def test_version() -> None:
    """Test package version."""
    assert __version__ == "0.1.0"


def test_cli_module_importable() -> None:
    """Test CLI module can be imported."""
    from miu_mono.cli import cli, code, main, serve, tui

    assert cli is not None
    assert main is not None
    assert serve is not None
    assert code is not None
    assert tui is not None


def test_exports() -> None:
    """Test that main classes are exported."""
    from miu_mono import (
        Agent,
        AgentConfig,
        ReActAgent,
        Tool,
        ToolContext,
        ToolRegistry,
        ToolResult,
        create_provider,
    )

    # All imports should work
    assert Agent is not None
    assert AgentConfig is not None
    assert ReActAgent is not None
    assert Tool is not None
    assert ToolContext is not None
    assert ToolRegistry is not None
    assert ToolResult is not None
    assert create_provider is not None
