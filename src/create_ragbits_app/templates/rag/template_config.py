"""
Configuration for the RAG template.
"""

from create_ragbits_app.template_config_base import (
    ConfirmQuestion,
    ListQuestion,
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
        ConfirmQuestion(
            name="hybrid_search", message="Do you want to use hybrid search with sparse embeddings?", default=True
        ),
        ConfirmQuestion(
            name="image_description", message="Do you want to describe images with multi-modal LLM?", default=True
        ),
    ]

    def build_context(self, context: dict) -> dict:  # noqa: PLR6301
        """Build additional context based on the answers."""
        vector_store = context.get("vector_store")
        parser = context.get("parser")
        hybrid_search = context.get("hybrid_search")

        # Collect all ragbits extras
        ragbits_extras = []

        if vector_store == "Qdrant":
            ragbits_extras.append("qdrant")
        elif vector_store == "Postgresql with pgvector":
            ragbits_extras.append("pgvector")

        if parser == "docling":
            ragbits_extras.append("docling")

        if hybrid_search:
            ragbits_extras.append("fastembed")

        # Build dependencies list
        dependencies = [
            f"ragbits[{','.join(ragbits_extras)}]=={context.get('ragbits_version')}",
            "pydantic-settings",
        ]

        if parser == "unstructured":
            dependencies.append("unstructured[pdf]>=0.17.2")

        return {"dependencies": dependencies}


# Create instance of the config to be imported
config = RagTemplateConfig()
