"""OpenTelemetry integration for miu-core.

This module provides OpenTelemetry tracing setup and utilities.
Requires: pip install miu-core[tracing]
"""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from miu_core.tracing.types import TracingConfig

# Global tracer provider
_tracer_provider: TracerProvider | None = None


def setup_tracing(config: TracingConfig | None = None) -> trace.Tracer:
    """Setup OpenTelemetry tracing with OTLP exporter.

    Args:
        config: Tracing configuration. Uses defaults if not provided.

    Returns:
        Configured tracer instance.
    """
    global _tracer_provider

    if config is None:
        config = TracingConfig()

    if not config.enabled:
        # Return no-op tracer if disabled
        return trace.get_tracer(config.service_name)

    # Create resource with service info
    resource = Resource.create(
        {
            "service.name": config.service_name,
            "service.version": "0.1.0",
        }
    )

    # Create sampler based on sample rate
    sampler = TraceIdRatioBased(config.sample_rate)

    # Create provider
    _tracer_provider = TracerProvider(resource=resource, sampler=sampler)

    # Add OTLP exporter if endpoint is configured
    if config.endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        otlp_exporter = OTLPSpanExporter(endpoint=config.endpoint)
        _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Add console exporter if enabled (for debugging)
    if config.console_export:
        _tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)

    return trace.get_tracer(config.service_name)


def get_tracer(name: str = "miu") -> trace.Tracer:
    """Get a tracer instance.

    If setup_tracing() hasn't been called, returns a no-op tracer.

    Args:
        name: Tracer name (defaults to "miu")

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def shutdown() -> None:
    """Shutdown the tracer provider and flush pending spans."""
    global _tracer_provider
    if _tracer_provider is not None:
        _tracer_provider.shutdown()
        _tracer_provider = None
