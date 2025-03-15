# create-ragbits-app

A CLI tool to create new ragbits applications from templates.

## Installation

```bash
pip install create-ragbits-app
```

## Usage

```bash
# Create a new ragbits application
create-ragbits-app

# Create a new template
create-ragbits-template
```

## Available Templates

- **rag**: Basic RAG (Retrieval Augmented Generation) application

## Creating Custom Templates

You can create custom templates using the `create-ragbits-template` command.

Templates are stored in the `templates/` directory. Each template consists of:

1. A directory with the template name
2. A `template_config.py` file with template metadata and questions
3. Template files, with `.j2` extension for files that should be processed as Jinja2 templates

Available variables in templates:
- `project_name`: Name of the project
- `ragbits_version`: Latest version of ragbits
- Custom variables from template questions
