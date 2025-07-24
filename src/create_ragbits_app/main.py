import asyncio
import os

import aiohttp
from aiohttp import ClientTimeout
from jinja2.filters import FILTERS

from create_ragbits_app.template_utils import (
    create_project,
    deep_merge_dicts,
    get_available_templates,
    get_template_config,
    prompt_template_questions,
)
from create_ragbits_app.ui import display_logo
from create_ragbits_app.ui_generator import Template_Type, UI_Type, UIOptions, generate_ui

FILTERS["python_safe"] = lambda value: value.replace("-", "_")


async def get_latest_ragbits_version() -> str:
    """Fetch the latest version of ragbits from PyPI or return a default version if unavailable."""
    url = "https://pypi.org/pypi/ragbits/json"
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=1)) as session, session.get(url) as response:
            response_json = await response.json()
            return response_json["info"]["version"]
    except TimeoutError:
        return "0.10.0"


def prompt_ui_options() -> UIOptions:
    """Prompt user for UI generation options."""
    from inquirer.shortcuts import list_input, text

    ui_choice = list_input(
        "How would you like to handle the UI?",
        choices=[
            "Default - Runs hosted UI on localhost:8000 (no modifications permitted).",
            "Copy - Clones UI from Ragbits source into local 'ui' directory (components can be customized).",
            "Empty - Initializes a blank UI project (full frontend implementation required).",
        ],
    )

    ui_options: UIOptions = {
        "ui_type": UI_Type.DEFAULT
        if "Default" in ui_choice
        else UI_Type.COPY
        if "Copy" in ui_choice
        else UI_Type.CREATE,
        "framework": None,
        "ui_project_name": "ui",
    }

    if ui_options["ui_type"] == UI_Type.CREATE:
        framework_choice = list_input(
            "What framework would you like to use for your UI project?",
            choices=["TypeScript", "TypeScript + React"],
        )
        ui_options["framework"] = Template_Type.REACT_TS if "React" in framework_choice else Template_Type.VANILLA_TS

        # Ask for UI project name
        ui_options["ui_project_name"] = text("UI project name", default=ui_options["ui_project_name"])

    return ui_options


async def run() -> None:
    """Guide the user through template selection and project creation process."""
    version = await get_latest_ragbits_version()
    display_logo(version)

    # Get available templates
    templates = get_available_templates()
    if not templates:
        print("No templates found. Please create templates in the 'templates' directory.")
        return

    # Create template choices with name and description
    template_choices = [f"{t['name']} - {t['description']}" if t["description"] else t["name"] for t in templates]

    # Let user select a template
    from inquirer.shortcuts import list_input, text

    selected_template_str = list_input("Select a template to use (more to come soon!)", choices=template_choices)

    # Get the directory name from the selection
    selected_idx = template_choices.index(selected_template_str)
    selected_template = templates[selected_idx]["dir_name"]

    # Get project name
    project_name = text("Project name", default=f"ragbits-{selected_template}")
    project_path = os.path.abspath(project_name)

    # Check if directory exists and is not empty
    if os.path.exists(project_path) and os.listdir(project_path):
        print(f"Directory '{project_name}' already exists and is not empty. Project creation aborted.")
        return

    # Get UI options
    ui_options = prompt_ui_options()

    # Get template config and prompt for questions
    template_config = get_template_config(selected_template)
    answers = prompt_template_questions(template_config)

    shared_config = get_template_config("shared")
    shared_answers = prompt_template_questions(shared_config)

    # Detect Python version
    import sys

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Create base context for template rendering
    context = {
        "project_name": project_name,
        "pkg_name": project_name.replace("-", "_"),
        "ragbits_version": version,
        "python_version": python_version,
        **answers,
        **ui_options,
        **shared_answers,
    }

    # Build additional context using template config's build_context method
    additional_context = template_config.build_context(context)
    context.update(additional_context)
    # Build additional context using shared template config's build_context method
    additional_shared_context = shared_config.build_context(context)
    context = deep_merge_dicts(context, additional_shared_context)

    # Create project from template
    create_project(selected_template, project_path, context)

    # Generate UI based on user selection
    generate_ui(project_path, context)


def entrypoint() -> None:
    """Serve as the main entry point for the application by running the async workflow."""
    asyncio.run(run())
