"""ReAct (Reasoning + Acting) agent implementation."""

from collections.abc import AsyncIterator
from typing import Any

from miu_core.agents.base import Agent, AgentConfig
from miu_core.memory import Memory
from miu_core.models import (
    Message,
    MessageStopEvent,
    Response,
    StreamEvent,
    TextContent,
    TextDeltaEvent,
    ToolExecutingEvent,
    ToolResultContent,
    ToolResultEvent,
    ToolUseContent,
    ToolUseStartEvent,
)
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

    async def run_stream(self, query: str) -> AsyncIterator[StreamEvent]:
        """Execute ReAct loop with streaming responses."""
        self.memory.add(Message(role="user", content=query))
        self.memory.truncate(self.config.max_context_tokens)

        for _ in range(self.config.max_iterations):
            # Collect full response while streaming text
            collected_text = ""
            tool_uses: list[dict[str, Any]] = []
            current_tool: dict[str, Any] | None = None
            stop_reason = "end_turn"

            async for event in self.provider.stream(
                messages=self.memory.get_messages(),
                tools=self.tools.get_schemas() if len(self.tools) > 0 else None,
                system=self.config.system_prompt,
            ):
                if isinstance(event, TextDeltaEvent):
                    collected_text += event.text
                    yield event
                elif isinstance(event, ToolUseStartEvent):
                    current_tool = {"id": event.id, "name": event.name, "input": {}}
                    yield event
                elif isinstance(event, MessageStopEvent):
                    stop_reason = event.stop_reason
                    if current_tool:
                        tool_uses.append(current_tool)

            # Build response content for memory
            content: list[TextContent | ToolUseContent] = []
            if collected_text:
                content.append(TextContent(text=collected_text))
            for tu in tool_uses:
                content.append(ToolUseContent(id=tu["id"], name=tu["name"], input=tu["input"]))

            if content:
                self.memory.add(Message(role="assistant", content=content))

            if stop_reason == "end_turn":
                yield MessageStopEvent(stop_reason="end_turn")
                return

            if stop_reason == "tool_use" and tool_uses:
                # Execute tools and yield events
                async for tool_event in self._execute_tools_stream(tool_uses):
                    yield tool_event

        yield MessageStopEvent(stop_reason="max_iterations")

    async def _execute_tools_stream(
        self, tool_uses: list[dict[str, Any]]
    ) -> AsyncIterator[StreamEvent]:
        """Execute tools and yield streaming events."""
        ctx = ToolContext(working_dir=self.working_dir)
        results: list[ToolResultContent] = []

        for tool_use in tool_uses:
            yield ToolExecutingEvent(tool_name=tool_use["name"], tool_id=tool_use["id"])

            result = await self.tools.execute(tool_use["name"], ctx, **tool_use.get("input", {}))

            yield ToolResultEvent(
                tool_name=tool_use["name"],
                tool_id=tool_use["id"],
                success=result.success,
                output=result.output[:200] if result.output else "",
            )

            results.append(
                ToolResultContent(
                    tool_use_id=tool_use["id"],
                    content=result.output,
                    is_error=not result.success,
                )
            )

        self.memory.add(Message(role="user", content=results))
