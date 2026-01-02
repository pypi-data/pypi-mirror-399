"""miu-mono - AI Agent Framework.

A batteries-included framework for building AI agents with:
- Multi-provider LLM support (Anthropic, OpenAI, Google)
- Tool creation and registration
- Memory management
- MCP integration
- Web UI (miu-studio)
- CLI and TUI interfaces (miu-code)
"""

__version__ = "0.1.0"

# Re-export core functionality
from miu_core.agents import Agent, AgentConfig, ReActAgent
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult

__all__ = [
    "Agent",
    "AgentConfig",
    "ReActAgent",
    "Tool",
    "ToolContext",
    "ToolRegistry",
    "ToolResult",
    "__version__",
    "create_provider",
]
