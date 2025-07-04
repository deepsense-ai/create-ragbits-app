"""
UI generation utilities for create-ragbits-app.

This module provides functionality for:
1. Using the default hosted UI on localhost:8000
2. Downloading UI from ragbits GitHub repository for customization
3. Creating UI projects from templates (TypeScript or React)
"""

import json
import pathlib
import shutil
import tempfile
import urllib.parse
import zipfile
from enum import Enum
from typing import Any, TypedDict

import jinja2
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Template_Type(Enum):
    """Enum for UI template types."""

    VANILLA_TS = "vanilla-ts"
    REACT_TS = "react-ts"


class UI_Type(Enum):
    """Enum for UI types."""

    DEFAULT = "default"
    COPY = "copy"
    CREATE = "create"


class UIOptions(TypedDict):
    """Type definition for UI options dictionary."""

    ui_type: UI_Type
    framework: Template_Type | None
    ui_project_name: str


# Path to UI templates
UI_TEMPLATES_DIR = pathlib.Path(__file__).parent / "static" / "ui"


def _validate_url(url: str) -> bool:
    """Validate that URL is safe to open."""
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc in ("api.github.com", "github.com")


def _get_latest_version() -> str:
    """Get the latest release version from GitHub API."""
    api_url = "https://api.github.com/repos/deepsense-ai/ragbits/releases/latest"

    if not _validate_url(api_url):
        raise ValueError("Invalid API URL")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        release_data = response.json()
        return release_data["tag_name"]
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch latest release, using v1.0.0: {e}[/yellow]")
        return "v1.0.0"


def _download_and_extract_ui(github_url: str, temp_path: pathlib.Path) -> pathlib.Path | None:
    """Download and extract the UI from GitHub."""
    if not _validate_url(github_url):
        console.print("[red]Error: Invalid GitHub URL[/red]")
        return None

    zip_path = temp_path / "ragbits.zip"

    try:
        response = requests.get(github_url, timeout=60, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        console.print(f"[red]Error downloading zip file: {e}[/red]")
        return None

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_path)
    except Exception as e:
        console.print(f"[red]Error extracting zip file: {e}[/red]")
        return None

    # Find the extracted directory
    for item in temp_path.iterdir():
        if item.is_dir() and item.name.startswith("ragbits-"):
            return item

    return None


def _find_ui_directory(extracted_dir: pathlib.Path) -> pathlib.Path | None:
    """Find the UI directory in the extracted repository."""
    # Try the current path first
    ragbits_ui_source = extracted_dir / "typescript" / "ui"
    if ragbits_ui_source.exists():
        return ragbits_ui_source

    # Try alternative paths
    old_paths = [extracted_dir / "ui"]  # v1.0.0

    for path in old_paths:
        if path.exists():
            console.print(f"[blue]Found UI at: {path}[/blue]")
            return path

    console.print(f"[red]Error: UI directory not found. Searched paths: {[str(p) for p in old_paths]}[/red]")
    return None


def _update_package_json(ui_path: pathlib.Path) -> None:
    """Update package.json to use published versions instead of workspace versions."""
    package_json_path = ui_path / "package.json"
    if not package_json_path.exists():
        return

    try:
        with open(package_json_path) as f:
            package_data = json.load(f)

        # Replace "*" versions with actual published versions for @ragbits packages
        if "dependencies" in package_data and "@ragbits/api-client-react" in package_data["dependencies"]:
            package_data["dependencies"]["@ragbits/api-client-react"] = "^0.0.3"

        # Write back the updated package.json
        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not update package.json: {e}[/yellow]")


def copy_ui_from_ragbits(project_path: str, context: dict[str, Any]) -> None:
    """Download and copy UI from ragbits GitHub repository."""
    ui_path = pathlib.Path(project_path) / "ui"

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("[cyan]Downloading UI from ragbits repository...", total=None)

        # Get the latest release version
        latest_version = _get_latest_version()
        github_url = f"https://github.com/deepsense-ai/ragbits/archive/refs/tags/{latest_version}.zip"

        try:
            # Create a temporary directory for the download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = pathlib.Path(temp_dir)

                # Download and extract the UI
                extracted_dir = _download_and_extract_ui(github_url, temp_path)
                if not extracted_dir:
                    return

                # Find the UI directory
                ragbits_ui_source = _find_ui_directory(extracted_dir)
                if not ragbits_ui_source:
                    return

                # Copy the UI directory
                shutil.copytree(ragbits_ui_source, ui_path, dirs_exist_ok=True)

                # Clean up temporary files
                for cleanup_path in [ui_path / "node_modules", ui_path / ".vite"]:
                    if cleanup_path.exists():
                        shutil.rmtree(cleanup_path)

                # Update package.json
                _update_package_json(ui_path)

        except Exception as e:
            console.print(f"[red]Error downloading UI: {e}[/red]")
            return

    console.print(f"[green]✓ UI downloaded and copied to {ui_path}[/green]")


def create_ui_from_template(project_path: str, context: dict[str, Any], template_type: Template_Type) -> None:
    """Create UI project from template files."""
    ui_project_name = context.get("ui_project_name", "ui")
    ui_path = pathlib.Path(project_path) / ui_project_name
    template_path = UI_TEMPLATES_DIR / template_type.value

    if not template_path.exists():
        console.print(f"[red]Error: Template not found at {template_path}[/red]")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("[cyan]Creating UI project...", total=None)

        # Create UI directory
        ui_path.mkdir(parents=True, exist_ok=True)

        # Process all template files
        for item in template_path.glob("**/*"):
            if item.is_file():
                # Get relative path from template root
                rel_path = item.relative_to(template_path)

                # Process path parts for Jinja templating (for directory names)
                path_parts = []
                for part in rel_path.parts:
                    if "{{" in part and "}}" in part:
                        # Render the directory name as a template
                        name_template = jinja2.Template(part)
                        rendered_part = name_template.render(**context)
                        path_parts.append(rendered_part)
                    else:
                        path_parts.append(part)

                # Construct the target path with processed directory names
                target_rel_path = pathlib.Path(*path_parts) if path_parts else pathlib.Path()
                target_path = ui_path / target_rel_path

                # Create parent directories if they don't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)

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
                    # Simple file copy
                    shutil.copy2(item, target_path)

    console.print(f"[green]✓ UI project created at {ui_path}[/green]")


def create_typescript_ui(project_path: str, context: dict[str, Any]) -> None:
    """Create an empty TypeScript UI project."""
    create_ui_from_template(project_path, context, Template_Type.VANILLA_TS)


def create_react_ui(project_path: str, context: dict[str, Any]) -> None:
    """Create an empty React UI project."""
    create_ui_from_template(project_path, context, Template_Type.REACT_TS)


def generate_ui(project_path: str, context: dict[str, Any]) -> None:
    """Generate UI based on the selected option."""
    ui_type = context.get("ui_type", UI_Type.DEFAULT)

    if ui_type == UI_Type.DEFAULT:
        console.print("[yellow]Using default hosted UI on localhost:8000[/yellow]")
        console.print("[blue]You can access the UI at http://localhost:8000 when your Ragbits app is running[/blue]")
        return

    elif ui_type == UI_Type.COPY:
        copy_ui_from_ragbits(project_path, context)

    elif ui_type == UI_Type.CREATE:
        framework = context.get("framework", Template_Type.VANILLA_TS)
        if framework == Template_Type.VANILLA_TS:
            create_typescript_ui(project_path, context)
        elif framework == Template_Type.REACT_TS:
            create_react_ui(project_path, context)
