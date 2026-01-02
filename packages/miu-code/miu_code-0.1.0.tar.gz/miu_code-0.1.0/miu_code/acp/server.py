"""ACP server for editor integration."""

import asyncio
import json
import sys
from typing import Any

from miu_code.agent.coding import CodingAgent


class ACPServer:
    """Agent Communication Protocol server for editor integration.

    This server enables editors like Zed and VSCode to communicate
    with the miu agent over stdio using JSON-RPC style messages.
    """

    def __init__(self, model: str = "anthropic:claude-sonnet-4-20250514") -> None:
        """Initialize ACP server.

        Args:
            model: Model specification (provider:model format)
        """
        self.model = model
        self._agent: CodingAgent | None = None

    async def run(self) -> None:
        """Run ACP server on stdio."""
        # Initialize agent
        import os

        self._agent = CodingAgent(
            model=self.model,
            working_dir=os.getcwd(),
        )

        # Set up stdin reader
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        # Process requests
        while True:
            line = await reader.readline()
            if not line:
                break

            try:
                request = json.loads(line.decode())
                response = await self._handle(request)
                self._send_response(response, request.get("id"))
            except json.JSONDecodeError:
                self._send_error("Invalid JSON", None)
            except Exception as e:
                self._send_error(str(e), None)

    async def _handle(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming request.

        Args:
            request: JSON-RPC style request

        Returns:
            Response dict
        """
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return await self._handle_initialize(params)
        elif method == "chat":
            return await self._handle_chat(params)
        elif method == "tools/list":
            return await self._handle_list_tools()
        elif method == "shutdown":
            return {"success": True}
        else:
            return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

    async def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle initialize request."""
        return {
            "capabilities": {
                "chat": True,
                "tools": True,
                "streaming": False,
            },
            "serverInfo": {
                "name": "miu-code",
                "version": "0.1.0",
            },
        }

    async def _handle_chat(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat request."""
        if not self._agent:
            return {"error": {"code": -32603, "message": "Agent not initialized"}}

        message = params.get("message", "")
        if not message:
            return {"error": {"code": -32602, "message": "Missing message parameter"}}

        try:
            response = await self._agent.run(message)
            return {"content": response.get_text()}
        except Exception as e:
            return {"error": {"code": -32603, "message": str(e)}}

    async def _handle_list_tools(self) -> dict[str, Any]:
        """Handle tools/list request."""
        if not self._agent:
            return {"tools": []}

        tools = self._agent.get_tools()
        return {"tools": [t.to_schema() for t in tools]}

    def _send_response(self, result: dict[str, Any], request_id: Any) -> None:
        """Send JSON-RPC response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }
        print(json.dumps(response), flush=True)

    def _send_error(self, message: str, request_id: Any) -> None:
        """Send JSON-RPC error response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": message},
        }
        print(json.dumps(response), flush=True)


async def run_acp_server(model: str = "anthropic:claude-sonnet-4-20250514") -> None:
    """Run the ACP server.

    Args:
        model: Model specification
    """
    server = ACPServer(model=model)
    await server.run()
