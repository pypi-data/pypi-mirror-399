"""CLI entry point."""

import asyncio
import os

import asyncclick as click
from rich.console import Console
from rich.markdown import Markdown

from miu_code.agent.coding import CodingAgent
from miu_code.commands import get_default_commands
from miu_core.commands import CommandExecutor

console = Console()


@click.group(invoke_without_command=True)
@click.option("--query", "-q", default=None, help="One-shot query")
@click.option(
    "--model",
    "-m",
    default="anthropic:claude-sonnet-4-20250514",
    help="Model to use (provider:model, e.g. openai:gpt-4o, google:gemini-2.0-flash)",
)
@click.option("--session", "-s", default=None, help="Session ID for persistence")
@click.option("--acp", is_flag=True, help="Run as ACP server for editor integration")
@click.pass_context
async def cli(
    ctx: click.Context, query: str | None, model: str, session: str | None, acp: bool
) -> None:
    """miu - AI coding agent.

    Run with --query for one-shot execution, or without for interactive REPL.
    Use 'miu code' to launch the TUI.

    Examples:
        miu -q "read pyproject.toml"
        miu code                     # Interactive TUI mode
        miu --model openai:gpt-4o -q "hello"
        miu -m google:gemini-2.0-flash -q "list files"
        miu --acp  # Run as ACP server for editor integration
    """
    # Store model and session in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["model"] = model
    ctx.obj["session"] = session

    # If a subcommand was invoked, let it handle things
    if ctx.invoked_subcommand is not None:
        return

    # ACP mode - run as server
    if acp:
        from miu_code.acp.server import run_acp_server

        await run_acp_server(model=model)
        return

    working_dir = os.getcwd()
    agent = CodingAgent(model=model, working_dir=working_dir, session_id=session)

    # Load commands for slash command support
    registry = get_default_commands()
    executor = CommandExecutor(registry)

    if query:
        # Expand slash commands in query
        expanded = executor.execute(query)
        actual_query = expanded if expanded else query

        response = await agent.run(actual_query)
        text = response.get_text()
        if text:
            console.print(Markdown(text))
    else:
        console.print("[bold blue]miu[/] - AI coding agent")
        console.print("Commands: /cook, /commit, /plan, /exit, /quit\n")

        while True:
            try:
                user_input = await click.prompt("miu", prompt_suffix="> ")
                stripped = user_input.strip()

                if stripped in ("/exit", "/quit"):
                    break
                if not stripped:
                    continue

                # Handle slash commands
                if stripped.startswith("/"):
                    try:
                        expanded = executor.execute(stripped)
                        if expanded:
                            user_input = expanded
                    except ValueError as e:
                        console.print(f"[red]{e}[/]")
                        continue

                response = await agent.run(user_input)
                text = response.get_text()
                if text:
                    console.print(Markdown(text))
                console.print()
            except (KeyboardInterrupt, EOFError):
                break

        console.print("\nGoodbye!")


@cli.command()
@click.pass_context
async def code(ctx: click.Context) -> None:
    """Launch interactive TUI mode."""
    from miu_code.tui.app import MiuCodeApp

    model = ctx.obj.get("model", "anthropic:claude-sonnet-4-20250514")
    session = ctx.obj.get("session")

    app = MiuCodeApp(model=model, session_id=session)
    await app.run_async()


def main() -> None:
    """Main entry point."""
    asyncio.run(cli())
