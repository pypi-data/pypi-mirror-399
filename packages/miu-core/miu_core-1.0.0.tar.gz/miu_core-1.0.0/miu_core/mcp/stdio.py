"""MCP stdio transport."""

import asyncio
import json
from typing import Any


class StdioTransport:
    """Transport for MCP communication over stdio."""

    def __init__(self, command: list[str]) -> None:
        """Initialize transport with server command.

        Args:
            command: Command to start the MCP server (e.g., ["npx", "@modelcontextprotocol/server-filesystem"])
        """
        self.command = command
        self._process: asyncio.subprocess.Process | None = None
        self._request_id = 0

    async def start(self) -> None:
        """Start the MCP server process."""
        self._process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def stop(self) -> None:
        """Stop the MCP server process."""
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None

    async def send(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send a message and receive response.

        Args:
            message: Message dict to send

        Returns:
            Response dict from server
        """
        if not self._process or not self._process.stdin or not self._process.stdout:
            raise RuntimeError("Transport not started")

        # Assign request ID if not present
        if "id" not in message or message["id"] is None:
            self._request_id += 1
            message["id"] = self._request_id

        # Send message
        data = json.dumps(message) + "\n"
        self._process.stdin.write(data.encode())
        await self._process.stdin.drain()

        # Read response
        response_line = await self._process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from MCP server")

        return json.loads(response_line.decode())  # type: ignore[no-any-return]

    @property
    def is_running(self) -> bool:
        """Check if transport is running."""
        return self._process is not None and self._process.returncode is None
