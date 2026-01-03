"""Logging type definitions."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LogEventType(str, Enum):
    """Types of log events."""

    SESSION_START = "session_start"
    SESSION_END = "session_end"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    SYSTEM = "system"


class LogEntry(BaseModel):
    """A single log entry."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: LogEventType
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None

    class Config:
        """Pydantic config."""

        use_enum_values = True
