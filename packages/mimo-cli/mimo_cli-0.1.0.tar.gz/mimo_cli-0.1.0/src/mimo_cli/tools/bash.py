"""Bash command execution tool."""

import subprocess
from typing import Any

from ..types import ToolError, ToolResult


class BashTool:
    """Tool for executing bash commands."""

    name = "bash"
    description = "Execute bash commands in the environment"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command string to execute; can span multiple lines and is used exactly as provided.",
                }
            },
            "required": ["command"],
        }

    def execute(self, params: dict[str, Any], timeout: int = 30) -> ToolResult:
        """Execute a bash command.

        Args:
            params: Dictionary with 'command' key
            timeout: Command timeout in seconds

        Returns:
            ToolResult with command output
        """
        command = params.get("command", "").strip()
        if not command:
            raise ToolError("Bash tool requires 'command' parameter")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}" if output else result.stderr

            return ToolResult(
                output=output if output else "(no output)",
                success=result.returncode == 0,
            )

        except subprocess.TimeoutExpired:
            raise ToolError(f"Command timed out after {timeout}s")
        except Exception as e:
            raise ToolError(f"Failed to execute command: {e}")
