"""MCP protocol types."""

from typing import Any

from pydantic import BaseModel, Field


class MCPMessage(BaseModel):
    """Base MCP message."""

    jsonrpc: str = "2.0"
    id: int | str | None = None


class ClientInfo(BaseModel):
    """MCP client information."""

    name: str
    version: str


class ServerInfo(BaseModel):
    """MCP server information."""

    name: str
    version: str


class MCPCapabilities(BaseModel):
    """MCP capabilities."""

    tools: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    prompts: dict[str, Any] | None = None


class InitializeRequest(MCPMessage):
    """MCP initialize request."""

    method: str = "initialize"
    params: dict[str, Any] = Field(default_factory=dict)

    def __init__(
        self,
        protocol_version: str = "2024-11-05",
        capabilities: dict[str, Any] | None = None,
        client_info: ClientInfo | None = None,
        **kwargs: Any,
    ) -> None:
        params = {
            "protocolVersion": protocol_version,
            "capabilities": capabilities or {},
            "clientInfo": client_info.model_dump()
            if client_info
            else {"name": "miu", "version": "0.1.0"},
        }
        super().__init__(params=params, **kwargs)


class InitializeResponse(BaseModel):
    """MCP initialize response."""

    protocol_version: str = Field(alias="protocolVersion")
    capabilities: MCPCapabilities
    server_info: ServerInfo = Field(alias="serverInfo")


class MCPToolInputSchema(BaseModel):
    """MCP tool input schema."""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str | None = None
    input_schema: MCPToolInputSchema = Field(
        alias="inputSchema", default_factory=MCPToolInputSchema
    )


class ListToolsRequest(MCPMessage):
    """MCP list tools request."""

    method: str = "tools/list"
    params: dict[str, Any] = Field(default_factory=dict)


class ListToolsResponse(BaseModel):
    """MCP list tools response."""

    tools: list[MCPTool]


class CallToolRequest(MCPMessage):
    """MCP call tool request."""

    method: str = "tools/call"
    params: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, name: str, arguments: dict[str, Any] | None = None, **kwargs: Any) -> None:
        params = {"name": name, "arguments": arguments or {}}
        super().__init__(params=params, **kwargs)


class ToolContent(BaseModel):
    """MCP tool response content."""

    type: str = "text"
    text: str = ""


class CallToolResponse(BaseModel):
    """MCP call tool response."""

    content: list[ToolContent]
    is_error: bool = Field(default=False, alias="isError")
