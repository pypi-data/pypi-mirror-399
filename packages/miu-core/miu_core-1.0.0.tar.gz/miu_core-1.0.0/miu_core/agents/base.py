"""Base agent interface."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from miu_core.memory import Memory as MemoryInterface
from miu_core.memory import ShortTermMemory
from miu_core.models import Response
from miu_core.providers.base import LLMProvider
from miu_core.tools.registry import ToolRegistry


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str = "agent"
    system_prompt: str = "You are a helpful AI assistant."
    max_iterations: int = 10
    max_context_tokens: int = 100000  # Auto-truncate at this limit


class Agent(ABC):
    """Abstract base class for agents."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: ToolRegistry | None = None,
        config: AgentConfig | None = None,
        memory: MemoryInterface | None = None,
    ) -> None:
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.config = config or AgentConfig()
        self.memory = memory or ShortTermMemory()

    @abstractmethod
    async def run(self, query: str) -> Response:
        """Process a query and return response."""
        ...
