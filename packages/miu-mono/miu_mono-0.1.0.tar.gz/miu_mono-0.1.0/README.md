# miu

AI Agent Framework - batteries included.

## Installation

```bash
# Basic installation
uv add miu

# With web UI
uv add "miu[studio]"

# With examples
uv add "miu[examples]"

# Everything
uv add "miu[all]"
```

## CLI Commands

```bash
# Default: Run interactive CLI
miu

# Start web server
miu serve --port 8000

# Run TUI interface
miu tui

# Show version
miu --version
```

## Python Usage

```python
import asyncio
from miu import ReActAgent, create_provider, AgentConfig

async def main():
    provider = create_provider("anthropic:claude-sonnet-4-20250514")
    agent = ReActAgent(
        provider=provider,
        config=AgentConfig(name="assistant"),
    )
    response = await agent.run("What is the capital of France?")
    print(response.get_text())

asyncio.run(main())
```

## Packages

- **miu-core**: Core framework (agents, providers, tools, memory)
- **miu-code**: CLI and TUI interfaces
- **miu-studio**: Web server and chat UI
- **miu-examples**: Example applications

## License

MIT
