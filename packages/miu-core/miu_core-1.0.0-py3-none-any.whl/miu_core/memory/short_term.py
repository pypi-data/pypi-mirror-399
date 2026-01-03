"""Short-term memory implementation."""

from miu_core.memory.base import Memory
from miu_core.memory.truncation import TruncationStrategy, truncate_fifo, truncate_sliding
from miu_core.models import Message


class ShortTermMemory(Memory):
    """In-memory conversation storage with truncation support."""

    def __init__(
        self,
        strategy: TruncationStrategy = TruncationStrategy.FIFO,
        max_messages: int = 100,
    ) -> None:
        self._messages: list[Message] = []
        self.strategy = strategy
        self.max_messages = max_messages

    @property
    def messages(self) -> list[Message]:
        """Get all messages."""
        return self._messages.copy()

    def add(self, message: Message) -> None:
        """Add a message to memory."""
        self._messages.append(message)

        # Auto-truncate if too many messages
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]

    def get_messages(self) -> list[Message]:
        """Get messages for LLM context."""
        return self._messages.copy()

    def truncate(self, max_tokens: int) -> int:
        """Truncate memory to fit within token limit."""
        if self.strategy == TruncationStrategy.FIFO:
            self._messages, removed = truncate_fifo(self._messages, max_tokens)
        elif self.strategy == TruncationStrategy.SLIDING:
            self._messages, removed = truncate_sliding(self._messages, max_tokens)
        else:
            removed = 0
        return removed

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()
