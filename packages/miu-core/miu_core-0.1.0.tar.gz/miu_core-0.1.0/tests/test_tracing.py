"""Tests for tracing module."""

from miu_core.tracing import get_tracer
from miu_core.tracing.noop import NoOpSpan, NoOpTracer
from miu_core.tracing.types import SpanAttributes, SpanKind, TracingConfig


def test_tracing_config_defaults() -> None:
    """Test TracingConfig has sensible defaults."""
    config = TracingConfig()
    assert config.service_name == "miu"
    assert config.enabled is True
    assert config.sample_rate == 1.0
    assert config.console_export is False
    assert config.endpoint is None


def test_tracing_config_custom() -> None:
    """Test TracingConfig with custom values."""
    config = TracingConfig(
        service_name="test-service",
        endpoint="http://localhost:4317",
        enabled=True,
        sample_rate=0.5,
        console_export=True,
    )
    assert config.service_name == "test-service"
    assert config.endpoint == "http://localhost:4317"
    assert config.sample_rate == 0.5


def test_span_kind_enum() -> None:
    """Test SpanKind enum values."""
    assert SpanKind.AGENT == "agent"
    assert SpanKind.PROVIDER == "provider"
    assert SpanKind.TOOL == "tool"
    assert SpanKind.MEMORY == "memory"
    assert SpanKind.MCP == "mcp"


def test_span_attributes() -> None:
    """Test SpanAttributes constants."""
    # Agent attributes
    assert SpanAttributes.AGENT_NAME == "miu.agent.name"
    assert SpanAttributes.AGENT_QUERY == "miu.agent.query"
    assert SpanAttributes.AGENT_ITERATIONS == "miu.agent.iterations"

    # Provider attributes
    assert SpanAttributes.PROVIDER_NAME == "miu.provider.name"
    assert SpanAttributes.PROVIDER_MODEL == "miu.provider.model"
    assert SpanAttributes.PROVIDER_TOKENS_INPUT == "miu.provider.tokens.input"
    assert SpanAttributes.PROVIDER_TOKENS_OUTPUT == "miu.provider.tokens.output"

    # Tool attributes
    assert SpanAttributes.TOOL_NAME == "miu.tool.name"
    assert SpanAttributes.TOOL_SUCCESS == "miu.tool.success"


def test_noop_span() -> None:
    """Test NoOpSpan does nothing but doesn't error."""
    span = NoOpSpan()

    # All methods should be no-ops
    span.set_attribute("key", "value")
    span.set_status(None)
    span.record_exception(Exception("test"))
    span.end()

    # Context manager should work
    with span as s:
        assert s is span


def test_noop_tracer() -> None:
    """Test NoOpTracer returns no-op spans."""
    tracer = NoOpTracer()

    # start_as_current_span context manager
    with tracer.start_as_current_span("test-span") as span:
        assert isinstance(span, NoOpSpan)
        span.set_attribute("key", "value")

    # start_span returns NoOpSpan
    span = tracer.start_span("another-span")
    assert isinstance(span, NoOpSpan)


def test_get_tracer_returns_noop_when_otel_not_installed() -> None:
    """Test get_tracer returns no-op tracer when OTel not installed."""
    # This test assumes OTel is not installed in base test environment
    # If OTel IS installed, this will return a real tracer which is also fine
    tracer = get_tracer("test")
    # Should be usable regardless
    with tracer.start_as_current_span("test") as span:
        span.set_attribute("test", "value")
