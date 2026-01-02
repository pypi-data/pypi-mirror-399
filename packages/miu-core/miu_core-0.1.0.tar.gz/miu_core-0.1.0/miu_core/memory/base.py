"""Base memory interface."""

from abc import ABC, abstractmethod

from miu_core.models import Message


class Memory(ABC):
    """Abstract base class for memory implementations."""

    @property
    @abstractmethod
    def messages(self) -> list[Message]:
        """Get all messages in memory."""
        ...

    @abstractmethod
    def add(self, message: Message) -> None:
        """Add a message to memory."""
        ...

    @abstractmethod
    def get_messages(self) -> list[Message]:
        """Get messages for LLM context."""
        ...

    @abstractmethod
    def truncate(self, max_tokens: int) -> int:
        """Truncate memory to fit within token limit. Returns tokens removed."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all messages from memory."""
        ...

    def __len__(self) -> int:
        """Get number of messages in memory."""
        return len(self.messages)
