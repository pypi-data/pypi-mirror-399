"""miu CLI - unified command dispatcher.

Provides access to all miu subcommands:
- miu (default): Run miu-code CLI
- miu serve: Run miu-studio web server
- miu code: Run miu-code CLI
- miu tui: Run miu-code TUI
"""

import sys

import asyncclick as click


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
async def cli(ctx: click.Context, version: bool) -> None:
    """miu - AI Agent Framework.

    Run without arguments to start the interactive CLI.
    """
    if version:
        from miu_mono import __version__

        click.echo(f"miu version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        # Default: run miu-code CLI
        await _run_code_cli()


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
async def serve(host: str, port: int, reload: bool) -> None:
    """Run miu-studio web server."""
    try:
        import uvicorn

        from miu_studio.main import create_app
    except ImportError:
        click.echo("Error: miu-studio not installed.", err=True)
        click.echo("Install with: uv add miu-mono[studio]", err=True)
        sys.exit(1)

    click.echo(f"Starting miu-studio at http://{host}:{port}")
    config = uvicorn.Config(
        app=create_app(),
        host=host,
        port=port,
        reload=reload,
    )
    server = uvicorn.Server(config)
    await server.serve()


@cli.command()
async def code() -> None:
    """Run miu-code CLI."""
    await _run_code_cli()


@cli.command()
def tui() -> None:
    """Run miu-code TUI (Terminal User Interface)."""
    try:
        from miu_code.tui.app import run

        run()
    except ImportError:
        click.echo("Error: miu-code TUI not available.", err=True)
        sys.exit(1)


async def _run_code_cli() -> None:
    """Run the miu-code CLI."""
    try:
        from miu_code.cli.entry import cli as code_cli

        await code_cli()
    except ImportError as e:
        click.echo(f"Error: miu-code not installed. {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the miu CLI."""
    cli()


if __name__ == "__main__":
    main()
