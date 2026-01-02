"""Coding tools."""

from miu_code.tools.bash import BashTool
from miu_code.tools.edit import EditTool
from miu_code.tools.glob import GlobTool
from miu_code.tools.grep import GrepTool
from miu_code.tools.read import ReadTool
from miu_code.tools.write import WriteTool
from miu_core.tools import Tool

__all__ = ["BashTool", "EditTool", "GlobTool", "GrepTool", "ReadTool", "WriteTool"]


def get_all_tools() -> list[Tool]:
    """Get all coding tools."""
    return [ReadTool(), WriteTool(), EditTool(), BashTool(), GlobTool(), GrepTool()]
