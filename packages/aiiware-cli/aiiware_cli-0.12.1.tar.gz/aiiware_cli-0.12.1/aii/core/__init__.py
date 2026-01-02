# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Core Layer - Minimal utilities for Pure CLI architecture

v0.12.0: Most core modules removed. CLI is a pure client.
Only prompt_engine remains for the `aii prompt` command.
"""

from .prompt_engine import (
    PromptInputType,
    TemplateEngine,
    TemplateNotFoundError,
    MissingVariableError,
    Template,
    TemplateCategory,
)

__all__ = [
    "PromptInputType",
    "TemplateEngine",
    "TemplateNotFoundError",
    "MissingVariableError",
    "Template",
    "TemplateCategory",
]
