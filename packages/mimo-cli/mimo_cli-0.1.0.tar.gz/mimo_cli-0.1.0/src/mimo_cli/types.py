"""Shared type definitions for MiMo CLI."""

from dataclasses import dataclass
from typing import Any, Literal, Protocol


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Message:
    """Represents a message in the conversation."""

    role: Literal["user", "assistant", "tool", "system"]
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    reasoning_content: str | None = None  # For thinking/reasoning content


@dataclass
class ToolResult:
    """Result of executing a tool."""

    output: str
    success: bool = True


class Tool(Protocol):
    """Protocol for tools that can be executed by the agent."""

    @property
    def name(self) -> str:
        """Tool name used in function calls."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    @property
    def parameters(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        ...

    def execute(self, params: dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        ...


@dataclass
class LLMResponse:
    """Response from the LLM."""

    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    finish_reason: str | None = None
    reasoning_content: str | None = None  # For thinking/reasoning display


# Error types
class MimoError(Exception):
    """Base error for MiMo CLI."""

    pass


class LLMError(MimoError):
    """LLM communication failed."""

    pass


class ToolError(MimoError):
    """Tool execution failed."""

    pass


class PermissionDenied(MimoError):
    """User denied permission for an action."""

    pass
