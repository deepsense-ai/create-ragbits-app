# create-ragbits-app

A CLI tool to create new ragbits applications from templates.

## Usage

```bash
# Create a new ragbits application
uvx create-ragbits-app
```

## Available Templates

### **Basic RAG (Retrieval Augmented Generation)**
A simple RAG application that wires together the core pieces:
- Uses Ragbits RAG components with your choice of vector store (`Qdrant` or `pgvector`).
- Document parsing with either `docling` or `unstructured`.
- Includes a CLI tool to ingest and index documents.

Good starting point if you just want a plain RAG setup to build on.

### **Simple Agent**
A minimal agent example that calls an external tool:
- Fetches the latest financial news from [Yahoo Finance](https://finance.yahoo.com/).
- Summarizes the news into a short response.

Useful as a first look at how to connect agents with external APIs.

### **Deep Research Type Agent**
A larger agent system that produces detailed reports:
- Runs a network of agents that split the task into smaller steps.
- Uses [Tavily](https://www.tavily.com/) to search the web for up-to-date information.
- Outputs a structured report with sections and references.

Good example if you want to see how to coordinate multiple agents to solve a complex task.

## UI Configuration

When setting up a new project you can pick how the UI should be included. There are three options:

### **1. Default**
Runs the prebuilt Ragbits Chat UI directly from the package.
- Works right away, no setup required.
- The UI can’t be modified.
- Good for quick tests and demos.

### **2. Copy**
Copies the Ragbits Chat UI source code into a local `ui` directory.
- You can change anything in the UI (components, styles, features).
- The code lives in your repo and evolves with your project.
- Best if you plan to customize or extend the UI.

### **3. Empty**
Creates a new [Vite](https://vitejs.dev/) project with Ragbits libraries already installed.
- Gives you a clean base to build your own UI.
- No predefined components — you decide how to connect to the backend.
- Useful if you want to integrate Ragbits into an existing design system or build something from scratch.

## Creating Custom Templates

Templates are stored in the `templates/` directory. Each template consists of:

1. A directory with the template name
2. A `template_config.py` file with template metadata and questions
3. Template files, with `.j2` extension for files that should be processed as Jinja2 templates

Available variables in templates:
- `project_name`: Name of the project
- `pkg_name`:  Name of the python package
- `ragbits_version`: Latest version of ragbits
- Custom variables from template questions

## Template structure

To create a new template, add a directory under `templates/` with:

1. Template files (ending in `.j2`) - these will be rendered using Jinja2
2. A `template_config.py` file with template metadata and questions

For example, see the `templates/example-template` directory.

### Template Configuration

The `template_config.py` file should define a `TemplateConfig` class that inherits from `TemplateConfig` and creates a `config` instance at the bottom of the file:

```python
from typing import List
from create_ragbits_app.template_config_base import (
    TemplateConfig,
    TextQuestion,
    ListQuestion,
    ConfirmQuestion
)

class ExampleTemplateConfig(TemplateConfig):
    name: str = "My Template Name"
    description: str = "Description of the template"

    questions: List = [
        TextQuestion(
            name="variable_name",
            message="Question to display to user",
            default="Default value"
        ),
        # More questions...
    ]

# Create instance of the config to be imported
config = ExampleTemplateConfig()
```
