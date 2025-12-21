"""Manage tools for StrictDoc operations.

This module provides management tools like auto-uid generation.
"""

import subprocess
from typing import Any, Dict, List

from ..config import get_config


async def manage_auto_uid(input_paths: List[str]) -> Dict[str, Any]:
    """Generate missing requirement UIDs automatically.

    Parameters
    ----------
    input_paths : List[str]
        One or more folders with *.sdoc files.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - files_modified: List[str] - List of modified files
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [
        config.get_strictdoc_command(),
        "manage",
        "auto-uid",
    ]
    cmd.extend(input_paths)

    files_modified: list[str] = []

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,  # 5 minutes timeout
        )

        # Parse output to find modified files (basic approach)
        # StrictDoc typically reports which files were modified
        if result.stdout:
            # Try to extract file paths from output
            lines = result.stdout.split("\n")
            for line in lines:
                if ".sdoc" in line or "Modified" in line:
                    # Basic extraction - may need refinement
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".sdoc"):
                            files_modified.append(part)

        return {
            "success": True,
            "message": f"Auto-UID generation completed for {len(input_paths)} path(s)",
            "files_modified": files_modified,
            "error": None,
            "metadata": {
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "input_paths": input_paths,
            },
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "message": "Auto-UID command timed out after 5 minutes",
            "files_modified": [],
            "error": f"Command timed out after 300 seconds: {e}",
            "metadata": {
                "command": " ".join(cmd),
                "error_type": "TimeoutExpired",
            },
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Auto-UID generation failed: {e.stderr or 'Unknown error'}",
            "files_modified": [],
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
            "message": f"Auto-UID generation failed: {str(e)}",
            "files_modified": [],
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }

