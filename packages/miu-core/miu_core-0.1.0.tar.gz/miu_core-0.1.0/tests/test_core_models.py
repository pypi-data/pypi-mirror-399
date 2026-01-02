"""Tests for message models."""

from miu_core.models import (
    Message,
    Response,
    TextContent,
    ToolResultContent,
    ToolUseContent,
    Usage,
)


class TestTextContent:
    def test_create(self) -> None:
        content = TextContent(text="Hello")
        assert content.type == "text"
        assert content.text == "Hello"


class TestToolUseContent:
    def test_create(self) -> None:
        content = ToolUseContent(
            id="tool_123",
            name="read_file",
            input={"path": "/tmp/test.txt"},
        )
        assert content.type == "tool_use"
        assert content.id == "tool_123"
        assert content.name == "read_file"
        assert content.input == {"path": "/tmp/test.txt"}


class TestToolResultContent:
    def test_create(self) -> None:
        content = ToolResultContent(
            tool_use_id="tool_123",
            content="File contents here",
        )
        assert content.type == "tool_result"
        assert content.tool_use_id == "tool_123"
        assert content.is_error is False

    def test_error_result(self) -> None:
        content = ToolResultContent(
            tool_use_id="tool_123",
            content="File not found",
            is_error=True,
        )
        assert content.is_error is True


class TestMessage:
    def test_string_content(self) -> None:
        msg = Message(role="user", content="Hello")
        assert msg.get_text() == "Hello"

    def test_list_content(self) -> None:
        msg = Message(
            role="assistant",
            content=[
                TextContent(text="Line 1"),
                TextContent(text="Line 2"),
            ],
        )
        assert msg.get_text() == "Line 1\nLine 2"

    def test_mixed_content_extracts_text(self) -> None:
        msg = Message(
            role="assistant",
            content=[
                TextContent(text="Hello"),
                ToolUseContent(id="1", name="test", input={}),
            ],
        )
        assert msg.get_text() == "Hello"


class TestResponse:
    def test_get_text(self) -> None:
        response = Response(
            id="resp_123",
            content=[TextContent(text="Hello"), TextContent(text="World")],
        )
        assert response.get_text() == "Hello\nWorld"

    def test_get_tool_uses(self) -> None:
        tool_use = ToolUseContent(id="1", name="test", input={})
        response = Response(
            id="resp_123",
            content=[TextContent(text="Hello"), tool_use],
        )
        tool_uses = response.get_tool_uses()
        assert len(tool_uses) == 1
        assert tool_uses[0].name == "test"

    def test_usage(self) -> None:
        response = Response(
            id="resp_123",
            content=[],
            usage=Usage(input_tokens=100, output_tokens=50),
        )
        assert response.usage is not None
        assert response.usage.input_tokens == 100
        assert response.usage.output_tokens == 50
