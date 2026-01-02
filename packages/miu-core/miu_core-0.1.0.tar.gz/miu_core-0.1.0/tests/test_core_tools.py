"""Tests for tool framework."""

import pytest
from pydantic import BaseModel

from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult


class EchoInput(BaseModel):
    message: str


class EchoTool(Tool):
    name = "echo"
    description = "Echoes the input message"

    def get_input_schema(self) -> type[BaseModel]:
        return EchoInput

    async def execute(self, ctx: ToolContext, message: str, **kwargs: object) -> ToolResult:
        return ToolResult(output=f"Echo: {message}")


class FailingTool(Tool):
    name = "failing"
    description = "Always fails"

    def get_input_schema(self) -> type[BaseModel]:
        return EchoInput

    async def execute(self, ctx: ToolContext, **kwargs: object) -> ToolResult:
        raise ValueError("Intentional failure")


class TestToolResult:
    def test_success_result(self) -> None:
        result = ToolResult(output="Success!")
        assert result.success is True
        assert result.error is None

    def test_error_result(self) -> None:
        result = ToolResult(output="Failed", success=False, error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"


class TestToolContext:
    def test_defaults(self) -> None:
        ctx = ToolContext()
        assert ctx.working_dir == "."
        assert ctx.session_id == "default"

    def test_custom_values(self) -> None:
        ctx = ToolContext(working_dir="/tmp", session_id="session_123")
        assert ctx.working_dir == "/tmp"
        assert ctx.session_id == "session_123"


class TestTool:
    def test_to_schema(self) -> None:
        tool = EchoTool()
        schema = tool.to_schema()
        assert schema["name"] == "echo"
        assert schema["description"] == "Echoes the input message"
        assert "message" in schema["input_schema"]["properties"]

    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        tool = EchoTool()
        ctx = ToolContext()
        result = await tool.execute(ctx, message="Hello")
        assert result.output == "Echo: Hello"
        assert result.success is True


class TestToolRegistry:
    def test_register_and_get(self) -> None:
        registry = ToolRegistry()
        tool = EchoTool()
        registry.register(tool)
        assert registry.get("echo") is tool

    def test_get_unknown_tool(self) -> None:
        registry = ToolRegistry()
        assert registry.get("unknown") is None

    def test_get_schemas(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())
        schemas = registry.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "echo"

    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())
        ctx = ToolContext()
        result = await registry.execute("echo", ctx, message="Test")
        assert result.output == "Echo: Test"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self) -> None:
        registry = ToolRegistry()
        ctx = ToolContext()
        result = await registry.execute("unknown", ctx)
        assert result.success is False
        assert "not found" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_handles_exception(self) -> None:
        registry = ToolRegistry()
        registry.register(FailingTool())
        ctx = ToolContext()
        result = await registry.execute("failing", ctx, message="test")
        assert result.success is False
        assert "Intentional failure" in result.error or ""

    def test_len(self) -> None:
        registry = ToolRegistry()
        assert len(registry) == 0
        registry.register(EchoTool())
        assert len(registry) == 1

    def test_iter(self) -> None:
        registry = ToolRegistry()
        registry.register(EchoTool())
        tools = list(registry)
        assert len(tools) == 1
        assert tools[0].name == "echo"
