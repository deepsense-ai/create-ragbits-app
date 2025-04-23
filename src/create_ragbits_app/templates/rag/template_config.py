"""
Configuration for the RAG template.
"""
from create_ragbits_app.template_config_base import (
    TemplateConfig, 
    ListQuestion,
)
from typing import List


class RagTemplateConfig(TemplateConfig):
    """Configuration for a RAG template"""
    name: str = "RAG (Retrieval Augmented Generation)"
    description: str = "Basic RAG (Retrieval Augmented Generation) application"
    
    questions: List = [
        ListQuestion(
            name="vector_db", 
            message="What Vector database you want to use?",
            choices=[
                "Qdrant",
                "Postgresql with pgvector",
            ]
        ),
        ListQuestion(
            name="parser", 
            message="What parser you want to use parse documents?",
            choices=[
                "unstructured",
                "docling",
            ]
        ),
    ]

# Create instance of the config to be imported
config = RagTemplateConfig()

