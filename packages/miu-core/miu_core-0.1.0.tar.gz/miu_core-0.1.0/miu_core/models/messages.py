"""Message and content block types."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class TextContent(BaseModel):
    """Text content block."""

    type: Literal["text"] = "text"
    text: str


class ToolUseContent(BaseModel):
    """Tool use request from assistant."""

    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict[str, Any]


class ToolResultContent(BaseModel):
    """Tool execution result."""

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool = False


ContentBlock = TextContent | ToolUseContent | ToolResultContent


class Message(BaseModel):
    """Conversation message."""

    role: Literal["user", "assistant", "system"]
    content: str | list[ContentBlock]

    def get_text(self) -> str:
        """Extract text content from message."""
        if isinstance(self.content, str):
            return self.content
        texts = [block.text for block in self.content if isinstance(block, TextContent)]
        return "\n".join(texts)


class Usage(BaseModel):
    """Token usage information."""

    input_tokens: int = 0
    output_tokens: int = 0


class Response(BaseModel):
    """LLM response."""

    id: str
    content: list[ContentBlock] = Field(default_factory=list)
    stop_reason: str = "end_turn"
    usage: Usage | None = None

    def get_text(self) -> str:
        """Extract text content from response."""
        texts = [block.text for block in self.content if isinstance(block, TextContent)]
        return "\n".join(texts)

    def get_tool_uses(self) -> list[ToolUseContent]:
        """Extract tool use blocks from response."""
        return [block for block in self.content if isinstance(block, ToolUseContent)]
