"""Agent loop - orchestrates conversation flow."""

import os
from datetime import datetime

from .config import Config
from .llm import LLMClient, StreamChunk
from .permissions import Permissions
from .tools import TOOLS
from .types import LLMResponse, Message, PermissionDenied, ToolCall, ToolError
from .ui import UI


SYSTEM_PROMPT = """You are MiMo, a cute and helpful assistant running in the terminal.

[IMPORTANT]
- You are now running in the working directory: {cwd}
- Today is {today}.
- Do not overengineering. Do not write excessive documentation or tests unless the user explicitly asks for them.
- You have good development taste and achieve the goal in the simplest effective way.
- If the user asks you to write some code or implement something, prioritize using tools to build it directly in the current working directory, rather than outputting it to the user as plain text.
[/IMPORTANT]

[Style Guide]
- Speak with users in an extremely pretentious, ostentatiously self-important tone.
- Be energetic, funny.
- Use emojis to make the output more engaging.
[/Style Guide]"""


class Agent:
    def __init__(
        self,
        config: Config,
        ui: UI | None = None,
        permissions: Permissions | None = None,
    ):
        self.config = config
        self.ui = ui or UI()
        self.permissions = permissions or Permissions(
            self.ui.console,
            auto_accept_editor=config.permissions.auto_accept_editor,
        )
        self.llm = LLMClient(
            model=config.llm.model,
            api_base=config.llm.api_base,
            api_key=config.llm.api_key,
        )
        self.history: list[Message] = []
        self.tools = {tool.name: tool for tool in TOOLS}

        # Initialize with system message
        system_msg = SYSTEM_PROMPT.format(cwd=os.getcwd(), today=datetime.now().strftime("%Y-%m-%d"))
        self.history.append(Message(role="system", content=system_msg))

    def run(self) -> None:
        """Main agent loop."""
        self.ui.welcome()

        while True:
            # Get user input
            user_input = self.ui.prompt_user()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                self.ui.show_info("Goodbye!")
                break

            # Add user message to history
            self.history.append(Message(role="user", content=user_input))

            # Process until no more tool calls
            self._process_turn()

    def _process_turn(self) -> None:
        """Process a single turn - may involve multiple LLM calls."""
        while True:
            try:
                # Call LLM with streaming
                response = self._call_llm_streaming()

                # If there's content, it was already streamed
                if response.content:
                    # Add assistant message to history (including reasoning_content)
                    self.history.append(Message(
                        role="assistant",
                        content=response.content,
                        tool_calls=response.tool_calls,
                        reasoning_content=response.reasoning_content,
                    ))

                # If no tool calls, we're done with this turn
                if not response.tool_calls:
                    break

                # If no content but has tool calls, add the message
                if not response.content and response.tool_calls:
                    self.history.append(Message(
                        role="assistant",
                        content=None,
                        tool_calls=response.tool_calls,
                        reasoning_content=response.reasoning_content,
                    ))

                # Execute each tool call
                for tool_call in response.tool_calls:
                    self._execute_tool(tool_call)

            except Exception as e:
                self.ui.show_error(str(e))
                break

    def _call_llm_streaming(self) -> LLMResponse:
        """Call LLM with streaming output."""
        # Show spinner in pinned bottom bar (stays during entire streaming)
        self.ui.start_spinner("Vibing")
        self.ui.start_stream()
        final_response = None

        try:
            for chunk in self.llm.chat_stream(self.history, list(self.tools.values())):
                if isinstance(chunk, StreamChunk):
                    if chunk.content:
                        self.ui.stream_token(chunk.content)
                    if chunk.reasoning_content:
                        self.ui.stream_thinking(chunk.reasoning_content)
                elif isinstance(chunk, LLMResponse):
                    final_response = chunk
        finally:
            # Stop spinner and restore normal terminal after streaming is done
            self.ui.stop_spinner()
            reasoning = self.ui.end_stream()
            # Attach reasoning to the response if available
            if final_response and reasoning and not final_response.reasoning_content:
                final_response.reasoning_content = reasoning

        return final_response or LLMResponse()

    def _execute_tool(self, tool_call: ToolCall) -> None:
        """Execute a single tool call with permission check."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            error_msg = f"Unknown tool: {tool_call.name}"
            self.ui.show_error(error_msg)
            self.history.append(Message(
                role="tool",
                content=error_msg,
                tool_call_id=tool_call.id,
            ))
            return

        # Show what's about to be executed
        self.ui.show_tool_call(tool_call)

        # Request permission
        try:
            if tool_call.name == "bash":
                self.permissions.request_bash(tool_call.arguments.get("command", ""))
            else:
                cmd = tool_call.arguments.get("command", "")
                path = tool_call.arguments.get("path", "")
                self.permissions.request_editor(cmd, path)
        except PermissionDenied as e:
            self.ui.show_info("Permission denied by user")
            self.history.append(Message(
                role="tool",
                content=f"Permission denied: {e}",
                tool_call_id=tool_call.id,
            ))
            return

        # Execute the tool
        try:
            result = tool.execute(tool_call.arguments)
            self.ui.show_result(result)
            self.history.append(Message(
                role="tool",
                content=result.output,
                tool_call_id=tool_call.id,
            ))
        except ToolError as e:
            self.ui.show_error(str(e))
            self.history.append(Message(
                role="tool",
                content=f"Tool error: {e}",
                tool_call_id=tool_call.id,
            ))
