# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
MCP (Model Context Protocol) command handler for AII CLI (v0.12.0).

v0.12.0: Rewritten to use standalone management operations.
No longer depends on aii.functions or aii.core.models.

Handles all MCP-related commands:
- mcp add/remove/list/enable/disable
- mcp catalog/install
- mcp status/test/update
- mcp list-tools
- mcp invoke (tool execution)
"""


import json
from typing import Any

from ...cli.command_router import CommandRoute


async def handle_mcp_command(route: CommandRoute, config_manager: Any, output_config: Any) -> int:
    """
    Handle MCP commands.

    Args:
        route: CommandRoute with command/subcommand/args
        config_manager: ConfigManager instance
        output_config: OutputConfig instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = route.args
    mcp_action = args.get("mcp_action")

    # Handle server management commands (v0.12.0: use standalone operations)
    if mcp_action in ["add", "remove", "list", "enable", "disable", "catalog", "install"]:
        from ...domains.mcp.management import (
            mcp_add,
            mcp_remove,
            mcp_list,
            mcp_enable,
            mcp_disable,
            mcp_catalog,
            mcp_install,
        )

        try:
            if mcp_action == "add":
                server_args = args.get("server_args", [])
                env = None
                if args.get("env"):
                    env = json.loads(args["env"])

                result = await mcp_add(
                    server_name=args.get("server_name"),
                    command=args.get("server_command"),
                    args=server_args,
                    env=env,
                    transport=args.get("transport", "stdio"),
                )

            elif mcp_action == "remove":
                result = await mcp_remove(server_name=args.get("server_name"))

            elif mcp_action == "list":
                result = await mcp_list()

            elif mcp_action == "enable":
                result = await mcp_enable(server_name=args.get("server_name"))

            elif mcp_action == "disable":
                result = await mcp_disable(server_name=args.get("server_name"))

            elif mcp_action == "catalog":
                result = await mcp_catalog()

            elif mcp_action == "install":
                env_vars = None
                if args.get("env"):
                    env_vars = json.loads(args["env"])
                result = await mcp_install(
                    server_name=args.get("server_name"),
                    env_vars=env_vars
                )

            # Print output
            print(result.message)
            return 0 if result.success else 1

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Handle list-tools subcommand
    if mcp_action == "list-tools":
        return await _handle_mcp_list_tools(args)

    # Handle status subcommand
    if mcp_action == "status":
        return await _handle_mcp_status(args)

    # Handle test subcommand
    if mcp_action == "test":
        return await _handle_mcp_test(args)

    # Handle update subcommand
    if mcp_action == "update":
        return await _handle_mcp_update(args)

    # Handle run subcommand - Client-Owned Workflow with positional args
    if mcp_action == "run" or mcp_action is None:
        return await _handle_mcp_run(args)

    # Unknown action
    print(f"❌ Unknown MCP action: {mcp_action}")
    print("\nAvailable MCP commands:")
    print("  add/remove/list/enable/disable - Server management")
    print("  catalog/install - Browse and install MCP servers")
    print("  status/test/update - Server diagnostics")
    print("  list-tools - List available MCP tools")
    print("  run - Execute MCP tool")
    return 1


async def _handle_mcp_status(args: dict) -> int:
    """Handle 'aii mcp status' command."""
    from ...domains.mcp.management import mcp_status

    server_name = args.get("server_name")
    show_all = args.get("all", False)

    try:
        result = await mcp_status(server_name=server_name, show_all=show_all)
        print(result.message)
        return 0 if result.success else 1

    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def _handle_mcp_test(args: dict) -> int:
    """Handle 'aii mcp test' command."""
    from ...domains.mcp.management import mcp_test

    server_name = args.get("server_name")
    verbose = args.get("verbose", False)

    try:
        result = await mcp_test(server_name=server_name, verbose=verbose)
        print(result.message)
        return 0 if result.success else 1

    except Exception as e:
        print(f"❌ Error testing MCP connection: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def _handle_mcp_update(args: dict) -> int:
    """Handle 'aii mcp update' command - supports batch updates."""
    from ...domains.mcp.management import mcp_update
    from ...data.integrations.mcp.config_loader import MCPConfigLoader

    server_names_input = args.get("server_names")
    auto_confirm = args.get("auto_confirm", False)

    try:
        # Parse server names (comma-separated or "all")
        if server_names_input == "all":
            config_loader = MCPConfigLoader()
            config_loader.load_configurations()
            server_names = list(config_loader.servers.keys())
            print(f"📦 Updating all {len(server_names)} servers: {', '.join(server_names)}\n")
        else:
            server_names = [s.strip() for s in server_names_input.split(",")]

        # Track results
        total_servers = len(server_names)
        updated_servers = []
        failed_servers = []
        up_to_date_servers = []

        # Process each server
        for i, server_name in enumerate(server_names, 1):
            if total_servers > 1:
                print(f"\n[{i}/{total_servers}] Checking {server_name}...")
                print("─" * 50)

            result = await mcp_update(server_name=server_name, auto_confirm=False)
            print(result.message)

            if not result.success:
                failed_servers.append(server_name)
                continue

            if result.data and result.data.get("up_to_date"):
                up_to_date_servers.append(server_name)
                continue

            if result.data and result.data.get("requires_confirmation"):
                should_update = auto_confirm

                if not auto_confirm:
                    response = input(f"\nUpdate {server_name}? (y/n/all): ").strip().lower()
                    if response == "all":
                        auto_confirm = True
                        should_update = True
                    elif response == "y":
                        should_update = True
                    else:
                        print(f"⏭️  Skipped {server_name}")
                        continue

                if should_update:
                    update_result = await mcp_update(server_name=server_name, auto_confirm=True)
                    print(update_result.message)

                    if update_result.success:
                        updated_servers.append(server_name)
                    else:
                        failed_servers.append(server_name)

        # Print summary for batch updates
        if total_servers > 1:
            print("\n" + "=" * 50)
            print("📊 Update Summary:")
            print("=" * 50)

            if updated_servers:
                print(f"✅ Updated ({len(updated_servers)}): {', '.join(updated_servers)}")
            if up_to_date_servers:
                print(f"✓  Up to date ({len(up_to_date_servers)}): {', '.join(up_to_date_servers)}")
            if failed_servers:
                print(f"❌ Failed ({len(failed_servers)}): {', '.join(failed_servers)}")

            print(f"\nTotal: {total_servers} servers")

        return 0 if not failed_servers else 1

    except Exception as e:
        print(f"❌ Error updating MCP server(s): {e}")
        import traceback
        traceback.print_exc()
        return 1


async def _handle_mcp_list_tools(args: dict) -> int:
    """Handle 'aii mcp list-tools' command."""
    from ...data.integrations.mcp.client_manager import MCPClientManager
    from ...data.integrations.mcp.config_loader import MCPConfigLoader

    server_filter = args.get("server_name")
    detailed = args.get("detailed", False)

    mcp_client = None
    try:
        config_loader = MCPConfigLoader()
        mcp_client = MCPClientManager(config_loader=config_loader)
        await mcp_client.initialize()

        all_tools = await mcp_client.discover_all_tools()

        # Group by server
        tools_by_server = {}
        for tool in all_tools:
            if tool.server_name not in tools_by_server:
                tools_by_server[tool.server_name] = []
            tools_by_server[tool.server_name].append(tool)

        # Filter by server if specified
        if server_filter:
            if server_filter not in tools_by_server:
                print(f"❌ Server '{server_filter}' not found")
                print(f"\nAvailable servers: {', '.join(tools_by_server.keys())}")
                return 1
            tools_by_server = {server_filter: tools_by_server[server_filter]}

        # Display
        for server_name, tools in tools_by_server.items():
            print(f"\n{'='*60}")
            print(f"📦 Server: {server_name}")
            print(f"{'='*60}")
            print(f"🔧 Total tools: {len(tools)}\n")

            for tool in tools:
                print(f"  • {tool.name}")
                if tool.description:
                    desc = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                    print(f"    {desc}")

                if detailed and tool.input_schema and 'properties' in tool.input_schema:
                    print(f"    Parameters:")
                    for param_name, param_info in tool.input_schema['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        required = '(required)' if param_name in tool.input_schema.get('required', []) else '(optional)'
                        print(f"      - {param_name} ({param_type}) {required}")
                print()

        print(f"\n📊 Summary:")
        print(f"  Servers: {len(tools_by_server)}")
        print(f"  Total tools: {sum(len(tools) for tools in tools_by_server.values())}")

        return 0

    except Exception as e:
        print(f"❌ Failed to list MCP tools: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if mcp_client:
            try:
                await mcp_client.shutdown()
            except Exception:
                pass


async def _handle_mcp_run(args: dict) -> int:
    """Handle 'aii mcp run' command - Execute MCP tool directly."""
    from ...domains.mcp.operations import MCPToolOperation
    from ...config.manager import get_config
    from ...cli.client import AiiCLIClient

    extra_args = args.get("extra_args", [])

    if not extra_args:
        print("❌ Usage: aii mcp run <server> <tool> [args...]")
        print()
        print("Examples:")
        print("  aii mcp run filesystem read_file README.md")
        print("  aii mcp run chrome-devtools new_page https://github.com")
        print("  aii mcp run github search_repos 'python ML'")
        print()
        print("To list servers/tools:")
        print("  aii mcp list                     # List configured servers")
        print("  aii mcp list-tools <server>      # List tools for server")
        return 1

    config_manager = get_config()
    client = AiiCLIClient(config_manager)

    try:
        op = MCPToolOperation(config_manager, client)
        return await op.execute(extra_args)
    finally:
        await client.close()


async def _handle_mcp_invoke(args: dict) -> int:
    """Handle 'aii mcp invoke' command - execute MCP tool (DEPRECATED - use 'aii mcp run' instead)."""
    from ...data.integrations.mcp.client_manager import MCPClientManager
    from ...data.integrations.mcp.config_loader import MCPConfigLoader

    tool_name = args.get("tool_name")

    if not tool_name:
        print("❌ Error: tool_name is required")
        print("\nUsage:")
        print("  aii mcp invoke <tool_name> --path <path> [--content <content>] [--args <json>]")
        print("  aii mcp list-tools [server_name] [--detailed]")
        print("\nExamples:")
        print("  aii mcp invoke read_text_file --path /path/to/file.txt")
        print("  aii mcp list-tools github")
        print("  aii mcp list-tools --detailed")
        return 1

    mcp_client = None
    try:
        # Build arguments dictionary
        tool_args = {}

        if args.get("path"):
            import os
            tool_args["path"] = os.path.realpath(args["path"])

        if args.get("content"):
            tool_args["content"] = args["content"]

        if args.get("args"):
            try:
                additional_args = json.loads(args["args"])
                tool_args.update(additional_args)
            except json.JSONDecodeError as e:
                print(f"❌ Error: Invalid JSON in --args: {e}")
                return 1

        config_loader = MCPConfigLoader()
        mcp_client = MCPClientManager(config_loader=config_loader)
        await mcp_client.initialize()

        print(f"🔧 Calling MCP tool: {tool_name}")
        if tool_args:
            print(f"📋 Arguments: {tool_args}")

        result = await mcp_client.call_tool(tool_name, tool_args)

        if result.success:
            print(f"\n✅ Success!")
            print()

            for item in result.content:
                if hasattr(item, 'text'):
                    print(item.text)
                elif hasattr(item, 'data'):
                    print(json.dumps(item.data, indent=2))
                else:
                    print(str(item))

            return 0
        else:
            error_msg = result.error or "Operation failed"
            print(f"\n❌ Error: {error_msg}")

            if "path" in tool_args and not result.success:
                print("\n💡 Hint: The MCP filesystem server may not have access to this path.")
                print("   Check your MCP configuration in ~/.aii/mcp_servers.json")

            return 1

    except Exception as e:
        print(f"❌ MCP command failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if mcp_client:
            try:
                await mcp_client.shutdown()
            except Exception:
                pass
