"""Anthropic Claude provider."""

from typing import Any

from miu_core.models import (
    Message,
    Response,
    TextContent,
    ToolUseContent,
    Usage,
)
from miu_core.providers.base import LLMProvider, ToolSchema
from miu_core.tracing import Tracer, get_tracer
from miu_core.tracing.types import SpanAttributes

try:
    from anthropic import AsyncAnthropic
except ImportError as e:
    raise ImportError("anthropic package required. Install with: uv add miu-core[anthropic]") from e


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model
        self._client = AsyncAnthropic()
        self._tracer: Tracer = get_tracer("miu.provider")

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Send messages to Claude and get response."""
        with self._tracer.start_as_current_span("provider.complete") as span:
            span.set_attribute(SpanAttributes.PROVIDER_NAME, self.name)
            span.set_attribute(SpanAttributes.PROVIDER_MODEL, self.model)

            api_messages = self._convert_messages(messages)

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": max_tokens,
            }
            if system:
                kwargs["system"] = system
            if tools:
                kwargs["tools"] = tools

            response = await self._client.messages.create(**kwargs)
            result = self._convert_response(response)

            # Record token usage and stop reason
            if result.usage:
                span.set_attribute(SpanAttributes.PROVIDER_TOKENS_INPUT, result.usage.input_tokens)
                span.set_attribute(
                    SpanAttributes.PROVIDER_TOKENS_OUTPUT, result.usage.output_tokens
                )
            span.set_attribute(SpanAttributes.PROVIDER_STOP_REASON, result.stop_reason)

            return result

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert internal messages to Anthropic format."""
        result: list[dict[str, Any]] = []
        for msg in messages:
            if msg.role == "system":
                continue  # System handled separately

            if isinstance(msg.content, str):
                result.append({"role": msg.role, "content": msg.content})
            else:
                content_blocks: list[dict[str, Any]] = []
                for block in msg.content:
                    if isinstance(block, TextContent):
                        content_blocks.append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolUseContent):
                        content_blocks.append(
                            {
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            }
                        )
                    else:
                        content_blocks.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.tool_use_id,
                                "content": block.content,
                                "is_error": block.is_error,
                            }
                        )
                result.append({"role": msg.role, "content": content_blocks})

        return result

    def _convert_response(self, response: Any) -> Response:
        """Convert Anthropic response to internal format."""
        content: list[TextContent | ToolUseContent] = []

        for block in response.content:
            if block.type == "text":
                content.append(TextContent(text=block.text))
            elif block.type == "tool_use":
                content.append(
                    ToolUseContent(
                        id=block.id,
                        name=block.name,
                        input=block.input,
                    )
                )

        return Response(
            id=response.id,
            content=content,
            stop_reason=response.stop_reason or "end_turn",
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
        )
