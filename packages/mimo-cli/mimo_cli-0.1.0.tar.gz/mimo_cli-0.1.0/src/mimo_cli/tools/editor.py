"""File editor tool for viewing, creating, and editing files."""

import os
from pathlib import Path
from typing import Any

from ..types import ToolError, ToolResult


class EditorTool:
    """Tool for file operations: view, create, and str_replace."""

    name = "editor"
    description = "View, create, and edit files"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "enum": ["view", "create", "str_replace"],
                    "description": "The editor command to execute.",
                },
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file or directory to operate on.",
                },
                "file_text": {
                    "type": "string",
                    "description": "Complete file contents when using the create command.",
                },
                "old_str": {
                    "type": "string",
                    "description": "Exact string to replace for the str_replace command.",
                },
                "new_str": {
                    "type": "string",
                    "description": "Replacement string for str_replace command.",
                },
                "view_range": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Line range to display as [start_line, end_line]; use -1 as end to show to EOF.",
                },
            },
            "required": ["command", "path"],
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        """Execute editor command."""
        command = params.get("command")
        if not command:
            raise ToolError("Missing required parameter: command")

        path = params.get("path")
        if not path:
            raise ToolError("Missing required parameter: path")

        if not path.startswith("/"):
            raise ToolError(f"Path must be absolute (start with /), got: {path}")

        handlers = {
            "view": self._handle_view,
            "create": self._handle_create,
            "str_replace": self._handle_str_replace,
        }

        if command not in handlers:
            raise ToolError(f"Unknown command: {command}. Valid commands: {list(handlers.keys())}")

        return handlers[command](path, params)

    def _handle_view(self, path: str, params: dict[str, Any]) -> ToolResult:
        """View file contents or list directory."""
        if os.path.isdir(path):
            # List directory contents
            try:
                entries = []
                for root, dirs, files in os.walk(path):
                    depth = root.replace(path, "").count(os.sep)
                    if depth > 2:
                        continue
                    indent = "  " * depth
                    entries.append(f"{indent}{os.path.basename(root)}/")
                    subindent = "  " * (depth + 1)
                    for file in files:
                        if not file.startswith("."):
                            entries.append(f"{subindent}{file}")
                    # Filter hidden dirs
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                return ToolResult(output="\n".join(entries))
            except Exception as e:
                return ToolResult(output=f"Error listing directory: {e}", success=False)

        if not os.path.exists(path):
            return ToolResult(output=f"Error: Path does not exist: {path}", success=False)

        try:
            with open(path, "r") as f:
                lines = f.readlines()

            view_range = params.get("view_range")
            if view_range:
                start = max(1, view_range[0])
                end = view_range[1]
                if end == -1:
                    end = len(lines)
                lines = lines[start - 1 : end]
                start_num = start
            else:
                start_num = 1
                # Limit to 500 lines
                if len(lines) > 500:
                    lines = lines[:500]
                    truncated = True
                else:
                    truncated = False

            # Format with line numbers
            output_lines = []
            for i, line in enumerate(lines, start=start_num):
                output_lines.append(f"{i:6}\t{line}")

            output = "\n".join(output_lines)
            if view_range is None and truncated:
                output += "\n<response clipped>"

            return ToolResult(output=output)

        except Exception as e:
            return ToolResult(output=f"Error reading file: {e}", success=False)

    def _handle_create(self, path: str, params: dict[str, Any]) -> ToolResult:
        """Create a new file."""
        if os.path.exists(path):
            return ToolResult(output=f"Error: File already exists: {path}", success=False)

        file_text = params.get("file_text", "")

        try:
            # Create parent directories if needed
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                f.write(file_text)

            lines = file_text.count("\n") + (1 if file_text and not file_text.endswith("\n") else 0)
            return ToolResult(output=f"File created successfully: {path} ({lines} lines)")

        except Exception as e:
            return ToolResult(output=f"Error creating file: {e}", success=False)

    def _handle_str_replace(self, path: str, params: dict[str, Any]) -> ToolResult:
        """Replace exact string in file."""
        if not os.path.exists(path):
            return ToolResult(output=f"Error: File not found: {path}", success=False)

        old_str = params.get("old_str")
        if old_str is None:
            raise ToolError("Missing required parameter for str_replace: old_str")

        new_str = params.get("new_str", "")

        try:
            with open(path, "r") as f:
                content = f.read()

            # Count occurrences
            count = content.count(old_str)

            if count == 0:
                return ToolResult(
                    output="Error: The exact string was not found in the file. Make sure the old_str matches exactly including whitespace and newlines.",
                    success=False,
                )

            if count > 1:
                return ToolResult(
                    output=f"Error: String found {count} times, must be unique. Please include more context to make the string unique.",
                    success=False,
                )

            # Perform replacement
            new_content = content.replace(old_str, new_str, 1)

            with open(path, "w") as f:
                f.write(new_content)

            return ToolResult(output="String replaced successfully.")

        except Exception as e:
            return ToolResult(output=f"Error during replacement: {e}", success=False)
