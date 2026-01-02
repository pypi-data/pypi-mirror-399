# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""Main AII CLI Entry Point (v0.6.0 - Unified WebSocket Architecture)"""


import asyncio
import sys
from pathlib import Path
from typing import Any

from .cli.command_parser import CommandParser
from .cli.command_router import CommandRouter
from .cli.client import AiiCLIClient
from .cli.confirmation import ConfirmationManager
from .config.manager import get_config, init_config
from .config.output_config import OutputConfig

# Import Tier 1 handlers
from .cli.handlers import (
    handle_config_command,
    handle_mcp_command,
    handle_serve_command,
    handle_prompt_command,
    handle_doctor_command,
    handle_completion_command,
    handle_help_command,
    handle_history_command,
    handle_stats_command,
)

# v0.12.0: Domain operations removed from thin CLI
# Domain operations (git commit, etc.) are now handled by the Aii Server
# CLI sends natural language requests to server which handles domain logic


def print_session_summary(metadata: dict[str, Any], output_mode: str = "STANDARD") -> None:
    """
    Print unified session summary for all functions.

    Args:
        metadata: Metadata dict from server response
        output_mode: Output mode (STANDARD, THINKING, VERBOSE)
    """
    if not metadata:
        return

    # Build compact single-line summary
    summary_parts = []

    # Function name with checkmark
    function_name = metadata.get("function_name", "unknown")
    summary_parts.append(f"✓ {function_name}")

    # Execution time
    execution_time = metadata.get("execution_time")
    if execution_time:
        summary_parts.append(f"⚡ Total time: {execution_time:.1f}s")

    # Tokens
    tokens_data = metadata.get("tokens", {})
    if tokens_data:
        input_tokens = tokens_data.get("input", 0)
        output_tokens = tokens_data.get("output", 0)
        total_tokens = input_tokens + output_tokens
        summary_parts.append(f"🔢 Tokens: {input_tokens}↗ {output_tokens}↘ ({total_tokens} total)")

    # Cost
    cost = metadata.get("cost")
    if cost and cost > 0:
        if cost < 0.001:
            cost_str = f"${cost:.6f}"
        elif cost < 0.01:
            cost_str = f"${cost:.4f}"
        else:
            cost_str = f"${cost:.2f}"
        summary_parts.append(f"💰 {cost_str}")

    # Model (strip openai: prefix for OpenAI-compatible providers like Moonshot/DeepSeek)
    model = metadata.get("model")
    if model:
        # Strip "openai:" prefix if present (used for OpenAI-compatible providers)
        display_model = model.replace("openai:", "") if model.startswith("openai:") else model
        summary_parts.append(f"🤖 {display_model}")

    # Print compact summary on single line (with blank line above for readability)
    print()  # Single blank line for readability
    print("📊 Execution Summary:")
    print(" • ".join(summary_parts))

    # VERBOSE mode: Add extended metrics
    if output_mode == "VERBOSE":
        # Quality and Confidence line
        quality_parts = []

        # Determine quality based on success_rate (default to 1.0 if not available)
        success_rate = metadata.get("success_rate")
        if success_rate is None:
            success_rate = 1.0  # Default to Excellent if no session data

        if success_rate == 1.0:
            quality_text = "Excellent"
        elif success_rate >= 0.8:
            quality_text = "Good"
        elif success_rate >= 0.5:
            quality_text = "Partial"
        else:
            quality_text = "Poor"
        quality_parts.append(f"🏆 Quality: {quality_text}")

        # Confidence
        confidence = metadata.get("confidence")
        if confidence is not None:
            # Normalize confidence to percentage (handle both 0-1 and 0-100 formats)
            if confidence <= 1.0:
                confidence_pct = confidence * 100
            else:
                confidence_pct = confidence
            quality_parts.append(f"🎯 Confidence: {confidence_pct:.1f}%")

        if quality_parts:
            print(" • ".join(quality_parts))

        # Performance line
        if execution_time and tokens_data:
            total_tokens = tokens_data.get("input", 0) + tokens_data.get("output", 0)
            tokens_per_sec = total_tokens / execution_time if execution_time > 0 else 0
            if tokens_per_sec > 100:
                efficiency = "excellent"
            elif tokens_per_sec > 50:
                efficiency = "good"
            elif tokens_per_sec > 20:
                efficiency = "moderate"
            else:
                efficiency = "wasteful"
            print(f"📈 Performance: Token efficiency: {efficiency}")

        # Pipeline status
        total_functions = metadata.get("total_functions")
        if total_functions is None:
            total_functions = 1  # Default to 1 if no session data

        if success_rate == 1.0:
            print(f"✅ Pipeline completed successfully ({total_functions} function{'s' if total_functions > 1 else ''})")
        elif success_rate > 0:
            print(f"⚠️  Pipeline partially completed ({total_functions} function{'s' if total_functions > 1 else ''})")
        else:
            print(f"❌ Pipeline failed ({total_functions} function{'s' if total_functions > 1 else ''})")


async def main() -> int:
    """Main entry point for AII CLI (v0.12.0 - Thin Client)"""
    try:
        # v0.12.0: Domain registration removed - domains handled by server

        # Parse command line arguments
        parser = CommandParser()
        parsed_cmd = parser.parse_args()

        # Initialize output configuration with CLI args
        class Args:
            def __init__(self, args_dict):
                if args_dict:
                    for key, value in args_dict.items():
                        setattr(self, key, value)

        args_obj = Args(parsed_cmd.args) if parsed_cmd.args else None
        output_config = OutputConfig.load(cli_args=args_obj)

        # Initialize config manager
        config_manager = init_config(Path.home() / ".aii")

        # Route command using CommandRouter
        command_router = CommandRouter()

        # Convert parsed_cmd to dict for routing
        # Extract subcommand from action fields (e.g., template_action, mcp_action, etc.)
        subcommand = getattr(parsed_cmd, "subcommand", None)
        if not subcommand and parsed_cmd.args:
            # Check for *_action fields in args
            for key in parsed_cmd.args:
                if key.endswith("_action") and parsed_cmd.args[key]:
                    subcommand = parsed_cmd.args[key]
                    break

        parsed_dict = {
            "command": parsed_cmd.command,
            "subcommand": subcommand,
            "input_text": parsed_cmd.input_text,
            "args": parsed_cmd.args,
            "interactive": parsed_cmd.interactive,
            "continue_chat": parsed_cmd.continue_chat,
            "new_chat": parsed_cmd.new_chat,
            "offline": parsed_cmd.offline,
        }

        route = command_router.route(parsed_dict)

        if route.tier == 1:
            # Tier 1: Local command (no server needed)
            return await handle_local_command(route, config_manager, output_config)

        elif route.tier == 2:
            # Tier 2: AI command (requires server + WebSocket)
            return await handle_ai_command(route, config_manager, output_config, parsed_cmd)

        else:
            print(f"❌ Unknown command tier: {route.tier}")
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


async def handle_removed_template_command(route: Any, config_manager: Any, output_config: Any) -> int:
    """
    Show migration message for removed 'aii template' command (v0.6.2).

    The template command has been replaced by 'aii prompt' for clarity.
    """
    print("❌ Command 'template' has been removed in v0.6.2\n")
    print("The 'aii template' command has been replaced by 'aii prompt'.\n")
    print("Migration:")
    print("  Old: aii template list")
    print("  New: aii prompt list\n")
    print("  Old: aii template show my-prompt")
    print("  New: aii prompt show my-prompt\n")
    print("  Old: aii template use my-prompt")
    print("  New: aii prompt use my-prompt\n")
    print("  Old: aii template validate my-prompt")
    print("  New: aii prompt validate my-prompt\n")
    print("See CHANGELOG: https://pypi.org/project/aiiware-cli/#history")
    return 1


async def handle_local_command(route: Any, config_manager: Any, output_config: Any) -> int:
    """
    Handle Tier 1 (local) commands that don't require server.

    Args:
        route: CommandRoute with command/subcommand/args
        config_manager: ConfigManager instance
        output_config: OutputConfig instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    command = route.command

    # v0.11.2: Apply --host override for commands that may need server access
    # Some Tier 1 commands like 'prompt use' still need server for LLM execution
    # v0.12.0: Skip host override if it's the default 0.0.0.0 (from serve command parser)
    # The 0.0.0.0 default is for binding servers, not for client connections
    host_override = route.args.get("host")
    if host_override and host_override != "0.0.0.0":
        if ":" in host_override:
            host_part, port_part = host_override.split(":", 1)
            api_url = f"http://{host_override}"
            api_host = host_part
            api_port = int(port_part)
        else:
            # Default port is 26169 for Aii Server
            api_url = f"http://{host_override}:26169"
            api_host = host_override
            api_port = 26169
        config_manager.set("api.url", api_url, save=False)
        config_manager.set("api.host", api_host, save=False)
        config_manager.set("api.port", api_port, save=False)

    # Map commands to handlers
    handlers = {
        "config": handle_config_command,
        "mcp": handle_mcp_command,
        "serve": handle_serve_command,
        "doctor": handle_doctor_command,
        "template": handle_removed_template_command,  # Removed in v0.6.2 - show migration message
        "prompt": handle_prompt_command,  # Prompt Library (v0.6.1)
        "stats": handle_stats_command,
        "history": handle_history_command,
        "help": handle_help_command,
        "run": handle_run_command,  # Domain operations (v0.6.0)
        "install-completion": handle_completion_command,
        "uninstall-completion": handle_completion_command,
    }

    handler = handlers.get(command)
    if not handler:
        print(f"❌ Unknown local command: {command}")
        print("Run 'aii help' for available commands")
        return 1

    # Call handler
    return await handler(route, config_manager, output_config)


async def handle_ai_command(route: Any, config_manager: Any, output_config: Any, parsed_cmd: Any) -> int:
    """
    Handle Tier 2 (AI) commands via WebSocket streaming.

    Args:
        route: CommandRoute with command/subcommand/args
        config_manager: ConfigManager instance
        output_config: OutputConfig instance
        parsed_cmd: Original parsed command (for interactive mode)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Override API URL if --host provided (v0.6.0)
    host_override = route.args.get("host")
    if host_override:
        # Parse host:port format
        if ":" in host_override:
            # User provided host:port (e.g., "localhost:16170")
            host_part, port_part = host_override.split(":", 1)
            api_url = f"http://{host_override}"
            api_host = host_part
            api_port = int(port_part)
        else:
            # User provided just host (e.g., "localhost"), use default port
            api_url = f"http://{host_override}:26169"
            api_host = host_override
            api_port = 26169

        # Override both api.url (for client) and api.host/api.port (for server_manager)
        # Use save=False to avoid persisting temporary --host override to config file
        config_manager.set("api.url", api_url, save=False)
        config_manager.set("api.host", api_host, save=False)
        config_manager.set("api.port", api_port, save=False)

    # Check for interactive mode
    if parsed_cmd.interactive or (not parsed_cmd.input_text and not parsed_cmd.command):
        # v0.6.0: Interactive mode via WebSocket
        from .cli.interactive_websocket import InteractiveChatSession

        session = InteractiveChatSession(config_manager)
        return await session.start()

    # Extract parameters from route
    user_input = route.args.get("user_input", "")
    if not user_input:
        print("❌ No input provided")
        print("Usage: aii \"your request\"")
        return 1

    # Determine output mode from args
    # v0.6.0: Default to STANDARD mode to ensure Session Summary is always shown
    output_mode = "STANDARD"  # Default to STANDARD
    args = route.args
    if args.get('clean'):
        output_mode = "CLEAN"
    elif args.get('standard'):
        output_mode = "STANDARD"
    elif args.get('thinking'):
        output_mode = "THINKING"
    elif args.get('minimal'):
        output_mode = "CLEAN"
    elif args.get('verbose'):
        output_mode = "VERBOSE"
    # else: Keep STANDARD as default

    offline = args.get("offline", False)

    # v0.8.0: Extract model override if provided
    model = args.get("model")

    # Create WebSocket client (already configured with --host override above)
    client = AiiCLIClient(config_manager)

    try:
        # Phase 0: Show immediate feedback that command is being processed
        import sys
        import asyncio
        from aii.cli.debug import debug_print
        from aii.cli.spinner import Spinner

        # Start universal processing spinner (animated for better UX)
        # IMPORTANT: Use sys.stdout to coordinate with token streaming
        processing_spinner = Spinner("Processing...", stream=sys.stdout)
        await processing_spinner.start()

        # v0.6.0 UNIFIED FLOW: Single request with intent recognition + execution
        # Server performs intent recognition, executes function, and returns complete metadata
        # Client checks metadata after response to see if confirmation/local execution needed

        debug_print("MAIN: Executing unified request (intent recognition + execution)...")

        # Pass the spinner to execute_command so it can be stopped when streaming starts
        result = await client.execute_command(
            user_input=user_input,
            output_mode=output_mode,
            offline=offline,
            model=model,  # v0.8.0: Pass model override
            spinner=processing_spinner  # Pass spinner so it can be stopped on first token
        )

        # Ensure spinner is stopped (in case streaming didn't occur)
        # If streaming occurred, this will be a no-op since spinner is already stopped
        await processing_spinner.stop(clear=True)

        debug_print(f"MAIN: Result received - checking for confirmation requirements...")

        # Check if result requires confirmation and local execution (shell commands)
        # v0.6.0: Check both data and metadata for requires_execution_confirmation
        # v0.9.5: Handle None values explicitly (result.get returns None if key exists with None value)
        data = result.get("data") or {}
        metadata = result.get("metadata") or {}

        # v0.12.0: Handle client-side MCP execution
        # Server returns client_side_execution=true when MCP tool needs to run locally
        if data.get("client_side_execution"):
            debug_print("MAIN: Server requested client-side MCP execution")
            return await _handle_client_side_mcp_execution(data, metadata, config_manager, output_mode)

        requires_execution_confirmation = (
            data.get("requires_execution_confirmation", False) or
            metadata.get("requires_execution_confirmation", False)
        )

        if requires_execution_confirmation:
            debug_print("MAIN: Shell command requires confirmation and local execution")
            debug_print(f"MAIN: Metadata received: {metadata}")
            debug_print(f"MAIN: Data received: {data}")

            # Extract command details from data (primary source) or metadata (fallback)
            command = data.get("command") or metadata.get("command")
            explanation = data.get("explanation") or metadata.get("explanation", "Execute shell command")
            risks = data.get("risks") or data.get("safety_notes") or metadata.get("risks", [])

            if not command:
                print("\n❌ Error: No command found in response")
                return 1

            # Display the result message if it wasn't already streamed
            if not result.get("_streaming_occurred", False):
                result_message = result.get("result", "")
                if result_message:
                    print(result_message)

            # Display risks prominently if any
            if risks:
                print("⚠️  POTENTIAL RISKS:")
                for risk in risks:
                    print(f"   • {risk}")
                print()  # Extra newline for readability

            # Display Session Summary BEFORE confirmation (v0.6.0 improvement)
            # This allows users to see token/cost info before deciding to execute
            metadata = result.get("metadata", {})
            print_session_summary(metadata, output_mode="STANDARD")
            print()  # Extra newline before confirmation prompt

            # v0.11.1: Check for --yes flag to auto-confirm
            auto_confirm = route.args.get("yes", False)

            if auto_confirm:
                # Auto-confirm: skip interactive prompt
                debug_print("MAIN: Auto-confirm enabled (--yes flag)")
                confirmed = True
            else:
                # Prompt user for confirmation
                import sys
                try:
                    response = input("⚡ Execute this command? [y/N]: ").strip().lower()
                    confirmed = response in ['y', 'yes']
                except (EOFError, KeyboardInterrupt):
                    print("\n❌ Operation cancelled")
                    return 1

            if not confirmed:
                print("\n❌ Operation cancelled by user")
                return 1

            debug_print(f"MAIN: User confirmed - executing locally: {command}")

            # Execute command locally using subprocess
            import subprocess
            try:
                proc_result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                # Display output
                if proc_result.stdout:
                    print(proc_result.stdout)
                if proc_result.stderr:
                    print(proc_result.stderr, file=sys.stderr)

                if proc_result.returncode != 0:
                    print(f"⚠️  Command exited with code {proc_result.returncode}")
                    return proc_result.returncode
                else:
                    print(f"✅ Command executed successfully")
                    return 0

            except subprocess.TimeoutExpired:
                print(f"\n❌ Command timed out after 60 seconds")
                return 1
            except Exception as e:
                print(f"\n❌ Command execution failed: {e}")
                return 1

        debug_print(f"MAIN: Result: {result}")

        # Display result
        if result.get("success"):

            # Special handling for git_commit - requires custom formatting and confirmation
            metadata = result.get("metadata", {})
            if metadata.get("function_name") == "git_commit":
                requires_commit_confirmation = metadata.get("requires_commit_confirmation", False)
                # For backward compatibility, also check data field
                if not requires_commit_confirmation:
                    result_data = result.get("data", {})
                    requires_commit_confirmation = result_data.get("requires_commit_confirmation", False)

                if requires_commit_confirmation:
                    # Extract git_commit data from metadata or result data
                    result_data = result.get("data", metadata)

                    # Display git diff
                    git_diff = result_data.get("git_diff", "")
                    if git_diff:
                        print("\n📋 Git Diff:")
                        # Truncate very long diffs
                        if len(git_diff) > 2000:
                            print(git_diff[:2000])
                            print("\n... (diff truncated, showing first 2000 chars)")
                        else:
                            print(git_diff)

                    # Display thinking/reasoning
                    reasoning = result_data.get("reasoning", metadata.get("reasoning", ""))
                    if reasoning:
                        print(f"\n🧠 Thinking: {reasoning}")

                    # Display generated commit message
                    commit_message = result_data.get("commit_message", "")
                    if commit_message:
                        print(f"\n💻 Generated Commit Message:")
                        print(commit_message)
                        print()  # Blank line

                    # Display confidence and tokens
                    confidence = result_data.get("confidence", metadata.get("confidence"))
                    if confidence:
                        print(f"🎯 Confidence: {confidence}%")

                    tokens_data = metadata.get("tokens", {})
                    if tokens_data:
                        input_tokens = tokens_data.get("input", 0)
                        output_tokens = tokens_data.get("output", 0)
                        print(f"🔢 Tokens: Input: {input_tokens} • Output: {output_tokens}")

                    # Prompt for confirmation to proceed with commit
                    print()
                    user_response = input("Proceed with this commit? (y/n): ").strip().lower()

                    if user_response in ['y', 'yes']:
                        # Execute the actual git commit
                        import subprocess
                        try:
                            # Write commit message to temp file
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                                f.write(commit_message)
                                commit_msg_file = f.name

                            # Execute git commit with the message file
                            commit_result = subprocess.run(
                                ["git", "commit", "-F", commit_msg_file],
                                capture_output=True,
                                text=True,
                                cwd=config_manager.get("git.repository_path", None)
                            )

                            # Clean up temp file
                            import os
                            os.unlink(commit_msg_file)

                            if commit_result.returncode == 0:
                                print("\n✅ Commit successful!")
                                if commit_result.stdout:
                                    print(commit_result.stdout)
                                return 0
                            else:
                                print(f"\n❌ Commit failed: {commit_result.stderr}")
                                return 1

                        except Exception as e:
                            print(f"\n❌ Failed to execute commit: {e}")
                            return 1
                    else:
                        print("\n❌ Commit cancelled")
                        return 1

            # Display the result ONLY if streaming didn't already print it
            # WebSocket streaming prints tokens in real-time via on_token callback
            # The result field contains the assembled output, but it was already displayed
            # So we should NOT print it again to avoid duplication
            #
            # Check if streaming occurred (at least one token was printed)
            if not result.get("_streaming_occurred", False):
                # No streaming occurred, print the result now
                output = result.get("result", "")
                if output:
                    print(output)
            else:
                # v0.11.0: Add blank line after streaming content for visual separation
                print()

            # For THINKING and VERBOSE modes, display reasoning first
            if output_mode in ["THINKING", "VERBOSE"]:
                metadata = result.get("metadata", {})
                reasoning = metadata.get("reasoning")
                if reasoning:
                    print()
                    print(f"💭 Reasoning: {reasoning}")

            # For STANDARD, THINKING, and VERBOSE modes, print session summary (even if streaming occurred)
            # The metadata contains tokens, cost, model, execution_time from the server
            if output_mode in ["STANDARD", "THINKING", "VERBOSE"]:
                metadata = result.get("metadata", {})
                print_session_summary(metadata, output_mode=output_mode)

            return 0
        else:
            # Clear loading line
            sys.stderr.write("\r\033[K")
            sys.stderr.flush()

            # Try both 'result' and 'message' fields for error message
            error_msg = result.get("result") or result.get("message", "Unknown error")
            print(f"❌ Error: {error_msg}")
            return 1

    except ConnectionRefusedError:
        print("\n❌ Failed to connect to Aii server")
        print("💡 Try starting the server manually: aii serve")
        return 1

    except RuntimeError as e:
        # RuntimeError from client already has formatted error message
        # Just print it without duplication
        error_msg = str(e)
        if not error_msg.startswith("❌"):
            print(f"\n❌ {error_msg}")
        else:
            print(f"\n{error_msg}")
        return 1

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await client.close()


async def handle_run_command(route: Any, config_manager: Any, output_config: Any) -> int:
    """
    Handle 'aii run <domain> <operation>' commands (v0.12.0 - Thin Client).

    In the thin client architecture, domain operations are delegated to the Aii Server.
    The CLI sends the domain/operation request to the server, which handles the logic
    and returns results that may require local execution (e.g., git commit).

    Args:
        route: CommandRoute with domain/operation args
        config_manager: ConfigManager instance
        output_config: OutputConfig instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    from aii.cli.debug import debug_print
    from aii.cli.spinner import Spinner

    # Extract domain and operation from args
    domain_name = route.args.get("domain")
    operation_name = route.args.get("operation")
    extra_args = route.args.get("extra_args", [])

    # Validate domain and operation were provided
    if not domain_name:
        print("❌ No domain specified")
        print("💡 Usage: aii run <domain> <operation>")
        print("💡 Available domains: git")
        return 1

    if not operation_name:
        print(f"❌ No operation specified for domain '{domain_name}'")
        print(f"💡 Usage: aii run {domain_name} <operation>")
        return 1

    # v0.12.0: Handle git commit specially - collect diff locally and ask server to generate message
    if domain_name == "git" and operation_name == "commit":
        return await _handle_git_commit_local(config_manager, output_config, extra_args)

    # v0.12.0: Handle git pr specially - collect branch info locally and ask server to generate PR
    if domain_name == "git" and operation_name == "pr":
        return await _handle_git_pr_local(config_manager, output_config, extra_args)

    # Build request for server
    # Format: "run <domain> <operation> [extra_args]"
    request_parts = [domain_name, operation_name]
    if extra_args:
        request_parts.extend(extra_args)
    user_input = " ".join(request_parts)

    debug_print(f"RUN: Sending domain operation to server: {user_input}")

    # Create WebSocket client
    client = AiiCLIClient(config_manager)

    try:
        # Start spinner
        processing_spinner = Spinner("Processing...", stream=sys.stdout)
        await processing_spinner.start()

        # Send to server for processing
        result = await client.execute_command(
            user_input=f"run {user_input}",
            output_mode="STANDARD",
            spinner=processing_spinner
        )

        await processing_spinner.stop(clear=True)

        # Check result
        if not result.get("success"):
            error_msg = result.get("result") or result.get("message", "Operation failed")
            print(f"❌ {error_msg}")
            return 1

        # Handle response based on domain/operation
        data = result.get("data") or {}
        metadata = result.get("metadata") or {}

        # Check if this is a git commit that needs local execution
        if domain_name == "git" and operation_name == "commit":
            return await _handle_git_commit_response(result, config_manager)

        # For other operations, just display the result
        if not result.get("_streaming_occurred", False):
            output = result.get("result", "")
            if output:
                print(output)
        else:
            print()

        # Print session summary
        print_session_summary(metadata, output_mode="STANDARD")
        return 0

    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await client.close()


async def _handle_git_commit_local(config_manager: Any, output_config: Any, extra_args: list) -> int:
    """
    Handle git commit locally by collecting diff and asking server for commit message.

    v0.12.0: This handles the thin-client workflow for git commit:
    1. Run git diff --staged locally to get staged changes
    2. Send the diff to the server with a request to generate a commit message
    3. Display the generated message for user approval
    4. Execute git commit locally with the approved message

    Args:
        config_manager: ConfigManager instance
        output_config: OutputConfig instance
        extra_args: Additional arguments (e.g., --dry-run)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    import subprocess
    import tempfile
    import os
    from aii.cli.debug import debug_print
    from aii.cli.spinner import Spinner

    debug_print("GIT COMMIT: Starting local git commit workflow")

    # Check if --dry-run flag is present
    dry_run = "--dry-run" in extra_args

    # v0.12.0: Check if --yes/-y flag is present for auto-confirm
    auto_confirm = "--yes" in extra_args or "-y" in extra_args

    # Step 1: Check for staged changes
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if status_result.returncode != 0:
            print("❌ Not in a git repository or git command failed")
            return 1

        # Check if there are any staged changes (lines starting with A, M, D, R, etc. in first column)
        staged_changes = [line for line in status_result.stdout.strip().split('\n') if line and line[0] != ' ' and line[0] != '?']
        if not staged_changes:
            print("❌ No staged changes to commit")
            print("💡 Use 'git add <file>' to stage changes first")
            return 1
    except FileNotFoundError:
        print("❌ git command not found")
        return 1

    # Step 2: Get staged diff (plain for sending to LLM, colored for display)
    try:
        # Plain diff for LLM
        diff_result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        git_diff = diff_result.stdout
        if not git_diff.strip():
            print("❌ No staged changes found")
            print("💡 Use 'git add <file>' to stage changes first")
            return 1

        # Colored diff for display
        colored_diff_result = subprocess.run(
            ["git", "diff", "--staged", "--color=always"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        git_diff_colored = colored_diff_result.stdout or git_diff
    except Exception as e:
        print(f"❌ Failed to get git diff: {e}")
        return 1

    debug_print(f"GIT COMMIT: Got diff ({len(git_diff)} chars)")

    # Step 3: Send request to server to generate commit message
    # Create a natural language request that includes the diff
    client = AiiCLIClient(config_manager)

    try:
        # Start spinner
        processing_spinner = Spinner("Generating commit message...", stream=sys.stdout)
        await processing_spinner.start()

        # Build request - ask for a commit message based on the diff
        # Truncate diff if too long (to avoid token limits)
        max_diff_chars = 8000
        if len(git_diff) > max_diff_chars:
            truncated_diff = git_diff[:max_diff_chars] + "\n\n... (diff truncated)"
        else:
            truncated_diff = git_diff

        user_input = f"""Generate a git commit message for the following staged changes.
Return ONLY the commit message, no explanation or markdown formatting.
Use conventional commit format (type: description).

Git diff:
```
{truncated_diff}
```"""

        # v0.12.0: Suppress streaming output for git commit to avoid showing message before diff
        # We'll display the commit message ourselves after showing the diff
        result = await client.execute_command(
            user_input=user_input,
            output_mode="CLEAN",  # We just want the message, no extra formatting
            spinner=processing_spinner,
            suppress_streaming=True  # Don't print tokens as they arrive
        )

        await processing_spinner.stop(clear=True)

        if not result.get("success"):
            error_msg = result.get("result") or result.get("message", "Failed to generate commit message")
            print(f"❌ {error_msg}")
            return 1

        # Extract the commit message from the result
        commit_message = result.get("result", "").strip()
        if not commit_message:
            print("❌ No commit message generated")
            return 1

        # Clean up the message (remove markdown code blocks if present)
        if commit_message.startswith("```"):
            lines = commit_message.split('\n')
            # Remove first and last line if they are code block markers
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            commit_message = '\n'.join(lines).strip()

        # Add Aii signature footer
        commit_message = f"{commit_message}\n\n🤖 Generated with [aii](https://pypi.org/project/aiiware-cli)"

        # Step 4: Display diff (colored) FIRST, then generated message
        # Note: No leading \n needed - spinner.stop(clear=True) already cleared the line
        print("📋 Git Diff:")
        if len(git_diff_colored) > 2000:
            print(git_diff_colored[:2000])
            print("\n... (diff truncated, showing first 2000 chars)")
        else:
            print(git_diff_colored)

        print(f"\n💻 Generated Commit Message:")
        print(commit_message)

        # Display standard execution summary
        metadata = result.get("metadata") or {}
        # Add function name for git_commit display
        metadata["function_name"] = "git_commit"
        print_session_summary(metadata, output_mode="STANDARD")

        # Step 5: Confirm with user (unless dry-run)
        if dry_run:
            print("\n🔍 Dry run mode - commit not executed")
            return 0

        print()

        # v0.12.0: Check for auto-confirm (--yes/-y flag)
        if auto_confirm:
            print("⚡ Auto-confirming commit (--yes flag)")
            user_response = 'y'
        else:
            try:
                user_response = input("Proceed with this commit? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Commit cancelled")
                return 1

        if user_response not in ['y', 'yes']:
            print("\n❌ Commit cancelled")
            return 1

        # Step 6: Execute git commit locally
        try:
            # Write commit message to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(commit_message)
                commit_msg_file = f.name

            # Execute git commit
            commit_result = subprocess.run(
                ["git", "commit", "-F", commit_msg_file],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            # Clean up temp file
            os.unlink(commit_msg_file)

            if commit_result.returncode == 0:
                print("\n✅ Commit successful!")
                if commit_result.stdout:
                    print(commit_result.stdout)
                return 0
            else:
                print(f"\n❌ Commit failed: {commit_result.stderr}")
                return 1

        except Exception as e:
            print(f"\n❌ Failed to execute commit: {e}")
            return 1

    except Exception as e:
        print(f"\n❌ Git commit failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await client.close()


async def _handle_git_commit_response(result: dict, config_manager: Any) -> int:
    """
    Handle git commit response from server.

    The server returns the generated commit message and git diff.
    Client shows the message, asks for confirmation, and executes git commit locally.
    """
    import subprocess
    import tempfile
    import os

    data = result.get("data") or {}
    metadata = result.get("metadata") or {}

    # Extract commit data
    commit_message = data.get("commit_message") or metadata.get("commit_message")
    git_diff = data.get("git_diff") or metadata.get("git_diff")
    reasoning = data.get("reasoning") or metadata.get("reasoning")
    confidence = data.get("confidence") or metadata.get("confidence")

    if not commit_message:
        print("❌ No commit message generated")
        return 1

    # Display git diff
    if git_diff:
        print("\n📋 Git Diff:")
        if len(git_diff) > 2000:
            print(git_diff[:2000])
            print("\n... (diff truncated, showing first 2000 chars)")
        else:
            print(git_diff)

    # Display reasoning
    if reasoning:
        print(f"\n🧠 Thinking: {reasoning}")

    # Display generated commit message
    print(f"\n💻 Generated Commit Message:")
    print(commit_message)
    print()

    # Display confidence
    if confidence:
        print(f"🎯 Confidence: {confidence}%")

    # Display tokens
    tokens_data = metadata.get("tokens", {})
    if tokens_data:
        input_tokens = tokens_data.get("input", 0)
        output_tokens = tokens_data.get("output", 0)
        print(f"🔢 Tokens: Input: {input_tokens} • Output: {output_tokens}")

    # Prompt for confirmation
    print()
    try:
        user_response = input("Proceed with this commit? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Commit cancelled")
        return 1

    if user_response not in ['y', 'yes']:
        print("\n❌ Commit cancelled")
        return 1

    # Execute git commit locally
    try:
        # Write commit message to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(commit_message)
            commit_msg_file = f.name

        # Execute git commit
        commit_result = subprocess.run(
            ["git", "commit", "-F", commit_msg_file],
            capture_output=True,
            text=True,
            cwd=config_manager.get("git.repository_path", None)
        )

        # Clean up temp file
        os.unlink(commit_msg_file)

        if commit_result.returncode == 0:
            print("\n✅ Commit successful!")
            if commit_result.stdout:
                print(commit_result.stdout)
            return 0
        else:
            print(f"\n❌ Commit failed: {commit_result.stderr}")
            return 1

    except Exception as e:
        print(f"\n❌ Failed to execute commit: {e}")
        return 1


async def _handle_git_pr_local(config_manager: Any, output_config: Any, extra_args: list) -> int:
    """
    Handle git PR creation locally by collecting branch info and asking server to generate PR content.

    v0.12.0: This handles the thin-client workflow for git pr:
    1. Run git commands locally to get branch info, commits, and diff
    2. Send the info to the server with a request to generate PR title/body
    3. Display the generated PR content for user approval
    4. Execute gh pr create locally with the approved content

    Args:
        config_manager: ConfigManager instance
        output_config: OutputConfig instance
        extra_args: Additional arguments (e.g., --dry-run)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    import subprocess
    import os
    from aii.cli.debug import debug_print
    from aii.cli.spinner import Spinner

    debug_print("GIT PR: Starting local git PR workflow")

    # Check if --dry-run flag is present
    dry_run = "--dry-run" in extra_args

    # Step 1: Check if in a git repository
    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if git_check.returncode != 0:
            print("❌ Not in a git repository")
            return 1
    except FileNotFoundError:
        print("❌ git command not found")
        return 1

    # Step 2: Check if gh CLI is installed
    try:
        gh_check = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True
        )
        if gh_check.returncode != 0:
            print("❌ GitHub CLI (gh) not found")
            print("💡 Install with: brew install gh")
            return 1
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found")
        print("💡 Install with: brew install gh")
        return 1

    # Step 3: Get current branch name
    try:
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        current_branch = branch_result.stdout.strip()
        if not current_branch:
            print("❌ Could not determine current branch")
            return 1

        # Check if we're on main/master (shouldn't create PR from default branch)
        if current_branch in ["main", "master"]:
            print(f"❌ Cannot create PR from '{current_branch}' branch")
            print("💡 Create a feature branch first: git checkout -b <branch-name>")
            return 1

    except Exception as e:
        print(f"❌ Failed to get current branch: {e}")
        return 1

    # Step 4: Get the base branch (main or master)
    try:
        # Try to find the default branch
        base_branch = "main"
        default_check = subprocess.run(
            ["git", "rev-parse", "--verify", "origin/main"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if default_check.returncode != 0:
            # Try master
            master_check = subprocess.run(
                ["git", "rev-parse", "--verify", "origin/master"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if master_check.returncode == 0:
                base_branch = "master"
            else:
                print("⚠️  Could not find origin/main or origin/master, using 'main' as base")
    except Exception:
        base_branch = "main"

    debug_print(f"GIT PR: Current branch: {current_branch}, Base branch: {base_branch}")

    # Step 5: Get commits between base and current branch
    try:
        commits_result = subprocess.run(
            ["git", "log", f"origin/{base_branch}..HEAD", "--oneline", "--no-merges"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        commits_log = commits_result.stdout.strip()
        if not commits_log:
            print(f"❌ No commits to create PR for (no difference from origin/{base_branch})")
            print("💡 Make sure you have committed and that commits are not already pushed to the base branch")
            return 1
    except Exception as e:
        print(f"❌ Failed to get commit log: {e}")
        return 1

    # Step 6: Get diff stats
    try:
        diff_stat_result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}..HEAD", "--stat"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        diff_stat = diff_stat_result.stdout.strip()

        # Get full diff (for LLM context)
        diff_result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}..HEAD"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        full_diff = diff_result.stdout
    except Exception as e:
        print(f"❌ Failed to get diff: {e}")
        return 1

    debug_print(f"GIT PR: Got {len(commits_log.splitlines())} commits, diff {len(full_diff)} chars")

    # Step 7: Send request to server to generate PR title and body
    client = AiiCLIClient(config_manager)

    try:
        # Start spinner
        processing_spinner = Spinner("Generating PR content...", stream=sys.stdout)
        await processing_spinner.start()

        # Truncate diff if too long
        max_diff_chars = 6000
        if len(full_diff) > max_diff_chars:
            truncated_diff = full_diff[:max_diff_chars] + "\n\n... (diff truncated)"
        else:
            truncated_diff = full_diff

        user_input = f"""Generate a GitHub Pull Request title and body for the following changes.

Branch: {current_branch} -> {base_branch}

Commits:
{commits_log}

Diff statistics:
{diff_stat}

Full diff:
```
{truncated_diff}
```

Return the response in this EXACT format (no extra text):
TITLE: <pr title in imperative mood, max 72 chars>
BODY:
<pr body with:
- Summary section (2-3 bullet points)
- Test plan section (how to test)
>"""

        # Suppress streaming - we'll display ourselves
        result = await client.execute_command(
            user_input=user_input,
            output_mode="CLEAN",
            spinner=processing_spinner,
            suppress_streaming=True
        )

        await processing_spinner.stop(clear=True)

        if not result.get("success"):
            error_msg = result.get("result") or result.get("message", "Failed to generate PR content")
            print(f"❌ {error_msg}")
            return 1

        # Parse the response
        response_text = result.get("result", "").strip()
        if not response_text:
            print("❌ No PR content generated")
            return 1

        # Parse TITLE and BODY from response
        pr_title = ""
        pr_body = ""

        if "TITLE:" in response_text and "BODY:" in response_text:
            title_start = response_text.find("TITLE:") + 6
            body_start = response_text.find("BODY:")
            pr_title = response_text[title_start:body_start].strip()
            pr_body = response_text[body_start + 5:].strip()
        else:
            # Fallback: use first line as title, rest as body
            lines = response_text.split('\n')
            pr_title = lines[0].strip()
            pr_body = '\n'.join(lines[1:]).strip()

        # Clean up markdown code blocks if present
        if pr_body.startswith("```"):
            lines = pr_body.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            pr_body = '\n'.join(lines).strip()

        # Step 8: Display generated PR content
        print(f"🌿 Branch: {current_branch} → {base_branch}")
        print()
        print("📝 Commits:")
        for line in commits_log.splitlines()[:10]:  # Show first 10 commits
            print(f"  • {line}")
        if len(commits_log.splitlines()) > 10:
            print(f"  ... and {len(commits_log.splitlines()) - 10} more commits")
        print()
        print("📊 Diff Stats:")
        print(diff_stat)
        print()
        print(f"📋 Generated PR Title:")
        print(f"  {pr_title}")
        print()
        print(f"📄 Generated PR Body:")
        print("-" * 50)
        print(pr_body)
        print("-" * 50)

        # Display execution summary
        metadata = result.get("metadata") or {}
        metadata["function_name"] = "git_pr"
        print_session_summary(metadata, output_mode="STANDARD")

        # Step 9: Confirm with user (unless dry-run)
        if dry_run:
            print("\n🔍 Dry run mode - PR not created")
            return 0

        print()
        try:
            user_response = input("Create this Pull Request? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ PR creation cancelled")
            return 1

        if user_response not in ['y', 'yes']:
            print("\n❌ PR creation cancelled")
            return 1

        # Step 10: Push branch if needed
        try:
            # Check if branch is pushed
            tracking_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if tracking_result.returncode != 0:
                # Branch not pushed, push it
                print("📤 Pushing branch to remote...")
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", current_branch],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                if push_result.returncode != 0:
                    print(f"❌ Failed to push branch: {push_result.stderr}")
                    return 1
                print("✅ Branch pushed")
        except Exception as e:
            print(f"⚠️  Could not check/push branch: {e}")

        # Step 11: Create PR using gh CLI
        try:
            # Add signature to PR body
            pr_body_with_sig = pr_body + "\n\n---\n🤖 Generated with [Aii CLI](https://pypi.org/project/aiiware-cli/)"

            pr_create_result = subprocess.run(
                ["gh", "pr", "create",
                 "--title", pr_title,
                 "--body", pr_body_with_sig,
                 "--base", base_branch],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            if pr_create_result.returncode == 0:
                print("\n✅ Pull Request created successfully!")
                # gh pr create outputs the PR URL
                if pr_create_result.stdout:
                    print(f"🔗 {pr_create_result.stdout.strip()}")
                return 0
            else:
                print(f"\n❌ Failed to create PR: {pr_create_result.stderr}")
                return 1

        except Exception as e:
            print(f"\n❌ Failed to create PR: {e}")
            return 1

    except Exception as e:
        print(f"\n❌ Git PR failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await client.close()


def _get_github_username() -> str:
    """Get GitHub username from gh CLI if authenticated."""
    import subprocess
    try:
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _format_github_result(data: dict, tool_name: str) -> str:
    """Format GitHub API response for better readability."""
    lines = []

    # Debug: print keys to understand structure
    import os
    if os.getenv("AII_DEBUG"):
        print(f"[DEBUG] _format_github_result: tool_name={tool_name}")
        print(f"[DEBUG] _format_github_result: data keys={list(data.keys()) if isinstance(data, dict) else type(data)}")
        if isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
            print(f"[DEBUG] First item keys: {list(data['items'][0].keys())}")

    # Handle search_repositories result
    if tool_name == "search_repositories" and "items" in data:
        total = data.get("total_count", 0)
        items = data.get("items", [])
        lines.append(f"📊 Found {total} repositories:\n")

        for i, repo in enumerate(items[:10], 1):  # Show top 10
            name = repo.get("full_name", "Unknown")
            desc_raw = repo.get("description") or "No description"
            desc = desc_raw[:80] if len(desc_raw) > 80 else desc_raw
            url = repo.get("html_url", "")

            # Check if extended stats are available (some GitHub API responses include them)
            has_stats = "stargazers_count" in repo

            if has_stats:
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                lang = repo.get("language") or "N/A"
                lines.append(f"{i}. **{name}** ⭐ {stars:,} 🍴 {forks:,}")
                if desc != "No description":
                    lines.append(f"   {desc}{'...' if len(desc_raw) > 80 else ''}")
                lines.append(f"   ���� {lang} | 🔗 {url}")
            else:
                # Minimal response format (common from GitHub MCP server)
                lines.append(f"{i}. **{name}**")
                if desc != "No description":
                    lines.append(f"   {desc}{'...' if len(desc_raw) > 80 else ''}")
                lines.append(f"   🔗 {url}")
            lines.append("")

        if total > 10:
            lines.append(f"... and {total - 10} more repositories")
        return "\n".join(lines)
    
    # Handle single repository result (get_repository)
    if "full_name" in data and "stargazers_count" in data:
        lines.append(f"📦 **{data.get('full_name')}**")
        lines.append(f"   {data.get('description', 'No description')}")
        lines.append("")
        lines.append(f"⭐ Stars: {data.get('stargazers_count', 0):,}")
        lines.append(f"🍴 Forks: {data.get('forks_count', 0):,}")
        lines.append(f"👁️ Watchers: {data.get('watchers_count', 0):,}")
        lines.append(f"📁 Language: {data.get('language', 'Unknown')}")
        lines.append(f"📅 Created: {data.get('created_at', 'Unknown')[:10]}")
        lines.append(f"🔄 Updated: {data.get('updated_at', 'Unknown')[:10]}")
        lines.append(f"🔗 URL: {data.get('html_url', '')}")
        
        if data.get("topics"):
            lines.append(f"🏷️ Topics: {', '.join(data['topics'][:10])}")
        
        return "\n".join(lines)
    
    # Handle list_issues result
    if isinstance(data, list) and len(data) > 0 and "title" in data[0] and "number" in data[0]:
        lines.append(f"📋 Found {len(data)} issues:\n")
        for i, issue in enumerate(data[:10], 1):
            state_emoji = "🟢" if issue.get("state") == "open" else "🔴"
            lines.append(f"{i}. {state_emoji} #{issue['number']}: {issue['title']}")
            if issue.get("labels"):
                labels = [l.get("name", "") for l in issue["labels"][:3]]
                lines.append(f"   🏷️ {', '.join(labels)}")
        return "\n".join(lines)
    
    # Default: return None to use raw JSON
    return None


async def _handle_client_side_mcp_execution(data: dict, metadata: dict, config_manager: Any, output_mode: str) -> int:
    """
    Handle client-side MCP tool execution.

    When the server returns client_side_execution=true, it means the MCP tool
    needs to be executed locally by the CLI (because MCP servers run on the client).

    Args:
        data: Data dict from server response
        metadata: Metadata dict from server response
        config_manager: ConfigManager instance
        output_mode: Output mode (CLEAN, STANDARD, THINKING)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    from aii.cli.debug import debug_print
    from aii.data.integrations.mcp.client_manager import MCPClientManager
    from aii.data.integrations.mcp.config_loader import MCPConfigLoader
    import time

    user_request = data.get("user_request", "")
    debug_print(f"MCP: Executing client-side MCP for request: {user_request}")

    mcp_client = None
    start_time = time.time()

    try:
        # Initialize MCP client
        config_loader = MCPConfigLoader()
        config_loader.load_configurations()

        if not config_loader.servers:
            print("❌ No MCP servers configured")
            print("💡 Use 'aii mcp catalog' to see available servers")
            print("💡 Use 'aii mcp install <server>' to install one")
            return 1

        mcp_client = MCPClientManager(config_loader=config_loader, enable_health_monitoring=False)
        await mcp_client.initialize()

        # Discover available tools
        all_tools = await mcp_client.discover_all_tools()
        debug_print(f"MCP: Discovered {len(all_tools)} tools across servers")

        if not all_tools:
            print("❌ No MCP tools available")
            print("💡 Check your MCP server configuration with 'aii mcp list'")
            return 1

        # v0.12.0: Use server's LLM for intelligent tool selection
        # Call /v0/mcp/select-tool endpoint to leverage server's LLM capability
        # This follows the LLM-First principle for understanding user intent
        from aii.cli.spinner import Spinner
        import httpx
        import json

        # Build tool info for server
        tools_info = []
        tools_by_name = {}
        for tool in all_tools:
            tools_by_name[tool.name] = tool
            tool_info = {
                "name": tool.name,
                "server_name": tool.server_name,
                "description": tool.description or "",
            }
            if tool.input_schema:
                tool_info["input_schema"] = tool.input_schema
            tools_info.append(tool_info)

        # Get API configuration (default port is 26169 for aii-server)
        api_url = config_manager.get("api.url", "http://localhost:26169")

        # Get API key using same approach as AiiCLIClient
        if hasattr(config_manager, 'get_or_create_api_key'):
            api_key = config_manager.get_or_create_api_key()
        else:
            # Fallback: get from config
            api_keys = config_manager.get("api.keys", [])
            api_key = api_keys[0] if api_keys else "aii_sk_7WyvfQ0PRzufJ1G66Qn8Sm4gW9Tealpo6vOWDDUeiv4"

        # Call server's MCP tool selection endpoint
        debug_print(f"MCP: Calling server for LLM-based tool selection")
        tool_name = None
        tool_args = {}
        # Token metrics from LLM tool selection (for execution summary)
        selection_input_tokens = 0
        selection_output_tokens = 0
        selection_cost = 0.0
        selection_model = None

        try:
            select_url = f"{api_url}/v0/mcp/select-tool"
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            request_payload = {
                "user_request": user_request,
                "tools": tools_info
            }

            # Add model override if configured
            model = config_manager.get("llm.model")
            if model:
                request_payload["model"] = model

            debug_print(f"MCP: Sending tool selection request to {select_url}")

            with httpx.Client(trust_env=False, timeout=30.0) as http_client:
                response = http_client.post(select_url, json=request_payload, headers=headers)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    tool_name = result.get("tool_name")
                    tool_args = result.get("arguments", {})
                    confidence = result.get("confidence", 0)
                    reasoning = result.get("reasoning", "")
                    # Capture token metrics for execution summary
                    selection_input_tokens = result.get("input_tokens", 0)
                    selection_output_tokens = result.get("output_tokens", 0)
                    selection_cost = result.get("cost", 0.0)
                    selection_model = result.get("model", "")
                    debug_print(f"MCP: LLM selected tool: {tool_name} (confidence: {confidence:.2f})")
                    debug_print(f"MCP: Reasoning: {reasoning}")
                    debug_print(f"MCP: Arguments: {tool_args}")
                else:
                    # Server couldn't select a tool
                    error_msg = result.get("error", "Unknown error")
                    reasoning = result.get("reasoning", "")
                    debug_print(f"MCP: Tool selection failed: {error_msg}")
                    if reasoning:
                        debug_print(f"MCP: Reasoning: {reasoning}")
            else:
                debug_print(f"MCP: Server returned status {response.status_code}: {response.text}")

        except httpx.ConnectError:
            debug_print("MCP: Could not connect to server for tool selection")
        except Exception as e:
            debug_print(f"MCP: Tool selection request failed: {e}")

        if tool_name is None:
            print(f"❌ Could not determine appropriate MCP tool for: {user_request}")
            print("\n📦 Available MCP tools:")
            for tool in all_tools[:10]:
                print(f"  • {tool.server_name}/{tool.name}: {(tool.description or '')[:60]}")
            print("\n💡 Try: aii mcp run <server> <tool> [args...]")
            return 1

        debug_print(f"MCP: LLM selected tool: {tool_name} with args: {tool_args}")

        # Post-process: Replace {{GITHUB_USERNAME}} placeholder with actual username
        # The server's LLM is instructed to use this placeholder when user intent requires their own repos
        # This follows LLM-First: the LLM decides when to use the placeholder, CLI just resolves it
        if tool_name == "search_repositories" and "query" in tool_args:
            query = tool_args["query"]
            if "{{GITHUB_USERNAME}}" in query or "{{github_username}}" in query:
                github_username = _get_github_username()
                if github_username:
                    query = query.replace("{{GITHUB_USERNAME}}", github_username)
                    query = query.replace("{{github_username}}", github_username)
                    tool_args["query"] = query
                    debug_print(f"MCP: Replaced username placeholder: {tool_args['query']}")
                else:
                    # Remove the placeholder if we can't get username
                    query = query.replace("user:{{GITHUB_USERNAME}} ", "")
                    query = query.replace("user:{{github_username}} ", "")
                    tool_args["query"] = query
                    debug_print(f"MCP: Could not get GitHub username, removed placeholder")

        # Execute the tool
        print(f"🔧 Executing MCP tool: {tool_name}")
        debug_print(f"MCP: Tool args: {tool_args}")

        result = await mcp_client.call_tool(tool_name, tool_args)

        execution_time = time.time() - start_time

        if result.success:
            print("\n✅ MCP Tool Result:\n")
            for item in result.content:
                if hasattr(item, 'text'):
                    # Try to parse JSON and format it nicely
                    try:
                        import json
                        data = json.loads(item.text)
                        formatted = _format_github_result(data, tool_name)
                        if formatted:
                            print(formatted)
                        else:
                            print(json.dumps(data, indent=2))
                    except (json.JSONDecodeError, TypeError):
                        print(item.text)
                elif hasattr(item, 'data'):
                    import json
                    formatted = _format_github_result(item.data, tool_name)
                    if formatted:
                        print(formatted)
                    else:
                        print(json.dumps(item.data, indent=2))
                else:
                    print(str(item))

            # Print execution summary with token metrics
            if output_mode in ["STANDARD", "THINKING", "VERBOSE"]:
                print()
                print("📊 Execution Summary:")
                # Consolidated format: mcp_tool::tool_name (e.g., mcp_tool::search_repositories)
                summary_parts = [f"✓ mcp_tool::{tool_name}", f"⚡ {execution_time:.1f}s"]

                # Add token metrics if available from tool selection LLM call
                if selection_input_tokens > 0 or selection_output_tokens > 0:
                    total_tokens = selection_input_tokens + selection_output_tokens
                    summary_parts.append(f"🔢 {selection_input_tokens}↗ {selection_output_tokens}↘ ({total_tokens})")

                # Add cost if available
                if selection_cost > 0:
                    if selection_cost < 0.001:
                        cost_str = f"${selection_cost:.6f}"
                    elif selection_cost < 0.01:
                        cost_str = f"${selection_cost:.4f}"
                    else:
                        cost_str = f"${selection_cost:.2f}"
                    summary_parts.append(f"💰 {cost_str}")

                # Add model if available
                if selection_model:
                    # Strip provider prefix for display
                    display_model = selection_model.replace("openai:", "") if selection_model.startswith("openai:") else selection_model
                    summary_parts.append(f"🤖 {display_model}")

                print(" • ".join(summary_parts))

            return 0
        else:
            print(f"\n❌ MCP tool failed: {result.error or 'Unknown error'}")
            return 1

    except Exception as e:
        print(f"\n❌ MCP execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if mcp_client:
            try:
                await mcp_client.shutdown()
            except Exception:
                pass


def cli_main() -> int:
    """CLI entry point (synchronous wrapper)"""
    # v0.11.2: Suppress asyncio subprocess transport cleanup errors at exit
    # These "Event loop is closed" errors occur when MCP subprocess transports
    # are garbage collected after the event loop ends. This is cosmetic only.
    import sys
    import os

    # Store original stderr for potential restoration
    original_stderr = sys.stderr

    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        # User cancelled - handler already displayed message
        # Return error code without showing traceback
        return 1
    finally:
        # Suppress stderr briefly during final garbage collection
        # to hide asyncio transport cleanup errors
        try:
            sys.stderr = open(os.devnull, 'w')
            import gc
            gc.collect()
        except Exception:
            pass
        finally:
            try:
                sys.stderr.close()
            except Exception:
                pass
            sys.stderr = original_stderr


if __name__ == "__main__":
    sys.exit(cli_main())
