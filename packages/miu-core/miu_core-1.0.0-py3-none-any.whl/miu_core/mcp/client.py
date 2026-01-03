"""MCP client implementation."""

from typing import Any

from miu_core.mcp.protocol import (
    CallToolRequest,
    CallToolResponse,
    InitializeRequest,
    InitializeResponse,
    ListToolsRequest,
    ListToolsResponse,
    MCPTool,
)
from miu_core.mcp.stdio import StdioTransport


class MCPClient:
    """MCP client for connecting to external tool servers."""

    def __init__(self, server_command: list[str]) -> None:
        """Initialize MCP client.

        Args:
            server_command: Command to start the MCP server
        """
        self.transport = StdioTransport(server_command)
        self._tools: list[MCPTool] = []
        self._server_info: dict[str, Any] = {}
        self._connected = False

    async def connect(self) -> None:
        """Initialize connection with MCP server."""
        await self.transport.start()

        # Send initialize request
        init_request = InitializeRequest()
        response = await self.transport.send(init_request.model_dump(by_alias=True))

        if "result" in response:
            init_response = InitializeResponse.model_validate(response["result"])
            self._server_info = init_response.server_info.model_dump()

        # List available tools
        list_request = ListToolsRequest()
        response = await self.transport.send(list_request.model_dump(by_alias=True))

        if "result" in response:
            list_response = ListToolsResponse.model_validate(response["result"])
            self._tools = list_response.tools

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        await self.transport.stop()
        self._connected = False

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        """Call a tool on the MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result text
        """
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")

        request = CallToolRequest(name=name, arguments=arguments or {})
        response = await self.transport.send(request.model_dump(by_alias=True))

        if "error" in response:
            error = response["error"]
            return f"Error: {error.get('message', 'Unknown error')}"

        if "result" in response:
            result = CallToolResponse.model_validate(response["result"])
            if result.content:
                return result.content[0].text
            return ""

        return ""

    def get_tools(self) -> list[dict[str, Any]]:
        """Get available tools as miu schemas.

        Returns:
            List of tool schemas compatible with miu agent
        """
        return [self._convert_tool(tool) for tool in self._tools]

    def _convert_tool(self, mcp_tool: MCPTool) -> dict[str, Any]:
        """Convert MCP tool to miu tool schema.

        Args:
            mcp_tool: MCP tool definition

        Returns:
            Miu-compatible tool schema
        """
        return {
            "name": f"mcp_{mcp_tool.name}",
            "description": mcp_tool.description or f"MCP tool: {mcp_tool.name}",
            "input_schema": mcp_tool.input_schema.model_dump(),
        }

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @property
    def server_info(self) -> dict[str, Any]:
        """Get server information."""
        return self._server_info

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.disconnect()
