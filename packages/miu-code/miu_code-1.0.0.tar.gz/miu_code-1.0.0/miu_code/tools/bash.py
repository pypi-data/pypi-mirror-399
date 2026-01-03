"""Bash command tool."""

import asyncio
import os
from pathlib import Path

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult


class BashInput(BaseModel):
    """Input for bash tool."""

    command: str = Field(description="Shell command to execute")
    timeout: int = Field(60, description="Timeout in seconds")


class BashTool(Tool):
    """Execute shell commands."""

    name = "Bash"
    description = "Execute shell commands. Use for running scripts, builds, tests, etc."

    def get_input_schema(self) -> type[BaseModel]:
        return BashInput

    async def execute(  # type: ignore[override]
        self,
        ctx: ToolContext,
        command: str,
        timeout: int = 60,
        **kwargs: object,
    ) -> ToolResult:
        """Execute shell command."""
        working_dir = Path(ctx.working_dir)
        if not working_dir.exists():
            working_dir = Path.cwd()

        env = os.environ.copy()

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(working_dir),
                env=env,
            )

            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except TimeoutError:
                process.kill()
                return ToolResult(
                    output=f"Command timed out after {timeout}s",
                    success=False,
                    error="Timeout",
                )

            output = stdout.decode("utf-8", errors="replace")
            exit_code = process.returncode

            if exit_code == 0:
                return ToolResult(output=output or "(no output)")
            else:
                return ToolResult(
                    output=f"Exit code: {exit_code}\n{output}",
                    success=False,
                    error=f"Exit code: {exit_code}",
                )

        except OSError as e:
            return ToolResult(
                output=f"Failed to execute: {e}",
                success=False,
                error=str(e),
            )
