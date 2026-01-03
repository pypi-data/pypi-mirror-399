"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, TypedDict


class ToolSchema(TypedDict):
    """Tool definition schema for LLM."""

    name: str
    description: str
    input_schema: dict[str, Any]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str
    model: str

    @abstractmethod
    async def complete(
        self,
        messages: list["Message"],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> "Response":
        """Send messages to LLM and get response."""
        ...

    async def stream(
        self,
        messages: list["Message"],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator["StreamEvent"]:
        """Stream messages from LLM. Override in subclass for streaming support."""
        # Default: just yield the complete response as a single event
        response = await self.complete(messages, tools, system, max_tokens)
        text = response.get_text()
        if text:
            yield TextDeltaEvent(text=text)
        yield MessageStopEvent(stop_reason=response.stop_reason)


# Import at end to avoid circular imports
from miu_core.models import (  # noqa: E402
    Message,
    MessageStopEvent,
    Response,
    StreamEvent,
    TextDeltaEvent,
)
