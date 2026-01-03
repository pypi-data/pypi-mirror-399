"""Google Gemini provider."""

import json
from typing import Any

from miu_core.models import (
    Message,
    Response,
    TextContent,
    ToolUseContent,
    Usage,
)
from miu_core.providers.base import LLMProvider, ToolSchema

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise ImportError("google-genai package required. Install with: uv add miu-core[google]") from e


class GoogleProvider(LLMProvider):
    """Google Gemini LLM provider."""

    name = "google"

    def __init__(self, model: str = "gemini-2.0-flash") -> None:
        self.model = model
        self._client = genai.Client()

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | list[dict[str, Any]] | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> Response:
        """Send messages to Gemini and get response."""
        contents = self._convert_messages(messages)

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            system_instruction=system,
        )

        if tools:
            config.tools = self._convert_tools(tools)

        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return self._convert_response(response)

    def _convert_messages(self, messages: list[Message]) -> list[types.Content]:
        """Convert internal messages to Gemini format."""
        result: list[types.Content] = []

        for msg in messages:
            if msg.role == "system":
                continue  # System handled via config

            role = "user" if msg.role == "user" else "model"

            if isinstance(msg.content, str):
                result.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))
            else:
                parts: list[types.Part] = []
                for block in msg.content:
                    if isinstance(block, TextContent):
                        parts.append(types.Part(text=block.text))
                    elif isinstance(block, ToolUseContent):
                        parts.append(
                            types.Part(
                                function_call=types.FunctionCall(
                                    name=block.name,
                                    args=block.input,
                                )
                            )
                        )
                    else:
                        # Tool result
                        parts.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name="tool_result",
                                    response={"result": block.content},
                                )
                            )
                        )
                if parts:
                    result.append(types.Content(role=role, parts=parts))

        return result

    def _convert_tools(self, tools: list[ToolSchema] | list[dict[str, Any]]) -> list[types.Tool]:
        """Convert tool schemas to Gemini format."""
        declarations = []
        for tool in tools:
            schema = tool.get("input_schema", {})
            # Clean schema for Gemini
            clean_schema = self._clean_schema(schema)
            declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    parameters=clean_schema,
                )
            )
        return [types.Tool(function_declarations=declarations)]

    def _clean_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Clean JSON schema for Gemini compatibility."""
        # Remove unsupported keys
        clean = {k: v for k, v in schema.items() if k not in ("title", "$defs", "definitions")}
        if "properties" in clean:
            clean["properties"] = {k: self._clean_schema(v) for k, v in clean["properties"].items()}
        return clean

    def _convert_response(self, response: Any) -> Response:
        """Convert Gemini response to internal format."""
        content: list[TextContent | ToolUseContent] = []
        stop_reason = "end_turn"

        if response.candidates:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    content.append(TextContent(text=part.text))
                elif hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    # Safely convert args to dict
                    args: dict[str, Any] = {}
                    if isinstance(fc.args, dict):
                        args = fc.args
                    elif fc.args:
                        try:
                            args = json.loads(str(fc.args))
                        except json.JSONDecodeError:
                            args = {}
                    content.append(
                        ToolUseContent(
                            id=f"call_{fc.name}",
                            name=fc.name,
                            input=args,
                        )
                    )
                    stop_reason = "tool_use"

        usage = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = Usage(
                input_tokens=response.usage_metadata.prompt_token_count or 0,
                output_tokens=response.usage_metadata.candidates_token_count or 0,
            )

        return Response(
            id=f"gemini_{id(response)}",
            content=content,
            stop_reason=stop_reason,
            usage=usage,
        )
