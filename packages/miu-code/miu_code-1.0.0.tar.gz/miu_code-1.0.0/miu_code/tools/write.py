"""Write file tool."""

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult

from .security import PathTraversalError, validate_path


class WriteInput(BaseModel):
    """Input for write tool."""

    file_path: str = Field(description="Absolute path to the file to write")
    content: str = Field(description="Content to write to the file")


class WriteTool(Tool):
    """Write content to a file."""

    name = "Write"
    description = "Write content to a file. Creates parent directories if needed."

    def get_input_schema(self) -> type[BaseModel]:
        return WriteInput

    async def execute(  # type: ignore[override]
        self,
        ctx: ToolContext,
        file_path: str,
        content: str,
        **kwargs: object,
    ) -> ToolResult:
        """Write content to file."""
        try:
            path = validate_path(file_path, ctx.working_dir)
        except PathTraversalError as e:
            return ToolResult(
                output=f"Access denied: {file_path}",
                success=False,
                error=str(e),
            )

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return ToolResult(output=f"Successfully wrote to {file_path}")
        except PermissionError:
            return ToolResult(
                output=f"Permission denied: {file_path}",
                success=False,
                error="Permission denied",
            )
        except OSError as e:
            return ToolResult(
                output=f"Failed to write: {e}",
                success=False,
                error=str(e),
            )
