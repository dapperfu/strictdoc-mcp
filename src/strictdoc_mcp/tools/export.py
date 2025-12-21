"""Export tool for StrictDoc operations.

This module provides the export tool that wraps the strictdoc export command.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_config


async def export_documents(
    input_paths: List[str],
    output_dir: Optional[str] = None,
    formats: Optional[str] = None,
    project_title: Optional[str] = None,
    fields: Optional[str] = None,
    generate_bundle_document: bool = False,
    no_parallelization: bool = False,
    enable_mathjax: bool = False,
    included_documents: bool = False,
    reqif_profile: Optional[str] = None,
    reqif_multiline_is_xhtml: bool = False,
    reqif_enable_mid: bool = False,
    filter_nodes: Optional[str] = None,
    view: Optional[str] = None,
    generate_diff_git: Optional[str] = None,
    generate_diff_dirs: Optional[List[str]] = None,
    chromedriver: Optional[str] = None,
    config: Optional[str] = None,
) -> Dict[str, Any]:
    """Export StrictDoc documents to various formats.

    Parameters
    ----------
    input_paths : List[str]
        One or more folders with *.sdoc files.
    output_dir : Optional[str]
        Output folder. If not provided, uses default from config or current directory.
    formats : Optional[str]
        Export formats (comma-separated).
    project_title : Optional[str]
        Project title.
    fields : Optional[str]
        Export fields, only used for Excel export.
    generate_bundle_document : bool
        Generate bundle document in addition to individual documents.
    no_parallelization : bool
        Disable parallelization.
    enable_mathjax : bool
        Enable MathJax support (only HTML export).
    included_documents : bool
        Export included documents as well.
    reqif_profile : Optional[str]
        ReqIF profile to use.
    reqif_multiline_is_xhtml : bool
        Export multiline fields as XHTML in ReqIF.
    reqif_enable_mid : bool
        Map MID field to ReqIF SPEC-OBJECT IDENTIFIER.
    filter_nodes : Optional[str]
        Filter which requirements will be exported.
    view : Optional[str]
        Choose which view will be exported.
    generate_diff_git : Optional[str]
        Generate diff/changelog for Git revisions (e.g., "HEAD^..HEAD").
    generate_diff_dirs : Optional[List[str]]
        Generate diff/changelog for directory pair [old_path, new_path].
    chromedriver : Optional[str]
        Path to chromedriver for html2pdf.
    config : Optional[str]
        Path to StrictDoc TOML config file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the command succeeded
        - message: str - User-friendly message
        - output_dir: Optional[str] - Output directory if successful
        - files_created: List[str] - List of created/modified files
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config_obj = get_config()
    cmd = [config_obj.get_strictdoc_command(), "export"]

    # Add output directory
    if output_dir:
        cmd.extend(["--output-dir", output_dir])
    elif config_obj.default_output_dir:
        cmd.extend(["--output-dir", config_obj.default_output_dir])
    else:
        # Use current directory as default
        output_dir = str(Path.cwd())

    # Add input paths
    cmd.extend(input_paths)

    # Add optional parameters
    if formats:
        cmd.extend(["--formats", formats])
    if project_title:
        cmd.extend(["--project-title", project_title])
    if fields:
        cmd.extend(["--fields", fields])
    if generate_bundle_document:
        cmd.append("--generate-bundle-document")
    if no_parallelization:
        cmd.append("--no-parallelization")
    if enable_mathjax:
        cmd.append("--enable-mathjax")
    if included_documents:
        cmd.append("--included-documents")
    if reqif_profile:
        cmd.extend(["--reqif-profile", reqif_profile])
    if reqif_multiline_is_xhtml:
        cmd.append("--reqif-multiline-is-xhtml")
    if reqif_enable_mid:
        cmd.append("--reqif-enable-mid")
    if filter_nodes:
        cmd.extend(["--filter-nodes", filter_nodes])
    if view:
        cmd.extend(["--view", view])
    if generate_diff_git:
        cmd.extend(["--generate-diff-git", generate_diff_git])
    if generate_diff_dirs and len(generate_diff_dirs) == 2:
        cmd.extend(["--generate-diff-dirs", generate_diff_dirs[0], generate_diff_dirs[1]])
    if chromedriver:
        cmd.extend(["--chromedriver", chromedriver])
    if config:
        cmd.extend(["--config", config])

    # Determine output directory for file tracking
    final_output_dir = output_dir or config_obj.default_output_dir or str(Path.cwd())
    files_created: List[str] = []

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,  # 5 minutes timeout for export
        )

        # Try to detect created files (basic approach - list output directory)
        output_path = Path(final_output_dir)
        if output_path.exists():
            files_created = [str(f) for f in output_path.rglob("*") if f.is_file()]

        return {
            "success": True,
            "message": f"Documents exported successfully to {final_output_dir}",
            "output_dir": final_output_dir,
            "files_created": files_created,
            "error": None,
            "metadata": {
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "files_count": len(files_created),
            },
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "message": "Export command timed out after 5 minutes",
            "output_dir": None,
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
            "message": f"Export failed: {e.stderr or 'Unknown error'}",
            "output_dir": None,
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
            "message": f"Export failed: {str(e)}",
            "output_dir": None,
            "files_created": [],
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }

