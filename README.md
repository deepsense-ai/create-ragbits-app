# create-ragbits-app

A CLI tool to create new ragbits applications from templates.

## Usage

```bash
# Create a new ragbits application
uvx create-ragbits-app
```

## Available Templates

- **rag**: Basic RAG (Retrieval Augmented Generation) application

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
from create_ragbits_app.template_config_base import (
    BaseTemplateConfig,
    TextQuestion,
    ListQuestion,
    ConfirmQuestion
)

class TemplateConfig(TemplateConfig):
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
config = TemplateConfig()
```
