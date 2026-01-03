"""Message and content block types."""

from typing import Any, Literal

from pydantic import BaseModel, Field


# Streaming event types
class StreamEvent(BaseModel):
    """Base streaming event."""

    type: str


class TextDeltaEvent(StreamEvent):
    """Text chunk event during streaming."""

    type: Literal["text_delta"] = "text_delta"
    text: str


class ToolUseStartEvent(StreamEvent):
    """Tool use started event."""

    type: Literal["tool_use_start"] = "tool_use_start"
    id: str
    name: str


class ToolUseInputEvent(StreamEvent):
    """Tool use input delta event."""

    type: Literal["tool_use_input"] = "tool_use_input"
    id: str
    input_delta: str


class MessageStopEvent(StreamEvent):
    """Message complete event."""

    type: Literal["message_stop"] = "message_stop"
    stop_reason: str
    usage: dict[str, int] | None = None


class ToolExecutingEvent(StreamEvent):
    """Tool execution started event."""

    type: Literal["tool_executing"] = "tool_executing"
    tool_name: str
    tool_id: str


class ToolResultEvent(StreamEvent):
    """Tool execution result event."""

    type: Literal["tool_result"] = "tool_result"
    tool_name: str
    tool_id: str
    success: bool
    output: str


class ReasoningStartEvent(StreamEvent):
    """Agent started reasoning/thinking."""

    type: Literal["reasoning_start"] = "reasoning_start"


class ReasoningDeltaEvent(StreamEvent):
    """Reasoning content chunk."""

    type: Literal["reasoning_delta"] = "reasoning_delta"
    text: str


class ReasoningEndEvent(StreamEvent):
    """Agent finished reasoning."""

    type: Literal["reasoning_end"] = "reasoning_end"


class ToolApprovalRequestEvent(StreamEvent):
    """Tool execution needs approval."""

    type: Literal["tool_approval_request"] = "tool_approval_request"
    tool_name: str
    args: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class ToolApprovalResponseEvent(StreamEvent):
    """Response to tool approval request."""

    type: Literal["tool_approval_response"] = "tool_approval_response"
    tool_name: str
    approved: bool
    feedback: str | None = None


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
