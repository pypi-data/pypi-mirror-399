"""OpenAI GPT provider."""

import json
from typing import Any

from miu_core.models import (
    Message,
    Response,
    TextContent,
    ToolUseContent,
    Usage,
)
from miu_core.providers.base import LLMProvider, ToolSchema

try:
    from openai import AsyncOpenAI
except ImportError as e:
    raise ImportError("openai package required. Install with: uv add miu-core[openai]") from e


class OpenAIProvider(LLMProvider):
    """OpenAI GPT LLM provider."""

    name = "openai"

    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model
        self._client = AsyncOpenAI()

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Send messages to OpenAI and get response."""
        api_messages = self._convert_messages(messages, system)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self._client.chat.completions.create(**kwargs)
        return self._convert_response(response)

    def _convert_messages(
        self, messages: list[Message], system: str | None
    ) -> list[dict[str, Any]]:
        """Convert internal messages to OpenAI format."""
        result: list[dict[str, Any]] = []

        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            if msg.role == "system":
                result.append({"role": "system", "content": msg.get_text()})
            elif isinstance(msg.content, str):
                result.append({"role": msg.role, "content": msg.content})
            else:
                # Handle content blocks
                for block in msg.content:
                    if isinstance(block, TextContent):
                        result.append({"role": msg.role, "content": block.text})
                    elif isinstance(block, ToolUseContent):
                        # OpenAI uses tool_calls in assistant message
                        result.append(
                            {
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "id": block.id,
                                        "type": "function",
                                        "function": {
                                            "name": block.name,
                                            "arguments": str(block.input),
                                        },
                                    }
                                ],
                            }
                        )
                    else:
                        # Tool result
                        result.append(
                            {
                                "role": "tool",
                                "tool_call_id": block.tool_use_id,
                                "content": block.content,
                            }
                        )

        return result

    def _convert_tools(
        self, tools: list[ToolSchema] | list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert tool schemas to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                },
            }
            for tool in tools
        ]

    def _convert_response(self, response: Any) -> Response:
        """Convert OpenAI response to internal format."""
        choice = response.choices[0]
        message = choice.message
        content: list[TextContent | ToolUseContent] = []

        if message.content:
            content.append(TextContent(text=message.content))

        if message.tool_calls:
            for tool_call in message.tool_calls:
                # Safely parse tool arguments
                tool_input: dict[str, Any] = {}
                if tool_call.function.arguments:
                    try:
                        tool_input = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}
                content.append(
                    ToolUseContent(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        input=tool_input,
                    )
                )

        stop_reason = "end_turn"
        if choice.finish_reason == "tool_calls":
            stop_reason = "tool_use"
        elif choice.finish_reason == "stop":
            stop_reason = "end_turn"

        return Response(
            id=response.id,
            content=content,
            stop_reason=stop_reason,
            usage=Usage(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
            ),
        )
