# Diagnostic Findings: MCP Tool Visibility Issue

## Summary

Diagnostic tests were run to identify why strictdoc-mcp tools aren't appearing in Cursor's function list. The server implementation is correct, but a configuration issue was identified.

## Server Status: ✅ WORKING

All server-side checks passed:

- ✅ Tool registration: All 8 tools are properly registered
- ✅ Tool capabilities: Server correctly declares tools capability
- ✅ Tool schemas: All tool input schemas are valid JSON Schema
- ✅ Server initialization: Initialization options are correctly configured
- ✅ Protocol compliance: Server follows MCP protocol correctly

## Identified Issue: ⚠️ CONFIGURATION PROBLEM

### Problem

The Cursor MCP configuration file (`~/.cursor/mcp.json`) contains a redundant argument that may prevent proper server initialization:

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/projects/vibe_mcp/strictdoc-mcp/venv_strictdoc-mcp/bin/strictdoc-mcp",
      "args": ["-m", "strictdoc_mcp.server"]
    }
  }
}
```

### Why This Is a Problem

The `strictdoc-mcp` command is an entry point script that already runs the server. Adding `-m strictdoc_mcp.server` as an argument is redundant and may cause:

1. The script to misinterpret the arguments
2. Server initialization to fail
3. Cursor to not properly connect to the server

### Solution

**Option 1: Remove the args (Recommended)**

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/projects/vibe_mcp/strictdoc-mcp/venv_strictdoc-mcp/bin/strictdoc-mcp"
    }
  }
}
```

**Option 2: Use Python module directly**

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/projects/vibe_mcp/strictdoc-mcp/venv_strictdoc-mcp/bin/python3.12",
      "args": ["-m", "strictdoc_mcp"]
    }
  }
}
```

## Verification Results

### Tool Registration
- **Status**: ✅ PASS
- **Details**: All 8 tools are registered:
  - strictdoc_export
  - strictdoc_import_reqif
  - strictdoc_import_excel
  - strictdoc_manage_auto_uid
  - strictdoc_server
  - strictdoc_server_stop
  - strictdoc_version
  - strictdoc_dump_grammar

### Server Capabilities
- **Status**: ✅ PASS
- **Details**: Server correctly declares tools capability:
  ```json
  {
    "tools": {
      "listChanged": false
    }
  }
  ```

### Tool Schemas
- **Status**: ✅ PASS
- **Details**: All tool input schemas are valid JSON Schema with proper structure

### Server Initialization
- **Status**: ✅ PASS
- **Details**: 
  - Server name: strictdoc-mcp
  - Server version: 1.25.0
  - Initialization options correctly configured

## Multiple Server Processes

**Observation**: 4 server processes are running (PIDs: 421844-421847)

**Possible Causes**:
1. Cursor restarting the server due to initialization failures
2. Multiple Cursor instances
3. Orphaned processes from previous sessions

**Recommendation**: After fixing the configuration, kill all processes and restart Cursor:
```bash
pkill -f strictdoc-mcp
```

## Next Steps

1. **Fix Cursor Configuration**: Update `~/.cursor/mcp.json` to remove the redundant `-m` argument
2. **Restart Cursor**: Close and restart Cursor to reload MCP configuration
3. **Verify Tools Appear**: Check that all 8 tools appear in Cursor's function list
4. **Monitor Server**: Watch for any errors in server logs after restart

## Diagnostic Tools Created

1. **`tests/diagnostic/test_mcp_server.py`**: Comprehensive MCP protocol tests
   - Tests server initialization
   - Tests tool listing
   - Validates tool schemas

2. **`tests/diagnostic/verify_server.py`**: Quick verification script
   - Checks tool registration
   - Verifies server capabilities
   - Validates Cursor configuration
   - Can be run standalone: `python tests/diagnostic/verify_server.py`

3. **`docs/TROUBLESHOOTING.md`**: Complete troubleshooting guide
   - Common issues and solutions
   - Configuration examples
   - Diagnostic procedures

## Conclusion

The strictdoc-mcp server implementation is correct and all tools are properly registered. The issue is in the Cursor MCP configuration file, which contains a redundant argument that may prevent proper server initialization. Fixing the configuration should resolve the tool visibility issue.

