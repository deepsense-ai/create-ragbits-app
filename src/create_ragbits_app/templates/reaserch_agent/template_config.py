"""
Configuration for the Deep Research Agent template.
"""

import pathlib

from create_ragbits_app.template_config_base import (
    Question,
    TemplateConfig,
)


class DeepResearchTemplateConfig(TemplateConfig):
    """Configuration for a Deep Research Agent template"""

    name: str = "Deep Research type Agent"
    description: str = "Agentic system that creates comprehensive reports on given subject"

    questions: list[Question] = []

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        # Build dependencies list
        dependencies = [
            f"ragbits>={context.get('ragbits_version')}",
            f"ragbits-agents>={context.get('ragbits_version')}",
            "pydantic-settings",
            "docling",
            "markdownify",
            "tavily-python",
        ]
        return {
            "dependencies": dependencies,
        }

    def get_conditional_directories(self) -> dict[str, str]:
        """Define directories that should be conditionally included."""
        return {}

    def should_include_file(self, file_path: pathlib.Path, context: dict) -> bool:
        """Custom file inclusion logic for Research agent template."""
        # Exclude observability.py.j2 when observability is disabled
        if str(file_path).endswith("observability.py.j2") and not context.get("observability", False):
            return False

        return True


# Create instance of the config to be imported
config = DeepResearchTemplateConfig()
