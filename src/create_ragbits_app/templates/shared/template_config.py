"""
Configuration for the RAG template.
"""

import pathlib

from create_ragbits_app.template_config_base import (
    MultiSelectQuestion,
    Question,
    TemplateConfig,
)


class SharedTemplateConfig(TemplateConfig):
    """Configuration for a Shared elements between templates"""

    name: str = "Shared content"
    description: str = "Shared content between templates"

    questions: list[Question] = [
        MultiSelectQuestion(
            name="shared_features",
            message="Select additional features you want to include",
            choices=[
                {
                    "display_name": "Observability stack with Grafana, Tempo, and OpenTelemetry",
                    "value": "observability",
                },
            ],
            default=["observability"],
        ),
    ]

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        shared_features = context.get("shared_features", [])

        # Check for specific features
        observability = "observability" in shared_features

        # Build dependencies list
        dependencies = []

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
        """Custom file inclusion logic for RAG template."""
        # Exclude observability.py.j2 when observability is disabled
        if str(file_path).endswith("observability.py.j2") and not context.get("observability", False):
            return False

        return True


# Create instance of the config to be imported
config = SharedTemplateConfig()
