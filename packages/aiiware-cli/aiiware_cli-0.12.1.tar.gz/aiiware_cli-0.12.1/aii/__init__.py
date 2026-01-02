# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
AII CLI - Command Line Interface for Aii Server (v0.12.0 - Pure CLI)

A feature-rich CLI that communicates with the Aii Server for AI operations.
The CLI handles user interaction, MCP server management, and local operations.

AI/LLM capabilities are provided by the Aii Server (Go or Python).
"""

# Dynamic versioning - reads from pyproject.toml
try:
    from importlib.metadata import version
    __version__ = version("aiiware-cli")
except Exception:
    # Fallback for development/edge cases
    __version__ = "0.12.0"

__author__ = "AII Development Team"

# v0.12.0: Core engine exports removed - AI engine is now in aii-server-py
# CLI is now a pure client that communicates with the server

__all__ = [
    "__version__",
    "__author__",
]