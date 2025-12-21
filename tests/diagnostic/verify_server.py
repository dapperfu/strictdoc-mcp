"""Verification script for MCP server capabilities and initialization.

This script verifies that the server properly initializes and declares
tool capabilities.

Run this script to diagnose server initialization issues:
    python -m tests.diagnostic.verify_server
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from strictdoc_mcp.server import app


def verify_tool_registration() -> bool:
    """Verify that tools are properly registered.

    Returns
    -------
    bool
        True if tools are registered correctly.
    """
    print("Verifying tool registration...")

    # Check if list_tools handler is registered
    if not hasattr(app, "request_handlers"):
        print("❌ Server doesn't have request_handlers attribute")
        return False

    # Import types to check handler registration
    try:
        from mcp.types import ListToolsRequest

        if ListToolsRequest not in app.request_handlers:
            print("❌ ListToolsRequest handler not registered")
            return False
        print("✓ ListToolsRequest handler is registered")
    except ImportError as e:
        print(f"⚠️  Could not import MCP types: {e}")
        return False

    return True


def verify_initialization_options() -> bool:
    """Verify that initialization options are correctly configured.

    Returns
    -------
    bool
        True if initialization options are valid.
    """
    print("\nVerifying initialization options...")

    try:
        init_options = app.create_initialization_options()
        print(f"✓ Server name: {init_options.server_name}")
        print(f"✓ Server version: {init_options.server_version}")

        # Check capabilities
        capabilities = init_options.capabilities
        print(f"✓ Capabilities: {capabilities.model_dump_json(indent=2)}")

        # Verify tools capability is declared
        if hasattr(capabilities, "tools") and capabilities.tools:
            print("✓ Tools capability is declared")
            return True
        else:
            print("❌ Tools capability is NOT declared")
            print("  This means tools won't be available to clients!")
            return False

    except Exception as e:
        print(f"❌ Error creating initialization options: {e}")
        import traceback

        traceback.print_exc()
        return False


async def verify_list_tools() -> bool:
    """Verify that list_tools returns the expected tools.

    Returns
    -------
    bool
        True if tools are returned correctly.
    """
    print("\nVerifying list_tools() function...")

    try:
        # Import the list_tools function
        from strictdoc_mcp.server import list_tools

        tools = await list_tools()

        if not isinstance(tools, list):
            print(f"❌ list_tools() returned {type(tools)}, expected list")
            return False

        print(f"✓ list_tools() returned {len(tools)} tools")

        # Verify expected tools
        expected_tools = {
            "strictdoc_export",
            "strictdoc_import_reqif",
            "strictdoc_import_excel",
            "strictdoc_manage_auto_uid",
            "strictdoc_server",
            "strictdoc_server_stop",
            "strictdoc_version",
            "strictdoc_dump_grammar",
        }

        tool_names = {tool.name for tool in tools}
        missing_tools = expected_tools - tool_names
        extra_tools = tool_names - expected_tools

        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False

        if extra_tools:
            print(f"⚠️  Unexpected tools: {extra_tools}")

        print(f"✓ All expected tools present: {', '.join(sorted(tool_names))}")

        # Verify tool schemas
        schema_errors = []
        for tool in tools:
            if not hasattr(tool, "inputSchema"):
                schema_errors.append(f"Tool '{tool.name}' missing inputSchema")
                continue

            schema = tool.inputSchema
            if not isinstance(schema, dict):
                schema_errors.append(f"Tool '{tool.name}' inputSchema is not a dict")
                continue

            if "type" not in schema:
                schema_errors.append(f"Tool '{tool.name}' inputSchema missing 'type'")

        if schema_errors:
            print("❌ Schema validation errors:")
            for error in schema_errors:
                print(f"  - {error}")
            return False

        print("✓ All tool schemas are valid")

        return True

    except Exception as e:
        print(f"❌ Error calling list_tools(): {e}")
        import traceback

        traceback.print_exc()
        return False


def check_cursor_config() -> None:
    """Check Cursor MCP configuration for common issues."""
    print("\nChecking Cursor MCP configuration...")

    config_path = Path.home() / ".cursor" / "mcp.json"
    if not config_path.exists():
        print(f"⚠️  Cursor config not found at {config_path}")
        return

    try:
        with open(config_path) as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        if "strictdoc-mcp" not in servers:
            print("❌ strictdoc-mcp not found in Cursor config")
            return

        server_config = servers["strictdoc-mcp"]
        command = server_config.get("command", "")
        args = server_config.get("args", [])

        print(f"✓ Command: {command}")
        if args:
            print(f"✓ Args: {args}")

        # Check for common configuration errors
        if command.endswith("strictdoc-mcp") and "-m" in args:
            print("\n⚠️  POTENTIAL ISSUE DETECTED:")
            print("  The command uses 'strictdoc-mcp' script with '-m' argument.")
            print("  The script already runs the server, so '-m strictdoc_mcp.server' is redundant.")
            print("  This might cause the server to fail or not start correctly.")
            print("\n  Recommended fix:")
            print('  Remove the "args" field or use python -m strictdoc_mcp directly')

        # Check if command path exists
        if command and not command.startswith("python") and not command.startswith("/usr"):
            cmd_path = Path(command)
            if not cmd_path.exists():
                print(f"\n❌ Command path does not exist: {command}")
            else:
                print(f"✓ Command path exists: {command}")

    except Exception as e:
        print(f"⚠️  Error reading Cursor config: {e}")


async def main() -> None:
    """Run all verification checks."""
    print("=" * 60)
    print("StrictDoc MCP Server Verification")
    print("=" * 60)

    all_passed = True

    # Check tool registration
    if not verify_tool_registration():
        all_passed = False

    # Check initialization options
    if not verify_initialization_options():
        all_passed = False

    # Check list_tools function
    if not await verify_list_tools():
        all_passed = False

    # Check Cursor config
    check_cursor_config()

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All server checks passed!")
        print("\nIf tools still don't appear in Cursor:")
        print("  1. Restart Cursor")
        print("  2. Check Cursor MCP server logs")
        print("  3. Verify server process is running: ps aux | grep strictdoc-mcp")
    else:
        print("❌ Some checks failed. Review errors above.")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())

