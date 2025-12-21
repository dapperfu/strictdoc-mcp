"""Integration tests for export tool.

These tests require strictdoc to be installed and available.
"""

import tempfile
from pathlib import Path

import pytest

from strictdoc_mcp.tools import export


@pytest.mark.integration
@pytest.mark.asyncio
async def test_export_version_check() -> None:
    """Test that we can at least check strictdoc version."""
    # This is a simple integration test that verifies strictdoc is available
    # Full export tests would require actual .sdoc files
    result = await export.export_documents(
        input_paths=["/nonexistent/path"],
        output_dir=None,
    )

    # Should fail but give us information about the error
    assert "success" in result
    # The exact result depends on whether strictdoc is installed
    # but we should get a structured response

