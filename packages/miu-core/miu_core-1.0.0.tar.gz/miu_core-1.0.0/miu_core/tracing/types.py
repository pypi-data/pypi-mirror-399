"""Tracing types and configuration."""

from enum import Enum

from pydantic import BaseModel, Field


class SpanKind(str, Enum):
    """Types of spans for categorization."""

    AGENT = "agent"
    PROVIDER = "provider"
    TOOL = "tool"
    MEMORY = "memory"
    MCP = "mcp"


class TracingConfig(BaseModel):
    """Configuration for OpenTelemetry tracing."""

    service_name: str = Field(default="miu", description="Service name for traces")
    endpoint: str | None = Field(
        default=None,
        description="OTLP endpoint (e.g., http://localhost:4317). Uses env var if not set.",
    )
    enabled: bool = Field(default=True, description="Enable/disable tracing")
    sample_rate: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Trace sample rate (0.0-1.0)"
    )
    console_export: bool = Field(
        default=False, description="Also export spans to console for debugging"
    )


# Semantic attribute names for miu spans
class SpanAttributes:
    """Standard attribute names for miu spans."""

    # Agent attributes
    AGENT_NAME = "miu.agent.name"
    AGENT_QUERY = "miu.agent.query"
    AGENT_ITERATIONS = "miu.agent.iterations"
    AGENT_MAX_ITERATIONS = "miu.agent.max_iterations"

    # Provider attributes
    PROVIDER_NAME = "miu.provider.name"
    PROVIDER_MODEL = "miu.provider.model"
    PROVIDER_TOKENS_INPUT = "miu.provider.tokens.input"
    PROVIDER_TOKENS_OUTPUT = "miu.provider.tokens.output"
    PROVIDER_STOP_REASON = "miu.provider.stop_reason"

    # Tool attributes
    TOOL_NAME = "miu.tool.name"
    TOOL_SUCCESS = "miu.tool.success"
    TOOL_ERROR = "miu.tool.error"

    # Memory attributes
    MEMORY_MESSAGE_COUNT = "miu.memory.message_count"
    MEMORY_TRUNCATED = "miu.memory.truncated"

    # Error attributes
    ERROR_TYPE = "miu.error.type"
    ERROR_MESSAGE = "miu.error.message"
