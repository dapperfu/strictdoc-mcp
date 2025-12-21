"""Unit tests for utility tools."""

from unittest.mock import AsyncMock, patch

import pytest

from strictdoc_mcp.tools import utils


@pytest.mark.asyncio
async def test_get_version_success() -> None:
    """Test successful version retrieval."""
    with patch("strictdoc_mcp.tools.utils.subprocess.run") as mock_run:
        mock_result = AsyncMock()
        mock_result.stdout = "strictdoc 1.0.0\n"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_result.check.return_value = True
        mock_run.return_value = mock_result

        result = await utils.get_version()

        assert result["success"] is True
        assert "version" in result
        assert result["version"] == "strictdoc 1.0.0"


@pytest.mark.asyncio
async def test_get_version_failure() -> None:
    """Test version retrieval failure."""
    with patch("strictdoc_mcp.tools.utils.subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Command not found")

        result = await utils.get_version()

        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_dump_grammar_success() -> None:
    """Test successful grammar dump."""
    with patch("strictdoc_mcp.tools.utils.subprocess.run") as mock_run:
        mock_result = AsyncMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_result.check.return_value = True
        mock_run.return_value = mock_result

        with patch("pathlib.Path.exists", return_value=True):
            result = await utils.dump_grammar("/tmp/grammar.tx")

            assert result["success"] is True
            assert result["output_path"] == "/tmp/grammar.tx"

