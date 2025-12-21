"""Diagnostic test for MCP server tool visibility.

This module tests the MCP server directly via stdio to verify that tools
are properly exposed and can be listed by clients.

Tests:
- Server initialization handshake
- Tool listing functionality
- Tool schema validation
- Protocol compliance
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


class MCPClient:
    """Simple MCP client for testing server via stdio.

    This client implements basic JSON-RPC 2.0 protocol over stdio to test
    the MCP server's tool listing functionality.

    Parameters
    ----------
    server_command : List[str]
        Command to start the MCP server.
    timeout : float
        Timeout in seconds for reading responses.

    Attributes
    ----------
    process : Optional[subprocess.Popen]
        Server subprocess instance.
    request_id : int
        Current request ID counter.
    """

    def __init__(self, server_command: List[str], timeout: float = 5.0) -> None:
        """Initialize MCP client.

        Parameters
        ----------
        server_command : List[str]
            Command to start the MCP server.
        timeout : float
            Timeout in seconds for reading responses.
        """
        self.server_command = server_command
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 1

    def start(self) -> None:
        """Start the MCP server subprocess."""
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )

    def stop(self) -> None:
        """Stop the MCP server subprocess."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server.

        Parameters
        ----------
        method : str
            Method name.
        params : Optional[Dict[str, Any]]
            Method parameters.

        Returns
        -------
        Dict[str, Any]
            Response from server.

        Raises
        ------
        RuntimeError
            If server is not running or communication fails.
        """
        if not self.process:
            raise RuntimeError("Server not started")

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        self.request_id += 1

        # Send request
        request_json = json.dumps(request) + "\n"
        if self.process.stdin:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()

        # Read response
        if not self.process.stdout:
            raise RuntimeError("No stdout available")

        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        try:
            response = json.loads(response_line.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {e}") from e

        return response

    def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a JSON-RPC notification to the server.

        Parameters
        ----------
        method : str
            Method name.
        params : Optional[Dict[str, Any]]
            Method parameters.

        Raises
        ------
        RuntimeError
            If server is not running.
        """
        if not self.process:
            raise RuntimeError("Server not started")

        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            notification["params"] = params

        notification_json = json.dumps(notification) + "\n"
        if self.process.stdin:
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()

    def read_stderr(self) -> str:
        """Read available stderr output from server.

        Returns
        -------
        str
            Stderr output.
        """
        if not self.process or not self.process.stderr:
            return ""
        # Non-blocking read of available stderr
        import select

        if select.select([self.process.stderr], [], [], 0.1)[0]:
            return self.process.stderr.read()
        return ""


def get_server_command() -> List[str]:
    """Get the command to start the MCP server.

    Returns
    -------
    List[str]
        Command to start the server.
    """
    # Try to use the installed script first
    venv_python = Path(__file__).parent.parent.parent / "venv_strictdoc-mcp" / "bin" / "python3.12"
    if venv_python.exists():
        return [str(venv_python), "-m", "strictdoc_mcp"]
    # Fallback to system python
    return [sys.executable, "-m", "strictdoc_mcp"]


@pytest.mark.asyncio
async def test_server_initialization() -> None:
    """Test that the server responds to initialization requests.

    This test verifies the MCP protocol handshake works correctly.
    """
    client = MCPClient(get_server_command())
    try:
        client.start()
        time.sleep(0.5)  # Give server time to start

        # Send initialize request
        init_response = client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0",
                },
            },
        )

        # Verify response structure
        assert "result" in init_response, f"Expected 'result' in response: {init_response}"
        assert "error" not in init_response, f"Initialization error: {init_response.get('error')}"

        result = init_response["result"]
        assert "protocolVersion" in result, "Missing protocolVersion in init result"
        assert "capabilities" in result, "Missing capabilities in init result"
        assert "serverInfo" in result, "Missing serverInfo in init result"

        # Send initialized notification
        client.send_notification("notifications/initialized")

        # Check for any errors in stderr
        stderr_output = client.read_stderr()
        if "error" in stderr_output.lower() or "exception" in stderr_output.lower():
            print(f"Server stderr: {stderr_output}", file=sys.stderr)

    finally:
        client.stop()


@pytest.mark.asyncio
async def test_list_tools() -> None:
    """Test that the server lists all available tools.

    This test verifies that all 8 strictdoc-mcp tools are properly
    registered and can be listed.
    """
    client = MCPClient(get_server_command())
    try:
        client.start()
        time.sleep(0.5)  # Give server time to start

        # Initialize
        init_response = client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0",
                },
            },
        )
        assert "error" not in init_response, f"Initialization failed: {init_response.get('error')}"

        client.send_notification("notifications/initialized")
        time.sleep(0.2)  # Allow notification to be processed

        # Request tools list
        tools_response = client.send_request("tools/list")

        # Verify response
        assert "result" in tools_response, f"Expected 'result' in response: {tools_response}"
        assert "error" not in tools_response, f"Tools list error: {tools_response.get('error')}"

        result = tools_response["result"]
        assert "tools" in result, "Missing 'tools' in result"

        tools = result["tools"]
        assert isinstance(tools, list), "Tools should be a list"

        # Verify expected tools are present
        expected_tool_names = {
            "strictdoc_export",
            "strictdoc_import_reqif",
            "strictdoc_import_excel",
            "strictdoc_manage_auto_uid",
            "strictdoc_server",
            "strictdoc_server_stop",
            "strictdoc_version",
            "strictdoc_dump_grammar",
        }

        tool_names = {tool["name"] for tool in tools if "name" in tool}
        assert tool_names == expected_tool_names, (
            f"Expected tools {expected_tool_names}, got {tool_names}"
        )

        print(f"\n✓ Found {len(tools)} tools: {', '.join(sorted(tool_names))}")

    finally:
        client.stop()


@pytest.mark.asyncio
async def test_tool_schemas() -> None:
    """Test that tool schemas are valid JSON Schema.

    This test verifies that each tool has a properly formatted inputSchema.
    """
    client = MCPClient(get_server_command())
    try:
        client.start()
        time.sleep(0.5)

        # Initialize
        client.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        )
        client.send_notification("notifications/initialized")
        time.sleep(0.2)

        # Get tools
        tools_response = client.send_request("tools/list")
        assert "result" in tools_response
        tools = tools_response["result"]["tools"]

        # Validate each tool schema
        schema_errors: List[str] = []

        for tool in tools:
            tool_name = tool.get("name", "unknown")
            if "inputSchema" not in tool:
                schema_errors.append(f"Tool '{tool_name}' missing inputSchema")
                continue

            schema = tool["inputSchema"]
            if not isinstance(schema, dict):
                schema_errors.append(f"Tool '{tool_name}' inputSchema is not a dict")
                continue

            # Basic JSON Schema validation
            if "type" not in schema:
                schema_errors.append(f"Tool '{tool_name}' inputSchema missing 'type'")

            # Check required fields for object schemas
            if schema.get("type") == "object":
                if "properties" not in schema:
                    schema_errors.append(f"Tool '{tool_name}' object schema missing 'properties'")

        assert not schema_errors, f"Schema validation errors:\n" + "\n".join(schema_errors)

        print(f"\n✓ All {len(tools)} tool schemas are valid")

    finally:
        client.stop()


if __name__ == "__main__":
    """Run diagnostic tests directly."""
    pytest.main([__file__, "-v", "-s"])

