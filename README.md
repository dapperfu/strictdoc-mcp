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
python -m strictdoc_mcp.server
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

[Add license information]

## Contributing

[Add contributing guidelines]

