"""
Configuration for the RAG template.
"""

# Template metadata
name = "rag"
description = "Basic RAG (Retrieval Augmented Generation) application"

# Questions to ask when creating a project
questions = [
    {
        "type": "text",
        "name": "author_name",
        "message": "Author name:",
        "default": ""
    },
    {
        "type": "list",
        "name": "vector_db",
        "message": "Vector database to use:",
        "choices": ["chroma", "qdrant", "pinecone"],
        "default": "chroma"
    },
    {
        "type": "confirm",
        "name": "include_examples",
        "message": "Include example documents?",
        "default": True
    }
]
