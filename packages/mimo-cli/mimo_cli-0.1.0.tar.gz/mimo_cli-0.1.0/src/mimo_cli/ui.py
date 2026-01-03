"""Terminal UI for MiMo CLI."""

import json

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.text import Text

from .types import ToolCall, ToolResult


class UI:
    """Rich terminal output with streaming support."""

    def __init__(self):
        self.console = Console()
        self._live: Live | None = None
        self._streamed_content = ""
        self._thinking_content = ""
        self._spinner_active = False
        self._spinner_message = ""

    def welcome(self) -> None:
        """Show welcome message."""
        self.console.print()
        self.console.print("[bold orange_red1]MiMo CLI[/bold orange_red1] - Your terminal assistant")
        self.console.print("[dim]Type 'exit' or 'quit' to leave[/dim]")
        self.console.print()

    def prompt_user(self) -> str:
        """Get user input with proper Unicode/Chinese support."""
        try:
            return prompt(HTML('<ansigreen><b>&gt;&gt;&gt; </b></ansigreen>'))
        except (EOFError, KeyboardInterrupt):
            return "exit"

    def start_spinner(self, message: str = "Vibing") -> None:
        """Mark spinner as active."""
        self._spinner_active = True
        self._spinner_message = message

    def stop_spinner(self) -> None:
        """Mark spinner as inactive."""
        self._spinner_active = False

    def start_stream(self) -> None:
        """Start streaming output."""
        self._streamed_content = ""
        self._thinking_content = ""
        self._live = Live(
            self._build_display(),
            console=self.console,
            refresh_per_second=12,
            vertical_overflow="visible",
        )
        self._live.start()

    def _build_display(self) -> Group:
        """Build the display content."""
        parts = []

        # Show thinking content first (if any)
        if self._thinking_content:
            thinking_text = Text(self._thinking_content, style="dim italic")
            parts.append(Panel(thinking_text, title="[dim]Thinking[/dim]", border_style="dim"))

        # Show main content (if any)
        if self._streamed_content:
            parts.append(Markdown(self._streamed_content))

        # Show spinner if active and no content yet
        if self._spinner_active and not self._streamed_content and not self._thinking_content:
            spinner = Spinner("dots", text=self._spinner_message, style="cyan")
            parts.append(spinner)

        return Group(*parts) if parts else Group()

    def stream_token(self, token: str) -> None:
        """Stream a single token."""
        self._streamed_content += token
        if self._live:
            self._live.update(self._build_display())

    def stream_thinking(self, token: str) -> None:
        """Stream thinking/reasoning content."""
        self._thinking_content += token
        if self._live:
            self._live.update(self._build_display())

    def end_stream(self) -> str:
        """End streaming output. Returns thinking content for API response."""
        if self._live:
            self._live.stop()
            self._live = None

        # Print final rendered content
        if self._streamed_content:
            self.console.print()

        thinking = self._thinking_content
        self._thinking_content = ""
        return thinking

    def show_assistant_message(self, content: str) -> None:
        """Show a complete assistant message."""
        self.console.print()
        self.console.print(Markdown(content))
        self.console.print()

    def show_tool_call(self, tool_call: ToolCall) -> None:
        """Show a tool call about to be executed."""
        args_str = json.dumps(tool_call.arguments, indent=2, ensure_ascii=False)

        if tool_call.name == "bash":
            # Show bash command nicely
            cmd = tool_call.arguments.get("command", "")
            syntax = Syntax(cmd, "bash", theme="monokai", line_numbers=False)
            self.console.print(Panel(
                syntax,
                title=f"[bold cyan]Tool: {tool_call.name}[/bold cyan]",
                border_style="cyan",
            ))
        else:
            # Generic tool display
            self.console.print(Panel(
                Syntax(args_str, "json", theme="monokai"),
                title=f"[bold cyan]Tool: {tool_call.name}[/bold cyan]",
                border_style="cyan",
            ))

    def show_result(self, result: ToolResult) -> None:
        """Show tool execution result."""
        style = "green" if result.success else "red"
        title = "Result" if result.success else "Error"

        # Truncate long output
        output = result.output
        if len(output) > 2000:
            output = output[:2000] + "\n... (truncated)"

        self.console.print(Panel(
            output,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
        ))

    def show_error(self, error: str) -> None:
        """Show an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {error}")

    def show_info(self, info: str) -> None:
        """Show an info message."""
        self.console.print(f"[dim]{info}[/dim]")
