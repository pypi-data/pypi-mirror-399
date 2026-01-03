"""Truncation strategies for memory management."""

from enum import Enum

from miu_core.models import Message


class TruncationStrategy(str, Enum):
    """Strategy for truncating conversation history."""

    FIFO = "fifo"  # First In, First Out - remove oldest messages
    SLIDING = "sliding"  # Keep first + last N messages
    SUMMARIZE = "summarize"  # Placeholder for future summarization


def estimate_tokens(message: Message) -> int:
    """Estimate token count for a message.

    Uses ~4 chars per token as rough estimate.
    """
    content = message.content
    if isinstance(content, str):
        text = content
    else:
        text = " ".join(block.text if hasattr(block, "text") else str(block) for block in content)
    # Rough estimate: ~4 chars per token
    return len(text) // 4 + 1


def truncate_fifo(messages: list[Message], max_tokens: int) -> tuple[list[Message], int]:
    """Truncate using FIFO strategy.

    Removes oldest messages (except first user message) until under limit.

    Returns: (truncated messages, tokens removed)
    """
    if not messages:
        return messages, 0

    total_tokens = sum(estimate_tokens(m) for m in messages)
    if total_tokens <= max_tokens:
        return messages, 0

    # Keep first message (usually important context)
    result = [messages[0]]
    tokens_kept = estimate_tokens(messages[0])

    # Add messages from end until we hit limit
    for msg in reversed(messages[1:]):
        msg_tokens = estimate_tokens(msg)
        if tokens_kept + msg_tokens <= max_tokens:
            result.insert(1, msg)
            tokens_kept += msg_tokens
        else:
            break

    tokens_removed = total_tokens - tokens_kept
    return result, tokens_removed


def truncate_sliding(
    messages: list[Message], max_tokens: int, keep_first: int = 1, keep_last: int = 10
) -> tuple[list[Message], int]:
    """Truncate using sliding window strategy.

    Keeps first N and last M messages.

    Returns: (truncated messages, tokens removed)
    """
    if len(messages) <= keep_first + keep_last:
        return messages, 0

    total_tokens = sum(estimate_tokens(m) for m in messages)

    # Keep first and last messages
    first = messages[:keep_first]
    last = messages[-keep_last:]
    result = first + last

    tokens_kept = sum(estimate_tokens(m) for m in result)
    tokens_removed = total_tokens - tokens_kept

    return result, tokens_removed
