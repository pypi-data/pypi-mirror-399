"""Hook event definitions."""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class HookEvent(str, Enum):
    """Lifecycle events that can trigger hooks."""

    SESSION_START = "session_start"
    SESSION_END = "session_end"
    PRE_MESSAGE = "pre_message"
    POST_MESSAGE = "post_message"
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"


class HookInput(BaseModel):
    """Input passed to hook scripts."""

    event: HookEvent
    session_id: str | None = None
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    message: str | None = None
    extra: dict[str, Any] | None = None


class HookResult(BaseModel):
    """Result from hook execution."""

    success: bool = True
    output: str = ""
    should_block: bool = False
    modified_input: dict[str, Any] | None = None
