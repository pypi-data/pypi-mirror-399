"""Session logger for debugging and replay."""

from datetime import datetime
from pathlib import Path
from typing import Any

from miu_core.logging.types import LogEntry, LogEventType
from miu_core.paths import MiuPaths


class SessionLogger:
    """Log session interactions for debugging and replay."""

    def __init__(self, save_dir: Path | None = None) -> None:
        """Initialize session logger.

        Args:
            save_dir: Directory to save log files (defaults to ~/.miu/logs)
        """
        self.save_dir = save_dir or MiuPaths.get().logs
        self._entries: list[LogEntry] = []
        self._session_id: str = ""
        self._active = False

    def start_session(self, session_id: str | None = None) -> str:
        """Start a new logging session.

        Args:
            session_id: Optional session ID, generates if not provided

        Returns:
            The session ID
        """
        if session_id is None:
            session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._session_id = session_id
        self._entries = []
        self._active = True

        self.log(LogEventType.SESSION_START, f"Session started: {session_id}")
        return session_id

    def end_session(self) -> None:
        """End the current session."""
        if self._active:
            self.log(LogEventType.SESSION_END, "Session ended")
            self._active = False

    def log(
        self,
        event_type: LogEventType,
        content: str = "",
        **metadata: Any,
    ) -> LogEntry:
        """Log an event.

        Args:
            event_type: Type of event
            content: Event content/message
            **metadata: Additional metadata

        Returns:
            Created log entry
        """
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            content=content,
            metadata=metadata,
            session_id=self._session_id,
        )
        self._entries.append(entry)
        return entry

    def log_user_message(self, message: str) -> LogEntry:
        """Log a user message."""
        return self.log(LogEventType.USER_MESSAGE, message)

    def log_assistant_message(self, message: str) -> LogEntry:
        """Log an assistant message."""
        return self.log(LogEventType.ASSISTANT_MESSAGE, message)

    def log_tool_call(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> LogEntry:
        """Log a tool call."""
        return self.log(
            LogEventType.TOOL_CALL,
            f"Calling tool: {tool_name}",
            tool_name=tool_name,
            tool_input=tool_input,
        )

    def log_tool_result(
        self,
        tool_name: str,
        result: str,
        success: bool = True,
    ) -> LogEntry:
        """Log a tool result."""
        return self.log(
            LogEventType.TOOL_RESULT,
            result,
            tool_name=tool_name,
            success=success,
        )

    def log_error(self, error: str, **metadata: Any) -> LogEntry:
        """Log an error."""
        return self.log(LogEventType.ERROR, error, **metadata)

    def save(self) -> Path:
        """Save session log to file.

        Returns:
            Path to saved file
        """
        self.save_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.save_dir / f"session_{self._session_id}.jsonl"

        with open(filepath, "w", encoding="utf-8") as f:
            for entry in self._entries:
                f.write(entry.model_dump_json() + "\n")

        return filepath

    @classmethod
    def load(cls, filepath: Path) -> list[LogEntry]:
        """Load session log from file.

        Args:
            filepath: Path to log file

        Returns:
            List of log entries
        """
        entries: list[LogEntry] = []
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(LogEntry.model_validate_json(line))
        return entries

    @classmethod
    def replay(cls, filepath: Path) -> list[LogEntry]:
        """Load session log for replay.

        This is an alias for load() for semantic clarity.

        Args:
            filepath: Path to log file

        Returns:
            List of log entries
        """
        return cls.load(filepath)

    @property
    def session_id(self) -> str:
        """Get current session ID."""
        return self._session_id

    @property
    def entries(self) -> list[LogEntry]:
        """Get all log entries."""
        return self._entries.copy()

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self._active
