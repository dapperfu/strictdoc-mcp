"""Main MCP server for StrictDoc.

This module implements the Model Context Protocol server that exposes
all StrictDoc tooling features as MCP tools.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from .config import get_config
from .tools import export, import_tools, manage, server as server_tool, utils

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


async def list_tools() -> List[Tool]:
    """List all available tools.

    Returns
    -------
    List[Tool]
        List of available MCP tools.
    """
    return [
        Tool(
            name="strictdoc_export",
            description="Export StrictDoc documents to various formats (HTML, PDF, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "One or more folders with *.sdoc files",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output folder",
                    },
                    "formats": {
                        "type": "string",
                        "description": "Export formats (comma-separated)",
                    },
                    "project_title": {
                        "type": "string",
                        "description": "Project title",
                    },
                    "fields": {
                        "type": "string",
                        "description": "Export fields (only for Excel export)",
                    },
                    "generate_bundle_document": {
                        "type": "boolean",
                        "description": "Generate bundle document",
                        "default": False,
                    },
                    "no_parallelization": {
                        "type": "boolean",
                        "description": "Disable parallelization",
                        "default": False,
                    },
                    "enable_mathjax": {
                        "type": "boolean",
                        "description": "Enable MathJax support (HTML export only)",
                        "default": False,
                    },
                    "included_documents": {
                        "type": "boolean",
                        "description": "Export included documents",
                        "default": False,
                    },
                    "reqif_profile": {
                        "type": "string",
                        "description": "ReqIF profile",
                    },
                    "reqif_multiline_is_xhtml": {
                        "type": "boolean",
                        "description": "Export multiline fields as XHTML in ReqIF",
                        "default": False,
                    },
                    "reqif_enable_mid": {
                        "type": "boolean",
                        "description": "Map MID field to ReqIF SPEC-OBJECT IDENTIFIER",
                        "default": False,
                    },
                    "filter_nodes": {
                        "type": "string",
                        "description": "Filter which requirements will be exported",
                    },
                    "view": {
                        "type": "string",
                        "description": "Choose which view will be exported",
                    },
                    "generate_diff_git": {
                        "type": "string",
                        "description": "Generate diff for Git revisions (e.g., 'HEAD^..HEAD')",
                    },
                    "generate_diff_dirs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Generate diff for directory pair [old_path, new_path]",
                    },
                    "chromedriver": {
                        "type": "string",
                        "description": "Path to chromedriver for html2pdf",
                    },
                    "config": {
                        "type": "string",
                        "description": "Path to StrictDoc TOML config file",
                    },
                },
                "required": ["input_paths"],
            },
        ),
        Tool(
            name="strictdoc_import_reqif",
            description="Import ReqIF document to StrictDoc format",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "string",
                        "description": "ReqIF import/export profile (e.g., 'p01_sdoc')",
                    },
                    "input_path": {
                        "type": "string",
                        "description": "Path to input ReqIF file",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to output SDoc file",
                    },
                    "reqif_enable_mid": {
                        "type": "boolean",
                        "description": "Map MID field to ReqIF SPEC-OBJECT IDENTIFIER",
                        "default": False,
                    },
                    "reqif_import_markup": {
                        "type": "string",
                        "description": "Markup option for imported SDoc documents (RST or HTML)",
                    },
                },
                "required": ["profile", "input_path", "output_path"],
            },
        ),
        Tool(
            name="strictdoc_import_excel",
            description="Import Excel document to StrictDoc format",
            inputSchema={
                "type": "object",
                "properties": {
                    "parser": {
                        "type": "string",
                        "description": "Excel parser to use (e.g., 'basic')",
                    },
                    "input_path": {
                        "type": "string",
                        "description": "Path to input Excel file",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to output SDoc file",
                    },
                },
                "required": ["parser", "input_path", "output_path"],
            },
        ),
        Tool(
            name="strictdoc_manage_auto_uid",
            description="Generate missing requirement UIDs automatically",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "One or more folders with *.sdoc files",
                    },
                },
                "required": ["input_paths"],
            },
        ),
        Tool(
            name="strictdoc_server",
            description="Run StrictDoc web server (runs as background process)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "One or more folders with *.sdoc files",
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port number for the server",
                    },
                    "host": {
                        "type": "string",
                        "description": "Host address for the server",
                    },
                },
                "required": ["input_paths"],
            },
        ),
        Tool(
            name="strictdoc_server_stop",
            description="Stop a running StrictDoc server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_key": {
                        "type": "string",
                        "description": "Server key to stop (optional, stops all if not provided)",
                    },
                },
            },
        ),
        Tool(
            name="strictdoc_version",
            description="Get StrictDoc version",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="strictdoc_dump_grammar",
            description="Dump StrictDoc grammar to a .tx file",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Path where the grammar file should be written",
                    },
                },
                "required": ["output_path"],
            },
        ),
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls.

    Parameters
    ----------
    name : str
        Name of the tool to call.
    arguments : Dict[str, Any]
        Tool arguments.

    Returns
    -------
    List[TextContent]
        Tool execution results.
    """
    try:
        result: Dict[str, Any] = {}

        if name == "strictdoc_export":
            result = await export.export_documents(
                input_paths=arguments.get("input_paths", []),
                output_dir=arguments.get("output_dir"),
                formats=arguments.get("formats"),
                project_title=arguments.get("project_title"),
                fields=arguments.get("fields"),
                generate_bundle_document=arguments.get("generate_bundle_document", False),
                no_parallelization=arguments.get("no_parallelization", False),
                enable_mathjax=arguments.get("enable_mathjax", False),
                included_documents=arguments.get("included_documents", False),
                reqif_profile=arguments.get("reqif_profile"),
                reqif_multiline_is_xhtml=arguments.get("reqif_multiline_is_xhtml", False),
                reqif_enable_mid=arguments.get("reqif_enable_mid", False),
                filter_nodes=arguments.get("filter_nodes"),
                view=arguments.get("view"),
                generate_diff_git=arguments.get("generate_diff_git"),
                generate_diff_dirs=arguments.get("generate_diff_dirs"),
                chromedriver=arguments.get("chromedriver"),
                config=arguments.get("config"),
            )

        elif name == "strictdoc_import_reqif":
            result = await import_tools.import_reqif(
                profile=arguments["profile"],
                input_path=arguments["input_path"],
                output_path=arguments["output_path"],
                reqif_enable_mid=arguments.get("reqif_enable_mid", False),
                reqif_import_markup=arguments.get("reqif_import_markup"),
            )

        elif name == "strictdoc_import_excel":
            result = await import_tools.import_excel(
                parser=arguments["parser"],
                input_path=arguments["input_path"],
                output_path=arguments["output_path"],
            )

        elif name == "strictdoc_manage_auto_uid":
            result = await manage.manage_auto_uid(
                input_paths=arguments["input_paths"],
            )

        elif name == "strictdoc_server":
            result = await server_tool.run_server(
                input_paths=arguments["input_paths"],
                port=arguments.get("port"),
                host=arguments.get("host"),
            )

        elif name == "strictdoc_server_stop":
            result = await server_tool.stop_server(
                server_key=arguments.get("server_key"),
            )

        elif name == "strictdoc_version":
            result = await utils.get_version()

        elif name == "strictdoc_dump_grammar":
            result = await utils.dump_grammar(
                output_path=arguments["output_path"],
            )

        else:
            result = {
                "success": False,
                "message": f"Unknown tool: {name}",
                "error": f"Tool '{name}' not found",
            }

        # Format result for MCP response
        if result.get("success"):
            message = result.get("message", "Operation completed successfully")
            # Include additional info if available
            details = []
            if "output_dir" in result:
                details.append(f"Output directory: {result['output_dir']}")
            if "output_path" in result:
                details.append(f"Output file: {result['output_path']}")
            if "files_created" in result and result["files_created"]:
                details.append(f"Files created: {len(result['files_created'])}")
            if "files_modified" in result and result["files_modified"]:
                details.append(f"Files modified: {len(result['files_modified'])}")
            if "version" in result:
                details.append(f"Version: {result['version']}")
            if "url" in result:
                details.append(f"Server URL: {result['url']}")

            full_message = message
            if details:
                full_message += "\n\n" + "\n".join(details)

            return [TextContent(type="text", text=full_message)]
        else:
            error_msg = result.get("message", "Operation failed")
            error_detail = result.get("error", "Unknown error")
            metadata = result.get("metadata", {})
            return [
                TextContent(
                    type="text",
                    text=f"{error_msg}\n\nError details: {error_detail}\n\nMetadata: {json.dumps(metadata, indent=2)}",
                )
            ]

    except KeyError as e:
        error_msg = f"Missing required argument: {e}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def handle_list_tools(
    _ctx: ServerRequestContext[Any],
    _params: Optional[PaginatedRequestParams],
) -> ListToolsResult:
    """MCP 2.x tools/list handler."""
    return ListToolsResult(tools=await list_tools())


async def handle_call_tool(
    _ctx: ServerRequestContext[Any],
    params: CallToolRequestParams,
) -> CallToolResult:
    """MCP 2.x tools/call handler."""
    content = await call_tool(params.name, params.arguments or {})
    return CallToolResult(content=content)


# Create MCP server instance (mcp>=2 uses constructor handlers, not decorators)
app = Server(
    "strictdoc-mcp",
    on_list_tools=handle_list_tools,
    on_call_tool=handle_call_tool,
)


async def main() -> None:
    """Main entry point for the MCP server."""
    config = get_config()
    logging.getLogger().setLevel(getattr(logging, config.log_level, logging.INFO))

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def cli_main() -> None:
    """Synchronous entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())

