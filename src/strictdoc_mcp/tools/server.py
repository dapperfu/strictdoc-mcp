"""Server tool for StrictDoc operations.

This module provides the server tool that runs StrictDoc web server.
"""

import asyncio
import subprocess
from typing import Any, Dict, List, Optional

from ..config import get_config

# Store running server processes
_running_servers: Dict[str, subprocess.Popen[str]] = {}


async def run_server(
    input_paths: List[str],
    port: Optional[int] = None,
    host: Optional[str] = None,
) -> Dict[str, Any]:
    """Run StrictDoc web server.

    This runs the server as a background process and returns immediately
    with process information.

    Parameters
    ----------
    input_paths : List[str]
        One or more folders with *.sdoc files.
    port : Optional[int]
        Port number for the server. If not provided, uses StrictDoc default.
    host : Optional[str]
        Host address for the server. If not provided, uses StrictDoc default.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the server started successfully
        - message: str - User-friendly message
        - process_id: Optional[int] - Process ID if started
        - port: Optional[int] - Port number if started
        - host: Optional[str] - Host address if started
        - url: Optional[str] - Server URL if started
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    config = get_config()
    cmd = [
        config.get_strictdoc_command(),
        "server",
    ]
    cmd.extend(input_paths)

    if port:
        cmd.extend(["--port", str(port)])
    if host:
        cmd.extend(["--host", host])

    # Create a unique key for this server instance
    server_key = f"{host or 'localhost'}:{port or 'default'}"

    try:
        # Start server as background process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Store process reference
        _running_servers[server_key] = process

        # Give it a moment to start
        await asyncio.sleep(1)

        # Check if process is still running
        if process.poll() is not None:
            # Process exited immediately - likely an error
            stdout, stderr = process.communicate()
            return {
                "success": False,
                "message": f"Server failed to start: {stderr or 'Unknown error'}",
                "process_id": None,
                "port": port,
                "host": host or "localhost",
                "url": None,
                "error": stderr or stdout or "Process exited immediately",
                "metadata": {
                    "command": " ".join(cmd),
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                },
            }

        # Determine URL
        final_port = port or 8000  # StrictDoc default
        final_host = host or "localhost"
        url = f"http://{final_host}:{final_port}"

        return {
            "success": True,
            "message": f"StrictDoc server started at {url}",
            "process_id": process.pid,
            "port": final_port,
            "host": final_host,
            "url": url,
            "error": None,
            "metadata": {
                "command": " ".join(cmd),
                "process_id": process.pid,
                "server_key": server_key,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to start server: {str(e)}",
            "process_id": None,
            "port": port,
            "host": host or "localhost",
            "url": None,
            "error": str(e),
            "metadata": {
                "command": " ".join(cmd),
                "error_type": type(e).__name__,
            },
        }


async def stop_server(server_key: Optional[str] = None) -> Dict[str, Any]:
    """Stop a running StrictDoc server.

    Parameters
    ----------
    server_key : Optional[str]
        Key identifying the server to stop. If None, stops all servers.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - success: bool - Whether the server was stopped
        - message: str - User-friendly message
        - stopped_servers: List[str] - List of stopped server keys
        - error: Optional[str] - Error message if failed
        - metadata: Dict[str, Any] - Detailed technical information
    """
    stopped: list[str] = []

    try:
        if server_key:
            if server_key in _running_servers:
                process = _running_servers[server_key]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del _running_servers[server_key]
                stopped.append(server_key)
        else:
            # Stop all servers
            for key, process in list(_running_servers.items()):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                stopped.append(key)
            _running_servers.clear()

        return {
            "success": True,
            "message": f"Stopped {len(stopped)} server(s)",
            "stopped_servers": stopped,
            "error": None,
            "metadata": {
                "stopped_count": len(stopped),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to stop server(s): {str(e)}",
            "stopped_servers": stopped,
            "error": str(e),
            "metadata": {
                "error_type": type(e).__name__,
            },
        }

