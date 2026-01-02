"""Tool registry for managing tools."""

from typing import Any

from miu_core.tools.base import Tool, ToolContext, ToolResult


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get tool by name."""
        return self._tools.get(name)

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas for LLM."""
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Execute a tool by name."""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                output=f"Tool not found: {name}",
                success=False,
                error=f"Unknown tool: {name}",
            )
        try:
            return await tool.execute(ctx, **kwargs)
        except Exception as e:
            return ToolResult(
                output=str(e),
                success=False,
                error=str(e),
            )

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self) -> Any:
        return iter(self._tools.values())
