"""Tests for coding tools."""

import tempfile
from pathlib import Path

import pytest

from miu_code.tools import BashTool, EditTool, GlobTool, GrepTool, ReadTool, WriteTool
from miu_core.tools import ToolContext


@pytest.fixture
def temp_dir() -> Path:
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def ctx(temp_dir: Path) -> ToolContext:
    return ToolContext(working_dir=str(temp_dir))


class TestReadTool:
    @pytest.mark.asyncio
    async def test_read_file(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "test.txt"
        test_file.write_text("line1\nline2\nline3")

        tool = ReadTool()
        result = await tool.execute(ctx, file_path=str(test_file))

        assert result.success
        assert "line1" in result.output
        assert "line2" in result.output

    @pytest.mark.asyncio
    async def test_read_nonexistent(self, temp_dir: Path, ctx: ToolContext) -> None:
        tool = ReadTool()
        # Use a path within the working directory that doesn't exist
        nonexistent = temp_dir / "nonexistent" / "file.txt"
        result = await tool.execute(ctx, file_path=str(nonexistent))

        assert not result.success
        assert "not found" in result.output.lower()

    @pytest.mark.asyncio
    async def test_read_path_traversal_blocked(self, ctx: ToolContext) -> None:
        """Test that path traversal attacks are blocked."""
        tool = ReadTool()
        result = await tool.execute(ctx, file_path="/etc/passwd")

        assert not result.success
        assert "access denied" in result.output.lower()

    @pytest.mark.asyncio
    async def test_read_with_offset_limit(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        tool = ReadTool()
        result = await tool.execute(ctx, file_path=str(test_file), offset=2, limit=2)

        assert result.success
        assert "line2" in result.output
        assert "line3" in result.output
        assert "line1" not in result.output
        assert "line4" not in result.output


class TestWriteTool:
    @pytest.mark.asyncio
    async def test_write_file(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "new.txt"

        tool = WriteTool()
        result = await tool.execute(ctx, file_path=str(test_file), content="hello world")

        assert result.success
        assert test_file.read_text() == "hello world"

    @pytest.mark.asyncio
    async def test_write_creates_dirs(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "subdir" / "new.txt"

        tool = WriteTool()
        result = await tool.execute(ctx, file_path=str(test_file), content="nested")

        assert result.success
        assert test_file.read_text() == "nested"


class TestEditTool:
    @pytest.mark.asyncio
    async def test_edit_file(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello world")

        tool = EditTool()
        result = await tool.execute(
            ctx,
            file_path=str(test_file),
            old_string="world",
            new_string="miu",
        )

        assert result.success
        assert test_file.read_text() == "hello miu"

    @pytest.mark.asyncio
    async def test_edit_multiple_requires_flag(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "test.txt"
        test_file.write_text("foo foo foo")

        tool = EditTool()
        result = await tool.execute(
            ctx,
            file_path=str(test_file),
            old_string="foo",
            new_string="bar",
        )

        assert not result.success
        assert "3" in result.output or "multiple" in result.output.lower()

    @pytest.mark.asyncio
    async def test_edit_replace_all(self, temp_dir: Path, ctx: ToolContext) -> None:
        test_file = temp_dir / "test.txt"
        test_file.write_text("foo foo foo")

        tool = EditTool()
        result = await tool.execute(
            ctx,
            file_path=str(test_file),
            old_string="foo",
            new_string="bar",
            replace_all=True,
        )

        assert result.success
        assert test_file.read_text() == "bar bar bar"


class TestGlobTool:
    @pytest.mark.asyncio
    async def test_glob_files(self, temp_dir: Path, ctx: ToolContext) -> None:
        (temp_dir / "file1.py").write_text("# py")
        (temp_dir / "file2.py").write_text("# py")
        (temp_dir / "file3.txt").write_text("txt")

        tool = GlobTool()
        result = await tool.execute(ctx, pattern="*.py")

        assert result.success
        assert "file1.py" in result.output
        assert "file2.py" in result.output
        assert "file3.txt" not in result.output


class TestGrepTool:
    @pytest.mark.asyncio
    async def test_grep_pattern(self, temp_dir: Path, ctx: ToolContext) -> None:
        (temp_dir / "test.py").write_text("def hello():\n    pass\n")

        tool = GrepTool()
        result = await tool.execute(ctx, pattern="def \\w+")

        assert result.success
        assert "def hello" in result.output

    @pytest.mark.asyncio
    async def test_grep_no_match(self, temp_dir: Path, ctx: ToolContext) -> None:
        (temp_dir / "test.py").write_text("hello world")

        tool = GrepTool()
        result = await tool.execute(ctx, pattern="notfound")

        assert result.success
        assert "no match" in result.output.lower()


class TestBashTool:
    @pytest.mark.asyncio
    async def test_simple_command(self, ctx: ToolContext) -> None:
        tool = BashTool()
        result = await tool.execute(ctx, command="echo hello")

        assert result.success
        assert "hello" in result.output

    @pytest.mark.asyncio
    async def test_failing_command(self, ctx: ToolContext) -> None:
        tool = BashTool()
        result = await tool.execute(ctx, command="exit 1")

        assert not result.success
        assert "exit code" in result.output.lower()
