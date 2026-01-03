"""LLM providers."""

from miu_core.providers.base import LLMProvider, ToolSchema

__all__ = ["LLMProvider", "ToolSchema", "create_provider"]


def create_provider(spec: str) -> LLMProvider:
    """Create provider from 'provider:model' spec.

    Examples:
        - anthropic:claude-sonnet-4-20250514
        - openai:gpt-4o
        - google:gemini-2.0-flash

    If no model specified, uses provider default.
    """
    if ":" in spec:
        provider_name, model = spec.split(":", 1)
    else:
        provider_name = spec
        model = None

    if provider_name == "anthropic":
        from miu_core.providers.anthropic import AnthropicProvider

        return AnthropicProvider(model=model) if model else AnthropicProvider()
    elif provider_name == "openai":
        from miu_core.providers.openai import OpenAIProvider

        return OpenAIProvider(model=model) if model else OpenAIProvider()
    elif provider_name == "google":
        from miu_core.providers.google import GoogleProvider

        return GoogleProvider(model=model) if model else GoogleProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


# Lazy imports for optional providers
def __getattr__(name: str) -> type:
    if name == "AnthropicProvider":
        from miu_core.providers.anthropic import AnthropicProvider

        return AnthropicProvider
    if name == "OpenAIProvider":
        from miu_core.providers.openai import OpenAIProvider

        return OpenAIProvider
    if name == "GoogleProvider":
        from miu_core.providers.google import GoogleProvider

        return GoogleProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
