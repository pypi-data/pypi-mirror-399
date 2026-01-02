"""ReAct (Reasoning + Acting) agent implementation."""

from miu_core.agents.base import Agent, AgentConfig
from miu_core.memory import Memory
from miu_core.models import Message, Response, TextContent, ToolResultContent
from miu_core.providers.base import LLMProvider
from miu_core.tools.base import ToolContext
from miu_core.tools.registry import ToolRegistry
from miu_core.tracing import Tracer, get_tracer
from miu_core.tracing.types import SpanAttributes


class ReActAgent(Agent):
    """Agent implementing ReAct pattern."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: ToolRegistry | None = None,
        config: AgentConfig | None = None,
        memory: Memory | None = None,
        working_dir: str = ".",
    ) -> None:
        super().__init__(provider, tools, config, memory)
        self.working_dir = working_dir
        self._tracer: Tracer = get_tracer("miu.agent")

    async def run(self, query: str) -> Response:
        """Execute ReAct loop for query."""
        with self._tracer.start_as_current_span("agent.run") as span:
            span.set_attribute(SpanAttributes.AGENT_NAME, self.config.name)
            span.set_attribute(SpanAttributes.AGENT_QUERY, query[:100])
            span.set_attribute(SpanAttributes.AGENT_MAX_ITERATIONS, self.config.max_iterations)

            self.memory.add(Message(role="user", content=query))

            # Auto-truncate if over context limit
            self.memory.truncate(self.config.max_context_tokens)

            iteration = 0
            for iteration in range(self.config.max_iterations):
                response = await self.provider.complete(
                    messages=self.memory.get_messages(),
                    tools=self.tools.get_schemas() if len(self.tools) > 0 else None,
                    system=self.config.system_prompt,
                )
                self.memory.add(Message(role="assistant", content=response.content))

                if response.stop_reason == "end_turn":
                    span.set_attribute(SpanAttributes.AGENT_ITERATIONS, iteration + 1)
                    return response

                if response.stop_reason == "tool_use":
                    await self._execute_tools(response)

            span.set_attribute(SpanAttributes.AGENT_ITERATIONS, iteration + 1)
            return Response(
                id="max_iterations",
                content=[TextContent(text="Maximum iterations reached")],
                stop_reason="max_iterations",
            )

    async def _execute_tools(self, response: Response) -> None:
        """Execute tool calls from response."""
        tool_uses = response.get_tool_uses()
        ctx = ToolContext(working_dir=self.working_dir)

        results: list[ToolResultContent] = []
        for tool_use in tool_uses:
            with self._tracer.start_as_current_span("tool.execute") as span:
                span.set_attribute(SpanAttributes.TOOL_NAME, tool_use.name)

                result = await self.tools.execute(tool_use.name, ctx, **tool_use.input)

                span.set_attribute(SpanAttributes.TOOL_SUCCESS, result.success)
                if not result.success and result.error:
                    span.set_attribute(SpanAttributes.TOOL_ERROR, result.error)

                results.append(
                    ToolResultContent(
                        tool_use_id=tool_use.id,
                        content=result.output,
                        is_error=not result.success,
                    )
                )

        self.memory.add(Message(role="user", content=results))
