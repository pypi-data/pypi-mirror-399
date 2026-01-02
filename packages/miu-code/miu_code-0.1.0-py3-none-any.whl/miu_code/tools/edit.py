"""Edit file tool."""

from pydantic import BaseModel, Field

from miu_core.tools import Tool, ToolContext, ToolResult

from .security import PathTraversalError, validate_path


class EditInput(BaseModel):
    """Input for edit tool."""

    file_path: str = Field(description="Absolute path to the file to edit")
    old_string: str = Field(description="Exact string to find and replace")
    new_string: str = Field(description="String to replace old_string with")
    replace_all: bool = Field(False, description="Replace all occurrences if True")


class EditTool(Tool):
    """Edit file by string replacement."""

    name = "Edit"
    description = "Edit a file by replacing old_string with new_string. Use for modifying files."

    def get_input_schema(self) -> type[BaseModel]:
        return EditInput

    async def execute(  # type: ignore[override]
        self,
        ctx: ToolContext,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
        **kwargs: object,
    ) -> ToolResult:
        """Replace string in file."""
        try:
            path = validate_path(file_path, ctx.working_dir)
        except PathTraversalError as e:
            return ToolResult(
                output=f"Access denied: {file_path}",
                success=False,
                error=str(e),
            )

        if not path.exists():
            return ToolResult(
                output=f"File not found: {file_path}",
                success=False,
                error=f"File does not exist: {file_path}",
            )

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(
                output=f"Cannot edit binary file: {file_path}",
                success=False,
                error="Binary file",
            )

        if old_string not in content:
            return ToolResult(
                output=f"String not found in {file_path}",
                success=False,
                error="old_string not found in file",
            )

        count = content.count(old_string)
        if count > 1 and not replace_all:
            return ToolResult(
                output=f"Found {count} occurrences. Set replace_all=True to replace all.",
                success=False,
                error=f"Multiple occurrences ({count}) found",
            )

        if replace_all:
            new_content = content.replace(old_string, new_string)
            replaced = count
        else:
            new_content = content.replace(old_string, new_string, 1)
            replaced = 1

        try:
            path.write_text(new_content, encoding="utf-8")
            return ToolResult(output=f"Replaced {replaced} occurrence(s) in {file_path}")
        except PermissionError:
            return ToolResult(
                output=f"Permission denied: {file_path}",
                success=False,
                error="Permission denied",
            )
