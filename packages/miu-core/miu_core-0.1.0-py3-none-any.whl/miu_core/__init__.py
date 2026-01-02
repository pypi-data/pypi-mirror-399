"""miu-core: Core framework library for miu AI agent."""

from miu_core.version import get_version

__version__ = get_version()

# Lazy imports to avoid circular dependencies
__all__ = [
    "Orchestrator",
    "OrchestratorConfig",
    "Pipeline",
    "PipelineConfig",
    "Router",
    "RouterConfig",
    "__version__",
]


def __getattr__(name: str) -> object:
    """Lazy import patterns module."""
    if name in (
        "Orchestrator",
        "OrchestratorConfig",
        "Pipeline",
        "PipelineConfig",
        "Router",
        "RouterConfig",
    ):
        from miu_core import patterns

        return getattr(patterns, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
