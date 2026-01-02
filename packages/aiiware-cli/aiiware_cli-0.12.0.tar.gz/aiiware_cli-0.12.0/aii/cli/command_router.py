# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Two-tier command routing for AII CLI.

Tier 1: Local commands (no server required)
  - config (init, show, model)
  - mcp (add, remove, list, status)
  - serve (start, stop, status, restart)
  - version, help

Tier 2: AI function commands (server required)
  - All natural language prompts
  - Interactive mode
"""


from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CommandRoute:
    """Command routing result"""
    tier: int  # 1 = local, 2 = server
    command: str  # Command name
    subcommand: Optional[str] = None  # Subcommand (e.g., config init)
    args: Optional[Dict[str, Any]] = None  # Command arguments

    def __post_init__(self):
        """Ensure args is a dict"""
        if self.args is None:
            self.args = {}


class CommandRouter:
    """Route commands to appropriate handlers"""

    # Local commands that don't require server
    LOCAL_COMMANDS = {
        "config": {"init", "show", "model", "list", "set", "validate", "reset", "backup", "provider", "web-search", "oauth"},
        "mcp": {"add", "remove", "list", "status", "enable", "disable", "catalog", "install", "test", "update", "list-tools", "run"},
        "serve": {"start", "stop", "status", "restart"},
        "doctor": set(),
        "template": {"list", "show", "use"},
        "prompt": {"list", "show", "validate", "use"},  # Prompt Library (v0.6.1) - list/show/validate are local, use requires server
        "stats": set(),
        "history": {"list", "search", "continue", "export", "delete"},
        "run": set(),  # Domain operations (v0.6.0) - no subcommands, uses domain/operation args
        "install-completion": set(),
        "uninstall-completion": set(),
        "version": set(),
        "help": set(),
    }

    def route(self, parsed_command: Dict[str, Any]) -> CommandRoute:
        """
        Route command to appropriate tier.

        Args:
            parsed_command: Parsed command from CommandParser

        Returns:
            CommandRoute with tier, command, subcommand, args
        """

        # Check if it's a local command (Tier 1)
        command = parsed_command.get("command")

        if command in self.LOCAL_COMMANDS:
            subcommand = parsed_command.get("subcommand")
            return CommandRoute(
                tier=1,
                command=command,
                subcommand=subcommand,
                args=parsed_command.get("args", {})
            )

        # Check if input_text is actually a local command name
        # (CommandParser treats single words like "help" as input_text)
        # v0.11.2: Also check if input_text STARTS with a local command
        # This handles cases like: aii --host localhost:26169 prompt use dict Happy
        # where argparse puts "prompt use dict Happy" in input_text
        input_text = parsed_command.get("input_text", "")
        if input_text:
            input_text_stripped = input_text.strip()
            # Check exact match first
            if input_text_stripped in self.LOCAL_COMMANDS:
                return CommandRoute(
                    tier=1,
                    command=input_text_stripped,
                    subcommand=None,
                    args=parsed_command.get("args", {})
                )
            # Check if starts with a local command (e.g., "prompt use dict Happy")
            first_word = input_text_stripped.split()[0] if input_text_stripped else ""
            if first_word in self.LOCAL_COMMANDS:
                # Parse the rest as subcommand and additional args
                parts = input_text_stripped.split(maxsplit=2)
                local_command = parts[0]
                subcommand = parts[1] if len(parts) > 1 else None
                # For 'prompt use', the rest after subcommand is prompt_name + extra
                # e.g., "prompt use dict Happy" -> command=prompt, subcommand=use
                # The handler will parse additional args from the original args dict
                extra_parts = parts[2].split() if len(parts) > 2 else []

                # Build args dict with extra parts
                args = parsed_command.get("args", {}) or {}
                if extra_parts:
                    # For prompt use: first extra is prompt_name, rest are extra_vars
                    args["prompt_name"] = extra_parts[0]
                    if len(extra_parts) > 1:
                        args["extra_vars"] = extra_parts[1:]

                return CommandRoute(
                    tier=1,
                    command=local_command,
                    subcommand=subcommand,
                    args=args
                )

        # Otherwise, it's an AI prompt (Tier 2)
        # Extract user input from various possible keys
        user_input = (
            parsed_command.get("user_input") or
            input_text or
            parsed_command.get("prompt") or
            ""
        )

        # Get args safely (handle None)
        extra_args = parsed_command.get("args")
        if extra_args is None:
            extra_args = {}

        return CommandRoute(
            tier=2,
            command="execute",  # Generic execution command
            args={
                "user_input": user_input,
                **extra_args
            }
        )

    def is_local_command(self, command: str) -> bool:
        """
        Check if command is local (Tier 1).

        Args:
            command: Command name

        Returns:
            True if command is local, False if requires server
        """
        return command in self.LOCAL_COMMANDS

    def get_local_subcommands(self, command: str) -> set:
        """
        Get valid subcommands for a local command.

        Args:
            command: Local command name

        Returns:
            Set of valid subcommands (empty set if none)
        """
        return self.LOCAL_COMMANDS.get(command, set())

    def validate_route(self, route: CommandRoute) -> tuple[bool, Optional[str]]:
        """
        Validate a command route.

        Args:
            route: CommandRoute to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Tier 1 validation
        if route.tier == 1:
            if route.command not in self.LOCAL_COMMANDS:
                return False, f"Unknown local command: {route.command}"

            # Check if subcommand is valid (if any)
            if route.subcommand:
                valid_subcommands = self.LOCAL_COMMANDS[route.command]
                if valid_subcommands and route.subcommand not in valid_subcommands:
                    return False, f"Unknown subcommand '{route.subcommand}' for command '{route.command}'"

        # Tier 2 validation
        elif route.tier == 2:
            if not route.args.get("user_input"):
                return False, "No input provided for AI command"

        else:
            return False, f"Invalid tier: {route.tier}"

        return True, None
