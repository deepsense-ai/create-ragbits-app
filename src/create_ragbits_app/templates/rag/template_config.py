"""
Configuration for the RAG template.
"""

from create_ragbits_app.template_config_base import (
    TemplateConfig,
)


class RagTemplateConfig(TemplateConfig):
    """Configuration for a RAG template"""

    name: str = "RAG (Retrieval Augmented Generation)"
    description: str = "Basic RAG (Retrieval Augmented Generation) application"

    questions: list = []


# Create instance of the config to be imported
config = RagTemplateConfig()
