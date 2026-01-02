"""Base LLM provider interface."""

from abc import ABC, abstractmethod
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


# Import at end to avoid circular imports
from miu_core.models import Message, Response  # noqa: E402
