"""
UI generation utilities for create-ragbits-app.

This module provides functionality for:
1. Using the default hosted UI on localhost:8000
2. Downloading UI from ragbits GitHub repository for customization
3. Creating UI projects from templates (TypeScript or React)
"""

import pathlib
import shutil
from enum import Enum
from typing import Any

import jinja2
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Template_Type(Enum):
    """Enum for UI template types."""
    VANILLA_TS = "vanilla-ts"
    REACT_TS = "react-ts"


# Path to UI templates
UI_TEMPLATES_DIR = pathlib.Path(__file__).parent / "static" / "ui"


def copy_ui_from_ragbits(project_path: str, context: dict[str, Any]) -> None:
    """Download and copy UI from ragbits GitHub repository."""
    ui_path = pathlib.Path(project_path) / "ui"
    
    import tempfile
    import zipfile
    import urllib.request
    import json
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("[cyan]Downloading UI from ragbits repository...", total=None)
        
        # Get the latest release version
        try:
            # Fetch latest release info from GitHub API
            api_url = "https://api.github.com/repos/deepsense-ai/ragbits/releases/latest"
            with urllib.request.urlopen(api_url) as response:
                release_data = json.loads(response.read().decode())
                latest_version = release_data['tag_name']
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch latest release, using v1.0.0: {e}[/yellow]")
            latest_version = "v1.0.0"
        
        # Download the latest release from GitHub
        github_url = f"https://github.com/deepsense-ai/ragbits/archive/refs/tags/{latest_version}.zip"
        
        try:
            # Create a temporary directory for the download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = pathlib.Path(temp_dir)
                zip_path = temp_path / "ragbits.zip"
                
                # Download the zip file
                urllib.request.urlretrieve(github_url, zip_path)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find the extracted directory (should be ragbits-main)
                extracted_dir = None
                for item in temp_path.iterdir():
                    if item.is_dir() and item.name.startswith("ragbits-"):
                        extracted_dir = item
                        break
                
                if not extracted_dir:
                    console.print("[red]Error: Could not find extracted ragbits directory[/red]")
                    return
                
                # The UI is located at typescript/ui in the root of the repository
                ragbits_ui_source = extracted_dir / "typescript" / "ui"
                
                if not ragbits_ui_source.exists():
                    # Try alternative paths
                    old_paths = [
                        extracted_dir / "ui", # v1.0.0
                    ]
                    
                    for path in old_paths:
                        if path.exists():
                            ragbits_ui_source = path
                            console.print(f"[blue]Found UI at: {path}[/blue]")
                            break
                    else:
                        console.print(f"[red]Error: UI directory not found. Searched paths: {[str(p) for p in old_paths]}[/red]")
                        return
                

                
                # Copy the UI directory
                shutil.copytree(ragbits_ui_source, ui_path, dirs_exist_ok=True)
                
                # Remove node_modules if it exists (will be reinstalled)
                node_modules = ui_path / "node_modules"
                if node_modules.exists():
                    shutil.rmtree(node_modules)
                
                # Remove .vite cache if it exists
                vite_cache = ui_path / ".vite"
                if vite_cache.exists():
                    shutil.rmtree(vite_cache)
                
                # Update package.json to use published versions instead of workspace "*" versions
                package_json_path = ui_path / "package.json"
                if package_json_path.exists():
                    import json
                    with open(package_json_path, "r") as f:
                        package_data = json.load(f)
                    
                    # Replace "*" versions with actual published versions for @ragbits packages
                    if "dependencies" in package_data:
                        if "@ragbits/api-client-react" in package_data["dependencies"]:
                            package_data["dependencies"]["@ragbits/api-client-react"] = "^0.0.3"
                    
                    # Write back the updated package.json
                    with open(package_json_path, "w") as f:
                        json.dump(package_data, f, indent=2)
        
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
        progress.add_task(f"[cyan]Creating UI project...", total=None)
        
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
    ui_type = context.get("ui_type", "default")

    if ui_type == "default":
        console.print("[yellow]Using default hosted UI on localhost:8000[/yellow]")
        console.print("[blue]You can access the UI at http://localhost:8000 when your Ragbits app is running[/blue]")
        return

    elif ui_type == "copy":
        copy_ui_from_ragbits(project_path, context)

    elif ui_type == "create":
        framework = context.get("framework", "vanilla-ts")
        if framework == "vanilla-ts":
            create_typescript_ui(project_path, context)
        elif framework == "react-ts":
            create_react_ui(project_path, context)

    # Add UI setup instructions to the main README
    if ui_type in ["copy", "create"]:
        add_ui_instructions_to_readme(project_path, context)


def add_ui_instructions_to_readme(project_path: str, context: dict[str, Any]) -> None:
    """Add UI setup instructions to the main project README."""
    readme_path = pathlib.Path(project_path) / "README.md"
    if not readme_path.exists():
        return

    # Load and render the UI instructions template
    ui_instructions_template_path = UI_TEMPLATES_DIR / "ui_instructions.md.j2"
    
    if not ui_instructions_template_path.exists():
        console.print(f"[red]Error: UI instructions template not found at {ui_instructions_template_path}[/red]")
        return
    
    with open(ui_instructions_template_path) as f:
        template_content = f.read()
    
    # Add enum values to context for template usage
    template_context = context.copy()
    template_context.update({
        "VANILLA_TS": Template_Type.VANILLA_TS.value,
        "REACT_TS": Template_Type.REACT_TS.value,
    })
    
    # Render template with context
    template = jinja2.Template(template_content)
    ui_instructions = template.render(**template_context)

    # Append to README
    with open(readme_path, "a") as f:
        f.write(ui_instructions)
