"""
Configuration for the RAG template.
"""

import pathlib

from create_ragbits_app.template_config_base import (
    ListQuestion,
    MultiSelectQuestion,
    Question,
    TemplateConfig,
)


class RagTemplateConfig(TemplateConfig):
    """Configuration for a RAG template"""

    name: str = "RAG (Retrieval Augmented Generation)"
    description: str = "Basic RAG (Retrieval Augmented Generation) application"

    questions: list[Question] = [
        ListQuestion(
            name="vector_store",
            message="What Vector database you want to use?",
            choices=[
                "Qdrant",
                "Postgresql with pgvector",
            ],
        ),
        ListQuestion(
            name="parser",
            message="What parser you want to use parse documents?",
            choices=[
                "docling",
                "unstructured",
            ],
        ),
        MultiSelectQuestion(
            name="additional_features",
            message="Select additional features you want to include:",
            choices=[
                {
                    "display_name": "Hybrid search with sparse embeddings",
                    "value": "hybrid_search",
                },
                {
                    "display_name": "Image description with multi-modal LLM",
                    "value": "image_description",
                },
                {
                    "display_name": "Observability stack with Grafana, Tempo, and OpenTelemetry",
                    "value": "observability",
                },
            ],
            default=["hybrid_search", "image_description"],
        ),
    ]

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        vector_store = context.get("vector_store")
        parser = context.get("parser")
        additional_features = context.get("additional_features", [])

        # Check for specific features
        hybrid_search = "hybrid_search" in additional_features
        image_description = "image_description" in additional_features
        observability = "observability" in additional_features

        # Collect all ragbits extras
        ragbits_extras = []

        if vector_store == "Qdrant":
            ragbits_extras.append("qdrant")
        elif vector_store == "Postgresql with pgvector":
            ragbits_extras.append("pgvector")

        if parser == "unstructured":
            ragbits_extras.append("unstructured")

        if hybrid_search:
            ragbits_extras.append("fastembed")

        # Build dependencies list
        dependencies = [
            f"ragbits[{','.join(ragbits_extras)}]=={context.get('ragbits_version')}",
            "pydantic-settings",
        ]

        if parser == "unstructured":
            dependencies.append("unstructured[pdf]>=0.17.2")

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
            "hybrid_search": hybrid_search,
            "image_description": image_description,
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
config = RagTemplateConfig()
