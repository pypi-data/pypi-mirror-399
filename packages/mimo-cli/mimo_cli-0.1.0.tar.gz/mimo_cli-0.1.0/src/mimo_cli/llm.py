"""LLM client wrapper using litellm."""

import json
from dataclasses import dataclass
from typing import Any, Generator

import litellm

from .types import LLMError, LLMResponse, Message, ToolCall

litellm.suppress_debug_info = True

@dataclass
class StreamChunk:
    """A chunk from streaming response."""
    content: str | None = None
    reasoning_content: str | None = None


class LLMClient:
    """Thin wrapper over litellm for OpenAI-compatible LLM calls."""

    def __init__(self, model: str, api_base: str | None = None, api_key: str | None = None):
        self.model = model
        self.api_base = api_base
        self.api_key = api_key

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert internal Message format to litellm format."""
        result = []
        for msg in messages:
            m: dict[str, Any] = {"role": msg.role}

            # For assistant messages with tool_calls, content must exist (even if empty)
            if msg.content is not None:
                m["content"] = msg.content
            elif msg.role == "assistant" and msg.tool_calls:
                m["content"] = ""  # API requires content field for assistant messages

            if msg.reasoning_content is not None:
                m["reasoning_content"] = msg.reasoning_content

            if msg.tool_calls:
                m["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                    }
                    for tc in msg.tool_calls
                ]

            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id

            result.append(m)
        return result

    def _convert_tools(self, tools: list[Any]) -> list[dict[str, Any]]:
        """Convert Tool protocol objects to litellm format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    def chat(self, messages: list[Message], tools: list[Any]) -> LLMResponse:
        """Send messages to LLM and get response. May contain tool calls."""
        try:
            response = litellm.completion(
                model=self.model,
                messages=self._convert_messages(messages),
                tools=self._convert_tools(tools) if tools else None,
                api_base=self.api_base,
                api_key=self.api_key,
            )

            choice = response.choices[0]
            message = choice.message

            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                    for tc in message.tool_calls
                ]

            return LLMResponse(
                content=message.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
            )

        except Exception as e:
            raise LLMError(f"LLM request failed: {e}") from e

    def chat_stream(
        self, messages: list[Message], tools: list[Any]
    ) -> Generator[StreamChunk | LLMResponse, None, None]:
        """Stream chat response token by token.

        Yields StreamChunk for content/reasoning tokens, and finally LLMResponse with tool calls if any.
        """
        try:
            response = litellm.completion(
                model=self.model,
                messages=self._convert_messages(messages),
                tools=self._convert_tools(tools) if tools else None,
                api_base=self.api_base,
                api_key=self.api_key,
                stream=True,
            )

            collected_content = ""
            collected_reasoning = ""
            collected_tool_calls: dict[int, dict[str, Any]] = {}

            for chunk in response:
                delta = chunk.choices[0].delta

                # Stream content tokens
                if delta.content:
                    collected_content += delta.content
                    yield StreamChunk(content=delta.content)

                # Stream reasoning/thinking tokens (some models use this field)
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    collected_reasoning += reasoning
                    yield StreamChunk(reasoning_content=reasoning)

                # Collect tool call chunks
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in collected_tool_calls:
                            collected_tool_calls[idx] = {
                                "id": tc.id or "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc.id:
                            collected_tool_calls[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                collected_tool_calls[idx]["name"] = tc.function.name
                            if tc.function.arguments:
                                collected_tool_calls[idx]["arguments"] += tc.function.arguments

                # Check if done
                if chunk.choices[0].finish_reason:
                    tool_calls = None
                    if collected_tool_calls:
                        tool_calls = [
                            ToolCall(
                                id=tc["id"],
                                name=tc["name"],
                                arguments=json.loads(tc["arguments"]) if tc["arguments"] else {},
                            )
                            for tc in collected_tool_calls.values()
                        ]

                    yield LLMResponse(
                        content=collected_content if collected_content else None,
                        tool_calls=tool_calls,
                        finish_reason=chunk.choices[0].finish_reason,
                        reasoning_content=collected_reasoning if collected_reasoning else None,
                    )

        except Exception as e:
            raise LLMError(f"LLM stream request failed: {e}") from e
