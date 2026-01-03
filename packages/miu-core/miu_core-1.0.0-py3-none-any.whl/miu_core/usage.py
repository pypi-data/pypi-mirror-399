"""Token usage tracking."""

from dataclasses import dataclass, field


@dataclass
class UsageStats:
    """Token usage statistics."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed."""
        return self.input_tokens + self.output_tokens

    def add(self, other: "UsageStats") -> None:
        """Accumulate usage from another stats object."""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.cache_write_tokens += other.cache_write_tokens


@dataclass
class UsageTracker:
    """Track token usage across a session."""

    context_limit: int = 200_000  # Default for Claude models
    stats: UsageStats = field(default_factory=UsageStats)

    def add_usage(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read: int = 0,
        cache_write: int = 0,
    ) -> None:
        """Add token usage from an API call."""
        self.stats.input_tokens += input_tokens
        self.stats.output_tokens += output_tokens
        self.stats.cache_read_tokens += cache_read
        self.stats.cache_write_tokens += cache_write

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.stats.total_tokens

    @property
    def usage_percent(self) -> float:
        """Percentage of context used (total tokens / limit)."""
        if self.context_limit == 0:
            return 0.0
        return (self.stats.total_tokens / self.context_limit) * 100

    def format_usage(self) -> str:
        """Format usage for display: '4% of 200k tokens'."""
        pct = self.usage_percent
        limit_k = self.context_limit // 1000
        return f"{pct:.0f}% of {limit_k}k tokens"

    def reset(self) -> None:
        """Reset usage statistics."""
        self.stats = UsageStats()
