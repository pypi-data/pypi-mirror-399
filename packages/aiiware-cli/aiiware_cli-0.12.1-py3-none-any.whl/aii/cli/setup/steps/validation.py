# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
API key validation step for setup wizard.

v0.12.0: In Pure CLI architecture, validation is done via the Aii Server.
The CLI no longer has local LLM capability.
"""


import time
from typing import Any

from aii.cli.setup.steps.base import WizardStep, StepResult


class ValidationStep(WizardStep):
    """
    Step 3: Validate API Key.

    v0.12.0: Validation is simplified - we save the config and trust
    the server to validate. The server handles all LLM operations.
    """

    title = "Validate API Key"

    async def execute(self, context: Any) -> StepResult:
        """
        Validate API key format (basic check).

        In v0.12.0 Pure CLI, we don't call LLM locally.
        Full validation happens when the server uses the key.

        Args:
            context: WizardContext with provider and api_key

        Returns:
            StepResult with success=True if key format looks valid
        """
        if not context.provider or not context.api_key:
            return StepResult(
                success=False,
                message="Missing provider or API key",
                fix_suggestion="This is a bug - previous steps should have set these"
            )

        self.console.print("✓ Validating API key format...", style="green")

        # Basic format validation (no LLM call)
        result = self._validate_key_format(context)

        if result.success:
            self.console.print(
                f"✅ API key format is valid for {context.provider}",
                style="green bold"
            )
            self.console.print(
                "   (Full validation will occur on first server request)",
                style="dim"
            )

            # Update context
            context.validation_latency_ms = 0  # No network call made
            context.validation_model = context.selected_model

        return result

    def _validate_key_format(self, context: Any) -> StepResult:
        """
        Basic format validation for API keys.

        Args:
            context: WizardContext

        Returns:
            StepResult with validation outcome
        """
        api_key = context.api_key.strip()
        provider = context.provider

        # Provider-specific format checks
        if provider == "anthropic":
            # Anthropic keys start with "sk-ant-"
            if not api_key.startswith("sk-ant-"):
                return StepResult(
                    success=False,
                    message="Invalid Anthropic API key format",
                    fix_suggestion="Anthropic API keys should start with 'sk-ant-'"
                )
            if len(api_key) < 40:
                return StepResult(
                    success=False,
                    message="API key appears too short",
                    fix_suggestion="Please check you copied the complete API key"
                )

        elif provider == "openai":
            # OpenAI keys start with "sk-"
            if not api_key.startswith("sk-"):
                return StepResult(
                    success=False,
                    message="Invalid OpenAI API key format",
                    fix_suggestion="OpenAI API keys should start with 'sk-'"
                )
            if len(api_key) < 40:
                return StepResult(
                    success=False,
                    message="API key appears too short",
                    fix_suggestion="Please check you copied the complete API key"
                )

        elif provider == "gemini":
            # Google AI keys have various formats
            if len(api_key) < 20:
                return StepResult(
                    success=False,
                    message="API key appears too short",
                    fix_suggestion="Please check you copied the complete API key"
                )

        elif provider == "deepseek":
            # DeepSeek keys start with "sk-"
            if not api_key.startswith("sk-"):
                return StepResult(
                    success=False,
                    message="Invalid DeepSeek API key format",
                    fix_suggestion="DeepSeek API keys should start with 'sk-'"
                )

        # Generic length check
        if len(api_key) < 10:
            return StepResult(
                success=False,
                message="API key is too short",
                fix_suggestion="Please enter a valid API key"
            )

        return StepResult(
            success=True,
            message="API key format validated",
            data={
                "latency_ms": 0,
                "model": context.selected_model or "default",
                "provider": provider
            }
        )
