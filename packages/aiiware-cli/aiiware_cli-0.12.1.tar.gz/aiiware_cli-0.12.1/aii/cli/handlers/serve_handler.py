# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Serve command handler for AII CLI (v0.12.0 - Pure CLI).

In v0.12.0, the API server has been separated into aii-server-py.
This handler provides migration guidance and server status checking.
"""


from typing import Any

from ...cli.command_router import CommandRoute


async def handle_serve_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle 'serve' command - manage API server.

    In v0.12.0, the API server is now a separate package (aii-server-py).
    This handler provides migration guidance.

    Args:
        route: CommandRoute with command/subcommand/args
        config_manager: ConfigManager instance
        output_config: OutputConfig instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = route.args
    subcommand = args.get("serve_subcommand")

    # Check server status is still supported
    if subcommand == "status":
        return await _handle_serve_status(config_manager)

    # For other commands, show migration message
    print("ℹ️  Server Management (v0.12.0)")
    print()
    print("The Aii API Server has been separated into a standalone package.")
    print()
    print("To run the Python server:")
    print("  pip install aii-server")
    print("  aii-server start")
    print()
    print("Or use the Go server:")
    print("  aii-server (native binary)")
    print()
    print("To check if a server is running:")
    print("  aii serve status")
    print()
    print("The CLI will automatically connect to the server at:")
    print(f"  http://{config_manager.get('api.host', '127.0.0.1')}:{config_manager.get('api.port', 26169)}")
    print()

    return 0


async def _handle_serve_status(config_manager: Any) -> int:
    """Handle 'serve status' (check server status)."""
    from pathlib import Path
    from urllib.parse import urlparse
    import os
    import httpx

    pid_file = Path.home() / ".aii" / "server.pid"

    # Parse host/port from api.url or use legacy api.host/api.port
    api_url = config_manager.get("api.url")
    if api_url:
        parsed = urlparse(api_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 26169
    else:
        host = config_manager.get("api.host", "127.0.0.1")
        port = config_manager.get("api.port", 26169)

    # Check PID file
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process exists
            try:
                os.kill(pid, 0)
                pid_status = f"✅ Running (PID: {pid})"
            except OSError:
                pid_status = "❌ Not running (stale PID file)"
                pid_file.unlink()
        except ValueError:
            pid_status = "❌ Invalid PID file"
            pid_file.unlink()
    else:
        pid_status = "❓ No local PID file (server may be running externally)"

    # Check HTTP health endpoint
    try:
        # Use 127.0.0.1 for localhost or 0.0.0.0 to avoid proxy/binding issues
        check_host = "127.0.0.1" if host in ("localhost", "0.0.0.0") else host
        # Disable system proxy for local connections (trust_env=False ignores proxy env vars)
        with httpx.Client(trust_env=False, timeout=2.0) as client:
            response = client.get(f"http://{check_host}:{port}/api/status")
        if response.status_code == 200:
            health_status = "✅ Healthy"
            data = response.json()
            # Go server uses "uptime_seconds", Python server uses "uptime"
            uptime = data.get("uptime_seconds") or data.get("uptime", 0)
            version = data.get("version", "unknown")
            server_type = data.get("server", "unknown")
        else:
            health_status = f"⚠️  HTTP {response.status_code}"
            uptime = 0
            version = "unknown"
            server_type = "unknown"
    except (httpx.ConnectError, httpx.TimeoutException):
        health_status = "❌ Not responding"
        uptime = 0
        version = "unknown"
        server_type = "unknown"
    except Exception as e:
        health_status = f"❌ Error: {e}"
        uptime = 0
        version = "unknown"
        server_type = "unknown"

    # Display status
    print("\n📊 Aii Server Status")
    print("=" * 50)
    print(f"Process:  {pid_status}")
    print(f"Health:   {health_status}")
    print(f"Address:  http://{host}:{port}")
    if uptime > 0:
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        print(f"Uptime:   {hours}h {minutes}m {seconds}s")
        print(f"Version:  {version}")
        if server_type != "unknown":
            print(f"Server:   {server_type}")
    print("=" * 50)
    print()

    # Return exit code based on health
    if "✅" in health_status:
        return 0
    else:
        return 1
