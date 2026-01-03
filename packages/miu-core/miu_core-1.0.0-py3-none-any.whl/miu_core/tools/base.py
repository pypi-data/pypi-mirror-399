"""Base tool interface."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from tool execution."""

    output: str
    success: bool = True
    error: str | None = None


class ToolContext(BaseModel):
    """Execution context for tools."""

    working_dir: str = "."
    session_id: str = "default"


class Tool(ABC):
    """Abstract base class for tools."""

    name: str
    description: str

    @abstractmethod
    def get_input_schema(self) -> type[BaseModel]:
        """Return Pydantic model for tool input."""
        ...

    @abstractmethod
    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Execute the tool with given inputs."""
        ...

    def to_schema(self) -> dict[str, Any]:
        """Convert tool to LLM-compatible schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema().model_json_schema(),
        }
