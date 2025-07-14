"""
Configuration for the Deep Research Agent template.
"""

import pathlib

from create_ragbits_app.template_config_base import (
    MultiSelectQuestion,
    Question,
    TemplateConfig,
)


class DeepResearchTemplateConfig(TemplateConfig):
    """Configuration for a Deep Research Agent template"""

    name: str = "Deep Research type Agent"
    description: str = "Agentic system that creates comprehensive reports on given subject"

    questions: list[Question] = [
        MultiSelectQuestion(
            name="additional_features",
            message="Select additional features you want to include:",
            choices=[
                {
                    "display_name": "Observability stack with Grafana, Tempo, and OpenTelemetry",
                    "value": "observability",
                },
            ],
            default=[],
        ),
    ]

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        additional_features = context.get("additional_features", [])

        # Check for specific features
        observability = "observability" in additional_features

        # Collect all ragbits extras
        ragbits_extras = []

        # Build dependencies list
        dependencies = [
            f"ragbits[{','.join(ragbits_extras)}]>={context.get('ragbits_version')}",
            f"ragbits-agents>={context.get('ragbits_version')}",
            "pydantic-settings",
            "docling",
            "markdownify",
            "tavily-python"
        ]

        # Add observability dependencies
        if observability:
            dependencies.extend(
                [
                    "opentelemetry-api",
                    "opentelemetry-sdk",
                    "opentelemetry-exporter-otlp",
                    "opentelemetry-instrumentation",
                ]
            )

        return {
            "dependencies": dependencies,
            "observability": observability,
        }

    def get_conditional_directories(self) -> dict[str, str]:
        """Define directories that should be conditionally included."""
        return {
            "observability": "observability",
        }

    def should_include_file(self, file_path: pathlib.Path, context: dict) -> bool:
        """Custom file inclusion logic for Research agent template."""
        # Exclude observability.py.j2 when observability is disabled
        if str(file_path).endswith("observability.py.j2") and not context.get("observability", False):
            return False

        return True


# Create instance of the config to be imported
config = DeepResearchTemplateConfig()
