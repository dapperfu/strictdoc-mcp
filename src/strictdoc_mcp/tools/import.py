"""Import tools for StrictDoc operations.

This module provides import tools for ReqIF and Excel formats.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import get_config


async def import_reqif(
    profile: str,
    input_path: str,
    output_path: str,
    reqif_enable_mid: bool = False,
    reqif_import_markup: Optional[str] = None,
) -> Dict[str, Any]:
    """Import ReqIF document to StrictDoc format.

    Parameters
    ----------
    profile : str
        ReqIF import/export profile (e.g., "p01_sdoc").
    input_path : str
        Path to input ReqIF file.
    output_path : str
        Path to output SDoc file.
    reqif_enable_mid : bool
        Map MID field to ReqIF SPEC-OBJECT IDENTIFIER.
    reqif_import_markup : Optional[str]
        Markup option for imported SDoc documents (RST or HTML).

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - output_path: Optional[str] - Path to output file if successful
        - files_created: List[str] - List of created/modified files
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [
        config.get_strictdoc_command(),
        "import",
        "reqif",
        profile,
        input_path,
        output_path,
    ]

    if reqif_enable_mid:
        cmd.append("--reqif-enable-mid")
    if reqif_import_markup:
        cmd.extend(["--reqif-import-markup", reqif_import_markup])

    files_created: list[str] = []
    output_file = Path(output_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,  # 5 minutes timeout
        )

        # Check if output file was created
        if output_file.exists():
            files_created = [str(output_file)]

        return {
            "success": True,
            "message": f"ReqIF document imported successfully to {output_path}",
            "output_path": output_path,
            "files_created": files_created,
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
            "message": "Import command timed out after 5 minutes",
            "output_path": None,
            "files_created": [],
            "error": f"Command timed out after 300 seconds: {e}",
            "metadata": {
                "command": " ".join(cmd),
                "error_type": "TimeoutExpired",
            },
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Import failed: {e.stderr or 'Unknown error'}",
            "output_path": None,
            "files_created": [],
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
            "message": f"Import failed: {str(e)}",
            "output_path": None,
            "files_created": [],
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }


async def import_excel(
    parser: str,
    input_path: str,
    output_path: str,
) -> Dict[str, Any]:
    """Import Excel document to StrictDoc format.

    Parameters
    ----------
    parser : str
        Excel parser to use (e.g., "basic").
    input_path : str
        Path to input Excel file.
    output_path : str
        Path to output SDoc file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - output_path: Optional[str] - Path to output file if successful
        - files_created: List[str] - List of created/modified files
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [
        config.get_strictdoc_command(),
        "import",
        "excel",
        parser,
        input_path,
        output_path,
    ]

    files_created: list[str] = []
    output_file = Path(output_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,  # 5 minutes timeout
        )

        # Check if output file was created
        if output_file.exists():
            files_created = [str(output_file)]

        return {
            "success": True,
            "message": f"Excel document imported successfully to {output_path}",
            "output_path": output_path,
            "files_created": files_created,
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
            "message": "Import command timed out after 5 minutes",
            "output_path": None,
            "files_created": [],
            "error": f"Command timed out after 300 seconds: {e}",
            "metadata": {
                "command": " ".join(cmd),
                "error_type": "TimeoutExpired",
            },
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Import failed: {e.stderr or 'Unknown error'}",
            "output_path": None,
            "files_created": [],
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
            "message": f"Import failed: {str(e)}",
            "output_path": None,
            "files_created": [],
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }

