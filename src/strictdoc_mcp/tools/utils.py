"""Utility tools for StrictDoc operations.

This module provides utility tools like version and grammar dumping.
"""

import subprocess
from typing import Any, Dict

from ..config import get_config


async def get_version() -> Dict[str, Any]:
    """Get StrictDoc version.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - version: Optional[str] - Version string if successful
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [config.get_strictdoc_command(), "version"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        version = result.stdout.strip()
        return {
            "success": True,
            "message": f"StrictDoc version: {version}",
            "version": version,
            "error": None,
            "metadata": {
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "message": "Failed to get StrictDoc version: command timed out",
            "version": None,
            "error": f"Command timed out after 30 seconds: {e}",
            "metadata": {
                "command": " ".join(cmd),
                "error_type": "TimeoutExpired",
            },
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Failed to get StrictDoc version: {e.stderr or 'Unknown error'}",
            "version": None,
            "error": e.stderr or str(e),
            "metadata": {
                "command": " ".join(cmd),
                "returncode": e.returncode,
                "stdout": e.stdout,
                "stderr": e.stderr,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get StrictDoc version: {str(e)}",
            "version": None,
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }


async def dump_grammar(output_path: str) -> Dict[str, Any]:
    """Dump StrictDoc grammar to a .tx file.

    Parameters
    ----------
    output_path : str
        Path where the grammar file should be written.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - output_path: Optional[str] - Path to output file if successful
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [config.get_strictdoc_command(), "dump-grammar", output_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return {
            "success": True,
            "message": f"Grammar dumped successfully to {output_path}",
            "output_path": output_path,
            "error": None,
            "metadata": {
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "message": f"Failed to dump grammar: command timed out",
            "output_path": None,
            "error": f"Command timed out after 30 seconds: {e}",
            "metadata": {
                "command": " ".join(cmd),
                "error_type": "TimeoutExpired",
            },
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Failed to dump grammar: {e.stderr or 'Unknown error'}",
            "output_path": None,
            "error": e.stderr or str(e),
            "metadata": {
                "command": " ".join(cmd),
                "returncode": e.returncode,
                "stdout": e.stdout,
                "stderr": e.stderr,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to dump grammar: {str(e)}",
            "output_path": None,
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }

