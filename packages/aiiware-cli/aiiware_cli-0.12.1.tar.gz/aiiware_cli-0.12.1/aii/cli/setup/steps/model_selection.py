# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Model selection step for setup wizard.

v0.12.0: In Pure CLI architecture, model information is static.
The server handles actual model routing.
"""


from typing import Any
from aii.cli.setup.steps.base import WizardStep, StepResult


# v0.12.0: Static model configuration (server handles actual LLM calls)
PROVIDER_MODELS = {
    "anthropic": [
        {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5", "description": "Best balance of speed and quality", "recommended": True},
        {"id": "claude-opus-4-5", "name": "Claude Opus 4.5", "description": "Most capable, for complex tasks"},
        {"id": "claude-3-5-haiku", "name": "Claude 3.5 Haiku", "description": "Fastest, for simple tasks"},
    ],
    "openai": [
        {"id": "gpt-4o", "name": "GPT-4o", "description": "Latest multimodal model", "recommended": True},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Faster, more affordable"},
        {"id": "o1", "name": "O1", "description": "Advanced reasoning"},
    ],
    "gemini": [
        {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "description": "Fast and capable", "recommended": True},
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "description": "Most capable Gemini"},
    ],
    "deepseek": [
        {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "General purpose chat", "recommended": True},
        {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "description": "Advanced reasoning"},
    ],
    "moonshot": [
        {"id": "kimi-k2-turbo-preview", "name": "Kimi K2 Turbo", "description": "Fast and capable", "recommended": True},
    ],
}


class ModelSelectionStep(WizardStep):
    """
    Step 1.5: Choose Model (optional customization).

    Shows available models for the selected provider and lets
    user choose or accept the recommended default.

    v0.12.0: Uses static model list. Server handles actual LLM routing.
    """

    title = "Choose Model (Optional)"

    async def execute(self, context: Any) -> StepResult:
        """
        Display model options and capture selection.

        Args:
            context: WizardContext with provider already selected

        Returns:
            StepResult with success=True if model selected
        """
        if not context.provider:
            return StepResult(
                success=False,
                message="No provider selected",
                fix_suggestion="This is a bug - provider should be selected first"
            )

        # Get models for this provider
        available_models = PROVIDER_MODELS.get(context.provider, [])
        if not available_models:
            # Provider has no model options, use empty (server default)
            context.selected_model = None
            return StepResult(
                success=True,
                message=f"Using default model for {context.provider}"
            )

        # Find recommended model
        default_model = None
        default_index = 0
        for idx, model in enumerate(available_models):
            if model.get("recommended"):
                default_model = model["id"]
                default_index = idx
                break
        if not default_model:
            default_model = available_models[0]["id"]

        # Build choices for interactive menu
        menu_choices = []
        for idx, model in enumerate(available_models, start=1):
            model_desc = model["name"]
            if model.get("recommended"):
                model_desc += " (Recommended)"
            model_desc += f" - {model['description']}"
            menu_choices.append((str(idx), model_desc))

        # Add custom option
        max_choice = len(available_models)
        custom_choice = str(max_choice + 1)
        menu_choices.append((custom_choice, "Custom model ID - Enter your own model ID"))

        # Use interactive menu with arrow keys
        choice = self._interactive_menu(
            "Which model would you like to use?",
            menu_choices,
            default_index=default_index
        )

        # Use default if empty
        if not choice:
            selected_model = default_model
            model_name = next((m["name"] for m in available_models if m["id"] == default_model), "Default")
        elif choice == custom_choice:
            # Custom model ID
            self.console.print("\n Enter custom model ID:", style="yellow bold")
            self.console.print(
                f"   Examples for {context.provider}:",
                style="dim"
            )

            # Show model examples
            examples = ", ".join([m["id"] for m in available_models[:3]])
            self.console.print(f"   {examples}", style="cyan dim")

            custom_model = input("\nModel ID: ").strip()

            if not custom_model:
                self.console.print("\n  No model ID provided, using default", style="yellow")
                selected_model = default_model
                model_name = "Default"
            else:
                selected_model = custom_model
                model_name = f"Custom ({custom_model})"
                self.console.print(
                    f"\n  Using custom model: {custom_model}",
                    style="yellow bold"
                )
                self.console.print(
                    "   Note: Ensure this model ID is valid for your provider",
                    style="dim"
                )
        else:
            # User selected a model from the list
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_models):
                selected_model = available_models[choice_idx]["id"]
                model_name = available_models[choice_idx]["name"]
            else:
                # Invalid choice, use default
                selected_model = default_model
                model_name = "Default"

        # Store in context
        context.selected_model = selected_model

        self.console.print(
            f"\n Selected model: {model_name}",
            style="green bold"
        )

        return StepResult(
            success=True,
            message=f"Selected model: {selected_model}",
            data={"model": selected_model}
        )
