"""
Template utility functions for create-ragbits-app.

This module provides functionality for:
1. Finding and loading template configurations
2. Rendering templates with user-provided context
3. Creating new projects from templates

The module works with template directories that contain:
- template_config.py: Configuration for the template
- Template files (*.j2): Jinja2 template files
- Static files: Other files to be copied as-is
"""

import importlib.util
import os
import pathlib
import shutil
import sys

import jinja2
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from create_ragbits_app.template_config_base import TemplateConfig

# Get templates directory
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"

console = Console()


def get_available_templates() -> list[dict]:
    """Get list of available templates from templates directory with their metadata."""
    if not TEMPLATES_DIR.exists():
        return []

    templates = []
    for d in TEMPLATES_DIR.iterdir():
        if d.is_dir():
            # Get template config to extract name and description
            config = get_template_config(d.name)
            templates.append({"dir_name": d.name, "name": config.name, "description": config.description})

    return templates


def get_template_config(template_name: str) -> TemplateConfig:
    """Get template configuration if available."""
    config_path = TEMPLATES_DIR / template_name / "template_config.py"
    if not config_path.exists():
        return {}  # type: ignore[return-value]

    # Use importlib to safely load the module
    spec = importlib.util.spec_from_file_location("template_config", config_path)
    if spec is None or spec.loader is None:
        return {}  # type: ignore[return-value]

    module = importlib.util.module_from_spec(spec)
    sys.modules["template_config"] = module

    try:
        spec.loader.exec_module(module)
        # Look for a 'config' variable which should be an instance of TemplateConfig
        if hasattr(module, "config"):
            return module.config
        return {}  # type: ignore[return-value]
    except Exception as e:
        print(f"Error loading template config: {e}")
        return {}  # type: ignore[return-value]


def prompt_template_questions(template_config: TemplateConfig) -> dict:
    """Prompt user for template-specific questions."""
    return {q.name: q.prompt() for q in template_config.questions}


def create_project(template_name: str, project_path: str, context: dict) -> None:
    """Create a new project from the selected template."""
    template_path = TEMPLATES_DIR / template_name

    # Create project directory if it doesn't exist
    os.makedirs(project_path, exist_ok=True)

    # Get template configuration to check for conditional inclusion logic
    template_config = get_template_config(template_name)
    conditional_directories = template_config.get_conditional_directories()

    def should_include_path(path: pathlib.Path) -> bool:
        """Check if a path should be included based on conditional directories and file inclusion logic."""
        rel_path = path.relative_to(template_path)

        # Check conditional directories
        for dir_name, context_var in conditional_directories.items():
            if str(rel_path).startswith(dir_name) or str(rel_path) == dir_name:  # noqa: SIM102
                # If this path is under a conditional directory, check the context variable
                if not context.get(context_var, False):
                    return False

        # Check template config's custom file inclusion logic
        return template_config.should_include_file(rel_path, context)

    # Process all template files and directories
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("[cyan]Creating project structure...", total=None)

        for item in template_path.glob("**/*"):
            if item.name == "template_config.py":
                continue  # Skip template config file

            # Check if this path should be included
            if not should_include_path(item):
                continue

            # Get relative path from template root
            rel_path = str(item.relative_to(template_path))

            # Process path parts for Jinja templating (for directory names)
            path_parts = []
            for part in pathlib.Path(rel_path).parts:
                if "{{" in part and "}}" in part:
                    # Render the directory name as a template
                    name_template = jinja2.Template(part)
                    rendered_part = name_template.render(**context)
                    path_parts.append(rendered_part)
                else:
                    path_parts.append(part)

            # Construct the target path with processed directory names
            target_rel_path = os.path.join(*path_parts) if path_parts else ""
            target_path = pathlib.Path(project_path) / target_rel_path

            if item.is_dir():
                os.makedirs(target_path, exist_ok=True)
            elif item.is_file():
                # Process as template if it's a .j2 file
                if item.suffix == ".j2":
                    with open(item) as f:
                        template_content = f.read()

                    # Render template with context
                    template = jinja2.Template(template_content)
                    rendered_content = template.render(**context)

                    # Save to target path without .j2 extension
                    target_path = target_path.with_suffix("")
                    with open(target_path, "w") as f:
                        f.write(rendered_content)
                else:
                    # Create parent directories if they don't exist
                    os.makedirs(target_path.parent, exist_ok=True)
                    # Simple file copy
                    shutil.copy2(item, target_path)

    # Display project structure
    console.print("\n[bold green]✓ Project created successfully![/bold green]")
    console.print(f"[bold]Project location:[/bold] {project_path}\n")

    # Create and display project tree
    tree = Tree("[bold blue]Project Structure[/bold blue]")
    project_root = pathlib.Path(project_path)

    def build_tree(node: Tree, path: pathlib.Path) -> None:
        for item in path.iterdir():
            if item.is_dir():
                branch = node.add(f"[bold cyan]{item.name}[/bold cyan]")
                build_tree(branch, item)
            else:
                node.add(f"[green]{item.name}[/green]")

    build_tree(tree, project_root)
    console.print(tree)
