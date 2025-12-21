# Troubleshooting StrictDoc MCP Server

This document provides troubleshooting steps for common issues with the strictdoc-mcp server, particularly when tools aren't appearing in Cursor's function list.

## Common Issues

### Tools Not Appearing in Cursor

If the strictdoc-mcp tools aren't appearing in Cursor's function list, check the following:

#### 1. Verify Server is Running

Check if the server process is running:

```bash
ps aux | grep strictdoc-mcp
```

You should see one or more processes running. Multiple processes might indicate connection issues.

#### 2. Check Cursor MCP Configuration

The Cursor MCP configuration is located at `~/.cursor/mcp.json`. Verify the server is properly configured:

**Correct Configuration:**

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/path/to/venv_strictdoc-mcp/bin/strictdoc-mcp"
    }
  }
}
```

**OR using Python module:**

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/path/to/venv_strictdoc-mcp/bin/python3.12",
      "args": ["-m", "strictdoc_mcp"]
    }
  }
}
```

**Common Configuration Errors:**

1. **Redundant `-m` argument**: If using the `strictdoc-mcp` script, don't add `-m strictdoc_mcp.server` as an argument. The script already runs the server.

   ❌ **Incorrect (Current Configuration):**
   ```json
   {
     "command": "/path/to/strictdoc-mcp",
     "args": ["-m", "strictdoc_mcp.server"]
   }
   ```
   
   This configuration causes the script to try to run `-m strictdoc_mcp.server` as an argument, which may cause the server to fail initialization or not start correctly.

   ✅ **Correct Option 1 (Using script):**
   ```json
   {
     "command": "/path/to/venv_strictdoc-mcp/bin/strictdoc-mcp"
   }
   ```
   
   ✅ **Correct Option 2 (Using Python module):**
   ```json
   {
     "command": "/path/to/venv_strictdoc-mcp/bin/python3.12",
     "args": ["-m", "strictdoc_mcp"]
   }
   ```

2. **Wrong Python path**: Ensure the Python path points to the virtual environment where strictdoc-mcp is installed.

3. **Missing virtual environment**: The server must be installed in a virtual environment with all dependencies.

#### 3. Test Server Directly

Run the diagnostic test to verify the server responds correctly:

```bash
cd /projects/vibe_mcp/strictdoc-mcp
python -m pytest tests/diagnostic/test_mcp_server.py -v
```

This will test:
- Server initialization
- Tool listing
- Tool schema validation

#### 4. Check Server Logs

The server logs to stderr. To see logs:

1. Stop any running server processes
2. Run the server manually to see output:

```bash
/path/to/venv_strictdoc-mcp/bin/strictdoc-mcp
```

Look for:
- Initialization errors
- Tool registration errors
- Protocol errors

#### 5. Verify Tool Registration

The server should register 8 tools:
- `strictdoc_export`
- `strictdoc_import_reqif`
- `strictdoc_import_excel`
- `strictdoc_manage_auto_uid`
- `strictdoc_server`
- `strictdoc_server_stop`
- `strictdoc_version`
- `strictdoc_dump_grammar`

If tools are missing, check:
- Server code in `src/strictdoc_mcp/server.py`
- `@app.list_tools()` decorator is applied
- Tool definitions are correct

#### 6. Restart Cursor

After fixing configuration issues:
1. Stop all strictdoc-mcp processes
2. Restart Cursor
3. Verify tools appear in function list

## Diagnostic Tools

### Running Diagnostic Tests

The diagnostic test suite can verify server functionality:

```bash
# Run all diagnostic tests
python -m pytest tests/diagnostic/ -v

# Run specific test
python -m pytest tests/diagnostic/test_mcp_server.py::test_list_tools -v
```

### Manual Server Test

You can manually test the server using a simple Python script:

```python
import subprocess
import json
import sys

# Start server
proc = subprocess.Popen(
    ["/path/to/venv_strictdoc-mcp/bin/strictdoc-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# Send initialize request
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"},
    },
}
proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
print("Initialize response:", json.dumps(response, indent=2))

# Send tools/list request
tools_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
}
proc.stdin.write(json.dumps(tools_request) + "\n")
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
print("\nTools list response:", json.dumps(response, indent=2))

proc.terminate()
```

## Server Implementation Details

### Tool Registration

Tools are registered using the `@app.list_tools()` decorator in `src/strictdoc_mcp/server.py`. The decorator automatically:
- Registers the handler with the MCP server
- Adds tool capabilities to server initialization
- Makes tools available via the `tools/list` request

### Server Initialization

The server uses `app.create_initialization_options()` which:
- Sets server name and version
- Declares capabilities (including tools capability)
- Configures protocol version

### Capabilities

The server automatically declares tool capabilities if `ListToolsRequest` is in the request handlers (which happens when `@app.list_tools()` is used).

## Getting Help

If issues persist:

1. Check server logs for errors
2. Run diagnostic tests
3. Verify MCP library version compatibility
4. Check Cursor MCP server logs (if available)
5. Review server implementation in `src/strictdoc_mcp/server.py`

## Known Issues

### Multiple Server Processes

If you see multiple server processes running, it might indicate:
- Cursor is restarting the server due to errors
- Multiple Cursor instances are running
- Orphaned processes from previous sessions

**Solution**: Kill all processes and restart Cursor:
```bash
pkill -f strictdoc-mcp
```

### Tools Not Updating

If you modify tool definitions but changes don't appear:
1. Restart the server (kill processes)
2. Restart Cursor
3. Verify changes in `src/strictdoc_mcp/server.py`

