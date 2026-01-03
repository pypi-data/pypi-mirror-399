"""Permission system for MiMo CLI."""

import os
import sys
from pathlib import Path
from typing import Union

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from .types import PermissionDenied


def _read_key() -> str:
    """Read a single keypress, handling arrow keys."""
    if sys.platform == "win32":
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':  # Arrow key prefix on Windows
            key = msvcrt.getch()
            if key == b'K':
                return 'left'
            elif key == b'M':
                return 'right'
        elif key == b'\r':
            return 'enter'
        return key.decode('utf-8', errors='ignore').lower()
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'D':
                        return 'left'
                    elif ch3 == 'C':
                        return 'right'
                return 'esc'
            elif ch == '\r' or ch == '\n':
                return 'enter'
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class Permissions:
    """Permission gate - every action must be approved."""

    # Options: 0 = Yes, 1 = No, 2 = No with feedback
    OPTIONS = ["Yes", "No", "No + Feedback"]

    def __init__(self, console: Console | None = None, auto_accept_editor: bool = False):
        self.console = console or Console()
        self.auto_accept_editor = auto_accept_editor
        self.cwd = Path(os.getcwd()).resolve()

    def _render_options(self, selected: int) -> Text:
        """Render the options with the selected one highlighted."""
        text = Text()
        text.append("  ← → ", style="dim")

        for i, option in enumerate(self.OPTIONS):
            if i > 0:
                text.append("  ", style="dim")

            if i == selected:
                if i == 0:  # Yes
                    text.append(f"[{option}]", style="bold green reverse")
                elif i == 1:  # No
                    text.append(f"[{option}]", style="bold red reverse")
                else:  # No + Feedback
                    text.append(f"[{option}]", style="bold yellow reverse")
            else:
                if i == 0:
                    text.append(f" {option} ", style="green dim")
                elif i == 1:
                    text.append(f" {option} ", style="red dim")
                else:
                    text.append(f" {option} ", style="yellow dim")

        text.append("  (Enter to confirm)", style="dim")
        return text

    def request(self, action: str, details: Union[str, RenderableType]) -> bool:
        """Ask user for permission to perform an action.

        Args:
            action: Short description of the action (e.g., "bash", "editor:create")
            details: Detailed info about what will be done (can be string or Rich renderable)

        Returns:
            True if approved, raises PermissionDenied if denied
        """
        # Display the action
        self.console.print()
        self.console.print(Panel(
            details,
            title=f"[bold yellow]Permission Required: {action}[/bold yellow]",
            border_style="yellow",
        ))

        selected = 0  # Start with "Yes" selected

        # Use Live display for interactive selection
        with Live(self._render_options(selected), console=self.console, refresh_per_second=30, transient=True) as live:
            while True:
                key = _read_key()

                if key == 'left':
                    selected = (selected - 1) % len(self.OPTIONS)
                    live.update(self._render_options(selected))
                elif key == 'right':
                    selected = (selected + 1) % len(self.OPTIONS)
                    live.update(self._render_options(selected))
                elif key == 'enter':
                    break
                elif key == 'y':
                    selected = 0
                    break
                elif key == 'n':
                    selected = 1
                    break
                elif key == 'f':
                    selected = 2
                    break

        # Show final selection
        self.console.print(self._render_options(selected))

        if selected == 0:  # Yes
            return True
        elif selected == 2:  # No + Feedback
            feedback = self.console.input("[bold yellow]Feedback: [/bold yellow]").strip()
            raise PermissionDenied(f"User denied with feedback: {feedback}")
        else:  # No
            raise PermissionDenied(f"User denied permission for: {action}")

    def request_bash(self, command: str) -> bool:
        """Request permission for bash command."""
        details = Syntax(command, "bash", theme="monokai", line_numbers=False)
        return self.request("bash", details)

    def _is_path_in_cwd(self, path: str) -> bool:
        """Check if a path is within the current working directory."""
        try:
            target = Path(path).resolve()
            return target == self.cwd or self.cwd in target.parents
        except (OSError, ValueError):
            return False

    def request_editor(self, command: str, path: str, extra: str = "") -> bool:
        """Request permission for editor operation."""
        # Auto-accept if enabled and path is within cwd
        if self.auto_accept_editor and self._is_path_in_cwd(path):
            self.console.print(f"[dim]Auto-accepted editor:{command} for {path}[/dim]")
            return True

        details = f"Command: {command}\nPath: {path}"
        if extra:
            details += f"\n{extra}"
        return self.request(f"editor:{command}", details)
