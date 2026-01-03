"""Grep search tool."""

import re

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult

from .security import PathTraversalError, validate_path


class GrepInput(BaseModel):
    """Input for grep tool."""

    pattern: str = Field(description="Regex pattern to search for")
    path: str | None = Field(None, description="File or directory to search in")
    glob: str | None = Field(None, description="File pattern filter (e.g., '*.py')")


class GrepTool(Tool):
    """Search file contents with regex."""

    name = "Grep"
    description = "Search for pattern in files. Use for finding code, strings, etc."

    def get_input_schema(self) -> type[BaseModel]:
        return GrepInput

    async def execute(  # type: ignore[override]
        self,
        ctx: ToolContext,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        **kwargs: object,
    ) -> ToolResult:
        """Search for pattern in files."""
        try:
            base = validate_path(path or ".", ctx.working_dir)
        except PathTraversalError as e:
            return ToolResult(
                output=f"Access denied: {path}",
                success=False,
                error=str(e),
            )

        if not base.exists():
            return ToolResult(
                output=f"Path not found: {base}",
                success=False,
                error="Path does not exist",
            )

        try:
            regex = re.compile(pattern)
        except re.error as e:
            return ToolResult(
                output=f"Invalid regex: {e}",
                success=False,
                error=str(e),
            )

        results: list[str] = []
        max_results = 100

        if base.is_file():
            files = [base]
        else:
            file_pattern = glob or "**/*"
            files = [f for f in base.glob(file_pattern) if f.is_file()]

        for file_path in files:
            if len(results) >= max_results:
                break

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            for line_num, line in enumerate(content.splitlines(), 1):
                if regex.search(line):
                    results.append(f"{file_path}:{line_num}: {line.strip()}")
                    if len(results) >= max_results:
                        break

        if not results:
            return ToolResult(output=f"No matches for pattern: {pattern}")

        output = "\n".join(results)
        if len(results) >= max_results:
            output += f"\n... (limited to {max_results} results)"

        return ToolResult(output=output)
