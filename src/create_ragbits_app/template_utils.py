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
from typing import Any

import jinja2
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from create_ragbits_app.template_config_base import TemplateConfig

# Get templates directory
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
SHARED_DIR = TEMPLATES_DIR / "shared"

console = Console()


def get_available_templates() -> list[dict]:
    """Get list of available templates from templates directory with their metadata."""
    if not TEMPLATES_DIR.exists():
        return []

    templates = []
    for d in TEMPLATES_DIR.iterdir():
        if d.is_dir() and d.name != "shared":
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


def merge_docker_compose_files(existing_content: str, new_content: str) -> str:
    """Merge two docker-compose YAML files intelligently."""
    try:
        existing_data = yaml.safe_load(existing_content)
        new_data = yaml.safe_load(new_content)

        # Deep merge the YAML data
        merged_data = deep_merge_dicts(existing_data, new_data)

        # Convert back to YAML with proper formatting and document separator
        yaml_content = yaml.dump(merged_data, default_flow_style=False, sort_keys=False)
        # Add the document separator at the beginning
        return f"---\n{yaml_content}"
    except Exception as e:
        console.print(f"[yellow]Warning: Could not merge docker-compose files: {e}[/yellow]")
        # If merging fails, return the new content (override)
        return new_content


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with dict2 values taking precedence."""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = deep_merge_dicts(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # For lists, we'll concatenate and remove duplicates (if they're simple values)
                if all(isinstance(item, (str, int, float)) for item in result[key] + value):
                    # Simple list - remove duplicates while preserving order
                    seen = set()
                    merged_list = []
                    for item in result[key] + value:
                        if item not in seen:
                            seen.add(item)
                            merged_list.append(item)
                    result[key] = merged_list
                else:
                    # Complex list - just concatenate
                    result[key] = result[key] + value
            else:
                # For other types, dict2 value takes precedence
                result[key] = value
        else:
            result[key] = value

    return result


def create_project(template_name: str, project_path: str, context: dict) -> None:
    """Create a new project from the selected template and shared template."""
    template_path = TEMPLATES_DIR / template_name
    shared_template_path = TEMPLATES_DIR / "shared"

    # Create project directory if it doesn't exist
    os.makedirs(project_path, exist_ok=True)

    # Get template configurations
    template_config = get_template_config(template_name)
    shared_config = get_template_config("shared")

    conditional_directories = template_config.get_conditional_directories()
    shared_conditional_directories = shared_config.get_conditional_directories()

    def should_include_path(path: pathlib.Path, base_path: pathlib.Path, config: TemplateConfig) -> bool:
        """Check if a path should be included based on conditional directories and file inclusion logic."""
        rel_path = path.relative_to(base_path)

        # Check conditional directories
        for dir_name, context_var in conditional_directories.items():
            if (str(rel_path).startswith(dir_name) or str(rel_path) == dir_name) and not context.get(
                context_var, False
            ):
                return False

        # Check shared conditional directories if processing shared template
        if base_path == shared_template_path:
            for dir_name, context_var in shared_conditional_directories.items():
                if (str(rel_path).startswith(dir_name) or str(rel_path) == dir_name) and not context.get(
                    context_var, False
                ):
                    return False

        # Check template config's custom file inclusion logic
        return config.should_include_file(rel_path, context)

    def process_template_file(item: pathlib.Path, target_path: pathlib.Path) -> None:
        """Process a single template file."""
        if item.suffix == ".j2":
            with open(item) as f:
                template_content = f.read()

            # Render template with context
            template = jinja2.Template(template_content)
            rendered_content = template.render(**context)

            # Remove .j2 extension for target
            target_path = target_path.with_suffix("")

            # Special handling for docker-compose files
            if (
                target_path.name in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
                and target_path.exists()
            ):
                # Read existing content and merge
                with open(target_path) as f:
                    existing_content = f.read()
                rendered_content = merge_docker_compose_files(existing_content, rendered_content)
                console.print(f"[cyan]Merged docker-compose files at {target_path.relative_to(project_path)}[/cyan]")

            # Write the (possibly merged) content
            with open(target_path, "w") as f:
                f.write(rendered_content)
        else:
            # Create parent directories if they don't exist
            os.makedirs(target_path.parent, exist_ok=True)
            # Simple file copy
            shutil.copy2(item, target_path)

    def process_template_files(source_path: pathlib.Path, config: TemplateConfig) -> None:
        """Process files from a template directory."""
        for item in source_path.glob("**/*"):
            if item.name == "template_config.py":
                continue  # Skip template config file

            # Check if this path should be included
            if not should_include_path(item, source_path, config):
                continue

            # Get relative path from template root
            rel_path = str(item.relative_to(source_path))

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
                process_template_file(item, target_path)

    # Process files with progress indicator
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        # First, process shared template files
        if shared_template_path.exists():
            progress.add_task("[cyan]Processing shared template files...", total=None)
            process_template_files(shared_template_path, shared_config)

        # Then, process selected template files (can override or merge with shared files)
        progress.add_task("[cyan]Creating project structure...", total=None)
        process_template_files(template_path, template_config)

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
