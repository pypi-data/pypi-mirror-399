# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Data & Integration Layer - Storage and external integrations

v0.12.0: LLM providers removed - CLI is pure client, all LLM on server.
"""

from .integrations.mcp.client_manager import MCPClientManager
from .integrations.mcp.models import ToolCallResult

__all__ = [
    "MCPClientManager",
    "ToolCallResult",
]
