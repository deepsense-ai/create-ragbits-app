"""
Configuration for the Simple Agent template.
"""

import pathlib

from create_ragbits_app.template_config_base import (
    Question,
    TemplateConfig,
)


class SimpleAgentTemplateConfig(TemplateConfig):
    """Configuration for the Simple Agent template"""

    name: str = "Simple Agent"
    description: str = "Simple agentic application that uses tool to check for latest financial news"

    questions: list[Question] = []

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        # Collect all ragbits extras
        ragbits_extras = []

        # Build dependencies list
        dependencies = [
            f"ragbits[{','.join(ragbits_extras)}]>={context.get('ragbits_version')}",
            "ragbits-agents",
            "pydantic-settings",
            "markdownify",
            "httpx",
        ]

        return {
            "dependencies": dependencies,
        }

    def get_conditional_directories(self) -> dict[str, str]:
        """Define directories that should be conditionally included."""
        return {}

    def should_include_file(self, file_path: pathlib.Path, context: dict) -> bool:
        """Custom file inclusion logic for Simple Agent template."""
        return True


# Create instance of the config to be imported
config = SimpleAgentTemplateConfig()
