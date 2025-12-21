# StrictDoc MCP Server

A Model Context Protocol (MCP) server that exposes all StrictDoc tooling features as MCP tools.

## Overview

This MCP server provides programmatic access to StrictDoc's command-line tools through the Model Context Protocol, enabling AI assistants and other tools to interact with StrictDoc documentation workflows.

## Features

- **Export**: Export StrictDoc documents to various formats (HTML, PDF, ReqIF, etc.)
- **Import**: Import documents from ReqIF and Excel formats
- **Manage**: Auto-generate missing requirement UIDs
- **Server**: Run StrictDoc web server for viewing/editing
- **Utilities**: Get version information and dump grammar

## Installation

### Prerequisites

- Python 3.10 or higher
- StrictDoc installed (`pip install strictdoc`)
- UV package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd strictdoc-mcp
```

2. Create virtual environment and install dependencies:
```bash
make install-dev
```

Or manually:
```bash
python3 -mvenv venv_strictdoc-mcp
source venv_strictdoc-mcp/bin/activate
uv pip install -e ".[dev]"
```

## Usage

### Running the MCP Server

The server can be run in two ways:

1. **As a module**:
```bash
python -m strictdoc_mcp
```

2. **As a CLI script** (after installation):
```bash
strictdoc-mcp
```

The server communicates via stdio using the MCP protocol.

### Configuration

Configuration can be provided via:

1. **Config file**: Create `strictdoc-mcp.toml` in the current directory or `~/.config/strictdoc-mcp/config.toml`
2. **Environment variables**: Override config file values

Example config file (`strictdoc-mcp.toml`):
```toml
log_level = "INFO"
strictdoc_cli_path = "/usr/local/bin/strictdoc"
default_output_dir = "./output"
```

Environment variables:
- `STRICTDOC_MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `STRICTDOC_MCP_CLI_PATH`: Path to strictdoc CLI executable
- `STRICTDOC_MCP_DEFAULT_OUTPUT_DIR`: Default output directory

### Available Tools

The MCP server exposes the following tools:

- `strictdoc_export`: Export documents to various formats
- `strictdoc_import_reqif`: Import ReqIF documents
- `strictdoc_import_excel`: Import Excel documents
- `strictdoc_manage_auto_uid`: Generate missing UIDs
- `strictdoc_server`: Run web server
- `strictdoc_server_stop`: Stop running server
- `strictdoc_version`: Get StrictDoc version
- `strictdoc_dump_grammar`: Dump grammar to file

### MCP Client Configuration

To use this MCP server with an MCP client (like Cursor, Claude Desktop, or other MCP-compatible tools), you need to configure the server in your client's settings.

#### Cursor IDE

Add the following configuration to your Cursor MCP settings (typically in `.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "python",
      "args": ["-m", "strictdoc_mcp"],
      "env": {
        "STRICTDOC_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

If using a virtual environment:

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "/path/to/venv_strictdoc-mcp/bin/python",
      "args": ["-m", "strictdoc_mcp"],
      "env": {
        "STRICTDOC_MCP_LOG_LEVEL": "INFO",
        "STRICTDOC_MCP_CLI_PATH": "/usr/local/bin/strictdoc"
      }
    }
  }
}
```

#### Claude Desktop

Add the following to your Claude Desktop configuration file (location varies by OS):
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "python",
      "args": ["-m", "strictdoc_mcp"],
      "env": {
        "STRICTDOC_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Using with UV (Recommended)

If you're using `uv` as your package manager, you can configure the server to use `uv run`:

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "uv",
      "args": ["run", "--frozen", "mcp", "run", "strictdoc_mcp.server:app"],
      "cwd": "/path/to/strictdoc-mcp",
      "env": {
        "STRICTDOC_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Direct Installation Script

Alternatively, if you've installed the package, you can use the CLI script directly:

```json
{
  "mcpServers": {
    "strictdoc-mcp": {
      "command": "strictdoc-mcp",
      "env": {
        "STRICTDOC_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Using MCP Tools

Once configured, the MCP client will automatically discover and make available all StrictDoc tools. You can interact with them through your AI assistant or MCP client interface.

#### Example Tool Usage

**Export documents to HTML:**
```json
{
  "name": "strictdoc_export",
  "arguments": {
    "input_paths": ["./docs"],
    "output_dir": "./output",
    "formats": "html"
  }
}
```

**Import ReqIF document:**
```json
{
  "name": "strictdoc_import_reqif",
  "arguments": {
    "profile": "p01_sdoc",
    "input_path": "./requirements.reqif",
    "output_path": "./requirements.sdoc"
  }
}
```

**Run web server:**
```json
{
  "name": "strictdoc_server",
  "arguments": {
    "input_paths": ["./docs"],
    "port": 8000,
    "host": "127.0.0.1"
  }
}
```

**Get version:**
```json
{
  "name": "strictdoc_version",
  "arguments": {}
}
```

### MCP Protocol Overview

The Model Context Protocol (MCP) enables AI assistants and other tools to interact with external systems through a standardized interface. This server implements the MCP protocol and exposes StrictDoc functionality as **tools** that can be called by MCP clients.

**Key MCP Concepts:**
- **Tools**: Functions that the AI can call to perform actions (e.g., export documents, import files)
- **Resources**: Read-only data that can be accessed (not currently implemented in this server)
- **Prompts**: Template-based interactions (not currently implemented in this server)

The server communicates via **stdio** (standard input/output), making it compatible with any MCP client that supports stdio transport.

### Troubleshooting

If the MCP server isn't working:

1. **Check the server is installed**: Verify you can run `python -m strictdoc_mcp` or `strictdoc-mcp` successfully
2. **Verify StrictDoc is available**: Ensure `strictdoc` CLI is in your PATH or set `STRICTDOC_MCP_CLI_PATH`
3. **Check logs**: Set `STRICTDOC_MCP_LOG_LEVEL=DEBUG` for detailed logging
4. **Verify configuration**: Ensure the command path in your MCP client config is correct
5. **Test manually**: Run the server directly to ensure it starts without errors

## Development

### Makefile Targets

- `make install`: Install package dependencies
- `make install-dev`: Install development dependencies
- `make develop`: Install in editable mode with dev dependencies
- `make format`: Format code with ruff
- `make check`: Check code with ruff
- `make lint`: Type check with mypy
- `make test`: Run all tests
- `make test-unit`: Run unit tests only
- `make test-integration`: Run integration tests only
- `make run`: Run MCP server
- `make clean`: Remove generated files
- `make clean-all`: Remove everything including venv

### Code Quality

The project follows these standards:
- **Type checking**: Full mypy typing required
- **Formatting**: Ruff for code formatting and linting
- **Documentation**: NumPy-style docstrings

### Testing

Run tests with:
```bash
make test
```

Unit tests mock external dependencies, while integration tests require strictdoc to be installed.

## Project Structure

```
strictdoc-mcp/
├── src/
│   └── strictdoc_mcp/
│       ├── __init__.py
│       ├── __main__.py        # Module entry point
│       ├── server.py          # Main MCP server
│       ├── config.py          # Configuration management
│       └── tools/
│           ├── export.py      # Export tool
│           ├── import_tools.py # Import tools
│           ├── manage.py       # Manage tools
│           ├── server.py      # Server tool
│           └── utils.py       # Utility tools
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/          # Integration tests
├── pyproject.toml             # Project configuration
├── Makefile                   # Build targets
└── README.md                  # This file
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

[Add contributing guidelines]

