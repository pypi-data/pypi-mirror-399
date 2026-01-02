# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""MCP Management Operations - Server configuration management.

v0.12.0: Standalone operations (no FunctionPlugin infrastructure).

This module handles MCP server configuration operations that are
inherently local to the CLI:
- add/remove/list/enable/disable servers
- catalog/install from pre-defined catalog
- status/test/update server health

These operations manage the ~/.aii/mcp_servers.json config file.
"""


import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class OperationResult:
    """Result of an MCP management operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class MCPConfigManager:
    """
    Manages MCP server configuration file operations.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Override config file path (default: ~/.aii/mcp_servers.json)
        """
        self.config_path = config_path or (Path.home() / ".aii" / "mcp_servers.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """Load MCP server configuration."""
        if not self.config_path.exists():
            return {"mcpServers": {}}

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            return config if isinstance(config, dict) else {"mcpServers": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {"mcpServers": {}}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save MCP server configuration."""
        try:
            self._ensure_config_dir()
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def backup_config(self) -> bool:
        """Create backup of current configuration."""
        if not self.config_path.exists():
            return True

        try:
            backup_path = self.config_path.with_suffix(".json.backup")
            import shutil
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Config backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup config: {e}")
            return False


# MCP Server Catalog (built-in server definitions)
MCP_CATALOG = {
    "github": {
        "name": "GitHub",
        "description": "GitHub API integration for repos, issues, PRs, and more",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
        "category": "development",
    },
    "filesystem": {
        "name": "Filesystem",
        "description": "Read/write files on the local filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.home())],
        "category": "system",
    },
    "brave-search": {
        "name": "Brave Search",
        "description": "Web search using Brave Search API",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-brave-search"],
        "env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"},
        "category": "search",
    },
    "sqlite": {
        "name": "SQLite",
        "description": "Query SQLite databases",
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "./database.db"],
        "category": "database",
    },
    "postgres": {
        "name": "PostgreSQL",
        "description": "Query PostgreSQL databases",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-postgres"],
        "env": {"DATABASE_URL": "${DATABASE_URL}"},
        "category": "database",
    },
    "chrome-devtools": {
        "name": "Chrome DevTools",
        "description": "Control Chrome browser via DevTools protocol",
        "command": "npx",
        "args": ["chrome-devtools-mcp@latest"],
        "category": "browser",
    },
    "memory": {
        "name": "Memory",
        "description": "Persistent memory storage for conversation context",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "category": "utility",
    },
    "puppeteer": {
        "name": "Puppeteer",
        "description": "Browser automation with Puppeteer",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-server-puppeteer"],
        "category": "browser",
    },
}


async def mcp_add(
    server_name: str,
    command: str,
    args: List[str],
    env: Optional[Dict[str, str]] = None,
    transport: str = "stdio"
) -> OperationResult:
    """Add MCP server to configuration."""
    config_manager = MCPConfigManager()

    # Validate transport
    if transport not in ["stdio", "sse", "http"]:
        return OperationResult(
            success=False,
            message=f"Invalid transport '{transport}'. Must be: stdio, sse, or http"
        )

    # Load existing config
    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    # Check if server already exists
    if server_name in servers:
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' already exists. Use 'aii mcp remove {server_name}' first."
        )

    # Build server config
    server_config = {
        "command": command,
        "args": args if isinstance(args, list) else [args],
    }

    if env:
        server_config["env"] = env

    # Add server to config
    servers[server_name] = server_config
    config["mcpServers"] = servers

    # Backup before saving
    config_manager.backup_config()

    # Save config
    if not config_manager.save_config(config):
        return OperationResult(
            success=False,
            message="Failed to save configuration"
        )

    # Build output message
    output_lines = [
        f"✓ Added '{server_name}' server",
        f"✓ Configuration saved to {config_manager.config_path}",
        f"✓ Transport: {transport}",
    ]

    if env:
        output_lines.append(f"✓ Environment variables: {', '.join(env.keys())}")

    output_lines.append("")
    output_lines.append(f"Try it: aii \"use {server_name} mcp server to [your task]\"")

    return OperationResult(
        success=True,
        message="\n".join(output_lines),
        data={"server_name": server_name, "config": server_config}
    )


async def mcp_remove(server_name: str) -> OperationResult:
    """Remove MCP server from configuration."""
    config_manager = MCPConfigManager()

    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' not found in configuration."
        )

    # Backup before removing
    config_manager.backup_config()

    # Remove server
    del servers[server_name]
    config["mcpServers"] = servers

    if not config_manager.save_config(config):
        return OperationResult(
            success=False,
            message="Failed to save configuration"
        )

    return OperationResult(
        success=True,
        message=f"✓ Removed '{server_name}' server\n✓ Configuration saved",
        data={"server_name": server_name}
    )


async def mcp_list() -> OperationResult:
    """List all configured MCP servers."""
    config_manager = MCPConfigManager()

    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    if not servers:
        return OperationResult(
            success=True,
            message="No MCP servers configured.\n\nTry: aii mcp catalog",
            data={"servers": {}, "count": 0}
        )

    # Build output
    output_lines = ["📦 Configured MCP Servers:", ""]

    for server_name, server_config in servers.items():
        command = server_config.get("command", "")
        args = server_config.get("args", [])
        args_str = " ".join(args) if isinstance(args, list) else str(args)
        enabled = server_config.get("enabled", True)

        status_icon = "✓" if enabled else "✗"
        status_text = "" if enabled else " (disabled)"
        output_lines.append(f"{status_icon} {server_name}{status_text}")
        output_lines.append(f"  Command: {command} {args_str}")

        if "env" in server_config:
            env_vars = ", ".join(server_config["env"].keys())
            output_lines.append(f"  Environment: {env_vars}")

        output_lines.append("")

    output_lines.append(f"Total: {len(servers)} server(s)")

    return OperationResult(
        success=True,
        message="\n".join(output_lines),
        data={"servers": servers, "count": len(servers)}
    )


async def mcp_enable(server_name: str) -> OperationResult:
    """Enable a disabled MCP server."""
    config_manager = MCPConfigManager()

    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' not found in configuration."
        )

    servers[server_name]["enabled"] = True
    config["mcpServers"] = servers
    config_manager.save_config(config)

    return OperationResult(
        success=True,
        message=f"✓ Enabled '{server_name}' server",
        data={"server_name": server_name}
    )


async def mcp_disable(server_name: str) -> OperationResult:
    """Disable an MCP server (keeps config)."""
    config_manager = MCPConfigManager()

    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' not found in configuration."
        )

    servers[server_name]["enabled"] = False
    config["mcpServers"] = servers
    config_manager.save_config(config)

    return OperationResult(
        success=True,
        message=f"✓ Disabled '{server_name}' server",
        data={"server_name": server_name}
    )


async def mcp_catalog() -> OperationResult:
    """List available MCP servers from catalog."""
    output_lines = ["📚 MCP Server Catalog:", ""]

    # Group by category
    categories = {}
    for name, info in MCP_CATALOG.items():
        cat = info.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))

    for category, servers in sorted(categories.items()):
        output_lines.append(f"📁 {category.title()}")
        for name, info in servers:
            output_lines.append(f"  • {name}: {info['description']}")
        output_lines.append("")

    output_lines.append("Install: aii mcp install <server-name>")
    output_lines.append("Example: aii mcp install github")

    return OperationResult(
        success=True,
        message="\n".join(output_lines),
        data={"catalog": MCP_CATALOG}
    )


async def mcp_install(server_name: str, env_vars: Optional[Dict[str, str]] = None) -> OperationResult:
    """Install MCP server from catalog."""
    if server_name not in MCP_CATALOG:
        available = ", ".join(MCP_CATALOG.keys())
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' not found in catalog.\n\nAvailable: {available}"
        )

    catalog_entry = MCP_CATALOG[server_name]

    # Use provided env vars or catalog defaults
    env = env_vars or catalog_entry.get("env", {})

    # Add the server
    return await mcp_add(
        server_name=server_name,
        command=catalog_entry["command"],
        args=catalog_entry["args"],
        env=env if env else None
    )


async def mcp_status(server_name: Optional[str] = None, show_all: bool = False) -> OperationResult:
    """Check status of MCP servers."""
    from ...data.integrations.mcp.client_manager import MCPClientManager
    from ...data.integrations.mcp.config_loader import MCPConfigLoader
    from ...data.integrations.mcp_health_monitor import MCPHealthMonitor, HealthStatus

    debug = os.getenv("AII_DEBUG", "").lower() in ("1", "true", "yes")

    config_loader = MCPConfigLoader()
    config_loader.load_configurations()

    if not config_loader.servers:
        return OperationResult(
            success=False,
            message="⚠️  No MCP servers configured\n\nTo set up MCP servers:\n  aii mcp catalog        # Browse available servers\n  aii mcp add <server>   # Add a server\n  aii mcp list           # List configured servers"
        )

    # Create MCP client without full initialization
    mcp_client = MCPClientManager(config_loader=config_loader, enable_health_monitoring=False)

    # Create health monitor
    health_monitor = MCPHealthMonitor(
        mcp_client=mcp_client,
        verbose=debug,
        check_interval=60.0,
        health_check_timeout=5.0
    )

    # Check servers
    servers_to_check = [server_name] if server_name else list(config_loader.servers.keys())
    results = {}

    for srv in servers_to_check:
        try:
            # _check_server updates internal health_status and returns ServerHealth
            health = await health_monitor._check_server(srv)
            results[srv] = health
        except Exception as e:
            results[srv] = {"status": "error", "error": str(e)}

    # Build output
    output_lines = ["📊 MCP Server Status:", ""]

    for srv, health in results.items():
        if isinstance(health, dict):
            # Error case
            output_lines.append(f"  ❌ {srv}: Error - {health.get('error', 'Unknown')}")
        else:
            # ServerHealth object
            if health.status == HealthStatus.HEALTHY:
                icon = "✓"
                state = "healthy"
                if health.response_time_ms:
                    state += f" ({health.response_time_ms:.0f}ms)"
            elif health.status == HealthStatus.DEGRADED:
                icon = "⚠"
                state = "degraded"
                if health.response_time_ms:
                    state += f" ({health.response_time_ms:.0f}ms)"
            elif health.status == HealthStatus.DISABLED:
                icon = "✗"
                state = "disabled"
            else:
                icon = "✗"
                state = "unhealthy"
                if health.last_error:
                    state += f" - {health.last_error}"
            output_lines.append(f"  {icon} {srv}: {state}")

    return OperationResult(
        success=True,
        message="\n".join(output_lines),
        data={"results": {k: str(v) for k, v in results.items()}}
    )


async def mcp_test(server_name: Optional[str] = None, verbose: bool = False) -> OperationResult:
    """Test MCP server connection."""
    from ...data.integrations.mcp.client_manager import MCPClientManager
    from ...data.integrations.mcp.config_loader import MCPConfigLoader

    config_loader = MCPConfigLoader()
    config_loader.load_configurations()

    if not config_loader.servers:
        return OperationResult(
            success=False,
            message="⚠️  No MCP servers configured"
        )

    servers_to_test = [server_name] if server_name else list(config_loader.servers.keys())

    output_lines = ["🧪 Testing MCP Servers:", ""]
    all_passed = True

    for srv in servers_to_test:
        if srv not in config_loader.servers:
            output_lines.append(f"  ❌ {srv}: Not found in configuration")
            all_passed = False
            continue

        try:
            # Create a temporary client just for this server
            mcp_client = MCPClientManager(config_loader=config_loader, enable_health_monitoring=False)
            await mcp_client.initialize()

            # Try to list tools as a connection test
            tools = await mcp_client.discover_all_tools()
            server_tools = [t for t in tools if t.server_name == srv]

            output_lines.append(f"  ✓ {srv}: Connected ({len(server_tools)} tools)")

            if verbose and server_tools:
                for tool in server_tools[:5]:  # Show first 5 tools
                    output_lines.append(f"      • {tool.name}")
                if len(server_tools) > 5:
                    output_lines.append(f"      ... and {len(server_tools) - 5} more")

            await mcp_client.shutdown()

        except Exception as e:
            output_lines.append(f"  ❌ {srv}: Failed - {e}")
            all_passed = False

    return OperationResult(
        success=all_passed,
        message="\n".join(output_lines)
    )


async def mcp_update(server_name: str, auto_confirm: bool = False) -> OperationResult:
    """Update MCP server to latest version."""
    config_manager = MCPConfigManager()

    config = config_manager.load_config()
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        return OperationResult(
            success=False,
            message=f"Server '{server_name}' not found in configuration."
        )

    server_config = servers[server_name]
    command = server_config.get("command", "")
    args = server_config.get("args", [])

    # Check if this is an npm package that can be updated
    if command == "npx" and args:
        package_name = args[0] if not args[0].startswith("-") else (args[1] if len(args) > 1 else None)

        if package_name:
            # For npx packages, suggest reinstalling
            output_lines = [
                f"📦 Server: {server_name}",
                f"   Package: {package_name}",
                "",
                "To update, run:",
                f"  npm install -g {package_name}@latest",
                "",
                "Or remove and reinstall:",
                f"  aii mcp remove {server_name}",
                f"  aii mcp install {server_name}",
            ]

            return OperationResult(
                success=True,
                message="\n".join(output_lines),
                data={"server_name": server_name, "up_to_date": False, "requires_confirmation": True}
            )

    return OperationResult(
        success=True,
        message=f"ℹ️  Server '{server_name}' uses command '{command}' - manual update may be required.",
        data={"server_name": server_name, "up_to_date": True}
    )


__all__ = [
    "OperationResult",
    "MCPConfigManager",
    "MCP_CATALOG",
    "mcp_add",
    "mcp_remove",
    "mcp_list",
    "mcp_enable",
    "mcp_disable",
    "mcp_catalog",
    "mcp_install",
    "mcp_status",
    "mcp_test",
    "mcp_update",
]