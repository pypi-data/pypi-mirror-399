# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Miscellaneous command handlers for AII CLI (v0.12.0).

v0.12.0: Pure CLI - simplified handlers without local LLM/function infrastructure.

Handles:
- history (chat history management)
- template (template operations)
- stats (usage statistics)
- doctor (health checks)
- install-completion/uninstall-completion (shell completion)
"""


from typing import Any

from ...cli.command_router import CommandRoute


async def handle_history_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle chat history commands.

    Note: This may be deprecated in v0.6.0 as history operations
    will be handled via WebSocket API in the future.
    """
    print("❌ History command not yet implemented in v0.12.0")
    print("💡 This feature will be available through the WebSocket API")
    return 1


async def handle_template_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle template commands - routes to AI functions via WebSocket.

    v0.6.0: Templates are Tier 2 AI commands, executed via server.
    """
    from aii.cli.client import AiiCLIClient

    try:
        # Parse template subcommand
        if not route.subcommand:
            print("❌ Missing template subcommand")
            print("\nUsage:")
            print("  aii template list                    # List available templates")
            print("  aii template show <name>             # Show template details")
            print("  aii template use <name> --var value  # Use template")
            return 1

        subcommand = route.subcommand
        args = route.args or {}

        # Create WebSocket client
        client = AiiCLIClient(config_manager)

        if subcommand == "list":
            # Execute natural language command to list templates
            result = await client.execute_command(
                user_input="list all available templates",
                output_mode="CLEAN"
            )
            return 0 if result.get("success") else 1

        elif subcommand == "show":
            # Get template name from args (argparse stores it as template_name)
            template_name = args.get("template_name")
            if not template_name:
                print("❌ Missing template name")
                print("\nUsage: aii template show <name>")
                return 1

            # Execute natural language command to show template
            result = await client.execute_command(
                user_input=f"show template {template_name}",
                output_mode="CLEAN"
            )
            return 0 if result.get("success") else 1

        elif subcommand == "use":
            # Get template name from args (argparse stores it as template_name)
            template_name = args.get("template_name")
            if not template_name:
                print("❌ Missing template name")
                print("\nUsage: aii template use <name> --var1 value1 --var2 value2")
                return 1

            # Collect template variables from args (skip internal argparse keys)
            skip_keys = {"template_name", "template_action", "command", "var"}
            variables = {k: v for k, v in args.items() if k not in skip_keys and v is not None}

            # Build natural language command with variables
            vars_str = " ".join([f"--{k} \"{v}\"" for k, v in variables.items()])
            user_input = f"use template {template_name} {vars_str}"

            # Execute template generation
            result = await client.execute_command(
                user_input=user_input,
                output_mode="CLEAN"
            )
            return 0 if result.get("success") else 1

        else:
            print(f"❌ Unknown template subcommand: {subcommand}")
            print("\nAvailable subcommands: list, show, use")
            return 1

    except Exception as e:
        print(f"❌ Template command failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def handle_stats_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle stats commands (v0.12.0).

    v0.12.0: Simplified stats - queries local analytics database.
    Advanced stats (models, cost) require server-side implementation.
    """
    from aii.data.storage.analytics import SessionAnalytics

    try:
        args = route.args if route.args else {}
        stats_action = args.get("stats_action")

        # v0.12.0: stats models/cost require server (not available locally)
        if stats_action == "models":
            print("⚠️  'stats models' requires the AII server")
            print("💡 Use: aii \"show model performance stats\" (via server)")
            return 1

        elif stats_action == "cost":
            print("⚠️  'stats cost' requires the AII server")
            print("💡 Use: aii \"show cost breakdown\" (via server)")
            return 1

        # Legacy: stats (no subcommand) - local analytics
        else:
            # Get period from args (default to 30d)
            period = args.get("period", "30d")

            # Create analytics instance
            analytics = SessionAnalytics()

            # Query analytics
            stats = await analytics.get_usage_stats(period, "all")

            # Format output
            output = _format_stats_output(stats, period)
            print(output)

            return 0

    except Exception as e:
        print(f"❌ Error generating statistics: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _format_stats_output(stats: dict, period: str) -> str:
    """Format statistics for display."""
    output = [f"📊 AII Usage Statistics (Last {period})\n"]

    # Session summary
    total_sessions = stats.get("total_sessions", 0)
    output.append(f"Total Executions: {total_sessions}")

    if total_sessions == 0:
        output.append("\nNo usage data available for this period.")
        return "\n".join(output)

    output.append("")  # Blank line

    # Function breakdown
    if "functions" in stats:
        functions = stats["functions"]
        output.append("📈 Top Functions:")

        total_executions = functions.get("total_executions", 0)
        for func_name, count in functions.get("by_function", [])[:5]:
            percentage = (count / total_executions * 100) if total_executions > 0 else 0
            output.append(f"  {count:3d}× {func_name:20s} ({percentage:.1f}%)")

        if len(functions.get("by_function", [])) > 5:
            remaining = len(functions.get("by_function", [])) - 5
            output.append(f"  ... and {remaining} more")

        output.append("")

    # Token breakdown
    if "tokens" in stats:
        tokens = stats["tokens"]
        total_tokens = tokens.get("total_tokens", 0)

        if total_tokens > 0:
            output.append("🔢 Token Usage:")
            output.append(f"  Total: {total_tokens:,} tokens")
            output.append(f"  Input: {tokens.get('total_input', 0):,} tokens")
            output.append(f"  Output: {tokens.get('total_output', 0):,} tokens")
            output.append("")

    # Cost breakdown
    if "costs" in stats:
        costs = stats["costs"]
        total_cost = costs.get("total_cost", 0.0)

        if total_cost > 0:
            output.append("💰 Cost Breakdown:")
            output.append(f"  Total: ${total_cost:.4f}\n")

            by_function = costs.get("by_function", [])
            if by_function:
                output.append("  Top 5 by cost:")
                for func_name, cost in by_function[:5]:
                    percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                    output.append(f"    {func_name:20s} ${cost:.4f} ({percentage:.1f}%)")

                if len(by_function) > 5:
                    remaining = len(by_function) - 5
                    output.append(f"  ... and {remaining} more")

    return "\n".join(output)


async def handle_doctor_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle doctor/health check commands.

    v0.12.0: Simplified health checks without local LLM infrastructure.
    """
    import os
    import asyncio
    from pathlib import Path

    use_colors = output_config.use_colors if output_config else True
    use_emojis = output_config.use_emojis if output_config else True

    results = []
    print("🏥 AII Health Check\n" if use_emojis else "AII Health Check\n")

    # 1. Check configuration file
    config_path = Path.home() / ".aii" / "config.yaml"
    if config_path.exists():
        results.append(("Configuration file", "✓" if use_emojis else "OK", "Found"))
    else:
        results.append(("Configuration file", "✗" if use_emojis else "FAIL", "Not found"))

    # 2. Check API key configuration
    try:
        provider = config_manager.get("llm.provider", "unknown")
        # API keys are stored as secrets with provider-specific names
        api_key = config_manager.get_secret(f"{provider}_api_key", "")
        if api_key:
            # Mask the API key
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            results.append(("API Key", "✓" if use_emojis else "OK", f"{provider} ({masked})"))
        else:
            results.append(("API Key", "⚠" if use_emojis else "WARN", f"{provider} - not found"))
    except Exception as e:
        results.append(("API Key", "⚠" if use_emojis else "WARN", f"Error: {str(e)[:30]}"))

    # 3. Check AII server connection
    try:
        from aii.cli.server_manager import ServerManager
        server_manager = ServerManager(config_manager)
        host = server_manager.host
        port = server_manager.port

        if server_manager.is_server_running():
            results.append(("AII Server", "✓" if use_emojis else "OK", f"Running at {host}:{port}"))
        else:
            results.append(("AII Server", "⚠" if use_emojis else "WARN", f"Not running at {host}:{port}"))
    except Exception as e:
        results.append(("AII Server", "⚠" if use_emojis else "WARN", f"Error: {str(e)[:40]}"))

    # 4. Check MCP servers configuration
    mcp_config_path = Path.home() / ".aii" / "mcp_servers.json"
    if mcp_config_path.exists():
        try:
            import json
            with open(mcp_config_path) as f:
                mcp_config = json.load(f)
            server_count = len(mcp_config.get("mcpServers", {}))
            results.append(("MCP Servers", "✓" if use_emojis else "OK", f"{server_count} configured"))
        except Exception:
            results.append(("MCP Servers", "⚠" if use_emojis else "WARN", "Invalid config"))
    else:
        results.append(("MCP Servers", "⚠" if use_emojis else "WARN", "Not configured"))

    # 5. Check storage directory
    storage_path = Path.home() / ".aii"
    if storage_path.exists() and storage_path.is_dir():
        results.append(("Storage Directory", "✓" if use_emojis else "OK", str(storage_path)))
    else:
        results.append(("Storage Directory", "✗" if use_emojis else "FAIL", "Not found"))

    # 6. Check Python environment
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        results.append(("Python Version", "✓" if use_emojis else "OK", python_version))
    else:
        results.append(("Python Version", "⚠" if use_emojis else "WARN", f"{python_version} (3.10+ recommended)"))

    # Format and display results
    max_name_len = max(len(r[0]) for r in results)
    failed_count = 0

    for name, status, detail in results:
        if status in ("✗", "FAIL"):
            failed_count += 1
            if use_colors:
                print(f"  {status} {name:<{max_name_len}}  \033[31m{detail}\033[0m")
            else:
                print(f"  {status} {name:<{max_name_len}}  {detail}")
        elif status in ("⚠", "WARN"):
            if use_colors:
                print(f"  {status} {name:<{max_name_len}}  \033[33m{detail}\033[0m")
            else:
                print(f"  {status} {name:<{max_name_len}}  {detail}")
        else:
            if use_colors:
                print(f"  {status} {name:<{max_name_len}}  \033[32m{detail}\033[0m")
            else:
                print(f"  {status} {name:<{max_name_len}}  {detail}")

    # Summary
    print()
    if failed_count == 0:
        print("✅ All checks passed!" if use_emojis else "All checks passed!")
    else:
        print(f"❌ {failed_count} check(s) failed" if use_emojis else f"{failed_count} check(s) failed")

    return 1 if failed_count > 0 else 0


async def handle_completion_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle install-completion/uninstall-completion commands.

    v0.12.0: Simplified - no function registry needed.
    """
    print("⚠️  Shell completion is being redesigned for v0.12.0")
    print("💡 Tab completion will be available in a future update")
    return 1


async def handle_help_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """Handle help command."""
    from aii.cli.command_parser import CommandParser

    parser = CommandParser()
    parser.print_help()
    return 0
