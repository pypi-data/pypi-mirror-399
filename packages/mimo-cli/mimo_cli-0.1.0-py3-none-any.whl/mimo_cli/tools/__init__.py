"""Tool registry for MiMo CLI."""

from .bash import BashTool
from .editor import EditorTool

# All available tools
TOOLS = [BashTool(), EditorTool()]

__all__ = ["TOOLS", "BashTool", "EditorTool"]
